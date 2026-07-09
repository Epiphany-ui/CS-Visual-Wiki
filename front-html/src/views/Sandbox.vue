<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { generationApi } from '@/api/generation'
import { videosApi } from '@/api/videos'
import { useSSE } from '@/composables/useSSE'
import { useTaskStore } from '@/stores/task'
import type { SSETaskEvent, SSEDoneEvent } from '@/types/api'
import { ElMessage } from 'element-plus'
import CodeEditor from '@/components/common/CodeEditor.vue'

const route = useRoute()
const router = useRouter()
const taskStore = useTaskStore()
const { connect, disconnect } = useSSE()

const requirement = ref('')
const code = ref('')
const videoPath = ref('')
const videoUrl = ref('')
const generating = ref(false)
const fixing = ref(false)
const progress = ref(0)
const progressMsg = ref('')
const logOutput = ref('')
const savedToGallery = ref(false)
const currentFilename = ref('')
let _activeTaskId = ''
let _progressTimer: ReturnType<typeof setInterval> | null = null
let _progressTarget = 0

// 平滑进度条：不跟随 tqdm 跳动，自动递增到目标值
function startSmoothProgress() {
  stopSmoothProgress()
  _progressTarget = 5
  _progressTimer = setInterval(() => {
    if (progress.value < _progressTarget) {
      progress.value = Math.round(Math.min(progress.value + 1, _progressTarget))
    }
    // 缓慢自动增长，最高到 92%
    if (_progressTarget < 92) {
      _progressTarget = Math.round((_progressTarget + 0.5) * 10) / 10
    }
  }, 200)
}

function setProgressStage(pct: number, msg: string) {
  _progressTarget = Math.max(_progressTarget, pct)
  progressMsg.value = msg
}

function stopSmoothProgress() {
  if (_progressTimer) { clearInterval(_progressTimer); _progressTimer = null }
  _progressTarget = 0
}

function getLastError(): string {
  const lines = logOutput.value.split('\n')
  const errStart = lines.findIndex(l => l.includes('Traceback') || l.includes('Error') || l.includes('❌'))
  if (errStart >= 0) return lines.slice(errStart).join('\n')
  return logOutput.value.slice(-500)
}

function restoreTaskFromSession() {
  const tid = sessionStorage.getItem('cs:active-task')
  if (!tid) return

  // 先检查任务是否已经完成（通过 taskStore 缓存的状态）
  const cached = taskStore.activeTask
  if (cached?.state === 'SUCCESS') {
    // 任务已完成，直接恢复 UI，不需要重连 SSE
    progress.value = 100
    generating.value = false
    if ((cached as any).code) code.value = (cached as any).code
    if (cached.videoPath) {
      videoPath.value = cached.videoPath
      videoUrl.value = `http://localhost:8000${cached.videoPath}`
      currentFilename.value = cached.videoPath.replace('/videos/', '')
    }
    return
  }
  if (cached?.state === 'FAILURE') {
    generating.value = false
    progressMsg.value = cached.message || '任务失败'
    return
  }

  // 任务仍在进行中，重连 SSE
  _activeTaskId = tid
  generating.value = true
  startSmoothProgress()
  // 从缓存的进度开始，不从 0 开始
  if (cached?.progress) _progressTarget = cached.progress
  progressMsg.value = cached?.message || '恢复中...'
  code.value = (cached as any)?.code || ''

  connect(tid, (data) => {
    if ((data as SSEDoneEvent).type === 'done') {
      stopSmoothProgress(); progress.value = 100; generating.value = false; disconnect(); return
    }
    const evt = data as SSETaskEvent
    progressMsg.value = evt.message
    if ((evt as any).code) code.value = (evt as any).code
    if (evt.video_path) {
      videoPath.value = evt.video_path
      videoUrl.value = `http://localhost:8000${evt.video_path}`
      currentFilename.value = evt.video_path.replace('/videos/', '')
      const works = JSON.parse(localStorage.getItem('cs:my-works') || '[]')
      if (!works.includes(currentFilename.value)) {
        works.unshift(currentFilename.value)
        localStorage.setItem('cs:my-works', JSON.stringify(works.slice(0, 50)))
      }
    }
    if (evt.log) logOutput.value += evt.log + '\n'
    taskStore.updateProgress(evt)
    if (evt.state === 'SUCCESS') {
      stopSmoothProgress(); progress.value = 100; generating.value = false; disconnect()
      sessionStorage.removeItem('cs:active-task')
    } else if (evt.state === 'FAILURE') {
      stopSmoothProgress(); generating.value = false; disconnect()
      sessionStorage.removeItem('cs:active-task')
    }
  }, () => { stopSmoothProgress(); generating.value = false })
}

async function handleSaveToGallery() {
  const fn = currentFilename.value
  if (!fn) return
  try {
    const res = await videosApi.saveVideo(fn)
    savedToGallery.value = res.data.data?.saved ?? false
    ElMessage.success(savedToGallery.value ? '已收藏' : '已取消收藏')
  } catch {
    ElMessage.error('操作失败')
  }
}

function handleGenerate() {
  if (!requirement.value.trim()) return
  startAsyncTask(() => generationApi.asyncGenerate(requirement.value.trim()))
}

function handleRender() {
  if (!code.value.trim()) { ElMessage.warning('请先输入或生成 Manim 代码'); return }
  startAsyncTask(() => generationApi.asyncRender(code.value))
}

async function handleFixCode() {
  if (!code.value.trim()) return
  const err = getLastError()
  if (!err.trim()) { ElMessage.warning('请先渲染代码获取错误信息'); return }
  fixing.value = true
  try {
    const res = await generationApi.fixCode(code.value, err)
    const fixed = res.data.data?.code
    if (fixed && fixed !== code.value) {
      code.value = fixed
      ElMessage.success('代码已修复')
    } else {
      ElMessage.info('AI 未找到可修复的问题')
    }
  } catch {
    ElMessage.error('修复失败，请重试')
  } finally { fixing.value = false }
}

async function startAsyncTask(apiCall: () => Promise<any>) {
  generating.value = true; videoPath.value = ''
  logOutput.value = ''; savedToGallery.value = false; currentFilename.value = ''
  startSmoothProgress()
  try {
    const res = await apiCall()
    const taskId = res.data.data?.task_id
    if (taskId) {
      _activeTaskId = taskId
      sessionStorage.setItem('cs:active-task', taskId)
      taskStore.startTask(taskId)
      connect(taskId, (data) => {
        if ((data as SSEDoneEvent).type === 'done') {
          stopSmoothProgress(); progress.value = 100; generating.value = false; disconnect(); return
        }
        const evt = data as SSETaskEvent
        progressMsg.value = evt.message
        if ((evt as any).code) code.value = (evt as any).code
        if (evt.video_path) {
          videoPath.value = evt.video_path
          videoUrl.value = `http://localhost:8000${evt.video_path}`
          currentFilename.value = evt.video_path.replace('/videos/', '')
          const works = JSON.parse(localStorage.getItem('cs:my-works') || '[]')
          if (!works.includes(currentFilename.value)) {
            works.unshift(currentFilename.value)
            localStorage.setItem('cs:my-works', JSON.stringify(works.slice(0, 50)))
          }
        }
        if (evt.log) logOutput.value += evt.log + '\n'
        taskStore.updateProgress(evt)
        if (evt.state === 'SUCCESS') {
          stopSmoothProgress(); progress.value = 100
          generating.value = false; disconnect()
          sessionStorage.removeItem('cs:active-task')
        } else if (evt.state === 'FAILURE') {
          stopSmoothProgress()
          generating.value = false; disconnect()
          sessionStorage.removeItem('cs:active-task')
        }
      }, () => { stopSmoothProgress(); generating.value = false })
    }
  } catch { stopSmoothProgress(); generating.value = false }
}

onMounted(() => {
  const prompt = route.query.prompt as string
  if (prompt) requirement.value = prompt
  restoreTaskFromSession()
})
onUnmounted(() => {
  // 清理旧的 SSE 连接和进度定时器
  // 任务状态保存在 sessionStorage + taskStore 中，回来时 restoreTaskFromSession 会重连
  disconnect()
  stopSmoothProgress()
})
</script>

<template>
  <div class="sandbox-page">
    <div class="sb-toolbar">
      <h1 class="sb-title"><el-icon :size="22"><EditPen /></el-icon> 动画沙箱</h1>
      <div class="sb-actions">
        <el-button :loading="generating" type="primary" round @click="handleGenerate">
          <el-icon><MagicStick /></el-icon> AI 生成
        </el-button>
        <el-button :loading="generating" round @click="handleRender" :disabled="!code">
          <el-icon><VideoPlay /></el-icon> 渲染
        </el-button>
      </div>
    </div>

    <div v-if="generating" class="progress-bar-wrap">
      <el-progress :percentage="progress" :color="'#7c3aed'" :stroke-width="6" />
      <span class="progress-msg">{{ progressMsg }}</span>
    </div>

    <div class="sb-panels">
      <!-- 左：AI 对话 -->
      <div class="sb-panel panel-chat">
        <div class="panel-header"><el-icon><ChatDotRound /></el-icon> AI 对话助手</div>
        <div class="panel-body">
          <el-input v-model="requirement" type="textarea" :rows="6"
            placeholder="描述你想要的动画效果...&#10;&#10;例如：&#10;• 冒泡排序算法可视化&#10;• 傅里叶级数分解方波动画" class="req-input" />
          <div class="quick-prompts">
            <span class="qp-label">快速模板：</span>
            <el-tag v-for="t in ['快速排序','Dijkstra算法','傅里叶变换','正态分布','二叉树遍历']" :key="t"
              size="small" class="qp-tag" @click="requirement = t + '动画可视化'">{{ t }}</el-tag>
          </div>
        </div>
      </div>

      <!-- 中：代码编辑器 -->
      <div class="sb-panel panel-code">
        <div class="panel-header">
          <el-icon><Document /></el-icon> Manim 代码
          <el-button link size="small" :loading="fixing" @click="handleFixCode" style="margin-left:auto">
            <el-icon><MagicStick /></el-icon> AI 修复
          </el-button>
        </div>
        <div class="panel-body code-panel-body">
          <CodeEditor v-model="code" :readonly="false" />
        </div>
      </div>

      <!-- 右：预览 -->
      <div class="sb-panel panel-preview">
        <div class="panel-header"><el-icon><VideoCamera /></el-icon> 预览</div>
        <div class="panel-body preview-body">
          <div v-if="videoUrl" class="video-player">
            <video :src="videoUrl" controls autoplay loop class="preview-video" />
            <div style="display:flex;gap:8px;margin-top:8px">
              <el-button :type="savedToGallery ? 'warning' : 'default'" size="small" round @click="handleSaveToGallery">
                <el-icon><StarFilled v-if="savedToGallery" /><Star v-else /></el-icon>
                {{ savedToGallery ? '已收藏' : '收藏' }}
              </el-button>
            </div>
          </div>
          <div v-else class="preview-empty">
            <el-icon :size="48"><VideoCamera /></el-icon>
            <p>生成动画后将在此处预览</p>
          </div>
        </div>
        <div v-if="logOutput" class="panel-log"><pre>{{ logOutput }}</pre></div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.sandbox-page { padding: var(--space-lg); max-width: 1500px; margin: 0 auto; }
.sb-toolbar { display: flex; align-items: center; justify-content: space-between; margin-bottom: var(--space-md); }
.sb-title { font-size: 1.3rem; font-weight: 800; display: flex; align-items: center; gap: var(--space-sm); background: var(--gradient-primary); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.sb-actions { display: flex; gap: var(--space-sm); }
.progress-bar-wrap { margin-bottom: var(--space-md); display: flex; align-items: center; gap: var(--space-md); background: var(--bg-card); padding: var(--space-sm) var(--space-md); border-radius: var(--radius-md); border: 1px solid var(--border-color); animation: scale-in 0.3s var(--ease-bounce) both; }
.progress-bar-wrap :deep(.el-progress-bar__outer) { background: var(--bg-secondary); overflow: hidden; }
.progress-bar-wrap :deep(.el-progress-bar__inner) { background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue), var(--accent-cyan)); background-size: 200% 100%; animation: gradient-shift 2s linear infinite; }
.progress-msg { color: var(--text-secondary); font-size: 0.85rem; white-space: nowrap; }
.preview-video { animation: scale-in 0.5s var(--ease-spring) both; max-width: 100%; max-height: 100%; border-radius: var(--radius-md); }
.sb-panels { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: var(--space-md); height: calc(100vh - 180px); }
.sb-panel { display: flex; flex-direction: column; border: 1px solid var(--border-color); border-radius: var(--radius-lg); background: var(--bg-card); overflow: hidden; }
.panel-header { padding: 10px var(--space-md); font-size: 0.85rem; font-weight: 600; color: var(--text-secondary); display: flex; align-items: center; gap: 6px; border-bottom: 1px solid var(--border-color); background: var(--bg-secondary); }
.panel-body { flex: 1; overflow: auto; padding: var(--space-md); }
.code-panel-body { padding: 0; }
.req-input :deep(.el-textarea__inner) { background: transparent; color: var(--text-primary); border: 1px solid var(--border-color); font-size: 0.9rem; resize: none; }
.quick-prompts { margin-top: var(--space-md); }
.qp-label { font-size: 0.78rem; color: var(--text-tertiary); }
.qp-tag { cursor: pointer; margin: 3px; background: var(--bg-card-hover) !important; border-color: var(--border-color) !important; color: var(--text-secondary); transition: all var(--transition-fast); }
.qp-tag:hover { border-color: var(--accent-purple) !important; color: var(--accent-purple-light); }
.preview-body { display: flex; align-items: center; justify-content: center; flex-direction: column; }
.preview-empty { text-align: center; color: var(--text-tertiary); }
.preview-empty .el-icon { margin-bottom: var(--space-md); opacity: 0.3; }
.preview-empty p { font-size: 0.9rem; }
.panel-log { max-height: 120px; overflow-y: auto; padding: var(--space-sm) var(--space-md); background: var(--bg-secondary); border-top: 1px solid var(--border-color); }
.panel-log pre { font-family: var(--font-mono); font-size: 0.72rem; color: var(--text-tertiary); white-space: pre-wrap; margin: 0; }
@media (max-width: 1024px) { .sb-panels { grid-template-columns: 1fr; height: auto; } .sb-panel { min-height: 300px; } }
</style>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRoute } from 'vue-router'
import { generationApi } from '@/api/generation'
import { videosApi } from '@/api/videos'
import { useSSE } from '@/composables/useSSE'
import { useTaskStore } from '@/stores/task'
import type { SSETaskEvent, SSEDoneEvent } from '@/types/api'
import { ElMessage } from 'element-plus'
import CodeEditor from '@/components/common/CodeEditor.vue'

const route = useRoute()
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
const publishDialogVisible = ref(false)
const publishDesc = ref('')
let _activeTaskId = ''
let _progressTimer: ReturnType<typeof setInterval> | null = null
let _progressTarget = 0
let _taskCompleted = false // 防止 onerror 覆盖已完成的结果

function startSmoothProgress(fromPct = 0) {
  stopSmoothProgress()
  progress.value = fromPct
  _progressTarget = Math.max(fromPct, 5)
  _taskCompleted = false
  _progressTimer = setInterval(() => {
    if (progress.value < _progressTarget) {
      progress.value = Math.round(progress.value + 1)
    }
    if (_progressTarget < 92) {
      _progressTarget += 0.3
    }
  }, 300)
}

function stopSmoothProgress() {
  if (_progressTimer) { clearInterval(_progressTimer); _progressTimer = null }
  _progressTarget = 0
}

function onTaskDone(success: boolean) {
  _taskCompleted = true
  stopSmoothProgress()
  progress.value = success ? 100 : progress.value
  generating.value = false
  disconnect()
  localStorage.removeItem('cs:active-task')
}

function onSSEEvent(evt: SSETaskEvent) {
  progressMsg.value = evt.message || progressMsg.value
  if ((evt as any).code) code.value = (evt as any).code
  if (evt.video_path) {
    videoPath.value = evt.video_path
    videoUrl.value = `http://localhost:8000${evt.video_path}`
    currentFilename.value = evt.video_path.replace('/videos/', '')
    // 加入"我的作品"（localStorage + 服务端双写）
    try {
      const works = JSON.parse(localStorage.getItem('cs:my-works') || '[]')
      if (!works.includes(currentFilename.value)) {
        works.unshift(currentFilename.value)
        localStorage.setItem('cs:my-works', JSON.stringify(works.slice(0, 50)))
      }
      // 同步到服务端（跨设备持久化）
      const name = localStorage.getItem('cs:nickname') || localStorage.getItem('username') || ''
      if (name) {
        videosApi.syncMyWorks(name, [currentFilename.value]).catch(() => {})
      }
    } catch { /* ignore */ }
  }
  if (evt.log) logOutput.value += evt.log + '\n'
  taskStore.updateProgress(evt)
  if (evt.state === 'SUCCESS') {
    onTaskDone(true)
  } else if (evt.state === 'FAILURE') {
    onTaskDone(false)
  }
}

function onSSEError() {
  if (_taskCompleted) return // SSE 关闭触发的 onerror，忽略
  stopSmoothProgress()
  generating.value = false
}

// --- 恢复 ---
function restoreTaskFromSession() {
  const tid = localStorage.getItem('cs:active-task')
  if (!tid) return

  const cached = taskStore.activeTask
  if (cached?.state === 'SUCCESS') {
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
  // 任务可能仍在运行
  if (cached?.state === 'PENDING' || cached?.state === 'STARTED' || cached?.state === 'RENDERING') {
    _activeTaskId = tid
    generating.value = true
    startSmoothProgress(cached.progress || 0)
    progressMsg.value = cached.message || '恢复中...'
    code.value = (cached as any)?.code || ''
    connect(tid, (data) => {
      if ((data as SSEDoneEvent).type === 'done') { onTaskDone(true); return }
      const evt = data as SSETaskEvent
      if (evt.state === 'UNKNOWN') {
        stopSmoothProgress(); generating.value = false; disconnect()
        localStorage.removeItem('cs:active-task')
        progressMsg.value = '任务已过期，请重新开始'
        return
      }
      onSSEEvent(evt)
    }, onSSEError)
    return
  }
  // 其他状态：清理
  localStorage.removeItem('cs:active-task')
}

// --- 操作 ---
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
    if (fixed && fixed !== code.value) { code.value = fixed; ElMessage.success('代码已修复') }
    else { ElMessage.info('AI 未找到可修复的问题') }
  } catch { ElMessage.error('修复失败，请重试') }
  finally { fixing.value = false }
}

function openPublishDialog() {
  publishDesc.value = requirement.value.slice(0, 200)
  publishDialogVisible.value = true
}

async function handlePublish() {
  const title = code.value.slice(0, 50).match(/class\s+(\w+)/)?.[1] || requirement.value.slice(0, 30) || '未命名作品'
  const token = localStorage.getItem('token')
  if (!token) { ElMessage.warning('请先登录再发布'); return }
  try {
    const body = new URLSearchParams()
    body.append('workTitle', title)
    body.append('workDesc', publishDesc.value)
    body.append('isPublic', 'true')
    body.append('code', code.value)
    body.append('previewUrl', videoUrl.value || '')
    const res = await fetch('/api/v1/work/publish', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body.toString(),
    })
    const data = await res.json()
    if (data.code === 200) {
      publishDialogVisible.value = false
      ElMessage.success('已发布到社区！')
    } else {
      ElMessage.error(data.msg || '发布失败')
    }
  } catch (e) { ElMessage.error('发布失败：' + (e as Error).message) }
}

async function handleSaveToGallery() {
  if (!currentFilename.value) return
  try {
    const res = await videosApi.saveVideo(currentFilename.value)
    savedToGallery.value = res.data.data?.saved ?? false
    ElMessage.success(savedToGallery.value ? '已收藏' : '已取消收藏')
  } catch { ElMessage.error('操作失败') }
}

function getLastError(): string {
  const lines = logOutput.value.split('\n')
  const errStart = lines.findIndex(l => l.includes('Traceback') || l.includes('Error') || l.includes('❌'))
  if (errStart >= 0) return lines.slice(errStart).join('\n')
  return logOutput.value.slice(-500)
}

// --- 异步任务核心 ---
async function startAsyncTask(apiCall: () => Promise<any>) {
  // 重置所有状态
  generating.value = true
  progress.value = 0
  progressMsg.value = ''
  videoPath.value = ''
  videoUrl.value = ''
  logOutput.value = ''
  savedToGallery.value = false
  currentFilename.value = ''
  // 不重置 code — 保留用户编辑的内容
  startSmoothProgress(0)

  try {
    const res = await apiCall()
    const taskId = res.data.data?.task_id
    if (!taskId) { generating.value = false; return }

    _activeTaskId = taskId
    localStorage.setItem('cs:active-task', taskId)
    try {
      const pending = JSON.parse(localStorage.getItem('cs:pending-tasks') || '[]')
      if (!pending.includes(taskId)) { pending.unshift(taskId); localStorage.setItem('cs:pending-tasks', JSON.stringify(pending.slice(0, 20))) }
    } catch { /* ignore */ }
    taskStore.startTask(taskId)

    connect(taskId, (data) => {
      if ((data as SSEDoneEvent).type === 'done') { onTaskDone(true); return }
      onSSEEvent(data as SSETaskEvent)
    }, onSSEError)
  } catch { stopSmoothProgress(); generating.value = false }
}

onMounted(() => {
  const prompt = route.query.prompt as string
  if (prompt) {
    // 从百科/首页跳转过来 → 清空旧任务，开始新的
    requirement.value = prompt
    localStorage.removeItem('cs:active-task')
  } else {
    // 正常导航返回 → 恢复之前的状态
    restoreTaskFromSession()
  }
})

onUnmounted(() => {
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
              <el-button size="small" type="success" round @click="openPublishDialog">
                <el-icon><Upload /></el-icon> 发布到社区
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

    <!-- 发布到社区弹窗 -->
    <el-dialog v-model="publishDialogVisible" title="发布到社区" width="480px">
      <el-input v-model="publishDesc" type="textarea" :rows="4" placeholder="写一段描述介绍你的作品..." />
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePublish">发布</el-button>
      </template>
    </el-dialog>
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

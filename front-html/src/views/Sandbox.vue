<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { generationApi } from '@/api/generation'
import { videosApi } from '@/api/videos'
import { useSSE } from '@/composables/useSSE'
import { useCurrentUser } from '@/composables/useCurrentUser'
import { useTaskStore } from '@/stores/task'
import type { SSETaskEvent, SSEDoneEvent } from '@/types/api'
import { ElMessage, ElMessageBox } from 'element-plus'
import CodeEditor from '@/components/common/CodeEditor.vue'
import CanvasTypewriter from '@/components/common/CanvasTypewriter.vue'

const route = useRoute()
const taskStore = useTaskStore()
const { connect, disconnect } = useSSE()
const { username, token } = useCurrentUser()

const requirement = ref('')
const code = ref('')
const typingActive = ref(false) // Canvas typewriter 动画进行中
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
const publishToGallery = ref(false)
const renderQuality = ref(localStorage.getItem('cs:render-quality') || '-qm')
let _activeTaskId = ''
let _aiChanging = false   // 标记正在由 AI 修改代码（触发 typewriter）
let _progressTimer: ReturnType<typeof setInterval> | null = null
let _progressTarget = 0
let _taskCompleted = false // 防止 onerror 覆盖已完成的结果

// ========== Canvas Typewriter 画笔写入效果 ==========
function onCanvasDone() {
  typingActive.value = false
}

// 监听 AI 带来的代码变更 → 触发 Canvas typewriter
watch(code, (newVal, oldVal) => {
  if (_aiChanging && newVal && newVal !== oldVal) {
    _aiChanging = false
    typingActive.value = true
  }
})

// ========== 状态持久化：离开再回来界面不变（按用户隔离） ==========
const STATE_KEY = computed(() => {
  const u = username.value || 'anon'
  return `cs:sandbox-state:${u}`
})

function saveState() {
  try {
    const state = {
      requirement: requirement.value,
      code: code.value,
      videoPath: videoPath.value,
      videoUrl: videoUrl.value,
      currentFilename: currentFilename.value,
      savedToGallery: savedToGallery.value,
      logOutput: logOutput.value,
      progress: progress.value,
      progressMsg: progressMsg.value,
      activeTaskId: _activeTaskId,
    }
    sessionStorage.setItem(STATE_KEY.value, JSON.stringify(state))
  } catch { /* ignore */ }
}

function restoreState() {
  try {
    const raw = sessionStorage.getItem(STATE_KEY.value)
    if (!raw) return
    const state = JSON.parse(raw)
    requirement.value = state.requirement || ''
    code.value = state.code || ''
    videoPath.value = state.videoPath || ''
    videoUrl.value = state.videoUrl || ''
    currentFilename.value = state.currentFilename || ''
    savedToGallery.value = state.savedToGallery || false
    logOutput.value = state.logOutput || ''
  } catch { /* ignore */ }
}

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
  if ((evt as any).code) { _aiChanging = true; code.value = (evt as any).code }
  if (evt.video_path) {
    videoPath.value = evt.video_path
    videoUrl.value = `http://localhost:8000${evt.video_path}`
    currentFilename.value = evt.video_path.replace('/videos/', '')
    // 加入"我的作品"（localStorage + 服务端双写）
    try {
      const u = username.value || 'anon'
      const works = JSON.parse(localStorage.getItem(`cs:my-works:${u}`) || '[]')
      if (!works.includes(currentFilename.value)) {
        works.unshift(currentFilename.value)
        localStorage.setItem(`cs:my-works:${u}`, JSON.stringify(works.slice(0, 50)))
      }
      // 同步到服务端（跨设备持久化）
      if (username.value) {
        videosApi.syncMyWorks(username.value, [currentFilename.value]).catch(() => {})
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
  // 从 sessionStorage 恢复进度（比 Pinia store 更准确）
  let savedProgress = 0
  try {
    const raw = sessionStorage.getItem(STATE_KEY.value)
    if (raw) {
      const state = JSON.parse(raw)
      savedProgress = state.progress || 0
      if (state.progressMsg) progressMsg.value = state.progressMsg
    }
  } catch { /* ignore */ }

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
  // 任务可能仍在运行 → 用上次保存的进度或店里的进度，取较大值避免"倒退"
  if (cached?.state === 'PENDING' || cached?.state === 'STARTED' || cached?.state === 'RENDERING') {
    _activeTaskId = tid
    generating.value = true
    const bestProgress = Math.max(savedProgress, cached?.progress || 0)
    // 估算离开期间的进度增量
    if (cached?.startTime) {
      const elapsed = (Date.now() - cached.startTime) / 1000
      // 假设 120 秒完成，线性估计额外进度
      const estimated = Math.min(92, Math.round(elapsed / 120 * 100))
      startSmoothProgress(Math.max(bestProgress, estimated))
    } else {
      startSmoothProgress(bestProgress)
    }
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
  startAsyncTask(() => generationApi.asyncGenerate(requirement.value.trim(), 3, renderQuality.value, username.value))
}

function handleRender() {
  if (!code.value.trim()) { ElMessage.warning('请先输入或生成 Manim 代码'); return }
  startAsyncTask(() => generationApi.asyncRender(code.value, renderQuality.value, username.value))
}

async function handleCancelTask() {
  if (!_activeTaskId) return
  try {
    await ElMessageBox.confirm('确定要停止当前任务吗？', '取消生成', { confirmButtonText: '停止', cancelButtonText: '继续等待', type: 'warning' })
  } catch { return } // 用户取消
  try {
    disconnect()
    stopSmoothProgress()
    generating.value = false
    progressMsg.value = '任务已取消'
    // 尝试通知后端取消 Celery 任务
    await fetch(`http://localhost:8000/api/tasks/${_activeTaskId}`, { method: 'DELETE' }).catch(() => {})
    localStorage.removeItem('cs:active-task')
  } catch { /* ignore */ }
}

async function handleFixCode() {
  if (!code.value.trim()) return
  const err = getLastError()
  fixing.value = true
  try {
    // 把错误信息和原始需求都传给 AI（无错误时仅传需求，AI 也能优化代码）
    const res = await generationApi.fixCode(code.value, err || '请根据用户需求优化代码', requirement.value || undefined)
    const fixed = res.data.data?.code
    if (fixed && fixed !== code.value) {
      _aiChanging = true
      code.value = fixed
      ElMessage.success(err.trim() ? 'AI 已根据错误信息修复代码' : 'AI 已根据需求优化代码，请渲染验证')
    } else {
      ElMessage.info('AI 未找到需要修改的地方')
    }
  } catch { ElMessage.error('修复失败，请重试') }
  finally { fixing.value = false }
}

function openPublishDialog() {
  publishDesc.value = requirement.value.slice(0, 200)
  publishToGallery.value = false
  publishDialogVisible.value = true
}

async function handlePublish() {
  // 从完整代码中提取场景类名作为智能标题（不截断，避免类名被切碎）
  const classMatch = code.value.match(/class\s+(\w+)\s*\(\s*\w*Scene/)
  const title = classMatch?.[1] || requirement.value.slice(0, 40) || '未命名作品'
  if (!token.value) { ElMessage.warning('请先登录再发布'); return }
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
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body.toString(),
    })
    const data = await res.json()
    if (data.code === 200) {
      publishDialogVisible.value = false
      // 如果勾选了发布到画廊，同步收藏
      if (publishToGallery.value && currentFilename.value) {
        videosApi.saveVideo(currentFilename.value, username.value).then(() => {
          savedToGallery.value = true
        }).catch(() => {})
      }
      ElMessage.success('已发布到社区！')
    } else {
      ElMessage.error(data.msg || '发布失败')
    }
  } catch (e) { ElMessage.error('发布失败：' + (e as Error).message) }
}

async function handleSaveToGallery() {
  if (!currentFilename.value) return
  try {
    const res = await videosApi.saveVideo(currentFilename.value, username.value)
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
  // Fork 过来的代码
  const forkedCode = sessionStorage.getItem('cs:forked-code')
  if (forkedCode) {
    code.value = forkedCode
    sessionStorage.removeItem('cs:forked-code')
    return
  }

  const prompt = route.query.prompt as string
  if (prompt) {
    // 从百科/首页跳转过来 → 全新任务，自动开始生成
    requirement.value = prompt
    code.value = ''
    videoUrl.value = ''
    videoPath.value = ''
    currentFilename.value = ''
    logOutput.value = ''
    typingActive.value = false
    localStorage.removeItem('cs:active-task')
    nextTick(() => handleGenerate())
  } else {
    // 正常导航返回 → 恢复之前的状态
    restoreState()
    restoreTaskFromSession()
  }
})

onUnmounted(() => {
  disconnect()
  stopSmoothProgress()
  saveState()
})
</script>

<template>
  <div class="sandbox-page">
    <div class="sb-toolbar">
      <h1 class="sb-title"><el-icon :size="22"><EditPen /></el-icon> 动画沙箱</h1>
      <div class="sb-actions">
        <el-select v-model="renderQuality" size="small" style="width:110px" @change="(v: string) => localStorage.setItem('cs:render-quality', v)">
          <el-option label="⚡ 480p" value="-ql" />
          <el-option label="🎯 720p" value="-qm" />
          <el-option label="✨ 1080p" value="-qh" />
        </el-select>
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
      <span class="progress-msg">{{ progressMsg || '生成中...' }}</span>
      <el-button size="small" type="danger" plain round @click="handleCancelTask" style="flex-shrink:0">
        <el-icon><Close /></el-icon> 取消
      </el-button>
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
        <div class="panel-body code-panel-body" style="position:relative">
          <CodeEditor v-if="!typingActive" v-model="code" :readonly="false" />
          <!-- Canvas 画笔覆盖层 -->
          <CanvasTypewriter
            v-if="typingActive"
            :code="code"
            :active="typingActive"
            @done="onCanvasDone"
          />
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
      <el-checkbox v-model="publishToGallery" style="margin-top:12px">同时发布到画廊</el-checkbox>
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handlePublish">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
/* ====== Canvas 画布风格沙箱 ====== */
.sandbox-page {
  padding: var(--space-lg); max-width: 1600px; margin: 0 auto;
  min-height: calc(100vh - var(--header-height));
  position: relative;
  /* 画布底色 */
  background:
    /* 噪点纹理 */
    repeating-conic-gradient(rgba(255,255,255,0.008) 0% 25%, transparent 0% 50%) 50% / 3px 3px,
    /* 暖灰画布 */
    var(--bg-primary);
}
[data-theme="light"] .sandbox-page {
  background:
    repeating-conic-gradient(rgba(0,0,0,0.02) 0% 25%, transparent 0% 50%) 50% / 3px 3px,
    #faf8f5;
}

/* 画布网格点阵 */
.sandbox-page::before {
  content: ''; position: absolute; inset: 0; pointer-events: none; z-index: 0;
  background-image: radial-gradient(circle, rgba(255,255,255,0.04) 1px, transparent 1px);
  background-size: 24px 24px;
  mask-image: radial-gradient(ellipse at 50% 0%, black 40%, transparent 80%);
}
[data-theme="light"] .sandbox-page::before {
  background-image: radial-gradient(circle, rgba(0,0,0,0.08) 1px, transparent 1px);
}

/* ====== 工具栏 — 调色板风格 ====== */
.sb-toolbar {
  display: flex; align-items: center; justify-content: space-between;
  margin-bottom: var(--space-md); position: relative; z-index: 1;
  padding: 10px 20px;
  background: linear-gradient(180deg, rgba(255,255,255,0.06) 0%, rgba(255,255,255,0.02) 100%);
  border: 1.5px solid var(--border-color); border-radius: var(--radius-xl);
  backdrop-filter: blur(16px);
  box-shadow: 0 2px 16px rgba(0,0,0,0.08);
}
[data-theme="light"] .sb-toolbar {
  background: linear-gradient(180deg, #fff 0%, #faf8f5 100%);
  border-color: #d4c8b8;
  box-shadow: 0 2px 12px rgba(0,0,0,0.04);
}
.sb-title {
  font-size: 1.1rem; font-weight: 800; display: flex; align-items: center; gap: var(--space-sm);
  background: var(--gradient-primary);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  letter-spacing: -0.01em;
}
.sb-actions { display: flex; gap: var(--space-sm); align-items: center; }

/* 进度条 — 颜料涂抹 */
.progress-bar-wrap {
  margin-bottom: var(--space-md); display: flex; align-items: center; gap: var(--space-md);
  padding: var(--space-sm) var(--space-lg);
  border-radius: var(--radius-xl); border: 1.5px solid var(--border-color);
  position: relative; z-index: 1;
  background: linear-gradient(135deg, rgba(124,58,237,0.06) 0%, rgba(6,182,212,0.04) 100%);
  animation: scale-in 0.4s cubic-bezier(0.16, 1, 0.3, 1) both;
  box-shadow: 0 2px 16px rgba(124,58,237,0.06);
}
.progress-bar-wrap :deep(.el-progress-bar__outer) { background: rgba(255,255,255,0.05); overflow: hidden; border-radius: var(--radius-full); }
.progress-bar-wrap :deep(.el-progress-bar__inner) {
  background: linear-gradient(90deg, var(--accent-purple), var(--accent-blue), var(--accent-cyan));
  background-size: 200% 100%; animation: gradient-shift 2s linear infinite;
}
.progress-msg { color: var(--text-secondary); font-size: 0.85rem; white-space: nowrap; flex: 1; }

@keyframes gradient-shift { 0% { background-position: 0% 50%; } 100% { background-position: 200% 50%; } }

/* 三栏画架布局 */
.sb-panels {
  display: grid; grid-template-columns: 1fr 1fr 1fr;
  gap: var(--space-md); height: calc(100vh - 220px);
  position: relative; z-index: 1;
}

/* 面板 — 画框风格 */
.sb-panel {
  display: flex; flex-direction: column;
  background: linear-gradient(180deg, rgba(255,255,255,0.04) 0%, rgba(255,255,255,0.01) 100%);
  border-radius: var(--radius-xl);
  border: 2px solid rgba(255,255,255,0.06);
  overflow: hidden; transition: all 0.3s ease;
  backdrop-filter: blur(8px);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.03),
    0 4px 24px rgba(0,0,0,0.1);
}
[data-theme="light"] .sb-panel {
  background: #fffefc;
  border: 2px solid #d4c8b8;
  box-shadow:
    inset 0 0 20px rgba(139,119,90,0.04),
    0 4px 20px rgba(0,0,0,0.04);
}
.sb-panel:hover {
  border-color: rgba(124,58,237,0.3);
  box-shadow:
    inset 0 1px 0 rgba(255,255,255,0.05),
    0 8px 32px rgba(124,58,237,0.08);
}
[data-theme="light"] .sb-panel:hover { border-color: rgba(124,58,237,0.25); }

.panel-header {
  padding: 12px 16px; font-size: 0.8rem; font-weight: 650;
  color: var(--text-secondary); display: flex; align-items: center; gap: 8px;
  border-bottom: 1px solid var(--border-color);
  background: rgba(255,255,255,0.02);
  letter-spacing: 0.02em; text-transform: uppercase; font-size: 0.72rem;
}
[data-theme="light"] .panel-header { background: rgba(0,0,0,0.015); }
.panel-body { flex: 1; overflow: auto; padding: var(--space-md); }

/* AI 对话面板 — 素描纸感 */
.panel-chat .panel-body {
  background:
    linear-gradient(rgba(255,255,255,0.01) 1px, transparent 1px);
  background-size: 100% 28px;
}
.req-input :deep(.el-textarea__inner) {
  background: rgba(255,255,255,0.03); color: var(--text-primary);
  border: 1.5px dashed rgba(255,255,255,0.1); font-size: 0.9rem; resize: none;
  border-radius: var(--radius-lg); line-height: 1.6; padding: var(--space-md);
  transition: all 0.3s ease;
  font-style: italic;
}
[data-theme="light"] .req-input :deep(.el-textarea__inner) {
  background: rgba(0,0,0,0.01); border: 1.5px dashed #c8bda8;
}
.req-input :deep(.el-textarea__inner:focus) {
  border-color: var(--accent-purple); border-style: solid;
  box-shadow: 0 0 0 4px rgba(124,58,237,0.06);
  font-style: normal;
}
.quick-prompts { margin-top: var(--space-md); }
.qp-label { font-size: 0.75rem; color: var(--text-tertiary); font-weight: 500; letter-spacing: 0.04em; text-transform: uppercase; }
.qp-tag {
  cursor: pointer; margin: 3px; font-size: 0.78rem;
  background: rgba(255,255,255,0.03) !important; border: 1px solid rgba(255,255,255,0.08) !important;
  color: var(--text-secondary); transition: all 0.25s ease;
  border-radius: var(--radius-full);
}
.qp-tag:hover { border-color: var(--accent-purple) !important; color: var(--accent-purple-light); transform: translateY(-2px); box-shadow: 0 4px 12px rgba(124,58,237,0.15); }

/* 代码面板 — 暗色画布 */
.code-panel-body { padding: 0; background: #161b22; }
.code-panel-body :deep(.cm-editor) { background: #161b22; }

/* 预览面板 — 画框 */
.preview-body { display: flex; align-items: center; justify-content: center; flex-direction: column; }
.preview-video {
  max-width: 100%; max-height: 100%; border-radius: var(--radius-lg);
  animation: scale-in 0.5s cubic-bezier(0.16, 1, 0.3, 1) both;
  box-shadow: 0 8px 32px rgba(0,0,0,0.3);
  border: 2px solid rgba(255,255,255,0.06);
}
.preview-empty { text-align: center; color: var(--text-tertiary); animation: fade-in 0.5s ease both; }
.preview-empty .el-icon { margin-bottom: var(--space-md); opacity: 0.15; }
.preview-empty p { font-size: 0.9rem; font-style: italic; }
.panel-log { max-height: 140px; overflow-y: auto; padding: var(--space-sm) var(--space-md); background: rgba(0,0,0,0.2); border-top: 1px solid var(--border-color); }
.panel-log pre { font-family: var(--font-mono); font-size: 0.7rem; color: var(--text-tertiary); white-space: pre-wrap; margin: 0; line-height: 1.5; }

@keyframes scale-in { from { opacity: 0; transform: scale(0.95); } to { opacity: 1; transform: scale(1); } }
@keyframes fade-in { from { opacity: 0; } to { opacity: 1; } }

@media (max-width: 1024px) {
  .sb-panels { grid-template-columns: 1fr; height: auto; }
  .sb-panel { min-height: 320px; }
}
</style>

<script setup lang="ts">
import { computed } from 'vue'
import { useTaskStore, type QueueTask } from '@/stores/task'
import { ElMessage, ElMessageBox } from 'element-plus'

const emit = defineEmits<{
  (e: 'load-task', taskId: string): void
}>()

const taskStore = useTaskStore()

const runningTask = computed(() => taskStore.runningTask)
const pendingCount = computed(() => taskStore.pendingTasks.length)
const finishedTasks = computed(() => taskStore.finishedTasks.slice(0, 10))

function formatTime(ts: number): string {
  const d = new Date(ts)
  return `${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`
}

function handleLoad(task: QueueTask) {
  if (task.state === 'SUCCESS') {
    emit('load-task', task.taskId)
  } else {
    ElMessage.info('任务尚未完成')
  }
}

async function handleClearFinished() {
  try {
    await ElMessageBox.confirm('确定清空所有已完成的任务记录吗？', '确认清空', {
      confirmButtonText: '清空',
      cancelButtonText: '取消',
      type: 'warning',
    })
    taskStore.clearFinished()
    ElMessage.success('已清空')
  } catch { /* cancel */ }
}

function getStatusColor(state: string): string {
  switch (state) {
    case 'RUNNING': return 'var(--accent-purple)'
    case 'PENDING': return 'var(--text-tertiary)'
    case 'SUCCESS': return '#10b981'
    case 'FAILURE': return '#ef4444'
    default: return 'var(--text-tertiary)'
  }
}

function getStatusText(state: string): string {
  switch (state) {
    case 'RUNNING': return '运行中'
    case 'PENDING': return '排队中'
    case 'SUCCESS': return '已完成'
    case 'FAILURE': return '失败'
    default: return state
  }
}
</script>

<template>
  <div class="task-queue glass-card">
    <div class="queue-header">
      <h4>
        <el-icon><List /></el-icon>
        任务中心
      </h4>
      <span v-if="pendingCount > 0" class="pending-badge">{{ pendingCount }} 排队</span>
    </div>

    <div class="queue-body">
      <!-- 运行中 -->
      <div v-if="runningTask" class="task-item running">
        <div class="task-info">
          <div class="task-title" :title="runningTask.title">{{ runningTask.title }}</div>
          <div class="task-status" :style="{ color: getStatusColor(runningTask.state) }">
            <span class="status-dot"></span>
            {{ runningTask.message || getStatusText(runningTask.state) }}
          </div>
        </div>
        <el-progress
          :percentage="Math.min(runningTask.progress, 100)"
          :stroke-width="4"
          :color="getStatusColor(runningTask.state)"
          class="task-progress"
        />
      </div>

      <div v-else class="no-running">
        <el-icon :size="20"><CircleCheck /></el-icon>
        <span>当前没有运行中的任务</span>
      </div>

      <!-- 排队中 -->
      <div v-if="pendingCount > 0" class="pending-section">
        <div class="section-title">
          排队中 ({{ pendingCount }})
        </div>
        <div class="pending-list">
          <div v-for="task in taskStore.pendingTasks.slice(0, 3)" :key="task.taskId" class="pending-item">
            <el-icon><Clock /></el-icon>
            <span class="pending-title">{{ task.title }}</span>
          </div>
          <div v-if="pendingCount > 3" class="pending-more">
            还有 {{ pendingCount - 3 }} 个任务等待中...
          </div>
        </div>
      </div>

      <!-- 已完成 -->
      <div class="finished-section">
        <div class="section-title">
          <span>已完成</span>
          <el-button v-if="finishedTasks.length > 0" link size="small" @click="handleClearFinished">
            清空
          </el-button>
        </div>

        <div v-if="finishedTasks.length === 0" class="empty-finished">
          暂无已完成任务
        </div>

        <div v-else class="finished-list">
          <div
            v-for="task in finishedTasks"
            :key="task.taskId"
            class="finished-item"
            :class="{ clickable: task.state === 'SUCCESS' }"
            @click="handleLoad(task)"
          >
            <div class="finished-left">
              <el-icon :style="{ color: getStatusColor(task.state) }">
                <CircleCheckFilled v-if="task.state === 'SUCCESS'" />
                <CircleCloseFilled v-else />
              </el-icon>
              <div class="finished-info">
                <div class="finished-title">{{ task.title }}</div>
                <div class="finished-time">{{ formatTime(task.finishedAt || task.createdAt) }}</div>
              </div>
            </div>
            <el-icon v-if="task.state === 'SUCCESS'" class="load-icon"><RefreshRight /></el-icon>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.task-queue {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 380px;
}

.queue-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  border-bottom: 1px solid var(--border-color);
}
.queue-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}
.pending-badge {
  font-size: 0.7rem;
  background: var(--accent-purple);
  color: white;
  padding: 2px 8px;
  border-radius: var(--radius-full);
}

.queue-body {
  padding: var(--space-md) var(--space-lg);
  overflow-y: auto;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

/* 运行中 */
.task-item.running {
  background: rgba(124, 58, 237, 0.08);
  border: 1px solid rgba(124, 58, 237, 0.2);
  border-radius: var(--radius-md);
  padding: var(--space-sm) var(--space-md);
}
.task-info { margin-bottom: var(--space-xs); }
.task-title {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.task-status {
  font-size: 0.75rem;
  display: flex;
  align-items: center;
  gap: 6px;
  margin-top: 2px;
}
.status-dot {
  width: 6px;
  height: 6px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 1.5s ease-in-out infinite;
}
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
.task-progress { margin-top: 4px; }

.no-running {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-tertiary);
  padding: var(--space-sm) 0;
}

/* 排队中 */
.section-title {
  font-size: 0.75rem;
  font-weight: 600;
  color: var(--text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin-bottom: var(--space-xs);
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.pending-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}
.pending-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.8rem;
  color: var(--text-secondary);
  padding: 4px 0;
}
.pending-item .el-icon { color: var(--text-tertiary); font-size: 14px; }
.pending-title {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.pending-more {
  font-size: 0.72rem;
  color: var(--text-tertiary);
  padding-left: 22px;
}

/* 已完成 */
.finished-section { flex: 1; min-height: 0; display: flex; flex-direction: column; }
.finished-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow-y: auto;
  flex: 1;
}
.finished-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.finished-item.clickable { cursor: pointer; }
.finished-item.clickable:hover { background: var(--bg-card-hover); }
.finished-left {
  display: flex;
  align-items: center;
  gap: 8px;
  min-width: 0;
}
.finished-left .el-icon { font-size: 14px; flex-shrink: 0; }
.finished-info { min-width: 0; }
.finished-title {
  font-size: 0.8rem;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.finished-time {
  font-size: 0.7rem;
  color: var(--text-tertiary);
}
.load-icon {
  color: var(--text-tertiary);
  font-size: 14px;
  opacity: 0;
  transition: opacity var(--transition-fast);
}
.finished-item:hover .load-icon { opacity: 1; }

.empty-finished {
  font-size: 0.78rem;
  color: var(--text-tertiary);
  text-align: center;
  padding: var(--space-md) 0;
}
</style>

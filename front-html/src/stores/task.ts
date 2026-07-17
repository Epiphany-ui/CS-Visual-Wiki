import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { TaskState } from '@/types/api'
import { useUserStore } from './user'

export interface QueueTask {
  taskId: string
  title: string          // 任务标题/描述
  type: 'generate' | 'render' | 'template'  // 任务类型
  state: 'PENDING' | 'RUNNING' | 'SUCCESS' | 'FAILURE'
  progress: number
  message: string
  videoPath: string
  code?: string          // 关联的代码（渲染任务）
  prompt?: string        // 关联的 prompt（生成任务）
  createdAt: number
  finishedAt?: number
}

export const useTaskStore = defineStore('task', () => {
  // 任务队列：所有任务按时间倒序排列
  const queue = ref<QueueTask[]>([])

  // 当前运行中的任务（第一个 RUNNING 状态的）
  const runningTask = computed(() => queue.value.find(t => t.state === 'RUNNING') || null)

  // 排队中的任务（按提交时间正序：最早的在前）
  const pendingTasks = computed(() => queue.value.filter(t => t.state === 'PENDING').reverse())

  // 下一个要执行的任务（FIFO：最早提交的排队任务）
  const nextPendingTask = computed(() => pendingTasks.value[0] || null)

  // 已完成的任务（成功 + 失败）
  const finishedTasks = computed(() =>
    queue.value.filter(t => t.state === 'SUCCESS' || t.state === 'FAILURE')
  )

  // ========== 添加任务 ==========
  function addTask(task: Omit<QueueTask, 'state' | 'progress' | 'message' | 'videoPath' | 'createdAt'>) {
    const newTask: QueueTask = {
      ...task,
      state: 'PENDING',
      progress: 0,
      message: '排队中...',
      videoPath: '',
      createdAt: Date.now(),
    }
    queue.value.unshift(newTask)

    // 如果当前没有运行中的任务，直接标记为运行中
    if (!runningTask.value) {
      newTask.state = 'RUNNING'
      newTask.message = '准备中...'
    }

    _persist()
    return newTask
  }

  // ========== 更新任务进度 ==========
  function updateTaskProgress(taskId: string, data: {
    state?: TaskState
    progress?: number
    message?: string
    video_path?: string
  }) {
    const task = queue.value.find(t => t.taskId === taskId)
    if (!task) return

    if (data.state) task.state = data.state as QueueTask['state']
    if (data.progress !== undefined) task.progress = data.progress
    if (data.message) task.message = data.message
    if (data.video_path) task.videoPath = data.video_path

    // 任务结束时记录完成时间
    if (data.state === 'SUCCESS' || data.state === 'FAILURE') {
      task.finishedAt = Date.now()
      _startNextTask()
    }

    _persist()
  }

  // ========== 启动下一个排队任务（FIFO）==========
  function _startNextTask() {
    const next = nextPendingTask.value
    if (next) {
      next.state = 'RUNNING'
      next.message = '准备中...'
    }
  }

  // ========== 标记任务开始运行 ==========
  function markTaskRunning(taskId: string) {
    const task = queue.value.find(t => t.taskId === taskId)
    if (task) {
      task.state = 'RUNNING'
      task.message = '渲染中...'
      _persist()
    }
  }

  // ========== 加载任务结果到沙箱 ==========
  function loadTaskResult(taskId: string) {
    const task = queue.value.find(t => t.taskId === taskId)
    return task || null
  }

  // ========== 清空已完成任务 ==========
  function clearFinished() {
    queue.value = queue.value.filter(t => t.state === 'PENDING' || t.state === 'RUNNING')
    _persist()
  }

  // ========== 删除单个任务 ==========
  function removeTask(taskId: string) {
    queue.value = queue.value.filter(t => t.taskId !== taskId)
    _persist()
  }

  // ========== 持久化到 localStorage（按用户隔离）==========
  function _storageKey(): string {
    const userStore = useUserStore()
    return `cs:task-queue:${userStore.username || 'anon'}`
  }

  function _persist() {
    try {
      localStorage.setItem(_storageKey(), JSON.stringify(queue.value.slice(0, 30)))
    } catch { /* ignore */ }
  }

  // ========== 从 localStorage 恢复 ==========
  function restore() {
    try {
      const saved = localStorage.getItem(_storageKey())
      if (saved) {
        queue.value = JSON.parse(saved)
        // 恢复后，运行中的任务重置为排队（刷新后需要重新连接）
        let changed = false
        queue.value.forEach(t => {
          if (t.state === 'RUNNING') {
            t.state = 'PENDING'
            t.message = '已暂停，点击继续'
            changed = true
          }
        })
        if (changed) _persist()
      } else {
        queue.value = []
      }
    } catch { /* ignore */ }
  }

  return {
    queue,
    runningTask,
    pendingTasks,
    nextPendingTask,
    finishedTasks,
    addTask,
    updateTaskProgress,
    markTaskRunning,
    loadTaskResult,
    clearFinished,
    removeTask,
    restore,
  }
})

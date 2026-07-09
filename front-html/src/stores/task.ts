import { defineStore } from 'pinia'
import { ref } from 'vue'
import type { TaskState } from '@/types/api'

export interface ActiveTask {
  taskId: string
  state: TaskState
  progress: number
  message: string
  videoPath: string
  startTime: number
}

export const useTaskStore = defineStore('task', () => {
  const activeTask = ref<ActiveTask | null>(null)
  const taskHistory = ref<ActiveTask[]>([])

  function startTask(taskId: string) {
    const task: ActiveTask = {
      taskId,
      state: 'PENDING',
      progress: 0,
      message: '任务已提交...',
      videoPath: '',
      startTime: Date.now(),
    }
    activeTask.value = task
    taskHistory.value.unshift(task)
  }

  function updateProgress(data: { state: TaskState; progress: number; message: string; video_path?: string }) {
    if (!activeTask.value) return
    activeTask.value.state = data.state
    activeTask.value.progress = data.progress
    activeTask.value.message = data.message
    if (data.video_path) {
      activeTask.value.videoPath = data.video_path
    }
  }

  function clearTask() {
    activeTask.value = null
  }

  return { activeTask, taskHistory, startTask, updateProgress, clearTask }
})

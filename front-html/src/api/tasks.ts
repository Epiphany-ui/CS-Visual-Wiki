import { pythonClient } from './client'
import type { ApiResponse, TaskInfo, PaginatedResult } from '@/types/api'

export const tasksApi = {
  /** 获取单个任务状态 */
  getTask(taskId: string) {
    return pythonClient.get<ApiResponse<TaskInfo>>(`/api/tasks/${taskId}`)
  },

  /** 列出所有任务 */
  listTasks(state?: string, page = 1, pageSize = 20) {
    return pythonClient.get<ApiResponse<PaginatedResult<TaskInfo>>>('/api/tasks', {
      params: { state, page, page_size: pageSize },
    })
  },

  /** 删除/取消任务 */
  deleteTask(taskId: string) {
    return pythonClient.delete<ApiResponse<null>>(`/api/tasks/${taskId}`)
  },

  /** 获取 SSE 进度流 URL */
  getTaskStreamUrl(taskId: string): string {
    return `http://localhost:8000/api/tasks/${taskId}/stream`
  },
}

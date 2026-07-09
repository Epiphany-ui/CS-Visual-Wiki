import { javaClient } from './client'
import type { ApiResponse } from '@/types/api'
import type { UserInfo } from '@/types/task'

export const authApi = {
  /** 注册 — Java 后端 @RequestParam 接口，用 query params */
  register(username: string, password: string) {
    return javaClient.post<ApiResponse<UserInfo>>('/api/v1/user/register', null, {
      params: { username, password },
    })
  },

  /** 登录 — Java 后端 @RequestParam 接口，用 query params */
  login(username: string, password: string) {
    return javaClient.post<ApiResponse<UserInfo>>('/api/v1/user/login', null, {
      params: { username, password },
    })
  },

  /** 提交生成任务 */
  submitTask(userInput: string, maxRetry = 3) {
    return javaClient.post<ApiResponse<number>>('/api/v1/template/generate', null, {
      params: { userInput, maxRetry },
    })
  },

  /** 查询任务状态 */
  getTaskStatus(taskId: number) {
    return javaClient.get<ApiResponse<any>>('/api/v1/render/status', {
      params: { taskId },
    })
  },

  /** 获取任务历史 */
  getTaskList() {
    return javaClient.get<ApiResponse<any>>('/api/v1/task/list')
  },
}

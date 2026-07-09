// API 统一响应格式
export interface ApiResponse<T = unknown> {
  code: number
  message: string
  data: T
}

// 任务状态
export type TaskState = 'PENDING' | 'STARTED' | 'RENDERING' | 'SUCCESS' | 'FAILURE' | 'UNKNOWN' | 'REVOKED'

// 异步任务
export interface TaskInfo {
  task_id: string
  state: TaskState
  progress: number
  message: string
  video_path: string
  log: string
  updated_at: string
}

// 生成结果
export interface GenerationResult {
  success: boolean
  code: string
  video_path: string
  try_count: number
  log: string
}

// SSE 事件
export interface SSETaskEvent {
  task_id: string
  state: TaskState
  progress: number
  message: string
  video_path: string
  log: string
  updated_at: string
}

export interface SSEDoneEvent {
  type: 'done'
  state: TaskState
}

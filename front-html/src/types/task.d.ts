// 用户信息
export interface UserInfo {
  token: string
  username: string
  userId: number
}

// 视频文件
export interface VideoFile {
  filename: string
  task_id: string
  size_bytes: number
  size_mb: number
  created_at: string
  url: string
  poster?: string
}

// 视频元数据（调试用）
export interface VideoMetadata {
  filename: string
  duration_seconds: number
  fps: number
  total_frames: number
  resolution: string
  codec: string
  size_bytes: number
  size_mb: number
}

// 帧信息
export interface FrameInfo {
  frame_index: number
  time_seconds: number
  url: string
  size_bytes: number
}

// 配置分页
export interface PaginatedResult<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

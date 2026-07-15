import { pythonClient } from './client'
import type { ApiResponse } from '@/types/api'
import type { VideoFile, VideoMetadata, FrameInfo } from '@/types/task'

const VIDEO_BASE = import.meta.env.VITE_PYTHON_BASE ?? ''

export const videosApi = {
  /** 获取视频列表。?published=true 仅返回已发布；?gallery=true 仅返回收藏 */
  getList(gallery = false, username = '', published = false) {
    const params: Record<string, any> = { _: Date.now() }
    if (gallery) { params.gallery = true; if (username) params.username = username }
    if (published) params.published = true
    return pythonClient.get<ApiResponse<{ items: VideoFile[]; total: number }>>('/api/videos/list', { params })
  },

  /** 发布视频到画廊 */
  publishVideo(filename: string, username?: string) {
    return pythonClient.post<ApiResponse<{ filename: string; published: boolean }>>(`/api/videos/${filename}/publish`, null, {
      params: username ? { username } : {},
    })
  },

  /** 切换公开/私有 */
  togglePublic(filename: string) {
    return pythonClient.post<ApiResponse<{ filename: string; published: boolean }>>(`/api/videos/${filename}/toggle-public`)
  },

  /** Toggle 画廊收藏：已收藏则取消，未收藏则添加 */
  saveVideo(filename: string, username = '') {
    const params: Record<string, any> = {}
    if (username) params.username = username
    return pythonClient.post<ApiResponse<{ filename: string; saved: boolean }>>(`/api/videos/${filename}/save`, null, { params })
  },

  /** 下载视频 */
  getDownloadUrl(filename: string): string {
    return `${VIDEO_BASE}/api/videos/${filename}/download`
  },

  /** 视频播放 URL */
  getPlayUrl(filename: string): string {
    return `${VIDEO_BASE}/videos/${filename}`
  },

  /** 转换为 GIF */
  convertGif(filename: string, fps = 10, width = 480) {
    return pythonClient.post<ApiResponse<{ filename: string; url: string; size_kb: number }>>(`/api/videos/${filename}/convert/gif`, null, {
      params: { fps, width },
    })
  },

  /** 修改视频标题 */
  renameVideo(filename: string, title: string) {
    return pythonClient.patch<ApiResponse<{ filename: string; title: string }>>(`/api/videos/${filename}/title`, null, {
      params: { title },
    })
  },

  /** 获取缩略图 URL（API 懒生成 + 缓存） */
  getThumbnailUrl(filename: string): string {
    return `${VIDEO_BASE}/api/videos/${filename}/thumbnail`
  },

  /** 获取用户作品列表（服务端） */
  getMyWorks(username: string) {
    return pythonClient.get<ApiResponse<{ items: VideoFile[]; total: number }>>('/api/videos/list', {
      params: { my_works: true, username, _: Date.now() },
    })
  },

  /** 同步本地作品列表到服务端 */
  async syncMyWorks(username: string, filenames: string[]) {
    return pythonClient.post<ApiResponse<{ synced_count: number; total: number }>>('/api/user/works/sync', null, {
      params: { username, works: filenames.join(',') },
    })
  },

  /** 删除视频 */
  deleteVideo(filename: string) {
    return pythonClient.delete(`/api/videos/${filename}`)
  },
}

export const debugApi = {
  /** 获取视频元数据 */
  getVideoInfo(filename: string) {
    return pythonClient.get<ApiResponse<VideoMetadata>>(`/api/debug/video/${filename}/info`)
  },

  /** 提取帧 */
  extractFrames(filename: string, startFrame = 0, endFrame = 10) {
    return pythonClient.get<ApiResponse<{ frames: FrameInfo[]; total_extracted: number }>>(`/api/debug/video/${filename}/frames`, {
      params: { start_frame: startFrame, end_frame: endFrame, format: 'jpg', quality: 85 },
    })
  },

  /** 获取缩略图网格 */
  getThumbnailSheet(filename: string, cols = 5, rows = 4) {
    return pythonClient.get<ApiResponse<{ url: string; cols: number; rows: number }>>(`/api/debug/video/${filename}/thumbnail-sheet`, {
      params: { cols, rows },
    })
  },
}

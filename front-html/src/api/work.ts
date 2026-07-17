import { javaClient } from './client'
import type { ApiResponse } from '@/types/api'

/** 作品发布请求参数 */
export interface PublishWorkParams {
  workTitle: string
  workDesc?: string
  tagList?: string
  isPublic: boolean
  code: string
  previewUrl?: string
}

/** 作品信息 */
export interface WorkInfo {
  id: number
  userId: number
  title: string
  description?: string
  manimCode?: string
  videoPath?: string
  cover?: string
  tags?: string
  isPublic: number
  status: number
  viewCount: number
  likeCount: number
  collectCount: number
  createTime?: string
}

export const workApi = {
  /** 发布作品到社区（沙箱→画廊，走 Vite 代理同源请求） */
  publish(params: PublishWorkParams) {
    const formData = new URLSearchParams()
    formData.append('workTitle', params.workTitle)
    formData.append('workDesc', params.workDesc || '')
    formData.append('tagList', params.tagList || '')
    formData.append('isPublic', String(params.isPublic))
    formData.append('code', params.code)
    formData.append('previewUrl', params.previewUrl || '')
    return javaClient.post<ApiResponse<{ publishedWorkId: number }>>('/work/publish', formData, {
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    })
  },

  /** 获取当前用户的作品列表 */
  listByUser(params: { status?: number; page?: number; size?: number } = {}) {
    const { status, page = 1, size = 10 } = params
    const query: Record<string, any> = { page, size }
    if (status != null) query.status = status
    return javaClient.get<ApiResponse<{ list: WorkInfo[]; total: number }>>('/user/work/list', { params: query })
  },

  /** 获取我的作品列表（个人中心首页数据） */
  getHomeData() {
    return javaClient.get<ApiResponse<{
      userInfo: { userId: number; nickname: string; avatar: string }
      workCount: number
      totalStudyMinutes: number
      checkinDays: number
      followerCount: number
      followeeCount: number
    }>>('/user/home/data')
  },

  /** 删除作品（仅创建者或管理员） */
  delete(workId: number) {
    return javaClient.delete(`/work/${workId}`)
  },

  /** 根据视频路径删除已发布的作品（删除视频时同步清理） */
  deleteByVideoPath(videoPath: string) {
    return javaClient.delete(`/work/by-video-path`, { params: { path: videoPath } })
  },
}

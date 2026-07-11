import { pythonClient } from './client'
import type { ApiResponse } from '@/types/api'

export interface Comment {
  id: string
  workId: number
  username: string
  text: string
  likes: number
  avatar?: string
}

export const communityApi = {
  /** 点赞/取消点赞 */
  toggleLike(workId: number, username: string) {
    return pythonClient.post<ApiResponse<{ liked: boolean; count: number }>>(`/api/community/like/${workId}`, null, {
      params: { username },
    })
  },

  /** 批量获取点赞数 */
  getLikeCounts(workIds: number[]) {
    return pythonClient.get<ApiResponse<{ counts: Record<number, number> }>>('/api/community/likes', {
      params: { ids: workIds.join(',') },
    })
  },

  /** 查询用户是否已点赞 */
  checkLiked(workIds: number[], username: string) {
    return pythonClient.get<ApiResponse<{ liked: Record<number, boolean> }>>('/api/community/likes/check', {
      params: { ids: workIds.join(','), username },
    })
  },

  /** 递增浏览量 */
  incrementView(workId: number) {
    return pythonClient.post<ApiResponse<{ count: number }>>(`/api/community/view/${workId}`)
  },

  /** 批量获取浏览量 */
  getViewCounts(workIds: number[]) {
    return pythonClient.get<ApiResponse<{ counts: Record<number, number> }>>('/api/community/views', {
      params: { ids: workIds.join(',') },
    })
  },

  /** 获取评论列表 */
  getComments(workId: number, limit = 3) {
    return pythonClient.get<ApiResponse<{ comments: Comment[]; total: number }>>(`/api/community/comments/${workId}`, {
      params: { limit, sort: 'likes' },
    })
  },

  /** 发表评论 */
  addComment(workId: number, username: string, text: string, avatar?: string) {
    return pythonClient.post<ApiResponse<{ comment: Comment }>>(`/api/community/comments/${workId}`, null, {
      params: { username, text, avatar: avatar || '' },
    })
  },

  /** 评论点赞/取消 */
  likeComment(workId: number, commentId: string, username: string) {
    return pythonClient.post<ApiResponse<{ commentId: string; liked: boolean; likes: number }>>(`/api/community/comments/${workId}/like/${commentId}`, null, {
      params: { username },
    })
  },
}

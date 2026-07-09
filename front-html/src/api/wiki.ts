import { pythonClient } from './client'
import type { ApiResponse } from '@/types/api'
import type { WikiMeta, WikiDetail } from '@/types/wiki'

export const wikiApi = {
  /** 获取分类列表 */
  getCategories() {
    return pythonClient.get<ApiResponse<{ categories: string[] }>>('/api/wiki/categories')
  },

  /** 获取词条列表 */
  getList(category?: string) {
    return pythonClient.get<ApiResponse<{ items: WikiMeta[]; total: number }>>('/api/wiki/list', {
      params: category ? { category } : {},
    })
  },

  /** 搜索词条 */
  search(keyword: string, limit = 10) {
    return pythonClient.get<ApiResponse<{ items: WikiMeta[]; total: number }>>('/api/wiki/search', {
      params: { q: keyword, limit },
    })
  },

  /** 获取词条详情 */
  getDetail(slug: string) {
    return pythonClient.get<ApiResponse<WikiDetail>>(`/api/wiki/${slug}`)
  },
}

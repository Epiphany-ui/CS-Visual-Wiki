import { pythonClient } from './client'
import type { ApiResponse } from '@/types/api'
import type { TemplateDetail } from '@/types/template'

export const templatesApi = {
  /** 获取分类列表 */
  getCategories() {
    return pythonClient.get<ApiResponse<{ categories: string[] }>>('/api/templates/categories')
  },

  /** 获取模板列表 */
  getList(category?: string) {
    return pythonClient.get<ApiResponse<{ items: TemplateDetail[]; total: number }>>('/api/templates/list', {
      params: category ? { category } : {},
    })
  },

  /** 获取模板详情（含参数定义） */
  getDetail(templateId: string) {
    return pythonClient.get<ApiResponse<TemplateDetail>>(`/api/templates/${templateId}`)
  },

  /** 生成模板代码（不渲染） */
  generateCode(templateId: string, params: Record<string, unknown>) {
    return pythonClient.post<ApiResponse<{ code: string }>>('/api/templates/generate-code', {
      template_id: templateId,
      params,
    })
  },

  /** 模板同步渲染 */
  render(templateId: string, params: Record<string, unknown>) {
    return pythonClient.post<ApiResponse<{ success: boolean; code: string; log: string; video_path: string }>>('/api/templates/render', {
      template_id: templateId,
      params,
    })
  },
}

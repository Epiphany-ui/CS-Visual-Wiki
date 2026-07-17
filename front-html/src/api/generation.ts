import { pythonClient } from './client'
import type { ApiResponse, GenerationResult } from '@/types/api'

export const generationApi = {
  /** 同步全流程生成 */
  generate(requirement: string, maxRetry = 3) {
    return pythonClient.post<ApiResponse<GenerationResult>>('/api/generate', {
      requirement,
      max_retry: maxRetry,
    })
  },

  /** 仅生成代码 */
  generateCode(requirement: string) {
    return pythonClient.post<ApiResponse<{ code: string }>>('/api/ai/generate-code', {
      requirement,
    })
  },

  /** 渲染已有代码 */
  renderCode(code: string) {
    return pythonClient.post<ApiResponse<{ success: boolean; log: string; video_path: string }>>('/api/render', {
      code,
    })
  },

  /** AI 修复代码（可选传入原始需求帮助 AI 理解意图） */
  fixCode(code: string, errorMessage: string, context?: string) {
    return pythonClient.post<ApiResponse<{ code: string }>>('/api/ai/fix-code', {
      code,
      error_message: errorMessage,
      context,
    })
  },

  /** RAG 检索 */
  retrieveReferences(query: string) {
    return pythonClient.post<ApiResponse<{ references: string }>>('/api/rag/retrieve', {
      query,
    })
  },

  /** 异步全流程生成 */
  asyncGenerate(requirement: string, maxRetry = 3, quality?: string, username?: string) {
    return pythonClient.post<ApiResponse<{ task_id: string }>>('/api/async/generate', {
      requirement,
      max_retry: maxRetry,
      quality,
      username: username || undefined,
    })
  },

  /** 异步渲染 */
  asyncRender(code: string, quality?: string, username?: string) {
    return pythonClient.post<ApiResponse<{ task_id: string; warnings?: unknown[] }>>('/api/async/render', {
      code,
      quality,
      username: username || undefined,
    })
  },

  /** 异步模板渲染 */
  asyncTemplateRender(templateId: string, params: Record<string, unknown>, quality?: string, username?: string) {
    return pythonClient.post<ApiResponse<{ task_id: string }>>('/api/async/template-render', {
      template_id: templateId,
      params,
      quality,
      username: username || undefined,
    })
  },
}

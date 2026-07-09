export interface TemplateParam {
  name: string
  label: string
  type: 'string' | 'number' | 'integer' | 'boolean' | 'select'
  required: boolean
  default: unknown
  description: string
  min?: number
  max?: number
  options?: Array<{ label: string; value: string }>
}

export interface TemplateInfo {
  id: string
  name: string
  description: string
  category: string
  tags: string[]
  difficulty: string
  cover: string
  use_count: number
  params?: TemplateParam[]
}

export interface TemplateDetail extends TemplateInfo {
  params: TemplateParam[]
}

export interface TemplateCategory {
  name: string
  count: number
}

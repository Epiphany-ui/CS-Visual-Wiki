export interface WikiMeta {
  slug: string
  title: string
  category: string
  tags: string
  difficulty: string
  path?: string
}

export interface WikiDetail {
  slug: string
  meta: WikiMeta
  content: string
  related: RelatedArticle[]
}

export interface RelatedArticle {
  slug: string
  title: string
  category: string
  difficulty: string
}

export interface WikiCategory {
  name: string
  count: number
}

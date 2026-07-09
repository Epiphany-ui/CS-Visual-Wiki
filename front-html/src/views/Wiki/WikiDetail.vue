<script setup lang="ts">
import { ref, onMounted, onUnmounted, nextTick, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { wikiApi } from '@/api/wiki'
import type { WikiDetail } from '@/types/wiki'
import { marked } from 'marked'
import katex from 'katex'
import 'katex/dist/katex.min.css'

marked.setOptions({ breaks: true, gfm: true })

const route = useRoute()
const router = useRouter()
const detail = ref<WikiDetail | null>(null)
const loading = ref(true)
const contentHtml = ref('')  // 最终渲染的 HTML
const contentRef = ref<HTMLElement | null>(null)

// 文本选中
const selectedText = ref('')
const showTooltip = ref(false)
const tooltipPos = ref({ x: 0, y: 0 })
let hideTimer: ReturnType<typeof setTimeout> | null = null

function renderMath(html: string): string {
  try {
    // 1. Display math: $$...$$ (double dollar, most common in wiki files)
    html = html.replace(/\$\$([\s\S]*?)\$\$/g, (_, f: string) => {
      try { return katex.renderToString(f.trim(), { displayMode: true, throwOnError: false }) }
      catch { return `<pre class="math-error">${f}</pre>` }
    })
    // 2. Display math: \[...\] (bracket-style, some wiki files use this)
    html = html.replace(/\\\[([\s\S]*?)\\\]/g, (_, f: string) => {
      try { return katex.renderToString(f.trim(), { displayMode: true, throwOnError: false }) }
      catch { return `<pre class="math-error">${f}</pre>` }
    })
    // 3. Inline math: $...$ (single dollar, non-greedy within a paragraph)
    html = html.replace(/\$([^$]+?)\$/g, (_, f: string) => {
      try { return katex.renderToString(f.trim(), { displayMode: false, throwOnError: false }) }
      catch { return `<code class="math-error">${f}</code>` }
    })
    // 4. Inline math: \(...\) (bracket-style, less common)
    html = html.replace(/\\\(([\s\S]*?)\\\)/g, (_, f: string) => {
      try { return katex.renderToString(f.trim(), { displayMode: false, throwOnError: false }) }
      catch { return `<code class="math-error">${f}</code>` }
    })
  } catch { /* ignore */ }
  return html
}

/** 内链: /api/wiki/x → 相对 hash #/wiki/x（与 Vue Router hash 模式匹配） */
function fixLinks(html: string): string {
  return html.replace(/href="\/api\/wiki\/([^"]+)"/g, 'href="#/wiki/$1"')
}

function buildHtml(content: string): string {
  // Step 1: Render LaTeX math FIRST — marked.parse() would escape \( and \[
  // as literal ( and [, destroying the delimiters before renderMath sees them.
  let h = renderMath(content)
  // Step 2: Parse markdown to HTML (leaves KaTeX HTML spans intact)
  h = marked.parse(h) as string
  // Step 3: Fix internal wiki links for SPA hash routing
  h = fixLinks(h)
  return h
}

// ---- 文本选中 ----
function onMouseUp() {
  setTimeout(() => {
    const sel = window.getSelection()
    const text = sel?.toString().trim()
    if (text && text.length >= 3) {
      selectedText.value = text.slice(0, 300)
      const range = sel!.getRangeAt(0)
      const rect = range.getBoundingClientRect()
      tooltipPos.value = { x: rect.left + rect.width / 2, y: rect.top - 52 }
      showTooltip.value = true
    }
    // 注意：不在这里隐藏 —— 留给按钮 click 时间
  }, 50)
}

function onMouseDown(e: MouseEvent) {
  const target = e.target as HTMLElement
  if (!target.closest('.selection-tooltip')) {
    hideTimer = setTimeout(() => showTooltip.value = false, 150)
  }
}

function goGenerate() {
  showTooltip.value = false
  if (selectedText.value) {
    router.push({ path: '/sandbox', query: { prompt: selectedText.value } })
  }
}

async function load() {
  const slug = route.params.slug as string
  if (!slug) return
  loading.value = true
  try {
    const res = await wikiApi.getDetail(slug)
    detail.value = res.data.data
    contentHtml.value = buildHtml(res.data.data.content)
  } finally { loading.value = false }
}

// 监听路由变化，加载新词条
watch(() => route.params.slug, (newSlug) => {
  if (newSlug) {
    detail.value = null
    contentHtml.value = ''
    load()
  }
})

onMounted(() => {
  load()
  document.addEventListener('mouseup', onMouseUp)
  document.addEventListener('mousedown', onMouseDown)
})
onUnmounted(() => {
  document.removeEventListener('mouseup', onMouseUp)
  document.removeEventListener('mousedown', onMouseDown)
  if (hideTimer) clearTimeout(hideTimer)
})
</script>

<template>
  <div class="wiki-detail-page">
    <div v-if="loading" class="loading"><el-icon :size="32" class="is-loading"><Loading /></el-icon></div>
    <div v-else-if="detail" class="detail-content">
      <div class="detail-header">
        <el-button link @click="router.back()">
          <el-icon><ArrowLeft /></el-icon> 返回
        </el-button>
        <span class="detail-category">{{ detail.meta.category }}</span>
        <span class="detail-difficulty">{{ detail.meta.difficulty }}</span>
      </div>

      <h1 class="detail-title text-gradient">{{ detail.meta.title }}</h1>

      <!-- 词条正文 -->
      <div ref="contentRef" class="detail-body" v-html="contentHtml"></div>

      <!-- 浮动工具栏 -->
      <Teleport to="body">
        <div
          v-if="showTooltip"
          class="selection-tooltip glass-card"
          :style="{ left: tooltipPos.x + 'px', top: tooltipPos.y + 'px' }"
        >
          <span class="sel-text">"{{ selectedText.slice(0, 40) }}{{ selectedText.length > 40 ? '...' : '' }}"</span>
          <el-button type="primary" size="small" round @click="goGenerate">
            <el-icon><MagicStick /></el-icon> 生成动画
          </el-button>
        </div>
      </Teleport>

      <!-- 相关推荐 -->
      <div v-if="detail.related && detail.related.length" class="related-section">
        <h3>相关词条推荐</h3>
        <div class="related-grid">
          <div
            v-for="r in detail.related.slice(0, 4)" :key="r.slug"
            class="related-card glass-card"
            @click="router.push(`/wiki/${r.slug}`)"
          >
            <span class="r-cat">{{ r.category }}</span>
            <h4>{{ r.title }}</h4>
            <span class="r-diff">{{ r.difficulty }}</span>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="empty-state">
      <el-empty description="词条不存在" />
    </div>
  </div>
</template>

<style scoped>
.wiki-detail-page { padding-bottom: var(--space-3xl); }
.loading { display: flex; justify-content: center; padding: var(--space-3xl); color: var(--accent-purple); }
.detail-content { max-width: 860px; margin: 0 auto; padding: var(--space-2xl) var(--space-xl); }
.detail-header { display: flex; align-items: center; gap: var(--space-md); margin-bottom: var(--space-xl); }
.detail-category { font-size: 0.85rem; color: var(--accent-purple-light); font-weight: 600; }
.detail-difficulty { font-size: 0.8rem; padding: 2px 10px; border-radius: var(--radius-full); background: var(--bg-card); color: var(--text-tertiary); }
.detail-title { font-size: 2rem; font-weight: 800; margin-bottom: var(--space-xl); font-family: serif; }
/* ==================== 浮动工具栏 ==================== */
.selection-tooltip {
  position: fixed;
  z-index: 9999;
  transform: translate(-50%, -100%);
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 16px;
  background: var(--bg-secondary) !important;
  border-color: var(--accent-purple) !important;
  box-shadow: 0 8px 32px rgba(124, 58, 237, 0.3) !important;
  animation: slide-up 0.2s ease;
  white-space: nowrap;
}
.sel-text {
  color: var(--text-tertiary);
  font-size: 0.82rem;
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
/* ==================== Markdown 排版（维基百科风格） ==================== */
.detail-body {
  line-height: 1.75;
  color: var(--text-primary);
  font-size: 1.02rem;
  font-family: 'Georgia', 'Noto Serif SC', 'Source Han Serif SC', 'Songti SC', serif;
  word-break: break-word;
  letter-spacing: 0.01em;
}

/* 标题 — 衬线风格 */
.detail-body :deep(h1) { font-size: 1.8rem; font-weight: 700; color: var(--text-primary); margin: var(--space-xl) 0 var(--space-md); font-family: serif; }
.detail-body :deep(h2) { font-size: 1.45rem; font-weight: 700; color: var(--text-primary); margin: var(--space-2xl) 0 var(--space-sm); padding-bottom: 6px; border-bottom: 1px solid var(--border-color); font-family: serif; }
.detail-body :deep(h3) { font-size: 1.2rem; font-weight: 600; color: var(--text-primary); margin: var(--space-xl) 0 var(--space-xs); }
.detail-body :deep(h4) { font-size: 1.05rem; font-weight: 600; color: var(--text-primary); margin: var(--space-lg) 0 var(--space-xs); }

/* 段落 */
.detail-body :deep(p) { margin-bottom: 1em; text-indent: 0; }

/* 链接 — 蓝色下划线 */
.detail-body :deep(a) {
  color: var(--accent-blue-light);
  text-decoration: none;
}
.detail-body :deep(a:hover) { text-decoration: underline; }
.detail-body :deep(a:visited) { color: var(--accent-purple-light); }

/* 行内代码 */
.detail-body :deep(code:not(pre code)) {
  background: var(--bg-card-hover);
  padding: 2px 7px;
  border-radius: 4px;
  font-family: var(--font-mono);
  font-size: 0.88em;
  color: var(--accent-cyan-light);
}

/* 代码块 */
.detail-body :deep(pre) {
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-md);
  padding: var(--space-lg);
  overflow-x: auto;
  margin: var(--space-lg) 0;
  position: relative;
}
.detail-body :deep(pre code) {
  font-family: var(--font-mono);
  font-size: 0.85rem;
  line-height: 1.6;
  color: var(--text-primary);
  background: none;
  padding: 0;
}

/* 列表 */
.detail-body :deep(ul), .detail-body :deep(ol) {
  margin: var(--space-md) 0;
  padding-left: 1.8em;
}
.detail-body :deep(li) { margin-bottom: var(--space-xs); }

/* 引用 */
.detail-body :deep(blockquote) {
  border-left: 4px solid var(--accent-purple);
  padding: var(--space-sm) var(--space-lg);
  margin: var(--space-lg) 0;
  background: rgba(124, 58, 237, 0.05);
  border-radius: 0 var(--radius-sm) var(--radius-sm) 0;
  color: var(--text-secondary);
}

/* 表格 */
.detail-body :deep(table) {
  width: 100%;
  border-collapse: collapse;
  margin: var(--space-lg) 0;
  font-size: 0.9rem;
}
.detail-body :deep(th) {
  background: var(--bg-card-hover);
  padding: var(--space-sm) var(--space-md);
  text-align: left;
  font-weight: 700;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}
.detail-body :deep(td) {
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
}

/* 图片 */
.detail-body :deep(img) { max-width: 100%; border-radius: var(--radius-md); margin: var(--space-md) 0; }

/* 水平线 */
.detail-body :deep(hr) {
  border: none;
  border-top: 1px solid var(--border-color);
  margin: var(--space-xl) 0;
}

/* 强调 */
.detail-body :deep(strong) { color: var(--text-primary); font-weight: 700; }
.detail-body :deep(em) { color: var(--text-secondary); }

/* KaTeX 数学公式 */
.detail-body :deep(.katex-display) {
  margin: var(--space-lg) 0;
  overflow-x: auto;
  overflow-y: hidden;
  text-align: center;
}
.detail-body :deep(.katex) {
  font-size: 1.08em;
}
.detail-body :deep(.katex-display > .katex) {
  font-size: 1.15em;
}
.detail-body :deep(.math-error) {
  color: var(--accent-red);
  padding: 2px 6px;
  background: rgba(239, 68, 68, 0.1);
  border-radius: 3px;
  font-family: var(--font-mono);
  font-size: 0.85em;
}

/* 表格增强 */
.detail-body :deep(tbody tr:hover) {
  background: var(--bg-card-hover);
}

/* 有序列表数字颜色 */
.detail-body :deep(ol) { list-style-type: decimal; }
.detail-body :deep(ol li::marker) { color: var(--accent-purple-light); font-weight: 600; }

.related-section { margin-top: var(--space-3xl); padding-top: var(--space-xl); border-top: 1px solid var(--border-color); }
.related-section h3 { font-size: 1.2rem; font-weight: 700; color: var(--text-primary); margin-bottom: var(--space-lg); }
.related-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)); gap: var(--space-md); }
.related-card { cursor: pointer; padding: var(--space-md); }
.related-card:hover { transform: translateY(-2px); }
.r-cat { font-size: 0.72rem; color: var(--accent-purple-light); }
h4 { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); margin: var(--space-xs) 0; }
.r-diff { font-size: 0.72rem; color: var(--text-tertiary); }
.empty-state { padding: var(--space-3xl); }
</style>

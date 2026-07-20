<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { templatesApi } from '@/api/templates'
import type { TemplateInfo } from '@/types/template'
import PageHeader from '@/components/common/PageHeader.vue'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'

const router = useRouter()
const categories = ref<string[]>([])
const items = ref<TemplateInfo[]>([])
const loading = ref(false)

async function load() {
  loading.value = true
  try {
    const [catRes, listRes] = await Promise.all([
      templatesApi.getCategories(),
      templatesApi.getList(),
    ])
    categories.value = catRes.data.data?.categories || []
    items.value = listRes.data.data?.items || []
  } finally { loading.value = false }
}

function goDetail(id: string) { router.push(`/templates/${id}`) }

onMounted(load)
</script>

<template>
  <div class="templates-page">
    <PageHeader title="模板库" description="零代码创作动画，选择模板填写参数即刻生成" icon="Tickets" />

    <div class="template-grid stagger-cards" v-loading="loading">
      <RevealOnScroll v-for="t in items" :key="t.id" as-child>
      <div class="t-card glass-card" @click="goDetail(t.id)">
        <div class="t-category">{{ t.category }}</div>
        <h3>{{ t.name }}</h3>
        <p class="t-desc">{{ t.description }}</p>
        <div class="t-meta">
          <span class="t-diff" :class="'d-' + t.difficulty">{{ t.difficulty }}</span>
          <span class="t-use">已使用 {{ t.use_count ?? 0 }} 次</span>
          <span class="t-rating" v-if="t.rating_count">⭐ {{ t.rating.toFixed(1) }}</span>
        </div>
        <div class="t-tags">
          <el-tag v-for="tag in (t.tags || []).slice(0, 3)" :key="tag" size="small">{{ tag }}</el-tag>
        </div>
      </div>
      </RevealOnScroll>
    </div>
  </div>
</template>

<style scoped>
.templates-page { padding-bottom: var(--space-3xl); }
.template-grid {
  max-width: var(--max-content-width); margin: 0 auto; padding: 0 var(--space-xl);
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-lg);
}
.t-card { cursor: pointer; padding: var(--space-xl); }
.t-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
.t-category { font-size: 0.78rem; color: var(--accent-purple-light); font-weight: 600; margin-bottom: var(--space-sm); }
h3 { font-size: 1.15rem; font-weight: 700; color: var(--text-primary); }
.t-desc { color: var(--text-tertiary); font-size: 0.85rem; margin: var(--space-sm) 0; line-height: 1.5; }
.t-meta { display: flex; gap: var(--space-md); align-items: center; margin-top: var(--space-md); }
.t-diff { font-size: 0.75rem; padding: 2px 8px; border-radius: var(--radius-full); background: var(--bg-card-hover); }
.d-入门, .d-初级 { color: var(--accent-green); }
.d-中等 { color: var(--accent-orange); }
.d-困难, .d-高级 { color: var(--accent-red); }
.t-use { font-size: 0.75rem; color: var(--text-tertiary); }
.t-tags { display: flex; gap: 4px; margin-top: var(--space-sm); }
.t-tags :deep(.el-tag) { background: var(--bg-card-hover); border: none; color: var(--text-tertiary); font-size: 0.72rem; }
</style>

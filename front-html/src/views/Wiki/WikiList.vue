<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { wikiApi } from '@/api/wiki'
import type { WikiMeta } from '@/types/wiki'
import PageHeader from '@/components/common/PageHeader.vue'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'

const router = useRouter()
const route = useRoute()
const categories = ref<string[]>([])
const activeCategory = ref((route.query.category as string) || '')
const items = ref<WikiMeta[]>([])
const total = ref(0)
const loading = ref(false)
const searchKw = ref((route.query.q as string) || '')

async function loadCategories() {
  try {
      const res = await wikiApi.getCategories()
      categories.value = res.data.data?.categories || []
    } catch { /* 分类加载失败不阻塞列表 */ }
  }

async function loadList() {
  loading.value = true
  try {
    if (searchKw.value) {
      const res = await wikiApi.search(searchKw.value)
      items.value = res.data.data?.items || []
      total.value = res.data.data?.total || 0
    } else {
      const res = await wikiApi.getList(activeCategory.value || undefined)
      items.value = res.data.data?.items || []
      total.value = res.data.data?.total || 0
    }
  } finally {
    loading.value = false
  }
}

function selectCategory(cat: string) {
  activeCategory.value = cat
  searchKw.value = ''
  loadList()
}

function handleSearch() {
  activeCategory.value = ''
  loadList()
}

onMounted(() => { loadCategories(); loadList() })
</script>

<template>
  <div class="wiki-page">
    <PageHeader
      title="知识百科"
      description="结构化知识体系，可视化维基百科"
      icon="Collection"
    />

    <!-- 搜索 -->
    <div class="wiki-search">
      <el-input v-model="searchKw" placeholder="搜索知识点..." size="large" prefix-icon="Search" @keyup.enter="handleSearch" @clear="handleSearch" clearable />
    </div>

    <!-- 分类筛选 -->
    <div class="category-tabs">
      <el-button
        :type="!activeCategory ? 'primary' : 'default'"
        size="default" round
        @click="selectCategory('')"
      >全部</el-button>
      <el-button
        v-for="cat in categories" :key="cat"
        :type="activeCategory === cat ? 'primary' : 'default'"
        size="default" round
        @click="selectCategory(cat)"
      >{{ cat }}</el-button>
    </div>

    <!-- 词条列表 -->
    <div v-loading="loading" class="wiki-grid">
      <RevealOnScroll v-for="item in items" :key="item.slug" as-child>
      <div
        class="wiki-card glass-card"
        @click="router.push(`/wiki/${item.slug}`)"
      >
        <div class="wiki-card-header">
          <span class="wiki-category">{{ item.category }}</span>
          <span class="wiki-difficulty" :class="'diff-' + (item.difficulty || '未知')">
            {{ item.difficulty || '未知' }}
          </span>
        </div>
        <h3 class="wiki-title">{{ item.title }}</h3>
        <div v-if="item.tags" class="wiki-tags">
          <el-tag v-for="tag in item.tags.split(',').slice(0, 3)" :key="tag" size="small" class="w-tag">{{ tag.trim() }}</el-tag>
        </div>
      </div>
      </RevealOnScroll>
    </div>

    <div v-if="!loading && items.length === 0" class="empty-state">
      <el-empty description="暂无匹配的词条" />
    </div>
  </div>
</template>

<style scoped>
.wiki-page { padding-bottom: var(--space-3xl); }
.wiki-search { max-width: 500px; margin: 0 auto var(--space-xl); padding: 0 var(--space-xl); }
.category-tabs {
  display: flex; gap: var(--space-sm); padding: 0 var(--space-xl); margin-bottom: var(--space-xl);
  justify-content: center; flex-wrap: wrap;
}
.wiki-grid {
  max-width: var(--max-content-width); margin: 0 auto; padding: 0 var(--space-xl);
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-lg);
}
.wiki-card {
  cursor: pointer; padding: var(--space-lg);
}
.wiki-card:hover { transform: translateY(-2px); }
.wiki-card-header {
  display: flex; justify-content: space-between; align-items: center; margin-bottom: var(--space-sm);
}
.wiki-category { font-size: 0.78rem; color: var(--accent-purple-light); font-weight: 600; }
.wiki-difficulty { font-size: 0.75rem; padding: 2px 8px; border-radius: var(--radius-full); background: var(--bg-card-hover); color: var(--text-tertiary); }
.diff-入门, .diff-初级 { color: var(--accent-green); }
.diff-中等 { color: var(--accent-orange); }
.diff-困难, .diff-高级 { color: var(--accent-red); }
.wiki-title { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin-bottom: var(--space-sm); }
.wiki-tags { display: flex; gap: 4px; flex-wrap: wrap; }
.w-tag { background: var(--bg-card-hover) !important; border: none !important; color: var(--text-tertiary); font-size: 0.72rem; }
.empty-state { padding: var(--space-3xl); }
</style>

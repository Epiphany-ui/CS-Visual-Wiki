<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { videosApi } from '@/api/videos'
import type { VideoFile } from '@/types/task'
import PageHeader from '@/components/common/PageHeader.vue'

const router = useRouter()
const route = useRoute()
const allVideos = ref<VideoFile[]>([])
const starredVideos = ref<VideoFile[]>([])
const loading = ref(false)

const activeTab = ref<'all' | 'my-works' | 'stars'>(
  (route.query.tab as 'all' | 'my-works' | 'stars') || 'all',
)

function getMyWorks(): string[] {
  try { return JSON.parse(localStorage.getItem('cs:my-works') || '[]') }
  catch { return [] }
}

const videos = computed(() => {
  if (activeTab.value === 'stars') return starredVideos.value
  if (activeTab.value === 'my-works') {
    const works = getMyWorks()
    return allVideos.value.filter(v => works.includes(v.filename))
  }
  return allVideos.value
})

const myWorksCount = computed(() => getMyWorks().length)
const starsCount = computed(() => starredVideos.value.length)

function switchTab(tab: 'all' | 'my-works' | 'stars') {
  activeTab.value = tab
  router.replace({ query: { tab } })
}

async function loadAll() {
  loading.value = true
  try {
    const res = await videosApi.getList(false)  // all videos
    allVideos.value = res.data.data?.items || []
  } finally { loading.value = false }
}

async function loadStars() {
  try {
    const res = await videosApi.getList(true)  // starred only
    starredVideos.value = res.data.data?.items || []
  } catch { /* ignore */ }
}

function getTitle(v: VideoFile & { title?: string }) {
  return (v as any).title || v.filename
}

onMounted(() => { loadAll().then(() => loadStars()) })
watch(() => route.query.tab, (t) => {
  if (t === 'all' || t === 'my-works' || t === 'stars') activeTab.value = t
})
</script>

<template>
  <div class="gallery-page">
    <PageHeader title="精选画廊" description="动画作品展示与收藏" icon="PictureFilled" />

    <!-- 标签页 -->
    <div class="gallery-tabs">
      <el-button :type="activeTab === 'all' ? 'primary' : 'default'" round @click="switchTab('all')">
        全部作品 ({{ allVideos.length }})
      </el-button>
      <el-button :type="activeTab === 'my-works' ? 'primary' : 'default'" round @click="switchTab('my-works')">
        我的作品 ({{ myWorksCount }})
      </el-button>
      <el-button :type="activeTab === 'stars' ? 'primary' : 'default'" round @click="switchTab('stars')">
        我的收藏 ({{ starsCount }})
      </el-button>
    </div>

    <div class="gallery-grid" v-loading="loading">
      <div v-for="v in videos" :key="v.filename" class="g-card glass-card" @click="router.push(`/gallery/${v.filename}`)">
        <div class="g-thumb">
          <video :src="videosApi.getPlayUrl(v.filename)" preload="metadata" class="g-video" />
          <div class="g-play"><el-icon :size="32"><VideoPlay /></el-icon></div>
        </div>
        <div class="g-info">
          <h4 :title="getTitle(v)">{{ getTitle(v) }}</h4>
          <span class="g-size">{{ v.size_mb }} MB · {{ v.created_at?.slice(0, 10) }}</span>
        </div>
      </div>
    </div>

    <div v-if="!loading && videos.length === 0" class="empty-state">
      <el-empty :description="activeTab === 'stars' ? '还没有收藏作品' : activeTab === 'my-works' ? '还没有生成作品' : '还没有作品'" />
      <el-button v-if="activeTab !== 'stars'" type="primary" round @click="router.push('/sandbox')">去沙箱创作</el-button>
    </div>
  </div>
</template>

<style scoped>
.gallery-page { padding-bottom: var(--space-3xl); }
.gallery-tabs {
  display: flex; gap: var(--space-sm); justify-content: center; flex-wrap: wrap;
  max-width: var(--max-content-width); margin: 0 auto var(--space-xl); padding: 0 var(--space-xl);
}
.gallery-grid {
  max-width: var(--max-content-width); margin: 0 auto; padding: 0 var(--space-xl);
  display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: var(--space-lg);
}
.g-card { cursor: pointer; overflow: hidden; padding: 0; }
.g-card:hover { transform: translateY(-3px); box-shadow: var(--shadow-lg); }
.g-thumb { position: relative; aspect-ratio: 16/9; background: var(--bg-secondary); overflow: hidden; }
.g-video { width: 100%; height: 100%; object-fit: cover; }
.g-play { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); opacity: 0; transition: opacity var(--transition-fast); color: white; }
.g-card:hover .g-play { opacity: 1; }
.g-info { padding: var(--space-md); }
.g-info h4 { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.g-size { font-size: 0.75rem; color: var(--text-tertiary); }
.empty-state { text-align: center; padding: var(--space-3xl); }
</style>

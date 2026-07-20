<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { videosApi } from '@/api/videos'
import { tasksApi } from '@/api/tasks'
import type { VideoFile } from '@/types/task'
import PageHeader from '@/components/common/PageHeader.vue'
import { useCurrentUser } from '@/composables/useCurrentUser'

const router = useRouter()
const route = useRoute()
const { username } = useCurrentUser()
const allVideos = ref<VideoFile[]>([])
const starredVideos = ref<VideoFile[]>([])
const loading = ref(false)

const activeTab = ref<'all' | 'my-works' | 'stars'>(
  (route.query.tab as 'all' | 'my-works' | 'stars') || 'all',
)

function getMyWorks(): string[] {
  try {
    const u = username.value || 'anon'
    return JSON.parse(localStorage.getItem(`cs:my-works:${u}`) || '[]')
  } catch { return [] }
}

const videos = computed(() => {
  if (activeTab.value === 'stars') return starredVideos.value
  if (activeTab.value === 'my-works') {
    return serverMyWorks.value  // 只用服务端数据（per-user）
  }
  return allVideos.value
})

const myWorksCount = computed(() => serverMyWorks.value.length)
const starsCount = computed(() => starredVideos.value.length)

function switchTab(tab: 'all' | 'my-works' | 'stars') {
  activeTab.value = tab
  router.replace({ query: { tab } })
}

async function loadAll() {
  loading.value = true
  try {
    const res = await videosApi.getList(false, '', true)  // 只显示已发布到画廊的公开视频
    allVideos.value = res.data.data?.items || []
  } finally { loading.value = false }
}

async function loadStars() {
  try {
    const res = await videosApi.getList(true, username.value)  // starred only
    starredVideos.value = res.data.data?.items || []
  } catch { /* ignore */ }
}

// 从服务端加载"我的作品"列表（跨设备同步，不依赖 localStorage）
const serverMyWorks = ref<VideoFile[]>([])
async function loadMyWorksFromServer() {
  const name = username.value
  if (!name) return
  try {
    const r = await fetch(`/api/videos/list?my_works=true&username=${encodeURIComponent(name)}`)
    const d = await r.json()
    serverMyWorks.value = d.data?.items || []
  } catch { /* ignore */ }
}

const selectedFiles = ref<Set<string>>(new Set())
const batchDeleting = ref(false)
const batchPublishing = ref(false)

function toggleSelect(filename: string) {
  if (selectedFiles.value.has(filename)) {
    selectedFiles.value.delete(filename)
  } else {
    selectedFiles.value.add(filename)
  }
  selectedFiles.value = new Set(selectedFiles.value)
}

async function batchDelete() {
  try {
    await ElMessageBox.confirm(`确定要删除选中的 ${selectedFiles.value.size} 个视频吗？`, '批量删除', { type: 'warning' })
  } catch { return }
  batchDeleting.value = true
  let ok = 0
  for (const fn of selectedFiles.value) {
    try { await videosApi.deleteVideo(fn); ok++ } catch { /* skip */ }
  }
  selectedFiles.value = new Set()
  batchDeleting.value = false
  ElMessage.success(`已删除 ${ok} 个视频`)
  loadAll()
  loadMyWorksFromServer()
}

async function batchPublish() {
  batchPublishing.value = true
  let ok = 0
  for (const fn of selectedFiles.value) {
    try { await videosApi.togglePublic(fn); ok++ } catch { /* skip */ }
  }
  selectedFiles.value = new Set()
  batchPublishing.value = false
  ElMessage.success(`已切换 ${ok} 个视频的发布状态`)
  loadAll()
}

const sortBy = ref<'time' | 'title' | 'size' | 'popular'>('time')

async function applySort() {
  if (sortBy.value === 'popular') {
    // 收藏数排序走服务端
    loading.value = true
    try {
      const res = await videosApi.getList(false, '', true, 'popular')
      allVideos.value = res.data.data?.items || []
    } finally { loading.value = false }
  } else if (sortBy.value === 'time') {
    // 默认排序重新加载
    loadAll()
  }
}

const sortedVideos = computed(() => {
  const arr = [...videos.value]
  if (sortBy.value === 'title') {
    arr.sort((a, b) => getTitle(a).localeCompare(getTitle(b), 'zh'))
  } else if (sortBy.value === 'size') {
    arr.sort((a, b) => b.size_bytes - a.size_bytes)
  }
  // 'time' 和 'popular' 已由服务端排序
  return arr
})

function getTitle(v: VideoFile & { title?: string }) {
  return (v as any).title || v.filename
}

// 补漏：检查 pending tasks 中已完成但未加入"我的作品"的视频
async function syncPendingTasks() {
  try {
    const pending: string[] = JSON.parse(localStorage.getItem('cs:pending-tasks') || '[]')
    if (!pending.length) return
    const u = username.value || 'anon'
    const works: string[] = JSON.parse(localStorage.getItem(`cs:my-works:${u}`) || '[]')
    let changed = false
    for (const tid of pending.slice(0, 10)) {
      try {
        const res = await tasksApi.getTaskStatus(tid)
        const data = res.data
        const vp = data?.data?.video_path || ''
        const fn = vp.replace('/videos/', '')
        if (fn && data?.data?.state === 'SUCCESS' && !works.includes(fn)) {
          works.unshift(fn)
          changed = true
        }
      } catch { /* skip */ }
    }
    if (changed) {
      localStorage.setItem(`cs:my-works:${u}`, JSON.stringify(works.slice(0, 50)))
      // 重新加载全部列表以更新标题
      await loadAll()
    }
    // 清理已完成的 pending tasks
    localStorage.setItem('cs:pending-tasks', JSON.stringify(pending.slice(0, 5)))
  } catch { /* ignore */ }
}

onMounted(() => { loadAll().then(() => loadStars()).then(() => syncPendingTasks()).then(() => loadMyWorksFromServer()) })
watch(() => route.query.tab, (t) => {
  if (t === 'all' || t === 'my-works' || t === 'stars') activeTab.value = t
})
// 切换到"我的作品"或"我的收藏"时重新加载（处理用户切换场景）
watch(activeTab, (tab) => {
  if (tab === 'my-works') loadMyWorksFromServer()
  if (tab === 'stars') loadStars()
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
      <el-select v-model="sortBy" size="small" style="width:140px" @change="applySort">
        <el-option label="最新优先" value="time" />
        <el-option label="最多收藏" value="popular" />
        <el-option label="标题 A-Z" value="title" />
        <el-option label="文件大小" value="size" />
      </el-select>
    </div>

    <!-- 批量操作栏 -->
    <div v-if="activeTab === 'my-works' && selectedFiles.size > 0" class="batch-bar">
      <span>已选 {{ selectedFiles.size }} 个</span>
      <el-button size="small" type="primary" :loading="batchPublishing" @click="batchPublish">切换公开/私有</el-button>
      <el-button size="small" type="danger" :loading="batchDeleting" @click="batchDelete">批量删除</el-button>
      <el-button size="small" @click="selectedFiles = new Set()">取消选择</el-button>
    </div>

    <div class="gallery-grid" v-loading="loading">
      <div v-for="v in sortedVideos" :key="v.filename" class="g-card glass-card" v-tilt @click="router.push(`/gallery/${v.filename}`)">
        <div class="g-thumb">
          <el-checkbox
            v-if="activeTab === 'my-works'"
            :model-value="selectedFiles.has(v.filename)"
            class="g-check"
            @click.stop @change="toggleSelect(v.filename)"
          />
          <img :src="(v as any).poster || videosApi.getThumbnailUrl(v.filename)"
               loading="lazy"
               class="g-thumb-img"
               @error="($event.target as HTMLImageElement).style.display='none'"
               :alt="getTitle(v)" />
          <div class="g-play"><el-icon :size="32"><VideoPlay /></el-icon></div>
        </div>
        <div class="g-info">
          <h4 :title="getTitle(v)">{{ getTitle(v) }}</h4>
          <span class="g-size">{{ v.size_mb }} MB · {{ v.created_at?.slice(0, 10) }}<span v-if="(v as any).saved_count"> · ⭐ {{ (v as any).saved_count }} 收藏</span></span>
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
.g-thumb-img { width: 100%; height: 100%; object-fit: cover; }
.g-video { width: 100%; height: 100%; object-fit: cover; }
.g-play { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); opacity: 0; transition: opacity var(--transition-fast); color: white; }
.g-card:hover .g-play { opacity: 1; }
.g-info { padding: var(--space-md); }
.g-info h4 { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.g-size { font-size: 0.75rem; color: var(--text-tertiary); }
.g-check { position: absolute; top: 8px; left: 8px; z-index: 5; }
.batch-bar {
  display: flex; align-items: center; gap: var(--space-md);
  padding: var(--space-sm) var(--space-lg); margin-bottom: var(--space-md);
  background: var(--bg-card); border: 1px solid var(--accent-purple);
  border-radius: var(--radius-lg); max-width: var(--max-content-width);
  margin-left: auto; margin-right: auto;
}
.empty-state { text-align: center; padding: var(--space-3xl); }
</style>

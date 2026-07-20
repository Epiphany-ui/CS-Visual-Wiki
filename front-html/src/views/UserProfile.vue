<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { videosApi } from '@/api/videos'
import type { VideoFile } from '@/types/task'
import AvatarIcon from '@/components/common/AvatarIcon.vue'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'

const route = useRoute()
const router = useRouter()
const userId = computed(() => route.params.userId as string)

const avatarUrl = ref('')
const displayName = ref(userId.value)
const usernameRef = ref('')
const intro = ref('')
const loading = ref(true)
const works = ref<VideoFile[]>([])

async function loadAll() {
  loading.value = true
  try {
    let authorId: number | null = null
    const param = userId.value

    // 判断参数是用户ID（数字）还是用户名（非数字）
    if (/^\d+$/.test(param)) {
      authorId = parseInt(param, 10)
    } else {
      // 按用户名先查用户信息
      try {
        const infoRes = await fetch(`/api/v1/user/info-by-username?username=${encodeURIComponent(param)}`)
        if (infoRes.ok) {
          const infoData = await infoRes.json()
          if (infoData.data) {
            authorId = infoData.data.userId
            displayName.value = infoData.data.nickname || param
            avatarUrl.value = infoData.data.avatar || ''
            intro.value = infoData.data.intro || ''
            usernameRef.value = infoData.data.username || param
          }
        }
      } catch { /* ignore, continue fallback */ }
    }

    // 1. 用 authorId 从 Java 获取该用户的简介和公开作品列表
    if (authorId) {
      const ir = await fetch(`/api/v1/user/author/home?authorId=${authorId}`)
      if (ir.ok) {
        const idata = await ir.json()
        const info = idata.data?.authorInfo
        if (info) {
          displayName.value = info.nickname || displayName.value
          avatarUrl.value = info.avatar || avatarUrl.value
          intro.value = info.intro || ''
          if (!usernameRef.value) usernameRef.value = info.username || ''
        }
        // 该作者的公开作品
        const wList = idata.data?.workList || []
        if (wList.length > 0) {
          works.value = wList.map((w: any) => ({
            filename: w.videoPath?.split('/').pop() || '',
            task_id: w.videoPath?.split('/').pop()?.replace('.mp4','') || '',
            size_bytes: 0, size_mb: 0,
            created_at: w.createTime || '',
            url: w.videoPath || '',
            poster: '',
            title: w.title || '',
          }))
        }
      }
    }

    // 1b. fallback: 无 authorId 时从社区 API 获取头像和昵称
    if (!authorId && !/^\d+$/.test(param)) {
      try {
        const gRes = await fetch(`/api/v1/gallery/list?sort=time&size=100`)
        if (gRes.ok) {
          const gData = await gRes.json()
          // 精确匹配或前缀匹配（登录名"李哲希爸爸" vs 昵称"李哲希的爸爸"）
          const list = gData.data?.list || []
          let userPost = list.find((p: any) => p.authorName === param)
            || list.find((p: any) => p.authorName && param && p.authorName.includes(param))
            || list.find((p: any) => param && p.authorName && param.includes(p.authorName.replace('的', '')))
          if (userPost) {
            displayName.value = userPost.authorName || param
            avatarUrl.value = userPost.authorAvatar || ''
          }
        }
      } catch { /* ignore */ }
    }

    // 2. Fallback: 如果 Java 没有公开作品，尝试从 Python 后端按用户名查公开作品
    if (works.value.length === 0) {
      const tryName = usernameRef.value || (!/^\d+$/.test(param) ? param : '')
      if (tryName) {
        try {
          const pyRes = await fetch(`/api/videos/list?my_works=true&username=${encodeURIComponent(tryName)}&published=true`)
          if (pyRes.ok) {
            const pyData = await pyRes.json()
            if (pyData.data?.items?.length > 0) {
              works.value = pyData.data.items
            }
          }
        } catch { /* ignore */ }
      }
    }
  } catch { /* ignore */ }
  finally { loading.value = false }
}

onMounted(() => { loadAll() })
watch(() => route.params.userId, () => {
  if (route.params.userId) {
    // 切换用户时重置数据并重新加载
    works.value = []
    intro.value = ''
    loadAll()
  }
})
</script>

<template>
  <div class="user-profile-page">
    <el-button link @click="router.back()" style="margin-bottom:12px">
      <el-icon><ArrowLeft /></el-icon> 返回
    </el-button>

    <!-- 用户信息卡片 -->
    <RevealOnScroll>
      <div class="user-header glass-card">
        <AvatarIcon :name="displayName" :size="80" :avatar-url="avatarUrl" />
        <h2>{{ displayName }}</h2>
        <p class="user-id">@{{ displayName }}</p>
        <div v-if="intro" class="user-bio">{{ intro }}</div>
        <div v-else class="user-bio-placeholder">这个人很懒，还没有填写个人简介…</div>
      </div>
    </RevealOnScroll>

    <!-- 统计数据 -->
    <div class="user-stats">
      <RevealOnScroll :delay="0">
        <div class="stat-card glass-card">
          <el-icon :size="28" color="var(--accent-purple)"><PictureFilled /></el-icon>
          <h4>作品</h4>
          <span class="count">{{ works.length }}</span>
        </div>
      </RevealOnScroll>
    </div>

    <!-- 作品列表 -->
    <div class="user-works" v-loading="loading">
      <h3 v-if="works.length > 0" style="margin-bottom:16px;color:var(--text-primary)">作品列表</h3>
      <div class="works-grid">
        <div v-for="v in works" :key="v.filename" class="work-card glass-card" @click="router.push(`/gallery/${v.filename}`)">
          <div class="work-thumb">
            <img
              :src="v.poster || videosApi.getThumbnailUrl(v.filename)"
              loading="lazy"
              class="work-thumb-img"
              @error="($event.target as HTMLImageElement).style.display='none'"
              :alt="(v as any).title || v.filename"
            />
            <div class="work-play-overlay"><el-icon :size="24"><VideoPlay /></el-icon></div>
          </div>
          <div class="work-info">
            <h4 :title="(v as any).title || v.filename">{{ (v as any).title || v.filename }}</h4>
            <span class="work-size">{{ v.size_mb }} MB · {{ v.created_at?.slice(0, 10) }}</span>
          </div>
        </div>
      </div>
    </div>

    <div v-if="!loading && works.length === 0" class="empty-state">
      <el-empty description="该用户还没有公开作品" />
    </div>
  </div>
</template>

<style scoped>
.user-profile-page { max-width: 800px; margin: 0 auto; padding: var(--space-xl); }
.user-header { text-align: center; padding: var(--space-2xl); margin-bottom: var(--space-xl); }
.user-header h2 { margin: var(--space-md) 0 var(--space-xs); font-size: 1.3rem; font-weight: 700; color: var(--text-primary); }
.user-id { color: var(--text-tertiary); font-size: 0.9rem; margin-bottom: var(--space-md); }
.user-bio-placeholder { display: flex; align-items: center; justify-content: center; gap: 6px; color: var(--text-tertiary); font-size: 0.85rem; padding: var(--space-sm); border: 1px dashed var(--border-color); border-radius: var(--radius-md); max-width: 360px; margin: 0 auto; }
.user-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: var(--space-md); margin-bottom: var(--space-xl); }
.stat-card { text-align: center; padding: var(--space-lg); }
.stat-card h4 { font-size: 0.85rem; color: var(--text-secondary); margin: var(--space-sm) 0; }
.count { font-size: 1.8rem; font-weight: 800; color: var(--text-primary); }
.user-works h3 { font-size: 1.05rem; font-weight: 700; }
.works-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(240px, 1fr)); gap: var(--space-md); }
.work-card { cursor: pointer; overflow: hidden; padding: 0; }
.work-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.work-thumb { position: relative; aspect-ratio: 16/9; background: var(--bg-secondary); overflow: hidden; }
.work-thumb-img { width: 100%; height: 100%; object-fit: cover; }
.work-play-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.3); opacity: 0; transition: opacity var(--transition-fast); color: white; }
.work-card:hover .work-play-overlay { opacity: 1; }
.work-info { padding: var(--space-sm) var(--space-md); }
.work-info h4 { font-size: 0.85rem; font-weight: 600; color: var(--text-primary); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.work-size { font-size: 0.72rem; color: var(--text-tertiary); }
.empty-state { text-align: center; padding: var(--space-3xl); }
</style>

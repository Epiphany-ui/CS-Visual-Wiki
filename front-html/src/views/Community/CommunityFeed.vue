<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import PageHeader from '@/components/common/PageHeader.vue'
import AvatarIcon from '@/components/common/AvatarIcon.vue'

const router = useRouter()
const posts = ref<any[]>([])
const loading = ref(true)
const sortBy = ref<'time' | 'likes' | 'views'>('time')
const showVideo = ref<number | null>(null)

async function loadPosts() {
  loading.value = true
  try {
    const res = await fetch(`/api/v1/gallery/list?sort=${sortBy.value}`)
    const data = await res.json()
    posts.value = (data.data?.list || []).map((w: any) => ({
      ...w,
      authorName: w.authorName || '匿名用户',
      text: w.description || '',
      time: w.createTime || '',
    }))
  } catch { /* Java backend may not be running */ }
  finally { loading.value = false }
}

function formatTime(t: string) {
  if (!t) return ''
  const d = new Date(t)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

onMounted(loadPosts)
</script>

<template>
  <div class="community-page">
    <PageHeader title="社区广场" description="分享作品，交流心得，发现灵感" icon="User" />

    <!-- 排序 -->
    <div class="comm-toolbar">
      <el-radio-group v-model="sortBy" size="small" @change="loadPosts">
        <el-radio-button value="time">最新</el-radio-button>
        <el-radio-button value="likes">最多点赞</el-radio-button>
        <el-radio-button value="views">最多浏览</el-radio-button>
      </el-radio-group>
    </div>

    <!-- 动态列表 -->
    <div class="comm-feed" v-loading="loading">
      <div v-for="post in posts" :key="post.id" class="post-card glass-card">
        <!-- 作者信息 -->
        <div class="post-header">
          <AvatarIcon :name="post.authorName" :size="40" :avatar-url="post.authorAvatar || ''" />
          <div class="post-author-info">
            <span class="post-author-name">{{ post.authorName }}</span>
            <span class="post-time">{{ formatTime(post.time) }}</span>
          </div>
        </div>

        <!-- 文字内容 -->
        <div class="post-body">
          <h3 class="post-title">{{ post.title }}</h3>
          <p v-if="post.text" class="post-text">{{ post.text }}</p>
        </div>

        <!-- 嵌入视频 -->
        <div v-if="post.videoPath" class="post-video" @click="showVideo = showVideo === post.id ? null : post.id">
          <div v-if="showVideo === post.id" class="post-video-player">
            <video :src="`/videos/${post.videoPath.split('/').pop()}`" controls autoplay class="post-video-el" />
          </div>
          <div v-else class="post-video-thumb">
            <img v-if="post.cover" :src="post.cover" class="post-thumb-img" />
            <div v-else class="post-thumb-placeholder">
              <el-icon :size="40"><VideoPlay /></el-icon>
            </div>
            <div class="post-play-overlay"><el-icon :size="28"><VideoPlay /></el-icon></div>
          </div>
        </div>

        <!-- 互动栏 -->
        <div class="post-actions">
          <span class="post-action"><el-icon><Star /></el-icon> {{ post.likeCount || 0 }}</span>
          <span class="post-action"><el-icon><ChatDotRound /></el-icon> 评论</span>
          <span class="post-action"><el-icon><Share /></el-icon> Fork</span>
          <span class="post-action"><el-icon><View /></el-icon> {{ post.viewCount || 0 }}</span>
        </div>
      </div>
    </div>

    <div v-if="!loading && posts.length === 0" class="empty-state">
      <el-empty description="社区还没有动态，快去沙箱发布作品吧！" />
      <el-button type="primary" round @click="router.push('/sandbox')">去沙箱创作</el-button>
    </div>
  </div>
</template>

<style scoped>
.community-page { padding-bottom: var(--space-3xl); }
.comm-toolbar { max-width: 680px; margin: 0 auto var(--space-lg); padding: 0 var(--space-xl); }
.comm-feed { max-width: 680px; margin: 0 auto; padding: 0 var(--space-xl); display: flex; flex-direction: column; gap: var(--space-md); }

.post-card { padding: var(--space-lg); }
.post-header { display: flex; align-items: center; gap: var(--space-sm); margin-bottom: var(--space-md); }
.post-author-info { display: flex; flex-direction: column; }
.post-author-name { font-size: 0.9rem; font-weight: 600; color: var(--text-primary); }
.post-time { font-size: 0.75rem; color: var(--text-tertiary); }

.post-body { margin-bottom: var(--space-md); }
.post-title { font-size: 1.05rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.post-text { font-size: 0.9rem; color: var(--text-secondary); line-height: 1.6; }

.post-video { cursor: pointer; border-radius: var(--radius-md); overflow: hidden; margin-bottom: var(--space-md); }
.post-video-player { aspect-ratio: 16/9; background: #000; }
.post-video-el { width: 100%; height: 100%; }
.post-video-thumb { position: relative; aspect-ratio: 16/9; background: var(--bg-secondary); overflow: hidden; }
.post-thumb-img { width: 100%; height: 100%; object-fit: cover; }
.post-thumb-placeholder { width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; color: var(--text-tertiary); }
.post-play-overlay { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; background: rgba(0,0,0,0.4); color: #fff; opacity: 0; transition: opacity var(--transition-fast); }
.post-video-thumb:hover .post-play-overlay { opacity: 1; }

.post-actions { display: flex; gap: var(--space-lg); }
.post-action { display: flex; align-items: center; gap: 4px; font-size: 0.82rem; color: var(--text-tertiary); cursor: pointer; transition: color var(--transition-fast); }
.post-action:hover { color: var(--accent-purple-light); }

.empty-state { text-align: center; padding: var(--space-3xl); }
</style>

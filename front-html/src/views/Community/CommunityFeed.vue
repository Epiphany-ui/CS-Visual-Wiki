<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import AvatarIcon from '@/components/common/AvatarIcon.vue'
import { videosApi } from '@/api/videos'
import { communityApi, type Comment } from '@/api/community'

const router = useRouter()
const posts = ref<any[]>([])
const deletingPost = ref<Set<number>>(new Set())

async function handleDeletePost(post: any) {
  try {
    await ElMessageBox.confirm('确定要删除该作品吗？此操作不可恢复。', '删除确认', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }
  deletingPost.value.add(post.id)
  try {
    const token = localStorage.getItem('token')
    const res = await fetch(`/api/v1/work/${post.id}`, {
      method: 'DELETE',
      headers: token ? { 'Authorization': `Bearer ${token}` } : {},
    })
    if (res.ok) {
      posts.value = posts.value.filter(p => p.id !== post.id)
      ElMessage.success('删除成功')
    } else {
      ElMessage.error('删除失败')
    }
  } catch { ElMessage.error('删除失败，请检查网络') }
  finally { deletingPost.value.delete(post.id) }
}
const loading = ref(true)
const sortBy = ref<'time' | 'likes' | 'views'>('time')
const showVideo = ref<number | null>(null)
const expandedComments = ref<Set<number>>(new Set())
const commentInputs = reactive<Record<number, string>>({})
const currentUser = ref(localStorage.getItem('username') || '')
const currentDisplayName = ref(localStorage.getItem(`cs:nickname:${currentUser.value}`) || '')
const currentAvatar = ref(localStorage.getItem(`cs:avatar:${currentUser.value}`) || '')

function getThumbnailUrl(post: any): string {
  if (post.cover) return post.cover
  const vp = post.videoPath || ''
  const fn = vp.split('/').pop()
  if (fn) return videosApi.getThumbnailUrl(fn)
  return ''
}

async function loadPosts() {
  loading.value = true
  try {
    const res = await fetch(`/api/v1/gallery/list?sort=${sortBy.value}`)
    const data = await res.json()
    const list: any[] = data.data?.list || []
    const ids = list.map((w: any) => w.workId).filter(Boolean)
    let likeCounts: Record<number, number> = {}
    let viewCounts: Record<number, number> = {}
    let userLiked: Record<number, boolean> = {}
    try {
      const [lRes, vRes, cRes] = await Promise.all([
        communityApi.getLikeCounts(ids),
        communityApi.getViewCounts(ids),
        currentUser.value ? communityApi.checkLiked(ids, currentUser.value) : Promise.resolve(null),
      ])
      likeCounts = lRes.data.data?.counts || {}
      viewCounts = vRes.data.data?.counts || {}
      userLiked = cRes?.data.data?.liked || {}
    } catch { /* ignore */ }

    posts.value = list.map((w: any) => ({
      ...w,
      id: w.workId,
      authorName: w.authorName || '匿名用户',
      text: w.description || '',
      time: w.createTime || '',
      thumbnailUrl: getThumbnailUrl(w),
      _likes: likeCounts[w.workId] || w.likeCount || 0,
      _views: viewCounts[w.workId] || w.viewCount || 0,
      _liked: !!userLiked[w.workId],
      _comments: [] as Comment[],
      _commentTotal: 0,
    }))
    if (sortBy.value === 'likes') {
      posts.value.sort((a, b) => b._likes - a._likes)
    } else if (sortBy.value === 'views') {
      posts.value.sort((a, b) => b._views - a._views)
    }
  } catch { /* Java backend may not be running */ }
  finally { loading.value = false }
}

// --- 点赞 ---
async function handleLike(post: any) {
  if (!currentUser.value) return
  try {
    const res = await communityApi.toggleLike(post.id, currentUser.value)
    post._liked = res.data.data?.liked ?? false
    post._likes = res.data.data?.count ?? post._likes
  } catch { /* ignore */ }
}

// --- 浏览量 ---
function handleVideoPlay(post: any) {
  communityApi.incrementView(post.id).then(res => {
    post._views = res.data.data?.count ?? post._views + 1
  }).catch(() => {})
}

// --- 评论 ---
function toggleComments(postId: number) {
  if (expandedComments.value.has(postId)) {
    expandedComments.value.delete(postId)
  } else {
    expandedComments.value.add(postId)
    loadComments(postId)
  }
  expandedComments.value = new Set(expandedComments.value)
}

async function loadComments(postId: number, limit = 50) {
  try {
    const res = await communityApi.getComments(postId, limit)
    const post = posts.value.find(p => p.id === postId)
    if (post) {
      post._comments = res.data.data?.comments || []
      post._commentTotal = res.data.data?.total || 0
    }
  } catch { /* ignore */ }
}

async function submitComment(postId: number) {
  const text = commentInputs[postId]?.trim()
  if (!text || !currentUser.value) return
  try {
    await communityApi.addComment(postId, currentDisplayName.value || currentUser.value, text, currentAvatar.value)
    commentInputs[postId] = ''
    loadComments(postId)
  } catch { /* ignore */ }
}

async function handleCommentLike(postId: number, commentId: string) {
  if (!currentUser.value) return
  try {
    await communityApi.likeComment(postId, commentId, currentUser.value)
    loadComments(postId)
  } catch { /* ignore */ }
}

// 初始加载评论预览
async function preloadTopComments() {
  for (const post of posts.value) {
    if (post.id) {
      try {
        const res = await communityApi.getComments(post.id, 3)
        post._comments = res.data.data?.comments || []
        post._commentTotal = res.data.data?.total || 0
      } catch { /* ignore */ }
    }
  }
}

// 评论头像兜底：优先用存储的 avatar，其次从同帖其他评论/帖子作者中查找
function getCommentAvatar(comment: any, post: any): string {
  if (comment.avatar) return comment.avatar
  // 如果是当前用户，用 localStorage 头像
  if (comment.username === currentUser.value || comment.username === currentDisplayName.value) return currentAvatar.value
  // 如果是帖子作者，用帖子的头像
  if (comment.username === post.authorName) return post.authorAvatar || ''
  // 从已有评论中查找同用户名有头像的
  const other = post._comments?.find((c: any) => c.username === comment.username && c.avatar)
  return other?.avatar || ''
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

onMounted(async () => { await loadPosts(); preloadTopComments() })
</script>

<template>
  <div class="community-page">
    <PageHeader title="社区广场" description="分享作品，交流心得，发现灵感" icon="User" />

    <div class="comm-toolbar">
      <el-radio-group v-model="sortBy" size="small" @change="loadPosts">
        <el-radio-button value="time">最新</el-radio-button>
        <el-radio-button value="likes">最多点赞</el-radio-button>
        <el-radio-button value="views">最多浏览</el-radio-button>
      </el-radio-group>
    </div>

    <div class="comm-feed" v-loading="loading">
      <div v-for="post in posts" :key="post.id" class="post-card glass-card">
        <!-- 作者信息 -->
        <div class="post-header">
          <div class="post-avatar-clickable" @click="router.push(`/user/${encodeURIComponent(post.authorName || '匿名用户')}`)">
            <AvatarIcon :name="post.authorName" :size="44" :avatar-url="post.authorAvatar || ''" />
          </div>
          <div class="post-author-info">
            <span class="post-author-name" @click="router.push(`/user/${encodeURIComponent(post.authorName || '匿名用户')}`)">{{ post.authorName }}</span>
            <span class="post-time">{{ formatTime(post.time) }}</span>
          </div>
          <button v-if="post.authorName === currentUser" class="post-del-btn" :disabled="deletingPost.has(post.id)" @click.stop="handleDeletePost(post)" title="删除作品">
            <el-icon :size="14"><Delete /></el-icon>
          </button>
        </div>

        <!-- 文字内容 -->
        <div class="post-body">
          <h3 class="post-title">{{ post.title }}</h3>
          <p v-if="post.text" class="post-text">{{ post.text }}</p>
        </div>

        <!-- 嵌入视频 -->
        <div v-if="post.videoPath" class="post-video" @click="showVideo = showVideo === post.id ? null : post.id">
          <div v-if="showVideo === post.id" class="post-video-player">
            <video :src="`/videos/${post.videoPath.split('/').pop()}`" controls autoplay class="post-video-el" @play="handleVideoPlay(post)" />
          </div>
          <div v-else class="post-video-thumb">
            <img v-if="post.thumbnailUrl" :src="post.thumbnailUrl" class="post-thumb-img" @error="($event.target as HTMLImageElement).style.display='none'" />
            <div v-if="!post.thumbnailUrl" class="post-thumb-placeholder">
              <el-icon :size="40"><VideoPlay /></el-icon>
            </div>
            <div class="post-play-overlay"><el-icon :size="28"><VideoPlay /></el-icon></div>
          </div>
        </div>

        <!-- 互动栏 -->
        <div class="post-actions">
          <span class="post-action" :class="{ 'action-active': post._liked }" @click="handleLike(post)">
            {{ post._liked ? '👍' : '👍🏻' }} {{ post._likes }}
          </span>
          <span class="post-action" @click="toggleComments(post.id)">
            💬 {{ post._commentTotal || '' }}
          </span>
          <span class="post-action">
            🔗 Fork
          </span>
          <span class="post-action">
            👁 {{ post._views }}
          </span>
        </div>

        <!-- 评论预览（点赞数最高的 3 条） -->
        <div v-if="post._comments.length > 0 && !expandedComments.has(post.id)" class="comments-preview">
          <div v-for="c in post._comments.slice(0, 3)" :key="c.id" class="comment-item">
            <AvatarIcon :name="c.username" :size="22" :avatar-url="getCommentAvatar(c, post)" />
            <div class="comment-body">
              <span class="comment-name">{{ c.username }}</span>
              <span class="comment-text">{{ c.text }}</span>
            </div>
            <span class="comment-likes" @click.stop="handleCommentLike(post.id, c.id)">👍🏻 {{ c.likes }}</span>
          </div>
          <div v-if="post._commentTotal > 3" class="comments-toggle" @click="toggleComments(post.id)">
            查看全部 {{ post._commentTotal }} 条评论 →
          </div>
        </div>

        <!-- 展开评论区 -->
        <div v-if="expandedComments.has(post.id)" class="comments-expanded">
          <div v-for="c in post._comments" :key="c.id" class="comment-item">
            <AvatarIcon :name="c.username" :size="28" :avatar-url="getCommentAvatar(c, post)" />
            <div class="comment-body">
              <div class="comment-header">
                <span class="comment-name">{{ c.username }}</span>
                <span class="comment-likes" @click="handleCommentLike(post.id, c.id)">
                  👍🏻 {{ c.likes }}
                </span>
              </div>
              <span class="comment-text">{{ c.text }}</span>
            </div>
          </div>
          <div v-if="post._comments.length === 0" class="comments-empty">暂无评论，来发表第一条吧</div>
          <div class="comment-input-row">
            <el-input v-model="commentInputs[post.id]" placeholder="写下你的评论..." size="small" @keyup.enter="submitComment(post.id)" />
            <el-button size="small" type="primary" @click="submitComment(post.id)" :disabled="!commentInputs[post.id]?.trim()">发送</el-button>
          </div>
          <div class="comments-toggle" @click="toggleComments(post.id)">收起 ↑</div>
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

/* ---- 排序栏 ---- */
.comm-toolbar {
  max-width: 680px; margin: 0 auto 28px; padding: 0 var(--space-xl);
  display: flex; justify-content: center;
}
.comm-toolbar :deep(.el-radio-button__inner) {
  padding: 8px 20px; font-size: 0.85rem; font-weight: 500;
  border: 1px solid var(--border-color); transition: all 0.2s;
}
.comm-toolbar :deep(.el-radio-button__original-radio:checked + .el-radio-button__inner) {
  background: var(--gradient-primary); border-color: transparent; box-shadow: 0 2px 8px rgba(124,58,237,0.3);
}

.comm-feed { max-width: 680px; margin: 0 auto; padding: 0 var(--space-xl); display: flex; flex-direction: column; gap: 20px; }

/* ---- 帖子卡片 ---- */
.post-card {
  padding: 28px;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: 16px;
  transition: all 0.25s ease;
}
.post-card:hover {
  border-color: var(--border-color-light);
  box-shadow: 0 4px 24px rgba(0,0,0,0.08);
}

/* ---- 作者区 ---- */
.post-header { display: flex; align-items: center; gap: 12px; margin-bottom: 18px; }
.post-avatar-clickable { cursor: pointer; transition: transform 0.2s ease; flex-shrink: 0; }
.post-avatar-clickable:hover { transform: scale(1.08); }
.post-author-info { display: flex; flex-direction: column; gap: 2px; }
.post-author-name {
  font-size: 0.92rem; font-weight: 650; color: var(--text-primary);
  cursor: pointer; transition: color 0.15s;
}
.post-author-name:hover { color: var(--accent-purple-light); }
.post-time { font-size: 0.75rem; color: var(--text-tertiary); letter-spacing: 0.02em; }
.post-del-btn {
  margin-left: auto; background: none; border: none; cursor: pointer;
  color: var(--text-tertiary); padding: 4px 8px; border-radius: 8px;
  transition: all 0.15s; font-size: 1rem; line-height: 1;
}
.post-del-btn:hover { color: #e74c3c; background: rgba(231,76,60,0.08); }

/* ---- 正文 ---- */
.post-body { margin-bottom: 20px; }
.post-title {
  font-size: 1.25rem; font-weight: 750; color: var(--text-primary);
  margin-bottom: 10px; line-height: 1.4; letter-spacing: -0.01em;
}
.post-text {
  font-size: 0.92rem; color: var(--text-secondary);
  line-height: 1.75; margin: 0;
}

/* ---- 视频 ---- */
.post-video {
  cursor: pointer; border-radius: 12px; overflow: hidden;
  margin-bottom: 18px; border: 1px solid var(--border-color);
  transition: border-color 0.2s;
}
.post-video:hover { border-color: var(--accent-purple); }
.post-video-player { aspect-ratio: 16/9; background: #000; }
.post-video-el { width: 100%; height: 100%; display: block; }
.post-video-thumb { position: relative; aspect-ratio: 16/9; background: var(--bg-secondary); overflow: hidden; }
.post-thumb-img { width: 100%; height: 100%; object-fit: cover; transition: transform 0.3s ease; }
.post-video:hover .post-thumb-img { transform: scale(1.03); }
.post-thumb-placeholder {
  width: 100%; height: 100%; display: flex; align-items: center;
  justify-content: center; color: var(--text-tertiary);
  background: linear-gradient(135deg, var(--bg-secondary) 0%, var(--bg-card) 100%);
}
.post-play-overlay {
  position: absolute; inset: 0; display: flex; align-items: center;
  justify-content: center; background: rgba(0,0,0,0.35); color: #fff;
  opacity: 0; transition: opacity 0.25s ease; backdrop-filter: blur(2px);
}
.post-video-thumb:hover .post-play-overlay { opacity: 1; }

/* ---- 互动栏 ---- */
.post-actions {
  display: flex; gap: 6px; margin-bottom: 0; padding: 4px 0;
  flex-wrap: wrap;
}
.post-action {
  display: inline-flex; align-items: center; gap: 5px;
  font-size: 0.85rem; color: var(--text-tertiary);
  cursor: pointer; user-select: none;
  padding: 6px 14px; border-radius: 20px;
  background: var(--bg-secondary);
  border: 1px solid transparent;
  transition: all 0.2s ease;
}
.post-action:hover {
  color: var(--text-primary);
  background: var(--bg-card-hover);
  border-color: var(--border-color);
  transform: translateY(-1px);
}
.post-action.action-active {
  color: #e8a840;
  background: rgba(232,168,64,0.1);
  border-color: rgba(232,168,64,0.25);
}

/* ---- 评论预览 ---- */
.comments-preview {
  margin-top: 14px; padding-top: 14px;
  border-top: 1px solid var(--border-color);
}
.comments-expanded {
  margin-top: 14px; padding-top: 14px;
  border-top: 1px solid var(--border-color);
}
.comment-item {
  display: flex; gap: 10px; padding: 8px 0; align-items: flex-start;
}
.comment-body { flex: 1; min-width: 0; }
.comment-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 2px; }
.comment-name { font-size: 0.8rem; font-weight: 650; color: var(--text-secondary); }
.comment-text {
  font-size: 0.86rem; color: var(--text-primary);
  word-break: break-word; display: block; margin-top: 3px;
  line-height: 1.55; padding: 6px 10px;
  background: var(--bg-secondary);
  border-radius: 8px;
}
.comment-likes {
  font-size: 0.75rem; color: var(--text-tertiary); cursor: pointer;
  display: flex; align-items: center; gap: 3px;
  padding: 2px 8px; border-radius: 12px;
  transition: all 0.15s ease;
}
.comment-likes:hover { color: #e8a840; background: rgba(232,168,64,0.1); transform: scale(1.08); }
.comments-toggle {
  font-size: 0.8rem; color: var(--accent-purple-light);
  cursor: pointer; text-align: center; padding: 10px 0 4px;
  font-weight: 500; transition: opacity 0.15s;
}
.comments-toggle:hover { opacity: 0.8; }
.comments-empty { font-size: 0.82rem; color: var(--text-tertiary); text-align: center; padding: 12px 0; }
.comment-input-row { display: flex; gap: 8px; margin-top: 10px; }
.comment-input-row :deep(.el-input__wrapper) { background: var(--bg-secondary); border-radius: 20px; }

.empty-state { text-align: center; padding: 60px 0; }
</style>

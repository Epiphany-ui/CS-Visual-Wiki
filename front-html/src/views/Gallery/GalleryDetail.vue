<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { videosApi } from '@/api/videos'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCurrentUser } from '@/composables/useCurrentUser'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'
import AvatarIcon from '@/components/common/AvatarIcon.vue'

const PY_BASE = import.meta.env.VITE_PYTHON_BASE ?? ''

const route = useRoute()
const router = useRouter()
const { username, token } = useCurrentUser()
const filename = route.params.filename as string
const videoUrl = videosApi.getPlayUrl(filename)
const downloadUrl = videosApi.getDownloadUrl(filename)
const converting = ref(false)
const gifUrl = ref('')
const saved = ref(false)
const videoTitle = ref('')
const editingTitle = ref(false)
const titleInput = ref('')
const videoOwner = ref('')
const isOwner = ref(false)
const showSource = ref(false)
const sourceCode = ref('')

// 创作者信息（从 Java 画廊接口直接拿，authorId 即 userId）
const authorInfo = ref<{ userId: string | number; username: string; nickname: string; avatar: string; workId?: number }>({
  userId: '', username: '', nickname: '', avatar: '', workId: undefined,
})

// 相关推荐
interface RelatedItem {
  id: number
  title: string
  cover?: string
  authorName: string
  authorId?: number
  videoPath?: string
}
const relatedVideos = ref<RelatedItem[]>([])

// ========== 加载数据 ==========
async function loadTitle() {
  try {
    const res = await videosApi.getList(false)
    const items: any[] = res.data.data?.items || []
    const meta = items.find((v: any) => v.filename === filename)
    videoTitle.value = meta?.title || filename
    titleInput.value = videoTitle.value
    // 作者永远取服务端记录，不因当前登录用户而改变
    videoOwner.value = meta?.username || meta?.created_by || '匿名'
    const curUser = username.value
    // 判断是否为作者本人（或文件名与当前用户关联）
    isOwner.value = !!curUser && (videoOwner.value === curUser)
    isPublished.value = (meta as any)?.published === '1'
    // 从服务端获取真实源码
    const taskId = filename.replace('.mp4', '')
    try {
      const codeRes = await fetch(`/api/code/${taskId}.py`)
      if (codeRes.ok) {
        sourceCode.value = await codeRes.text()
      }
    } catch { /* ignore */ }
    if (!sourceCode.value) sourceCode.value = '// 源码未找到: ' + filename
  } catch { videoTitle.value = filename }
}

async function handleRename() {
  const newTitle = titleInput.value.trim()
  if (!newTitle) return
  try {
    await videosApi.renameVideo(filename, newTitle)
    videoTitle.value = newTitle
    editingTitle.value = false
    ElMessage.success('标题已更新')
  } catch { ElMessage.error('修改失败') }
}

async function checkSaved() {
  try {
    const res = await videosApi.getList(true, username.value)
    const items: { filename: string }[] = res.data.data?.items || []
    saved.value = items.some((v) => v.filename === filename)
  } catch { /* ignore */ }
}

const publishing = ref(false)
const publishDialogVisible = ref(false)
const publishDesc = ref('')

async function handlePublishToCommunity() {
  if (!token.value) { ElMessage.warning('请先登录再发布'); return }
  publishing.value = true
  try {
    const body = new URLSearchParams()
    body.append('workTitle', videoTitle.value || filename)
    body.append('workDesc', publishDesc.value)
    body.append('isPublic', 'true')
    body.append('code', sourceCode.value || '')
    body.append('previewUrl', videoUrl || '')
    const res = await fetch('/api/v1/work/publish', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token.value}`,
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: body.toString(),
    })
    const data = await res.json()
    if (data.code === 200) {
      publishDialogVisible.value = false
      // 发布到社区 = 自动设为公开
      videosApi.togglePublic(filename).then(() => { isPublished.value = true }).catch(() => {})
      ElMessage.success('已发布到社区！')
    } else {
      ElMessage.error(data.msg || data.message || '发布失败')
    }
  } catch (e) {
    ElMessage.error('发布失败：' + (e as Error).message)
  } finally {
    publishing.value = false
  }
}

async function handleSave() {
  try {
    const res = await videosApi.saveVideo(filename, username.value)
    saved.value = res.data.data?.saved ?? false
    ElMessage.success(saved.value ? '已收藏' : '已取消收藏')
  } catch {
    ElMessage.error('操作失败，请重试')
  }
}

function handleFork() {
  // 把源码写入 sessionStorage，沙箱 onMounted 会读取
  if (sourceCode.value) {
    sessionStorage.setItem('cs:forked-code', sourceCode.value)
  }
  router.push({ path: '/sandbox', query: { fork: filename, title: videoTitle.value } })
  ElMessage.success('已 Fork 到沙箱，开始你的二次创作吧！')
}

async function handleConvertGif() {
  converting.value = true
  try {
    const res = await videosApi.convertGif(filename)
    const data = res.data.data
    if (data) {
      gifUrl.value = `${PY_BASE}${data.url}`
      ElMessage.success(`GIF 转换完成（${data.size_kb}KB）`)
    }
  } catch { /* handled */ }
  finally { converting.value = false }
}

const deleting = ref(false)
const isPublished = ref(false)
async function handleTogglePublic() {
  try {
    const res = await videosApi.togglePublic(filename)
    isPublished.value = res.data.data?.published ?? false
    ElMessage.success(isPublished.value ? '已设为公开' : '已设为私有')
  } catch { ElMessage.error('操作失败') }
}

async function handleDelete() {
  try {
    await ElMessageBox.confirm('确定要删除该视频吗？此操作不可恢复。', '删除确认', {
      confirmButtonText: '删除', cancelButtonText: '取消', type: 'warning',
    })
  } catch { return }
  deleting.value = true
  try {
    await videosApi.deleteVideo(filename)
    ElMessage.success('已删除')
    router.push('/gallery')
  } catch { ElMessage.error('删除失败') }
  finally { deleting.value = false }
}

// ========== 从 Java 画廊接口加载作品信息（作者 + 推荐） ==========
function extractFilename(path: string): string {
  if (!path) return ''
  // 取最后一段，去掉查询参数和扩展名，统一小写
  const name = path.split('/').pop()?.split('?')[0] || ''
  return name.replace(/\.[^.]+$/, '').toLowerCase()
}

async function loadWorkFromGallery() {
  try {
    const res = await fetch('/api/v1/gallery/list?sort=time&size=200')
    const data = await res.json()
    const list: any[] = data.data?.list || []
    if (!list.length) return

    const targetFn = extractFilename(filename)

    // 1. 找到当前视频对应的作品，提取作者信息
    const currentWork = list.find((item: any) => {
      return extractFilename(item.videoPath) === targetFn
    })
    if (currentWork) {
      authorInfo.value = {
        userId: currentWork.authorId || '',
        username: currentWork.authorName || '',
        nickname: currentWork.authorName || '',
        avatar: currentWork.authorAvatar || '',
        workId: currentWork.workId,
      }
      videoOwner.value = currentWork.authorName || ''
      // 判断是否是作者本人
      const curUser = username.value
      if (curUser && currentWork.authorName === curUser) {
        isOwner.value = true
      }

      // 加载真实源码
      if (currentWork.workId) {
        try {
          const detailRes = await fetch(`/api/v1/work/public/detail?workId=${currentWork.workId}`)
          const detailData = await detailRes.json()
          if (detailData.code === 200 && detailData.data?.manimCode) {
            sourceCode.value = detailData.data.manimCode
          }
        } catch { /* 拿不到就保持默认模拟代码 */ }
      }
    }

    // 2. 相关推荐
    const authorId = authorInfo.value.userId
    const notCurrent = (item: any) => extractFilename(item.videoPath) !== targetFn

    // 同作者的最多取1条
    const sameAuthor = list
      .filter(notCurrent)
      .filter(i => authorId && i.authorId === authorId)
      .slice(0, 1)

    // 热门补齐，排除同作者已选的，且尽量不同作者
    const seenAuthors = new Set(sameAuthor.map(i => i.authorId))
    const hotFill = list
      .filter(notCurrent)
      .filter(i => !sameAuthor.find(s => s.workId === i.workId))
      .sort((a, b) => (b.likeCount || 0) - (a.likeCount || 0))
      .filter(item => {
        // 尽量多样化：同一个作者最多出现1次
        if (seenAuthors.has(item.authorId)) return false
        seenAuthors.add(item.authorId)
        return true
      })
      .slice(0, 3 - sameAuthor.length)

    relatedVideos.value = [...sameAuthor, ...hotFill].map((item: any) => ({
      id: item.workId,
      title: item.title,
      cover: item.cover,
      authorName: item.authorName || '匿名',
      authorId: item.authorId,
      videoPath: item.videoPath,
    }))
  } catch (e) {
    console.warn('[gallery-detail] load from gallery failed', e)
  }

  // 兜底：画廊匹配不到时，用 username 查 Java 接口拿 userId
  if (!authorInfo.value.userId && videoOwner.value) {
    try {
      const res = await fetch(`/api/v1/user/info-by-username?username=${encodeURIComponent(videoOwner.value)}`)
      const data = await res.json()
      if (data.code === 200 && data.data?.userId) {
        authorInfo.value.userId = data.data.userId
        authorInfo.value.nickname = data.data.nickname || videoOwner.value
        authorInfo.value.avatar = data.data.avatar || ''
      }
    } catch { /* 查不到就算了，跳转时走 username 兜底 */ }
  }
}

function goToUser() {
  if (authorInfo.value.userId) {
    router.push(`/user/${authorInfo.value.userId}`)
  } else if (videoOwner.value) {
    router.push(`/user/${videoOwner.value}`)
  }
}

onMounted(async () => {
  checkSaved()
  await loadTitle()
  loadWorkFromGallery()
})
</script>

<template>
  <div class="gallery-detail">
    <el-button link @click="router.back()" class="back-btn">
      <el-icon><ArrowLeft /></el-icon> 返回画廊
    </el-button>

    <div class="detail-layout">
      <!-- 左侧主内容 -->
      <div class="main-col">
        <RevealOnScroll>
          <!-- 标题 -->
          <div class="gd-title-row">
            <template v-if="editingTitle">
              <el-input v-model="titleInput" size="default" class="title-input" @keyup.enter="handleRename" />
              <el-button size="small" type="primary" @click="handleRename">确认</el-button>
              <el-button size="small" @click="editingTitle = false">取消</el-button>
            </template>
            <template v-else>
              <h1 class="video-title">{{ videoTitle }}</h1>
              <el-button v-if="isOwner" link size="small" @click="editingTitle = true">
                <el-icon><EditPen /></el-icon>
              </el-button>
            </template>
          </div>
        </RevealOnScroll>

        <RevealOnScroll :delay="80">
          <!-- 视频播放器 -->
          <div class="gd-player glass-card">
            <video :src="videoUrl" controls autoplay loop class="gd-video" />
          </div>
        </RevealOnScroll>

        <RevealOnScroll :delay="120">
          <!-- 操作按钮 -->
          <div class="gd-actions">
            <el-button round :type="saved ? 'warning' : 'default'" @click="handleSave" v-ripple>
              <el-icon><StarFilled v-if="saved" /><Star v-else /></el-icon>
              {{ saved ? '已收藏' : '收藏' }}
            </el-button>
            <el-button v-if="isOwner" round type="success" @click="publishDialogVisible = true" v-ripple>
              <el-icon><Upload /></el-icon> 发布到社区
            </el-button>
            <el-button round type="primary" @click="handleFork" v-ripple>
              <el-icon><CopyDocument /></el-icon> Fork 改编
            </el-button>
            <el-button round :loading="converting" @click="handleConvertGif">
              <el-icon><PictureFilled /></el-icon> 转 GIF
            </el-button>
            <el-button round>
              <el-icon><Download /></el-icon>
              <a :href="downloadUrl" download style="text-decoration:none;color:inherit">下载 MP4</a>
            </el-button>
            <el-button v-if="isOwner" round @click="handleTogglePublic">
              <el-icon><View /></el-icon> {{ isPublished ? '设为私有' : '设为公开' }}
            </el-button>
            <el-button v-if="isOwner" round type="danger" :loading="deleting" @click="handleDelete">
              <el-icon><Delete /></el-icon> 删除
            </el-button>
          </div>
        </RevealOnScroll>

        <RevealOnScroll :delay="160">
          <!-- GIF 预览 -->
          <div v-if="gifUrl" class="gd-gif glass-card">
            <h4>GIF 预览</h4>
            <img :src="gifUrl" class="gif-img" alt="GIF preview" />
          </div>
        </RevealOnScroll>

        <RevealOnScroll :delay="200">
          <!-- 源码查看 -->
          <div class="gd-source glass-card">
            <div class="source-header" @click="showSource = !showSource">
              <h4>Manim 源码</h4>
              <el-icon :class="{ rotate: showSource }"><ArrowDown /></el-icon>
            </div>
            <div v-show="showSource" class="source-code">
              <pre>{{ sourceCode }}</pre>
            </div>
          </div>
        </RevealOnScroll>
      </div>

      <!-- 右侧边栏 -->
      <div class="side-col">
        <RevealOnScroll :delay="100">
          <!-- 作者信息 -->
          <div class="author-card glass-card">
            <div class="author-header" @click="goToUser" style="cursor:pointer">
              <AvatarIcon :name="authorInfo.nickname || videoOwner || 'anon'" :size="48" :avatar-url="authorInfo.avatar || ''" />
              <div class="author-info">
                <div class="author-name">{{ authorInfo.nickname || videoOwner || '匿名创作者' }}</div>
                <div class="author-desc">创作者</div>
              </div>
            </div>
            <el-button v-if="!isOwner" type="primary" size="small" round full @click="goToUser" v-ripple>
              查看主页
            </el-button>
          </div>
        </RevealOnScroll>

        <RevealOnScroll :delay="150">
          <!-- 相关推荐 -->
          <div class="related-card glass-card">
            <h4>相关推荐</h4>
            <div class="related-list">
              <div
                v-for="v in relatedVideos"
                :key="v.id"
                class="related-item"
                @click="v.videoPath && router.push(`/gallery/${v.videoPath.split('/').pop()}`)"
              >
                <div class="related-thumb">
                  <img v-if="v.cover" :src="v.cover" class="related-thumb-img" />
                  <el-icon v-else><VideoPlay /></el-icon>
                </div>
                <div class="related-text">
                  <div class="related-title">{{ v.title }}</div>
                  <div class="related-author">{{ v.authorName }}</div>
                </div>
              </div>
              <div v-if="relatedVideos.length === 0" class="related-empty">
                暂无推荐作品
              </div>
            </div>
          </div>
        </RevealOnScroll>
      </div>
    </div>

    <!-- 发布到社区弹窗 -->
    <el-dialog v-model="publishDialogVisible" title="发布到社区" width="480px">
      <el-input v-model="publishDesc" type="textarea" :rows="4" placeholder="写一段描述介绍这个作品..." />
      <template #footer>
        <el-button @click="publishDialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="publishing" @click="handlePublishToCommunity">发布</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.gallery-detail {
  max-width: 1200px;
  margin: 0 auto;
  padding: var(--space-xl);
}
.back-btn {
  margin-bottom: var(--space-md);
  color: var(--text-secondary);
}

.detail-layout {
  display: grid;
  grid-template-columns: 1fr 300px;
  gap: var(--space-xl);
}
.main-col { display: flex; flex-direction: column; gap: var(--space-md); }
.side-col { display: flex; flex-direction: column; gap: var(--space-md); }

/* 标题 */
.gd-title-row {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
.video-title {
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin: 0;
}
.title-input { max-width: 400px; }

/* 播放器 */
.gd-player {
  overflow: hidden;
  border-radius: var(--radius-lg);
  padding: 0;
}
.gd-video { width: 100%; display: block; }

/* 操作按钮 */
.gd-actions {
  display: flex;
  gap: var(--space-sm);
  flex-wrap: wrap;
}

/* GIF */
.gd-gif { padding: var(--space-lg); }
.gd-gif h4 { margin: 0 0 var(--space-md); color: var(--text-primary); }
.gif-img { max-width: 100%; border-radius: var(--radius-md); }

/* 源码 */
.gd-source { padding: 0; overflow: hidden; }
.source-header {
  padding: var(--space-md) var(--space-lg);
  display: flex;
  justify-content: space-between;
  align-items: center;
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
}
.source-header h4 { margin: 0; color: var(--text-primary); font-size: 0.95rem; }
.source-header .el-icon {
  transition: transform var(--transition-normal);
  color: var(--text-tertiary);
}
.source-header .el-icon.rotate { transform: rotate(180deg); }
.source-code {
  padding: var(--space-lg);
  max-height: 400px;
  overflow: auto;
  background: var(--bg-secondary);
}
.source-code pre {
  margin: 0;
  font-family: 'JetBrains Mono', Consolas, monospace;
  font-size: 0.85rem;
  color: var(--text-secondary);
  line-height: 1.7;
  white-space: pre-wrap;
}

/* 作者卡片 */
.author-card { padding: var(--space-lg); }
.author-header {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  margin-bottom: var(--space-md);
}
.author-info { flex: 1; }
.author-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.95rem;
}
.author-desc {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

/* 相关推荐 */
.related-card { padding: var(--space-lg); }
.related-card h4 {
  margin: 0 0 var(--space-md);
  color: var(--text-primary);
  font-size: 0.95rem;
}
.related-list { display: flex; flex-direction: column; gap: var(--space-sm); }
.related-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: background var(--transition-fast);
  font-size: 0.85rem;
  color: var(--text-secondary);
}
.related-item:hover { background: var(--bg-card-hover); color: var(--text-primary); }
.related-thumb {
  width: 56px;
  height: 36px;
  background: var(--bg-secondary);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-tertiary);
  flex-shrink: 0;
  overflow: hidden;
}
.related-thumb-img { width: 100%; height: 100%; object-fit: cover; }
.related-text { flex: 1; min-width: 0; }
.related-title {
  font-size: 0.85rem;
  color: var(--text-primary);
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.related-author { font-size: 0.72rem; color: var(--text-tertiary); }
.related-empty {
  text-align: center;
  color: var(--text-tertiary);
  font-size: 0.8rem;
  padding: 16px 0;
}

@media (max-width: 900px) {
  .detail-layout { grid-template-columns: 1fr; }
  .side-col { order: -1; }
}
</style>

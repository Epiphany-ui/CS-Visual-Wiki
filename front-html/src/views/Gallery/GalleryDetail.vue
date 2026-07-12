<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { videosApi } from '@/api/videos'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useCurrentUser } from '@/composables/useCurrentUser'

const route = useRoute()
const router = useRouter()
const { username } = useCurrentUser()
const filename = route.params.filename as string
const videoUrl = videosApi.getPlayUrl(filename)
const downloadUrl = videosApi.getDownloadUrl(filename)
const converting = ref(false)
const gifUrl = ref('')
const saved = ref(false)
const videoTitle = ref('')
const editingTitle = ref(false)
const titleInput = ref('')
const videoOwner = ref('')       // 视频所有者用户名
const isOwner = ref(false)

async function loadTitle() {
  try {
    const res = await videosApi.getList(false)
    const items: any[] = res.data.data?.items || []
    const meta = items.find((v: any) => v.filename === filename)
    videoTitle.value = meta?.title || filename
    titleInput.value = videoTitle.value
    // 检查所有权
    videoOwner.value = meta?.username || meta?.created_by || ''
    const curUser = username.value
    // 检查所有权：视频 username 匹配当前用户，或视频在服务端 user-works 中
    if (curUser && videoOwner.value !== curUser) {
      // 异步查询服务端是否在 user-works 中（用于"匿名"视频的认领）
      videosApi.getMyWorks(curUser).then(res => {
        const myFiles = (res.data.data?.items || []).map((v: any) => v.filename)
        if (myFiles.includes(filename)) {
          videoOwner.value = curUser
          isOwner.value = true
        }
      }).catch(() => {})
    }
    isOwner.value = !!curUser && videoOwner.value === curUser
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

async function handleSave() {
  try {
    const res = await videosApi.saveVideo(filename, username.value)
    saved.value = res.data.data?.saved ?? false
    ElMessage.success(saved.value ? '已收藏' : '已取消收藏')
  } catch {
    ElMessage.error('操作失败，请重试')
  }
}

async function handleConvertGif() {
  converting.value = true
  try {
    const res = await videosApi.convertGif(filename)
    const data = res.data.data
    if (data) {
      gifUrl.value = `http://localhost:8000${data.url}`
      ElMessage.success(`GIF 转换完成（${data.size_kb}KB）`)
    }
  } catch { /* handled */ }
  finally { converting.value = false }
}

const deleting = ref(false)
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

onMounted(() => { checkSaved(); loadTitle() })
</script>

<template>
  <div class="gallery-detail">
    <el-button link @click="router.back()" style="margin-bottom:16px"><el-icon><ArrowLeft /></el-icon> 返回画廊</el-button>

    <!-- 标题 -->
    <div class="gd-title-row" style="margin-bottom:16px;display:flex;align-items:center;gap:8px">
      <template v-if="editingTitle">
        <el-input v-model="titleInput" size="default" style="max-width:400px" @keyup.enter="handleRename" />
        <el-button size="small" type="primary" @click="handleRename">确认</el-button>
        <el-button size="small" @click="editingTitle = false">取消</el-button>
      </template>
      <template v-else>
        <h2 style="font-size:1.3rem;font-weight:700;color:var(--text-primary)">{{ videoTitle }}</h2>
        <el-button link size="small" @click="editingTitle = true"><el-icon><EditPen /></el-icon></el-button>
      </template>
    </div>

    <!-- 视频播放器 -->
    <div class="gd-player glass-card">
      <video :src="videoUrl" controls autoplay loop class="gd-video" />
    </div>

    <div class="gd-actions">
      <el-button round><el-icon><Download /></el-icon> <a :href="downloadUrl" download style="text-decoration:none;color:inherit">下载 MP4</a></el-button>
      <el-button round :loading="converting" @click="handleConvertGif"><el-icon><PictureFilled /></el-icon> 转为 GIF</el-button>
      <el-button round :type="saved ? 'warning' : 'default'" @click="handleSave">
        <el-icon><StarFilled v-if="saved" /><Star v-else /></el-icon> {{ saved ? '已收藏' : '收藏' }}
      </el-button>
      <el-button v-if="isOwner" round type="danger" :loading="deleting" @click="handleDelete">
        <el-icon><Delete /></el-icon> 删除
      </el-button>
    </div>

    <div v-if="gifUrl" class="gd-gif glass-card" style="margin-top:16px;padding:16px;">
      <h4>GIF 预览</h4>
      <img :src="gifUrl" style="max-width:100%;border-radius:8px;" alt="GIF preview" />
    </div>
  </div>
</template>

<style scoped>
.gallery-detail { max-width: 800px; margin: 0 auto; padding: var(--space-xl); }
.gd-player { overflow: hidden; border-radius: var(--radius-lg); }
.gd-video { width: 100%; display: block; }
.gd-actions { display: flex; gap: var(--space-md); margin-top: var(--space-lg); flex-wrap: wrap; }
</style>

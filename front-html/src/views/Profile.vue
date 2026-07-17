<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'
import { videosApi } from '@/api/videos'
import AvatarIcon from '@/components/common/AvatarIcon.vue'
import CountNumber from '@/components/common/CountNumber.vue'
import { useCurrentUser } from '@/composables/useCurrentUser'

const PY_BASE = import.meta.env.VITE_PYTHON_BASE ?? ''

const userStore = useUserStore()
const router = useRouter()
const { username, avatar: avatarUrl, displayName, token, userKey, refresh } = useCurrentUser()

const myWorksCount = ref(0)
const myStarsCount = ref(0)

const editingNickname = ref(false)
const editingBio = ref(false)
const nickname = ref(displayName.value)
const bio = ref(localStorage.getItem(userStore.username ? userKey('bio') : '') || '')

async function saveBio() {
  const text = bio.value.trim()
  localStorage.setItem(userKey('bio'), text)
  editingBio.value = false
  ElMessage.success('简介已更新')
  const ok = await syncProfileToBackend({ intro: text })
  if (!ok) ElMessage.warning('简介已本地保存，但同步到服务器失败')
}

async function syncProfileToBackend(fields: Record<string, string>, retries = 2): Promise<boolean> {
  if (!token.value) return false
  const params = new URLSearchParams(fields).toString()
  for (let i = 0; i <= retries; i++) {
    try {
      const res = await fetch(`/api/v1/user/profile/update?${params}`, {
        method: 'PUT',
        headers: { 'Authorization': `Bearer ${token.value}` },
      })
      if (res.ok) return true
    } catch { /* retry */ }
    if (i < retries) await new Promise(r => setTimeout(r, 500))
  }
  return false
}

async function saveNickname() {
  const name = nickname.value.trim()
  if (!name) return
  localStorage.setItem(userKey('nickname'), name)
  // 同步更新 login 时的 username（AppHeader 等组件 fallback 时会用到）
  localStorage.setItem('username', name)
  refresh() // 通知 composable 重新读取 localStorage
  editingNickname.value = false
  ElMessage.success('昵称已更新')
  // 异步同步到 Java 后端
  const ok = await syncProfileToBackend({ nickname: name })
  if (!ok) {
    ElMessage.warning('昵称已本地保存，但同步到服务器失败，重启后社区可能显示旧名字')
  }
}

function getMyWorksCount(): number {
  try {
    const u = username.value || 'anon'
    const works = JSON.parse(localStorage.getItem(`cs:my-works:${u}`) || '[]')
    return works.length
  } catch { return 0 }
}

// 从服务端加载我的作品数量（跨设备同步）
const serverWorksCount = ref(0)
async function loadServerWorksCount() {
  const name = username.value
  if (!name) return
  try {
    const r = await fetch(`/api/videos/list?my_works=true&username=${encodeURIComponent(name)}`)
    const d = await r.json()
    serverWorksCount.value = d.data?.total || 0
  } catch { /* ignore */ }
}

// 从 Java 后端加载作品总数（包含所有状态：草稿/发布/公开/私有）
const javaWorkCount = ref(0)
async function loadJavaWorkCount() {
  if (!token.value) return
  try {
    const res = await fetch('/api/v1/user/home/data', {
      headers: { 'Authorization': `Bearer ${token.value}` },
    })
    const data = await res.json()
    if (data.code === 200 && data.data?.workCount != null) {
      javaWorkCount.value = data.data.workCount
    }
  } catch { /* ignore */ }
}

// 同步 localStorage 的作品到服务端
async function syncWorksToServer() {
  const name = username.value
  if (!name) return
  try {
    const works = JSON.parse(localStorage.getItem(`cs:my-works:${name}`) || '[]')
    if (works.length > 0) {
      await videosApi.syncMyWorks(name, works)
      await loadServerWorksCount()
    }
  } catch { /* ignore */ }
}

// 自动将 localStorage 中已有的头像和昵称同步到 Java 后端
async function syncExistingProfileToBackend() {
  const fields: Record<string, string> = {}
  if (avatarUrl.value) fields.avatar = avatarUrl.value
  if (displayName.value) fields.nickname = displayName.value
  if (Object.keys(fields).length > 0) {
    await syncProfileToBackend(fields)
  }
}

async function loadStarsCount() {
  try {
    const res = await videosApi.getList(true, userStore.username)
    myStarsCount.value = res.data.data?.total || 0
  } catch { /* ignore */ }
}

async function handleAvatarUpload(e: Event) {
  const file = (e.target as HTMLInputElement).files?.[0]
  if (!file) return
  if (file.size > 2 * 1024 * 1024) { ElMessage.warning('头像不能超过 2MB'); return }
  const form = new FormData()
  form.append('file', file)
  try {
    const res = await fetch(`${PY_BASE}/api/user/avatar`, { method: 'POST', body: form })
    const data = await res.json()
    if (data.code === 0 && data.data?.url) {
      const fullUrl = `${PY_BASE}${data.data.url}`
      localStorage.setItem(userKey('avatar'), fullUrl)
      refresh() // 通知 composable 重新读取 localStorage
      ElMessage.success('头像已更新')
      // 同步头像 URL 到 Java 后端数据库
      const ok = await syncProfileToBackend({ avatar: fullUrl })
      if (!ok) {
        ElMessage.warning('头像已本地保存，但同步到服务器失败，其他用户可能看不到新头像')
      }
    } else {
      ElMessage.error(data.message || '上传失败')
    }
  } catch { ElMessage.error('上传失败，请检查网络') }
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出')
  router.push('/')
}

// 从 Java 后端拉取最新头像/昵称，更新 localStorage（跨设备同步）
async function pullProfileFromBackend() {
  if (!token.value) return
  try {
    const res = await fetch('/api/v1/user/info', { headers: { 'Authorization': `Bearer ${token.value}` } })
    if (!res.ok) return
    const data = (await res.json()).data
    if (data) {
      if (data.nickname) {
        localStorage.setItem(userKey('nickname'), data.nickname)
        nickname.value = data.nickname
      }
      if (data.avatar) {
        localStorage.setItem(userKey('avatar'), data.avatar)
      }
      refresh() // 通知 composable 重新读取 localStorage
    }
  } catch { /* ignore */ }
}

onMounted(() => {
  myWorksCount.value = getMyWorksCount()
  loadStarsCount()
  loadServerWorksCount().then(() => syncWorksToServer())
  loadJavaWorkCount()
  // 从 Java 后端拉取最新数据（覆盖本地），然后同步本地未同步的数据
  pullProfileFromBackend().then(() => syncExistingProfileToBackend())
})
// username 异步初始化时自动重试
watch(username, (name) => {
  if (name) loadServerWorksCount()
})
</script>

<template>
  <div class="profile-page">
    <RevealOnScroll>
      <div class="profile-header glass-card" style="animation: scale-in 0.6s var(--ease-bounce) both">
        <div class="avatar-upload-wrap" @click="($refs.avatarInput as any).click()">
          <AvatarIcon :name="userStore.username" :size="72" :avatar-url="avatarUrl" />
          <span class="avatar-hint">点击更换头像</span>
        </div>
        <input ref="avatarInput" type="file" accept="image/*" style="display:none" @change="handleAvatarUpload" />
        <div v-if="editingNickname" style="display:flex;gap:8px;justify-content:center;align-items:center;margin-top:8px">
          <el-input v-model="nickname" size="small" style="width:180px" @keyup.enter="saveNickname" />
          <el-button size="small" type="primary" @click="saveNickname">确认</el-button>
          <el-button size="small" @click="editingNickname = false; nickname = displayName">取消</el-button>
        </div>
        <h2 v-else style="cursor:pointer" @click="editingNickname = true">
          {{ nickname }} <el-icon :size="14"><EditPen /></el-icon>
        </h2>
        <p>ID: {{ userStore.userId }}</p>
        <!-- 个人简介 -->
        <div v-if="editingBio" style="display:flex;gap:8px;justify-content:center;align-items:center;margin-top:8px">
          <el-input v-model="bio" size="small" style="width:260px" maxlength="200" show-word-limit placeholder="介绍一下自己..." @keyup.enter="saveBio" />
          <el-button size="small" type="primary" @click="saveBio">确认</el-button>
          <el-button size="small" @click="editingBio = false">取消</el-button>
        </div>
        <p v-else style="cursor:pointer;margin-top:4px;color:var(--text-secondary);font-size:0.85rem" @click="editingBio = true">
          {{ bio || '点击添加个人简介...' }} <el-icon :size="12"><EditPen /></el-icon>
        </p>
        <el-button type="primary" round v-ripple @click="router.push('/sandbox')"><el-icon><EditPen /></el-icon> 开始创作</el-button>
      </div>
    </RevealOnScroll>

    <div class="profile-grid">
      <RevealOnScroll v-for="(card, i) in [
        { icon: 'PictureFilled', color: 'var(--accent-purple)', label: '我的作品', count: javaWorkCount.value || serverWorksCount.value || myWorksCount || 0, click: () => router.push('/gallery?tab=my-works') },
        { icon: 'Star', color: 'var(--accent-orange)', label: '我的收藏', count: myStarsCount, click: () => router.push('/gallery?tab=stars') },
        { icon: 'Collection', color: 'var(--accent-cyan)', label: '词条贡献', count: 0, click: () => router.push('/wiki') },
        { icon: 'Clock', color: 'var(--accent-green)', label: '模板贡献', count: 0, click: () => router.push('/templates') },
      ]" :key="card.label" :delay="i * 100">
        <div class="pf-card glass-card" v-tilt @click="card.click()">
          <el-icon :size="32" :color="card.color">
            <component :is="card.icon" />
          </el-icon>
          <h4>{{ card.label }}</h4>
          <CountNumber class="count" :value="card.count" :duration="1200" />
        </div>
      </RevealOnScroll>
    </div>

    <RevealOnScroll :delay="400">
      <div class="pf-settings glass-card">
        <h4>账号设置</h4>
        <el-button type="danger" plain round @click="handleLogout">退出登录</el-button>
      </div>
    </RevealOnScroll>
  </div>
</template>

<style scoped>
.profile-page { max-width: 680px; margin: 0 auto; padding: var(--space-xl); }
.avatar-upload-wrap { cursor: pointer; display: inline-block; position: relative; }
.avatar-upload-wrap:hover .avatar-hint { opacity: 1; }
.avatar-hint { position: absolute; bottom: -20px; left: 50%; transform: translateX(-50%); font-size: 0.72rem; color: var(--accent-purple-light); white-space: nowrap; opacity: 0; transition: opacity var(--transition-fast); }
.profile-header { text-align: center; padding: var(--space-2xl); margin-bottom: var(--space-xl); }
.profile-header h2 { margin: var(--space-md) 0 var(--space-xs); font-size: 1.3rem; font-weight: 700; color: var(--text-primary); }
.profile-header p { color: var(--text-tertiary); font-size: 0.85rem; margin-bottom: var(--space-lg); }
.profile-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-md); margin-bottom: var(--space-xl); }
.pf-card { text-align: center; padding: var(--space-lg); cursor: pointer; }
.pf-card h4 { font-size: 0.85rem; color: var(--text-secondary); margin: var(--space-sm) 0; }
.count { font-size: 1.8rem; font-weight: 800; color: var(--text-primary); }
.pf-settings { padding: var(--space-xl); }
.pf-settings h4 { font-size: 1rem; font-weight: 700; color: var(--text-primary); margin-bottom: var(--space-lg); }

@media (max-width: 480px) { .profile-grid { grid-template-columns: repeat(2, 1fr); } }
</style>

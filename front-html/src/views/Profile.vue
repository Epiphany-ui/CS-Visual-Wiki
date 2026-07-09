<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'
import { videosApi } from '@/api/videos'

const userStore = useUserStore()
const router = useRouter()

const myWorksCount = ref(0)
const myStarsCount = ref(0)

function getMyWorksCount(): number {
  try {
    const works = JSON.parse(localStorage.getItem('cs:my-works') || '[]')
    return works.length
  } catch { return 0 }
}

async function loadStarsCount() {
  try {
    const res = await videosApi.getList(true)
    myStarsCount.value = res.data.data?.total || 0
  } catch { /* ignore */ }
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出')
  router.push('/')
}

onMounted(() => {
  myWorksCount.value = getMyWorksCount()
  loadStarsCount()
})
</script>

<template>
  <div class="profile-page">
    <RevealOnScroll>
      <div class="profile-header glass-card" style="animation: scale-in 0.6s var(--ease-bounce) both">
        <el-avatar :size="72" :icon="'UserFilled'" />
        <h2>{{ userStore.username }}</h2>
        <p>ID: {{ userStore.userId }}</p>
        <el-button type="primary" round @click="router.push('/sandbox')"><el-icon><EditPen /></el-icon> 开始创作</el-button>
      </div>
    </RevealOnScroll>

    <div class="profile-grid">
      <RevealOnScroll v-for="(card, i) in [
        { icon: 'PictureFilled', color: 'var(--accent-purple)', label: '我的作品', count: myWorksCount, click: () => router.push('/gallery?tab=my-works') },
        { icon: 'Star', color: 'var(--accent-orange)', label: '我的收藏', count: myStarsCount, click: () => router.push('/gallery?tab=stars') },
        { icon: 'Collection', color: 'var(--accent-cyan)', label: '知识词条', count: 111, click: () => router.push('/wiki') },
        { icon: 'Clock', color: 'var(--accent-green)', label: '动画模板', count: 10, click: () => router.push('/templates') },
      ]" :key="card.label" :delay="i * 100">
        <div class="pf-card glass-card" @click="card.click()">
          <el-icon :size="32" :color="card.color">
            <component :is="card.icon" />
          </el-icon>
          <h4>{{ card.label }}</h4>
          <span class="count">{{ card.count }}</span>
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

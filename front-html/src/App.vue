<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AnimatedBackground from '@/components/common/AnimatedBackground.vue'
import CursorGlow from '@/components/common/CursorGlow.vue'

const userStore = useUserStore()
const router = useRouter()

onMounted(() => {
  // 检查 localStorage 中是否残留过期 token，有则清理并跳转登录
  if (localStorage.getItem('token') && !userStore.isLoggedIn) {
    userStore.logout()
    ElMessage.warning('请先登录')
    router.replace('/login')
  }
})
</script>

<template>
  <div class="app-layout">
    <AnimatedBackground :particle-count="12" />
    <CursorGlow />
    <AppHeader />
    <main class="main-content">
      <router-view v-slot="{ Component, route }">
        <transition name="page" mode="out-in">
          <component :is="Component" :key="route.path" />
        </transition>
      </router-view>
    </main>
    <AppFooter />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--bg-primary);
  color: var(--text-primary);
  transition: background var(--transition-base), color var(--transition-base);
}
.main-content {
  flex: 1;
  position: relative;
  z-index: 1;
  padding-top: var(--header-height);
}

/* 页面过渡动画 */
.page-enter-active {
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
}
.page-leave-active {
  transition: all 0.2s cubic-bezier(0.4, 0, 1, 1);
}
.page-enter-from {
  opacity: 0;
  transform: translateY(16px) scale(0.98);
}
.page-leave-to {
  opacity: 0;
  transform: translateY(-8px);
}
</style>

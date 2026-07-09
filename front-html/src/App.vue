<script setup lang="ts">
import AppHeader from '@/components/layout/AppHeader.vue'
import AppFooter from '@/components/layout/AppFooter.vue'
import AnimatedBackground from '@/components/common/AnimatedBackground.vue'
</script>

<template>
  <div class="app-layout">
    <AnimatedBackground :particle-count="12" />
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
</style>

<script setup lang="ts">
defineProps<{
  title: string
  description?: string
  icon?: string
}>()
</script>

<template>
  <div class="page-header">
    <div class="page-header-content">
      <h1 class="page-title">
        <el-icon v-if="icon" :size="28"><component :is="icon" /></el-icon>
        {{ title }}
      </h1>
      <p v-if="description" class="page-desc">{{ description }}</p>
    </div>
    <div class="page-header-bg">
      <div class="gradient-blob" style="top: -50px; right: -80px; width: 300px; height: 300px; background: var(--accent-purple);"></div>
      <div class="gradient-blob" style="top: 20px; left: -100px; width: 200px; height: 200px; background: var(--accent-blue);"></div>
    </div>
  </div>
</template>

<style scoped>
.page-header {
  position: relative;
  padding: var(--space-3xl) var(--space-xl) var(--space-xl);
  text-align: center;
  overflow: hidden;
}
.page-header-content {
  position: relative;
  z-index: 2;
}
.page-title {
  font-size: 2rem;
  font-weight: 800;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.page-desc {
  margin-top: var(--space-sm);
  color: var(--text-secondary);
  font-size: 1.05rem;
}
.page-header-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}
</style>

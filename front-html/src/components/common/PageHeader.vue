<script setup lang="ts">
import { ref, onMounted } from 'vue'

defineProps<{
  title: string
  description?: string
  icon?: string
}>()

const visible = ref(false)
onMounted(() => requestAnimationFrame(() => { visible.value = true }))
</script>

<template>
  <div class="page-header" :class="{ 'ph-visible': visible }">
    <div class="page-header-content">
      <h1 class="page-title">
        <span class="ph-icon" v-if="icon"><el-icon :size="28"><component :is="icon" /></el-icon></span>
        <span class="ph-title-text">{{ title }}</span>
      </h1>
      <p v-if="description" class="page-desc">{{ description }}</p>
    </div>
    <div class="page-header-bg">
      <div class="gradient-blob blob-1" />
      <div class="gradient-blob blob-2" />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  position: relative; padding: var(--space-3xl) var(--space-xl) var(--space-xl);
  text-align: center; overflow: hidden;
}
.page-header-content { position: relative; z-index: 2; }
.page-title {
  font-size: 2rem; font-weight: 800; display: flex;
  align-items: center; justify-content: center; gap: var(--space-sm);
}

/* 图标弹入 */
.ph-icon {
  display: inline-block; opacity: 0; transform: scale(0) rotate(-30deg);
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
}
.ph-visible .ph-icon {
  opacity: 1; transform: scale(1) rotate(0deg);
}

/* 标题文字飘入 + 渐变 */
.ph-title-text {
  display: inline-block; opacity: 0; transform: translateY(30px);
  transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.15s;
  background: var(--gradient-primary);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
}
.ph-visible .ph-title-text {
  opacity: 1; transform: translateY(0);
}

/* 描述淡入 */
.page-desc {
  margin-top: var(--space-sm); color: var(--text-secondary); font-size: 1.05rem;
  opacity: 0; transform: translateY(20px);
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.35s;
}
.ph-visible .page-desc {
  opacity: 1; transform: translateY(0);
}

.page-header-bg { position: absolute; inset: 0; pointer-events: none; }
.gradient-blob {
  position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0;
  transition: opacity 1s ease 0.5s;
}
.ph-visible .gradient-blob { opacity: 0.35; }
.blob-1 { top: -60px; right: -100px; width: 300px; height: 300px; background: var(--accent-purple); }
.blob-2 { top: 10px; left: -120px; width: 200px; height: 200px; background: var(--accent-blue); }
</style>

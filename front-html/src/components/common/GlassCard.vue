<script setup lang="ts">
defineProps<{ hover?: boolean }>()
</script>

<template>
  <div class="glass-card" :class="{ 'glass-card--hover': hover }">
    <slot />
  </div>
</template>

<style scoped>
.glass-card {
  position: relative;
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all 0.35s cubic-bezier(0.16, 1, 0.3, 1);
  overflow: hidden;
}

/* 悬停发光效果 */
.glass-card--hover:hover {
  background: var(--bg-card-hover);
  border-color: rgba(124, 58, 237, 0.5);
  transform: translateY(-4px);
  box-shadow:
    0 16px 48px rgba(0, 0, 0, 0.5),
    0 0 0 1px rgba(124, 58, 237, 0.2),
    0 0 40px rgba(124, 58, 237, 0.15);
}

/* 顶部渐变高光条 */
.glass-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg,
    transparent 0%,
    rgba(124, 58, 237, 0.5) 30%,
    rgba(59, 130, 246, 0.5) 60%,
    transparent 100%);
  opacity: 0;
  transition: opacity var(--transition-base);
}
.glass-card--hover:hover::before {
  opacity: 1;
}

/* 减少动效降级 */
@media (prefers-reduced-motion: reduce) {
  .glass-card, .glass-card--hover:hover {
    transition: none;
    transform: none;
  }
}
</style>

<script setup lang="ts">
withDefaults(defineProps<{
  /** 骨架形状 */
  variant?: 'text' | 'circle' | 'rect' | 'card'
  /** 宽度 */
  width?: string
  /** 高度 */
  height?: string
  /** 圆角 */
  radius?: string
  /** 动画数量（text模式下的行数） */
  rows?: number
}>(), {
  variant: 'text',
  width: '100%',
  height: '',
  radius: '',
  rows: 1,
})
</script>

<template>
  <!-- 卡片骨架：头像 + 标题 + 两行文本 -->
  <div v-if="variant === 'card'" class="skeleton-card">
    <div class="skeleton skeleton-rect thumb" />
    <div class="card-content">
      <div class="skeleton skeleton-text title" />
      <div class="skeleton skeleton-text meta" />
    </div>
  </div>

  <!-- 圆形骨架（头像） -->
  <div
    v-else-if="variant === 'circle'"
    class="skeleton skeleton-circle"
    :style="{ width, height: height || width }"
  />

  <!-- 矩形骨架 -->
  <div
    v-else-if="variant === 'rect'"
    class="skeleton skeleton-rect"
    :style="{ width, height, borderRadius: radius }"
  />

  <!-- 文本骨架（多行） -->
  <div v-else class="skeleton-text-group">
    <div
      v-for="i in rows" :key="i"
      class="skeleton skeleton-text"
      :style="{ width: i === rows ? '60%' : width }"
    />
  </div>
</template>

<style scoped>
.skeleton {
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0.04) 0%,
    rgba(255, 255, 255, 0.08) 50%,
    rgba(255, 255, 255, 0.04) 100%
  );
  background-size: 200% 100%;
  animation: skeleton-shimmer 1.5s ease-in-out infinite;
}

@keyframes skeleton-shimmer {
  0%   { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* 文本骨架 */
.skeleton-text {
  height: 14px;
  border-radius: 4px;
  margin-bottom: 10px;
}
.skeleton-text-group .skeleton-text:last-child {
  margin-bottom: 0;
}

/* 圆形骨架 */
.skeleton-circle {
  border-radius: 50%;
}

/* 矩形骨架 */
.skeleton-rect {
  border-radius: var(--radius-md);
}

/* 卡片骨架 */
.skeleton-card {
  border-radius: var(--radius-lg);
  overflow: hidden;
  background: var(--bg-card);
  border: 1px solid var(--border-color);
}
.skeleton-card .thumb {
  width: 100%;
  aspect-ratio: 16 / 9;
  border-radius: 0;
}
.skeleton-card .card-content {
  padding: var(--space-md);
}
.skeleton-card .title {
  height: 16px;
  width: 70%;
  margin-bottom: 10px;
  border-radius: 4px;
}
.skeleton-card .meta {
  height: 12px;
  width: 40%;
  border-radius: 4px;
}

/* 减少动效降级 */
@media (prefers-reduced-motion: reduce) {
  .skeleton {
    animation: none;
    background: rgba(255, 255, 255, 0.06);
  }
}
</style>

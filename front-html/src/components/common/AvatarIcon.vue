<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  name?: string
  size?: number
  avatarUrl?: string
}>(), {
  name: '',
  size: 36,
  avatarUrl: '',
})

const initials = computed(() => {
  if (!props.name) return '?'
  const parts = props.name.trim().split(/[\s@]+/).filter(Boolean)
  if (parts.length >= 2) return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase()
  return props.name.slice(0, 2).toUpperCase()
})

const bgColor = computed(() => {
  // 从用户名 hash 生成稳定颜色
  let hash = 0
  for (const c of props.name || '?') hash = c.charCodeAt(0) + ((hash << 5) - hash)
  const h = Math.abs(hash) % 360
  return `hsl(${h}, 55%, 45%)`
})
</script>

<template>
  <div
    class="avatar-icon"
    :style="{ width: size + 'px', height: size + 'px', fontSize: size * 0.4 + 'px', lineHeight: size + 'px', background: avatarUrl ? 'transparent' : bgColor }"
    :title="name"
  >
    <img v-if="avatarUrl" :src="avatarUrl" :width="size" :height="size" alt="" class="avatar-img" />
    <span v-else class="avatar-text">{{ initials }}</span>
  </div>
</template>

<style scoped>
.avatar-icon {
  border-radius: 50%;
  display: inline-flex; align-items: center; justify-content: center;
  color: #fff; font-weight: 700; flex-shrink: 0;
  overflow: hidden; user-select: none;
}
.avatar-text { font-family: var(--font-sans); }
.avatar-img { border-radius: 50%; object-fit: cover; }
</style>

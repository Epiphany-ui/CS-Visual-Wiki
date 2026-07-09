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
  background: var(--bg-card);
  backdrop-filter: blur(16px);
  -webkit-backdrop-filter: blur(16px);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: var(--space-lg);
  transition: all var(--transition-base);
}
.glass-card--hover:hover {
  background: var(--bg-card-hover);
  border-color: var(--border-color-light);
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
</style>

<script setup lang="ts">
defineProps<{
  label: string
  value: number | string
  suffix?: string
  color?: string
}>()
</script>

<template>
  <div class="stat-card" :style="{ '--stat-color': color || 'var(--accent-purple)' }">
    <div class="stat-value">
      <slot name="value">
        {{ value }}<span v-if="suffix" class="stat-suffix">{{ suffix }}</span>
      </slot>
    </div>
    <div class="stat-label">{{ label }}</div>
  </div>
</template>

<style scoped>
.stat-card {
  text-align: center;
  padding: var(--space-lg);
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
}
.stat-card:hover {
  border-color: var(--stat-color);
  box-shadow: 0 0 24px color-mix(in srgb, var(--stat-color) 20%, transparent);
}
.stat-value {
  font-size: 2rem;
  font-weight: 800;
  background: linear-gradient(135deg, var(--stat-color), color-mix(in srgb, var(--stat-color) 60%, white));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.stat-suffix {
  font-size: 1rem;
  font-weight: 500;
}
.stat-label {
  margin-top: var(--space-xs);
  color: var(--text-secondary);
  font-size: 0.85rem;
}
</style>

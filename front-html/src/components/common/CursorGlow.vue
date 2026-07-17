<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const glowX = ref(0)
const glowY = ref(0)
const targetX = ref(0)
const targetY = ref(0)
let rafId: number | null = null

function animate() {
  // 平滑跟随（lerp）
  glowX.value += (targetX.value - glowX.value) * 0.12
  glowY.value += (targetY.value - glowY.value) * 0.12
  rafId = requestAnimationFrame(animate)
}

function handleMouseMove(e: MouseEvent) {
  targetX.value = e.clientX
  targetY.value = e.clientY
}

onMounted(() => {
  // 移动端或触摸设备不启用
  if (window.matchMedia('(pointer: coarse)').matches) return
  // 减少动效模式不启用
  if (window.matchMedia('(prefers-reduced-motion: reduce)').matches) return

  window.addEventListener('mousemove', handleMouseMove)
  rafId = requestAnimationFrame(animate)
})

onUnmounted(() => {
  window.removeEventListener('mousemove', handleMouseMove)
  if (rafId) cancelAnimationFrame(rafId)
})
</script>

<template>
  <div
    class="cursor-glow"
    :style="{
      left: `${glowX}px`,
      top: `${glowY}px`,
    }"
    aria-hidden="true"
  />
</template>

<style scoped>
.cursor-glow {
  position: fixed;
  width: 400px;
  height: 400px;
  border-radius: 50%;
  background: radial-gradient(
    circle,
    rgba(124, 58, 237, 0.15) 0%,
    rgba(59, 130, 246, 0.08) 35%,
    transparent 70%
  );
  pointer-events: none;
  transform: translate(-50%, -50%);
  z-index: 0;
  filter: blur(20px);
  will-change: left, top;
  mix-blend-mode: screen;
}
</style>

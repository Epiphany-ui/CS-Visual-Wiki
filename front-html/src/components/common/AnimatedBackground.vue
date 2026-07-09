<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  particleCount?: number
}>(), {
  particleCount: 15,
})

interface ParticleConfig {
  left: string
  duration: string
  delay: string
  width: string
  height: string
}

// Pre-compute particle configs once — Math.random() in templates causes re-render jumps
const particles = computed<ParticleConfig[]>(() => {
  return Array.from({ length: props.particleCount }, () => ({
    left: `${Math.random() * 100}%`,
    duration: `${8 + Math.random() * 12}s`,
    delay: `${Math.random() * 10}s`,
    width: `${1 + Math.random() * 2}px`,
    height: `${1 + Math.random() * 2}px`,
  }))
})
</script>

<template>
  <div class="animated-bg">
    <!-- Grid layer -->
    <div class="bg-grid" />
    <!-- Floating blobs -->
    <div class="bg-blob bg-blob--1" />
    <div class="bg-blob bg-blob--2" />
    <div class="bg-blob bg-blob--3" />
    <!-- Particles -->
    <div v-if="particleCount > 0" class="particle-canvas" aria-hidden="true">
      <div
        v-for="(p, i) in particles" :key="i"
        class="particle"
        :style="{
          left: p.left,
          animationDuration: p.duration,
          animationDelay: p.delay,
          width: p.width,
          height: p.height,
        }"
      />
    </div>
  </div>
</template>

<style scoped>
.animated-bg {
  position: fixed;
  inset: 0;
  z-index: 0;
  pointer-events: none;
  overflow: hidden;
}

.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.12;
  animation: float-rotate 12s ease-in-out infinite;
}
.bg-blob--1 {
  width: 500px; height: 500px;
  background: var(--accent-purple);
  top: -10%; left: -5%;
  animation-delay: 0s;
}
.bg-blob--2 {
  width: 400px; height: 400px;
  background: var(--accent-blue);
  top: 40%; right: -8%;
  animation-delay: -4s;
  animation-duration: 15s;
}
.bg-blob--3 {
  width: 350px; height: 350px;
  background: var(--accent-cyan);
  bottom: -10%; left: 30%;
  animation-delay: -8s;
  animation-duration: 18s;
}
</style>

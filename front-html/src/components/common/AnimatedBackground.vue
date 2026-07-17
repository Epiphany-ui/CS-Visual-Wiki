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
  background: var(--bg-primary);
}

/* ========== 极光渐变光斑 ========== */
.bg-blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(100px);
  opacity: 0.25;
  animation: blob-drift 18s ease-in-out infinite alternate;
  will-change: transform;
}
.bg-blob--1 {
  width: 700px; height: 700px;
  background: var(--accent-purple);
  top: -20%; left: -15%;
  animation-delay: 0s;
}
.bg-blob--2 {
  width: 550px; height: 550px;
  background: var(--accent-blue);
  top: 30%; right: -15%;
  animation-delay: -6s;
  animation-duration: 22s;
}
.bg-blob--3 {
  width: 500px; height: 500px;
  background: var(--accent-cyan);
  bottom: -20%; left: 20%;
  animation-delay: -12s;
  animation-duration: 26s;
}

@keyframes blob-drift {
  0%   { transform: translate(0, 0) scale(1); }
  50%  { transform: translate(3%, -3%) scale(1.08); }
  100% { transform: translate(-2%, 2%) scale(0.95); }
}

/* ========== 网格底纹 ========== */
.bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.04) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.04) 1px, transparent 1px);
  background-size: 40px 40px;
  mask-image: radial-gradient(ellipse 90% 80% at 50% 30%, black 0%, transparent 90%);
  -webkit-mask-image: radial-gradient(ellipse 90% 80% at 50% 30%, black 0%, transparent 90%);
}

/* ========== 浮动粒子 ========== */
.particle-canvas {
  position: absolute;
  inset: 0;
}
.particle {
  position: absolute;
  top: 100%;
  background: rgba(255, 255, 255, 0.4);
  border-radius: 50%;
  box-shadow: 0 0 6px rgba(255, 255, 255, 0.5);
  animation: particle-float linear infinite;
  will-change: transform;
}

@keyframes particle-float {
  0% {
    transform: translateY(0) translateX(0);
    opacity: 0;
  }
  10% { opacity: 0.6; }
  90% { opacity: 0.4; }
  100% {
    transform: translateY(-110vh) translateX(20px);
    opacity: 0;
  }
}

/* ========== 减少动效降级 ========== */
@media (prefers-reduced-motion: reduce) {
  .bg-blob, .particle {
    animation: none;
  }
}
</style>

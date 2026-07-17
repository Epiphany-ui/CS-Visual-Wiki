<script setup lang="ts">
import { ref, computed } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'

const props = withDefaults(defineProps<{
  threshold?: number
  rootMargin?: string
  delay?: number
  once?: boolean
  /** 进入方向 */
  direction?: 'up' | 'down' | 'left' | 'right' | 'none'
  /** 弹入效果 */
  bounce?: boolean
  /** 模糊渐清 */
  blur?: boolean
  /** 缩放进入 */
  scale?: boolean
  /** 位移距离（px） */
  distance?: number
  /** 动画时长（ms） */
  duration?: number
}>(), {
  threshold: 0.12,
  rootMargin: '0px 0px -30px 0px',
  delay: 0,
  once: true,
  direction: 'up',
  bounce: false,
  blur: false,
  scale: false,
  distance: 40,
  duration: 700,
})

const el = ref<HTMLElement | null>(null)
const visible = ref(false)

const dirClass = computed(() => `reveal-${props.direction}`)

const { stop } = useIntersectionObserver(
  el,
  ([{ isIntersecting }]) => {
    if (isIntersecting) {
      setTimeout(() => { visible.value = true }, props.delay)
      if (props.once) stop()
    } else if (!props.once) {
      visible.value = false
    }
  },
  { threshold: props.threshold, rootMargin: props.rootMargin },
)
</script>

<template>
  <div
    ref="el"
    :class="[
      'reveal-on-scroll',
      dirClass,
      { 'reveal-bounce': bounce },
      { 'reveal-blur': blur },
      { 'reveal-scale': scale },
      { 'is-visible': visible },
    ]"
    :style="{
      '--reveal-distance': `${distance}px`,
      '--reveal-duration': `${duration}ms`,
    }"
  >
    <slot />
  </div>
</template>

<style scoped>
.reveal-on-scroll {
  opacity: 0;
  transition:
    opacity var(--reveal-duration) cubic-bezier(0.16, 1, 0.3, 1),
    transform var(--reveal-duration) cubic-bezier(0.16, 1, 0.3, 1),
    filter var(--reveal-duration) cubic-bezier(0.16, 1, 0.3, 1);
  will-change: opacity, transform, filter;
}

.reveal-on-scroll.is-visible {
  opacity: 1;
}

/* 模糊渐清 */
.reveal-on-scroll.reveal-blur {
  filter: blur(12px);
}
.reveal-on-scroll.reveal-blur.is-visible {
  filter: blur(0);
}

/* 缩放进入 */
.reveal-on-scroll.reveal-scale {
  transform: scale(0.92);
}
.reveal-on-scroll.reveal-scale.is-visible {
  transform: scale(1);
}

/* 方向位移 */
.reveal-up { transform: translateY(var(--reveal-distance)); }
.reveal-up.is-visible { transform: translateY(0); }

.reveal-down { transform: translateY(calc(var(--reveal-distance) * -1)); }
.reveal-down.is-visible { transform: translateY(0); }

.reveal-left { transform: translateX(calc(var(--reveal-distance) * -1.5)); }
.reveal-left.is-visible { transform: translateX(0); }

.reveal-right { transform: translateX(calc(var(--reveal-distance) * 1.5)); }
.reveal-right.is-visible { transform: translateX(0); }

.reveal-none { transform: none; }

/* 弹性弹入 */
.reveal-bounce {
  transition-timing-function: cubic-bezier(0.34, 1.56, 0.64, 1) !important;
}

/* 减少动效降级 */
@media (prefers-reduced-motion: reduce) {
  .reveal-on-scroll {
    opacity: 1 !important;
    transform: none !important;
    filter: none !important;
    transition: none !important;
  }
}
</style>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'

const props = withDefaults(defineProps<{
  /** 目标数值 */
  value: number
  /** 动画时长（毫秒） */
  duration?: number
  /** 小数位数 */
  decimals?: number
  /** 前缀文字 */
  prefix?: string
  /** 后缀文字 */
  suffix?: string
  /** 是否在进入视口时才开始动画 */
  startOnView?: boolean
}>(), {
  duration: 1500,
  decimals: 0,
  prefix: '',
  suffix: '',
  startOnView: true,
})

const displayValue = ref(0)
const el = ref<HTMLElement | null>(null)
const started = ref(false)
let rafId: number | null = null
let startTime: number | null = null

function easeOutExpo(t: number): number {
  return t === 1 ? 1 : 1 - Math.pow(2, -10 * t)
}

function animate(timestamp: number) {
  if (startTime === null) startTime = timestamp
  const progress = Math.min((timestamp - startTime) / props.duration, 1)
  const eased = easeOutExpo(progress)
  displayValue.value = props.value * eased

  if (progress < 1) {
    rafId = requestAnimationFrame(animate)
  }
}

function startAnimation() {
  if (started.value) return
  started.value = true
  startTime = null
  rafId = requestAnimationFrame(animate)
}

onMounted(() => {
  if (!props.startOnView) {
    startAnimation()
    return
  }
  // 进入视口再开始动画
  const observer = new IntersectionObserver(
    ([entry]) => {
      if (entry.isIntersecting) {
        startAnimation()
        observer.disconnect()
      }
    },
    { threshold: 0.3 }
  )
  if (el.value) observer.observe(el.value)
  onUnmounted(() => observer.disconnect())
})

onUnmounted(() => {
  if (rafId !== null) cancelAnimationFrame(rafId)
})

// 数值变化时重新动画
watch(() => props.value, () => {
  if (started.value) {
    startTime = null
    displayValue.value = 0
    if (rafId !== null) cancelAnimationFrame(rafId)
    rafId = requestAnimationFrame(animate)
  }
})

const formatted = computed(() => {
  const num = displayValue.value.toFixed(props.decimals)
  return `${props.prefix}${num}${props.suffix}`
})
</script>

<template>
  <span ref="el" class="count-number">
    {{ formatted }}
  </span>
</template>

<style scoped>
.count-number {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum';
}
</style>

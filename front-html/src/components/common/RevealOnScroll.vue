<script setup lang="ts">
import { ref } from 'vue'
import { useIntersectionObserver } from '@vueuse/core'

const props = withDefaults(defineProps<{
  threshold?: number
  rootMargin?: string
  delay?: number
  once?: boolean
}>(), {
  threshold: 0.15,
  rootMargin: '0px 0px -40px 0px',
  delay: 0,
  once: true,
})

const el = ref<HTMLElement | null>(null)
const visible = ref(false)

const { stop } = useIntersectionObserver(
  el,
  ([{ isIntersecting }]) => {
    if (isIntersecting) {
      setTimeout(() => { visible.value = true }, props.delay)
      if (props.once) {
        stop()
      }
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
    :class="['reveal-on-scroll', { 'is-visible': visible }]"
  >
    <slot />
  </div>
</template>

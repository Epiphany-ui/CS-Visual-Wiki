<script setup lang="ts">
import { computed } from 'vue'
import { useTransition } from '@vueuse/core'
import { useIntersectionObserver } from '@vueuse/core'
import { ref } from 'vue'

const props = withDefaults(defineProps<{
  target: number
  duration?: number
  decimals?: number
}>(), {
  duration: 1500,
  decimals: 0,
})

const el = ref<HTMLElement | null>(null)
const started = ref(false)

const { stop } = useIntersectionObserver(
  el,
  ([{ isIntersecting }]) => {
    if (isIntersecting) {
      started.value = true
      stop()
    }
  },
  { threshold: 0.3 },
)

const animated = useTransition(
  computed(() => started.value ? props.target : 0),
  { duration: props.duration, transition: [0.16, 1, 0.3, 1] },
)

const display = computed(() => animated.value.toFixed(props.decimals))
</script>

<template>
  <span ref="el" class="animated-counter">{{ display }}</span>
</template>

<style scoped>
.animated-counter {
  font-variant-numeric: tabular-nums;
  font-feature-settings: 'tnum';
}
</style>

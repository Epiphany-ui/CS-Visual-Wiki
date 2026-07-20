<script setup lang="ts">
import { ref, onMounted } from 'vue'

defineProps<{
  title: string
  description?: string
  icon?: string
}>()

const visible = ref(false)
onMounted(() => requestAnimationFrame(() => { visible.value = true }))
</script>

<template>
  <div class="page-header" :class="{ 'ph-visible': visible }">
    <div class="page-header-content">
      <h1 class="page-title">
        <span class="ph-icon" v-if="icon"><el-icon :size="28"><component :is="icon" /></el-icon></span>
        <span class="ph-title-text">{{ title }}</span>
      </h1>
      <p v-if="description" class="page-desc">{{ description }}</p>
    </div>
    <div class="page-header-bg">
      <div class="gradient-blob blob-1" />
      <div class="gradient-blob blob-2" />
    </div>
  </div>
</template>

<style scoped>
.page-header {
  position: relative; padding: var(--space-3xl) var(--space-xl) var(--space-xl);
  text-align: center; overflow: hidden;
}
.page-header-content { position: relative; z-index: 2; }
.page-title {
  font-size: 2.4rem; font-weight: 900; display: flex;
  align-items: center; justify-content: center; gap: var(--space-sm);
  letter-spacing: -0.02em;
  position: relative;
}

/* 装饰下线 */
.page-title::after {
  content: '';
  position: absolute;
  bottom: -10px; left: 50%; transform: translateX(-50%) scaleX(0);
  width: 60px; height: 3px;
  background: var(--gradient-primary);
  border-radius: 2px;
  transition: transform 0.6s var(--ease-out-expo) 0.5s;
}
.ph-visible .page-title::after { transform: translateX(-50%) scaleX(1); }

/* 图标弹入 + 旋转 */
.ph-icon {
  display: inline-block; opacity: 0; transform: scale(0) rotate(-30deg);
  transition: all 0.6s cubic-bezier(0.34, 1.56, 0.64, 1);
  filter: drop-shadow(0 0 12px rgba(124, 58, 237, 0.5));
}
.ph-visible .ph-icon {
  opacity: 1; transform: scale(1) rotate(0deg);
}

/* 标题文字飘入 + 流动渐变 + 发光 */
.ph-title-text {
  display: inline-block; opacity: 0; transform: translateY(30px);
  transition: all 0.7s cubic-bezier(0.16, 1, 0.3, 1) 0.15s;
  background: linear-gradient(135deg, var(--accent-purple) 0%, var(--accent-blue) 30%, var(--accent-cyan) 60%, var(--accent-purple) 100%);
  background-size: 300% 300%;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: title-shimmer 4s ease-in-out infinite;
  filter: drop-shadow(0 2px 8px rgba(124, 58, 237, 0.25));
}
.ph-visible .ph-title-text {
  opacity: 1; transform: translateY(0);
}
@keyframes title-shimmer {
  0%, 100% { background-position: 0% 50%; }
  50%      { background-position: 100% 50%; }
}

/* 描述淡入 */
.page-desc {
  margin-top: var(--space-md); color: var(--text-secondary); font-size: 1.05rem;
  opacity: 0; transform: translateY(20px);
  transition: all 0.6s cubic-bezier(0.16, 1, 0.3, 1) 0.35s;
  max-width: 500px; margin-left: auto; margin-right: auto;
}
.ph-visible .page-desc {
  opacity: 1; transform: translateY(0);
}

.page-header-bg { position: absolute; inset: 0; pointer-events: none; }
.gradient-blob {
  position: absolute; border-radius: 50%; filter: blur(100px); opacity: 0;
  transition: opacity 1s ease 0.5s;
}
.ph-visible .gradient-blob { opacity: 0.35; }
.blob-1 { top: -60px; right: -100px; width: 300px; height: 300px; background: var(--accent-purple); animation: blob-float 8s ease-in-out infinite; }
.blob-2 { top: 10px; left: -120px; width: 200px; height: 200px; background: var(--accent-blue); animation: blob-float 6s ease-in-out infinite reverse; }
@keyframes blob-float {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33%      { transform: translate(30px, -20px) scale(1.1); }
  66%      { transform: translate(-20px, 10px) scale(0.9); }
}
</style>

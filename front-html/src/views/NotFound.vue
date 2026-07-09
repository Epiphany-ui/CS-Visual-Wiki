<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
</script>

<template>
  <div class="not-found">
    <div class="nf-404">404</div>
    <h2>页面未找到</h2>
    <p>你访问的页面不存在或已被移除</p>
    <el-button type="primary" round size="large" @click="router.push('/')">返回首页</el-button>
  </div>
</template>

<style scoped>
.not-found {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  min-height: 70vh; text-align: center; animation: blur-in 0.8s var(--ease-out-expo);
}
.nf-404 {
  font-size: 8rem; font-weight: 900;
  background: var(--gradient-hero); background-size: 200% auto;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  line-height: 1; animation: gradient-shift 4s ease infinite, float 3s ease-in-out infinite;
}
h2 { margin-top: var(--space-lg); font-size: 1.5rem; color: var(--text-primary); }
p { margin: var(--space-md) 0 var(--space-xl); color: var(--text-secondary); }
</style>

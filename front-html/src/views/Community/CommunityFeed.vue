<script setup lang="ts">
import PageHeader from '@/components/common/PageHeader.vue'
</script>

<template>
  <div class="community-page">
    <PageHeader title="社区交流" description="创作者与学习者的交流平台" icon="User" />
    <div class="placeholder glass-card" style="animation: scale-in 0.5s var(--ease-bounce) both">
      <el-icon :size="64" color="var(--text-tertiary)"><ChatDotRound /></el-icon>
      <h3>社区功能即将上线</h3>
      <p>作品动态流、评论系统、Fork 机制正在开发中...</p>
      <div class="features-preview">
        <div class="fp-item"><el-icon><Comment /></el-icon> 评论与回复</div>
        <div class="fp-item"><el-icon><Star /></el-icon> 点赞与收藏</div>
        <div class="fp-item"><el-icon><Connection /></el-icon> Fork 二创</div>
        <div class="fp-item"><el-icon><UserFilled /></el-icon> 创作者主页</div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.community-page { padding-bottom: var(--space-3xl); }
.placeholder { max-width: 600px; margin: var(--space-2xl) auto; padding: var(--space-3xl); text-align: center; }
.placeholder h3 { margin: var(--space-lg) 0 var(--space-sm); font-size: 1.2rem; font-weight: 700; color: var(--text-primary); }
.placeholder p { color: var(--text-tertiary); }
.features-preview { display: grid; grid-template-columns: 1fr 1fr; gap: var(--space-md); margin-top: var(--space-xl); }
.fp-item { display: flex; align-items: center; gap: var(--space-sm); color: var(--text-secondary); font-size: 0.9rem; padding: var(--space-sm) var(--space-md); background: var(--bg-card); border-radius: var(--radius-md); }
</style>

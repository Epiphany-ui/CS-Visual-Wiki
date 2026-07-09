<script setup lang="ts">
import PageHeader from '@/components/common/PageHeader.vue'
</script>

<template>
  <div class="study-page">
    <PageHeader title="备考学习" description="系统化学习路径，每日打卡，追踪进度" icon="School" />

    <div class="path-grid">
      <div class="path-card glass-card">
        <div class="path-icon" style="background: rgba(124,58,237,0.15);color:#7c3aed;"><el-icon :size="28"><DataAnalysis /></el-icon></div>
        <h3>408 数据结构</h3>
        <p>线性表、栈队列、树与二叉树、图、查找、排序</p>
        <el-progress :percentage="0" :stroke-width="6" :color="'#7c3aed'" />
        <span class="status">即将上线</span>
      </div>
      <div class="path-card glass-card">
        <div class="path-icon" style="background: rgba(59,130,246,0.15);color:#3b82f6;"><el-icon :size="28"><TrendCharts /></el-icon></div>
        <h3>考研高数</h3>
        <p>极限、微积分、级数、微分方程</p>
        <el-progress :percentage="0" :stroke-width="6" :color="'#3b82f6'" />
        <span class="status">即将上线</span>
      </div>
      <div class="path-card glass-card">
        <div class="path-icon" style="background: rgba(6,182,212,0.15);color:#06b6d4;"><el-icon :size="28"><Grid /></el-icon></div>
        <h3>线性代数</h3>
        <p>矩阵运算、特征值、二次型、线性空间</p>
        <el-progress :percentage="0" :stroke-width="6" :color="'#06b6d4'" />
        <span class="status">即将上线</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.study-page { padding-bottom: var(--space-3xl); }
.path-grid { max-width: var(--max-content-width); margin: 0 auto; padding: 0 var(--space-xl); display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: var(--space-lg); }
.path-card { padding: var(--space-xl); }
.path-icon { width: 48px; height: 48px; border-radius: var(--radius-md); display: flex; align-items: center; justify-content: center; margin-bottom: var(--space-md); }
.path-card h3 { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.path-card p { font-size: 0.85rem; color: var(--text-tertiary); margin: var(--space-sm) 0 var(--space-lg); }
.status { display: inline-block; margin-top: var(--space-sm); font-size: 0.75rem; color: var(--text-tertiary); background: var(--bg-card); padding: 2px 10px; border-radius: var(--radius-full); }
</style>

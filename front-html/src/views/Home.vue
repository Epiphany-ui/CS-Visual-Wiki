<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import StatCard from '@/components/common/StatCard.vue'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'
import AnimatedCounter from '@/components/common/AnimatedCounter.vue'

const router = useRouter()
const inputRequirement = ref('')

const categories = [
  { name: '算法', icon: 'Operation', color: '#7c3aed', desc: '排序、搜索、贪心...', path: '/wiki?category=algorithm' },
  { name: '数据结构', icon: 'DataAnalysis', color: '#3b82f6', desc: '树、图、堆、哈希...', path: '/wiki?category=data-structures' },
  { name: '高等数学', icon: 'TrendCharts', color: '#06b6d4', desc: '微积分、级数、傅里叶...', path: '/wiki?category=math' },
  { name: '线性代数', icon: 'Grid', color: '#10b981', desc: '矩阵、特征值、SVD...', path: '/wiki?category=linear-algebra' },
  { name: '概率论', icon: 'PieChart', color: '#f59e0b', desc: '正态分布、贝叶斯...', path: '/wiki?category=probability' },
  { name: '图论', icon: 'Share', color: '#ec4899', desc: '最短路径、生成树...', path: '/wiki?category=graph-theory' },
]

function handleGenerate() {
  if (inputRequirement.value.trim()) {
    router.push({ path: '/sandbox', query: { prompt: inputRequirement.value.trim() } })
  }
}
</script>

<template>
  <div class="home-page">
    <!-- Hero -->
    <section class="hero">
      <div class="hero-content">
        <RevealOnScroll>
          <h1 class="hero-title">
            让抽象概念，<span class="shimmer-text">动</span>起来
          </h1>
          <p class="hero-subtitle">
            基于 AI 的可视化学习平台 — 输入知识点，即刻生成交互式数学动画
          </p>
          <div class="hero-input">
            <el-input
              v-model="inputRequirement"
              size="large"
              placeholder="例如：冒泡排序动画、傅里叶级数可视化、二叉树遍历..."
              @keyup.enter="handleGenerate"
              class="hero-search"
            >
              <template #suffix>
                <el-button type="primary" size="large" @click="handleGenerate" round>
                  <el-icon><MagicStick /></el-icon> 一键生成
                </el-button>
              </template>
            </el-input>
          </div>
          <div class="hero-tags">
            <span>热门：</span>
            <el-tag
              v-for="t in ['快速排序','二叉树遍历','傅里叶变换','Dijkstra算法']"
              :key="t" size="default" class="hero-tag"
              @click="router.push({path:'/sandbox', query:{prompt:t}})"
            >{{ t }}</el-tag>
          </div>
        </RevealOnScroll>
      </div>
      <div class="hero-scroll">
        <el-icon :size="24"><ArrowDownBold /></el-icon>
      </div>
    </section>

    <!-- 分类导航 -->
    <section class="section">
      <RevealOnScroll>
        <h2 class="section-title text-gradient">探索知识领域</h2>
        <p class="section-desc">从你最感兴趣的领域开始学习之旅</p>
      </RevealOnScroll>
      <div class="category-grid">
        <RevealOnScroll v-for="(cat, i) in categories" :key="cat.name" :delay="i * 100">
          <div class="category-card glass-card" @click="router.push(cat.path)">
            <div class="cat-icon" :style="{ color: cat.color, background: cat.color + '15' }">
              <el-icon :size="28"><component :is="cat.icon" /></el-icon>
            </div>
            <h3 class="cat-name">{{ cat.name }}</h3>
            <p class="cat-desc">{{ cat.desc }}</p>
          </div>
        </RevealOnScroll>
      </div>
    </section>

    <!-- 统计数据 -->
    <section class="section stats-section">
      <RevealOnScroll>
        <h2 class="section-title text-gradient">平台数据</h2>
      </RevealOnScroll>
      <div class="stats-row">
        <StatCard label="知识词条" value="111" suffix="+" color="#7c3aed">
          <template #value>
            <AnimatedCounter :target="111" :duration="1500" />+
          </template>
        </StatCard>
        <StatCard label="动画模板" value="10" suffix="+" color="#3b82f6">
          <template #value>
            <AnimatedCounter :target="10" :duration="1000" />+
          </template>
        </StatCard>
        <StatCard label="已生成动画" value="∞" color="#06b6d4" />
        <StatCard label="知识分类" value="7" suffix="个" color="#10b981">
          <template #value>
            <AnimatedCounter :target="7" :duration="800" />个
          </template>
        </StatCard>
      </div>
    </section>
  </div>
</template>

<style scoped>
/* Hero */
.hero {
  position: relative; min-height: 85vh; display: flex; align-items: center;
  justify-content: center; overflow: hidden; padding: var(--space-3xl) var(--space-xl);
}
.hero-content { position: relative; z-index: 2; text-align: center; max-width: 800px; }
.hero-title { font-size: 3.5rem; font-weight: 800; line-height: 1.2; color: var(--text-primary); }
.hero-subtitle { margin-top: var(--space-lg); font-size: 1.15rem; color: var(--text-secondary); line-height: 1.6; }
.hero-input { margin-top: var(--space-2xl); max-width: 600px; margin-inline: auto; }
.hero-search :deep(.el-input__wrapper) {
  background: var(--bg-card); backdrop-filter: blur(12px); border: 1px solid var(--border-color-light);
  border-radius: var(--radius-full); padding: 4px 4px 4px 20px; box-shadow: var(--shadow-lg);
}
.hero-search :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-purple); box-shadow: 0 0 0 3px rgba(124,58,237,0.15);
}
.hero-tags { margin-top: var(--space-lg); display: flex; align-items: center; justify-content: center; gap: var(--space-sm); color: var(--text-tertiary); font-size: 0.85rem; flex-wrap: wrap; }
.hero-tag { cursor: pointer; background: var(--bg-card) !important; border-color: var(--border-color) !important; color: var(--text-secondary); transition: all var(--transition-fast); }
.hero-tag:hover { border-color: var(--accent-purple) !important; color: var(--accent-purple-light); }
.hero-scroll { position: absolute; bottom: var(--space-xl); left: 50%; transform: translateX(-50%); color: var(--text-tertiary); animation: float 3s ease-in-out infinite; cursor: pointer; transition: color var(--transition-fast); }
.hero-scroll:hover { color: var(--accent-purple-light); }

/* Sections */
.section { max-width: var(--max-content-width); margin: 0 auto; padding: var(--space-2xl) var(--space-xl); }
.section-title { text-align: center; font-size: 1.8rem; font-weight: 800; }
.section-desc { text-align: center; margin-top: var(--space-sm); color: var(--text-secondary); }
.category-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: var(--space-lg); margin-top: var(--space-xl); }
.category-card { text-align: center; padding: var(--space-xl); cursor: pointer; }
.category-card:hover { transform: translateY(-4px); box-shadow: var(--shadow-lg); }
.cat-icon { width: 56px; height: 56px; border-radius: var(--radius-lg); display: flex; align-items: center; justify-content: center; margin: 0 auto var(--space-md); transition: transform var(--transition-fast); }
.category-card:hover .cat-icon { transform: scale(1.1); }
.cat-name { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.cat-desc { margin-top: var(--space-xs); color: var(--text-tertiary); font-size: 0.85rem; }

.stats-section { padding-bottom: var(--space-3xl); }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-lg); }

@media (max-width: 768px) {
  .hero-title { font-size: 2.2rem; }
  .category-grid { grid-template-columns: repeat(2, 1fr); }
  .stats-row { grid-template-columns: repeat(2, 1fr); }
}
</style>

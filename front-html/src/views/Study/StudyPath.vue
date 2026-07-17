<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'
import CountNumber from '@/components/common/CountNumber.vue'
import { useCurrentUser } from '@/composables/useCurrentUser'

const router = useRouter()
const { username } = useCurrentUser()

// ========== 学习路径数据（每个知识点绑定动画 prompt）==========
interface StudyItem {
  name: string
  prompt: string  // 对应沙箱生成的动画描述
}
interface Chapter {
  id: string
  name: string
  items: StudyItem[]
}
interface StudyPath {
  id: string
  name: string
  desc: string
  color: string
  icon: string
  chapters: Chapter[]
}

const paths: StudyPath[] = [
  {
    id: 'ds',
    name: '数据结构入门',
    desc: '从线性表到排序算法，逐个生成动画直观理解',
    color: '#7c3aed',
    icon: 'DataAnalysis',
    chapters: [
      {
        id: 'ch1', name: '线性表',
        items: [
          { name: '顺序表插入删除', prompt: '顺序表插入和删除操作的可视化动画' },
          { name: '单链表反转', prompt: '单链表反转过程的逐步动画演示' },
          { name: '双向链表操作', prompt: '双向链表插入删除节点的可视化' },
        ],
      },
      {
        id: 'ch2', name: '栈和队列',
        items: [
          { name: '栈的进出演示', prompt: '栈的 push 和 pop 操作动画演示' },
          { name: '循环队列', prompt: '循环队列入队出队的可视化动画' },
          { name: '栈实现队列', prompt: '用两个栈实现队列的原理动画' },
        ],
      },
      {
        id: 'ch3', name: '树与二叉树',
        items: [
          { name: '二叉树前序遍历', prompt: '二叉树前序遍历递归过程动画' },
          { name: '二叉树中序遍历', prompt: '二叉树中序遍历步骤可视化' },
          { name: '二叉树层序遍历', prompt: '二叉树层序遍历 BFS 动画演示' },
          { name: '哈夫曼树构建', prompt: '哈夫曼树构建过程逐步动画' },
        ],
      },
      {
        id: 'ch4', name: '排序算法',
        items: [
          { name: '冒泡排序', prompt: '冒泡排序算法执行过程可视化动画' },
          { name: '快速排序', prompt: '快速排序算法分治过程动画演示' },
          { name: '归并排序', prompt: '归并排序算法合并过程可视化' },
          { name: '堆排序', prompt: '堆排序算法建堆和调整动画' },
        ],
      },
    ],
  },
  {
    id: 'math',
    name: '高等数学',
    desc: '用动画理解极限、微积分的几何意义',
    color: '#3b82f6',
    icon: 'TrendCharts',
    chapters: [
      {
        id: 'ch1', name: '极限与连续',
        items: [
          { name: '函数极限逼近', prompt: '函数趋近于某点时极限的可视化动画' },
          { name: '无穷小比较', prompt: '不同阶无穷小趋近速度对比动画' },
        ],
      },
      {
        id: 'ch2', name: '导数与微分',
        items: [
          { name: '导数几何意义', prompt: '导数的切线斜率几何意义动画演示' },
          { name: '微分近似', prompt: '微分线性近似的几何解释动画' },
        ],
      },
      {
        id: 'ch3', name: '积分',
        items: [
          { name: '定积分黎曼和', prompt: '定积分黎曼和逼近过程动画' },
          { name: '牛顿莱布尼茨', prompt: '牛顿-莱布尼茨公式几何意义动画' },
        ],
      },
    ],
  },
  {
    id: 'algebra',
    name: '线性代数',
    desc: '矩阵变换、特征值的几何直观理解',
    color: '#06b6d4',
    icon: 'Grid',
    chapters: [
      {
        id: 'ch1', name: '矩阵运算',
        items: [
          { name: '矩阵乘法', prompt: '矩阵乘法行列对应计算过程动画' },
          { name: '矩阵转置', prompt: '矩阵转置行列交换的可视化' },
        ],
      },
      {
        id: 'ch2', name: '线性变换',
        items: [
          { name: '旋转变换', prompt: '二维旋转矩阵对空间的变换动画' },
          { name: '剪切变换', prompt: '剪切矩阵对单位正方形的变换动画' },
          { name: '缩放变换', prompt: '矩阵缩放变换的几何效果动画' },
        ],
      },
      {
        id: 'ch3', name: '特征值',
        items: [
          { name: '特征向量几何意义', prompt: '特征向量和特征值的几何直观动画' },
          { name: '矩阵对角化', prompt: '矩阵对角化分解过程可视化' },
        ],
      },
    ],
  },
]

// ========== 状态管理 ==========
const activePathId = ref<string | null>(null)
const learned = ref<Record<string, boolean>>({}) // key: pathId:chapterId:itemName

// 跨设备同步：优先从服务端加载，保存到服务端 + localStorage 双写
const storageKey = computed(() => `cs:learn:${username.value || 'anon'}`)

async function loadProgress() {
  // 从服务端加载
  try {
    const res = await fetch(`/api/study/progress?username=${encodeURIComponent(username.value || 'anon')}`)
    if (res.ok) {
      const data = await res.json()
      if (data.data?.progress && Object.keys(data.data.progress).length > 0) {
        learned.value = data.data.progress
        localStorage.setItem(storageKey.value, JSON.stringify(data.data.progress))
        return
      }
    }
  } catch { /* ignore */ }
  // fallback: localStorage
  try {
    const saved = localStorage.getItem(storageKey.value)
    if (saved) learned.value = JSON.parse(saved)
  } catch { /* ignore */ }
}

function saveProgress() {
  const json = JSON.stringify(learned.value)
  localStorage.setItem(storageKey.value, json)
  // 异步同步到服务端
  fetch(`/api/study/progress?username=${encodeURIComponent(username.value || 'anon')}&progress=${encodeURIComponent(json)}`, { method: 'POST' }).catch(() => {})
}

onMounted(loadProgress)
watch(learned, saveProgress, { deep: true })

// ========== 计算属性 ==========
const activePath = computed(() => paths.find(p => p.id === activePathId.value))

function getPathProgress(pathId: string): number {
  const path = paths.find(p => p.id === pathId)
  if (!path) return 0
  let total = 0
  let done = 0
  path.chapters.forEach(ch => {
    ch.items.forEach(item => {
      total++
      if (learned.value[`${pathId}:${ch.id}:${item.name}`]) done++
    })
  })
  return total === 0 ? 0 : Math.round((done / total) * 100)
}

function getItemKey(pathId: string, chId: string, itemName: string) {
  return `${pathId}:${chId}:${itemName}`
}

// ========== 核心：生成动画 + 标记已学习 ==========
function generateAnimation(item: StudyItem, pathId: string, chId: string) {
  const key = getItemKey(pathId, chId, item.name)
  learned.value[key] = true
  ElMessage.success(`开始生成「${item.name}」动画...`)
  router.push({ path: '/sandbox', query: { prompt: item.prompt } })
}

function toggleLearned(pathId: string, chId: string, itemName: string) {
  const key = getItemKey(pathId, chId, itemName)
  learned.value[key] = !learned.value[key]
}

// ========== 统计 ==========
const totalItems = computed(() => {
  let total = 0
  paths.forEach(p => p.chapters.forEach(ch => total += ch.items.length))
  return total
})
const learnedItems = computed(() => Object.values(learned.value).filter(Boolean).length)

// ========== 路径切换 ==========
function openPath(id: string) { activePathId.value = id }
function backToList() { activePathId.value = null }
</script>

<template>
  <div class="study-page">
    <PageHeader title="学习路径" description="按路线逐个生成动画，可视化掌握每个知识点" icon="Guide" />

    <!-- 学习统计 -->
    <RevealOnScroll>
      <div class="stats-row">
        <div class="stat-card glass-card">
          <div class="stat-num">
            <CountNumber :value="learnedItems" :duration="1000" />
            <span class="stat-total">/{{ totalItems }}</span>
          </div>
          <div class="stat-label">已生成动画</div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-num">
            <CountNumber :value="paths.length" :duration="800" />
          </div>
          <div class="stat-label">学习路线</div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-num">
            <CountNumber :value="Math.round(learnedItems / Math.max(totalItems, 1) * 100)" :duration="1000" />
            <span class="stat-percent">%</span>
          </div>
          <div class="stat-label">总体进度</div>
        </div>
      </div>
    </RevealOnScroll>

    <!-- 路径列表 -->
    <template v-if="!activePath">
      <div class="path-grid">
        <RevealOnScroll v-for="(path, i) in paths" :key="path.id" :delay="i * 100">
          <div class="path-card glass-card" v-tilt @click="openPath(path.id)">
            <div class="path-icon" :style="{ background: path.color + '20', color: path.color }">
              <el-icon :size="28"><component :is="path.icon" /></el-icon>
            </div>
            <h3>{{ path.name }}</h3>
            <p>{{ path.desc }}</p>
            <el-progress
              :percentage="getPathProgress(path.id)"
              :stroke-width="6"
              :color="path.color"
            />
            <div class="path-footer">
              <span class="chapter-count">{{ path.chapters.length }} 章 · {{ path.chapters.reduce((s, c) => s + c.items.length, 0) }} 个动画</span>
              <span class="enter-btn">开始学习 →</span>
            </div>
          </div>
        </RevealOnScroll>
      </div>
    </template>

    <!-- 路径详情 -->
    <template v-else>
      <div class="path-detail">
        <button class="back-btn" @click="backToList">← 返回路径列表</button>

        <RevealOnScroll>
          <div class="detail-header glass-card">
            <div class="path-icon large" :style="{ background: activePath!.color + '20', color: activePath!.color }">
              <el-icon :size="36"><component :is="activePath!.icon" /></el-icon>
            </div>
            <div class="detail-info">
              <h2>{{ activePath!.name }}</h2>
              <p>{{ activePath!.desc }}</p>
              <el-progress
                :percentage="getPathProgress(activePath!.id)"
                :stroke-width="8"
                :color="activePath!.color"
              />
            </div>
          </div>
        </RevealOnScroll>

        <!-- 章节列表 -->
        <div class="chapters">
          <RevealOnScroll v-for="(ch, i) in activePath!.chapters" :key="ch.id" :delay="i * 80">
            <div class="chapter-card glass-card">
              <div class="chapter-header">
                <h4>{{ ch.name }}</h4>
                <span class="chapter-count">
                  {{ ch.items.filter(item => learned[getItemKey(activePath!.id, ch.id, item.name)]).length }}/{{ ch.items.length }}
                </span>
              </div>
              <div class="item-list">
                <div
                  v-for="item in ch.items"
                  :key="item.name"
                  class="study-item"
                  :class="{ done: learned[getItemKey(activePath!.id, ch.id, item.name)] }"
                >
                  <div class="item-left" @click="toggleLearned(activePath!.id, ch.id, item.name)">
                    <el-icon class="check-icon">
                      <component :is="learned[getItemKey(activePath!.id, ch.id, item.name)] ? 'CircleCheckFilled' : 'Circle'" />
                    </el-icon>
                    <span class="item-name">{{ item.name }}</span>
                  </div>
                  <el-button
                    size="small"
                    type="primary"
                    round
                    @click="generateAnimation(item, activePath!.id, ch.id)"
                    v-ripple
                  >
                    <el-icon><MagicStick /></el-icon>
                    生成动画
                  </el-button>
                </div>
              </div>
            </div>
          </RevealOnScroll>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.study-page { padding-bottom: var(--space-3xl); }

/* 统计行 */
.stats-row {
  max-width: var(--max-content-width);
  margin: 0 auto var(--space-xl);
  padding: 0 var(--space-xl);
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: var(--space-md);
}
.stat-card {
  text-align: center;
  padding: var(--space-lg);
}
.stat-num {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--text-primary);
  font-variant-numeric: tabular-nums;
}
.stat-total, .stat-percent {
  font-size: 1rem;
  font-weight: 500;
  color: var(--text-tertiary);
}
.stat-label {
  font-size: 0.85rem;
  color: var(--text-secondary);
  margin-top: var(--space-xs);
}

/* 路径卡片 */
.path-grid {
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: 0 var(--space-xl);
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--space-lg);
}
.path-card {
  padding: var(--space-xl);
  cursor: pointer;
}
.path-icon {
  width: 52px;
  height: 52px;
  border-radius: var(--radius-md);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: var(--space-md);
}
.path-icon.large {
  width: 64px;
  height: 64px;
  flex-shrink: 0;
}
.path-card h3 {
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--text-primary);
}
.path-card p {
  font-size: 0.85rem;
  color: var(--text-tertiary);
  margin: var(--space-sm) 0 var(--space-lg);
  line-height: 1.6;
}
.path-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: var(--space-md);
}
.chapter-count {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  background: var(--bg-card);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}
.enter-btn {
  font-size: 0.85rem;
  color: var(--accent-purple);
  font-weight: 500;
}

/* 路径详情 */
.path-detail {
  max-width: var(--max-content-width);
  margin: 0 auto;
  padding: 0 var(--space-xl);
}
.back-btn {
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 0.9rem;
  margin-bottom: var(--space-md);
  padding: 4px 0;
}
.back-btn:hover { color: var(--accent-purple); }

.detail-header {
  display: flex;
  gap: var(--space-lg);
  align-items: center;
  padding: var(--space-xl);
  margin-bottom: var(--space-lg);
}
.detail-info { flex: 1; }
.detail-info h2 {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 4px;
}
.detail-info p {
  font-size: 0.9rem;
  color: var(--text-tertiary);
  margin-bottom: var(--space-md);
}

/* 章节卡片 */
.chapters {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
.chapter-card {
  padding: var(--space-lg);
}
.chapter-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: var(--space-md);
}
.chapter-header h4 {
  font-size: 1rem;
  font-weight: 600;
  color: var(--text-primary);
}
.chapter-count {
  font-size: 0.8rem;
  color: var(--text-tertiary);
}

.item-list {
  display: flex;
  flex-direction: column;
  gap: 6px;
}
.study-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.study-item:hover {
  background: var(--bg-card-hover);
}
.study-item.done .item-name {
  color: var(--text-tertiary);
  text-decoration: line-through;
}
.item-left {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  flex: 1;
}
.item-name {
  font-size: 0.9rem;
  color: var(--text-secondary);
}
.study-item.done .check-icon {
  color: var(--accent-purple);
}
.check-icon { font-size: 16px; flex-shrink: 0; color: var(--text-tertiary); }

@media (max-width: 640px) {
  .stats-row { grid-template-columns: 1fr; }
  .detail-header { flex-direction: column; text-align: center; }
}
</style>

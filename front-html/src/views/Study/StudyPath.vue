<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/common/PageHeader.vue'
import RevealOnScroll from '@/components/common/RevealOnScroll.vue'
import CountNumber from '@/components/common/CountNumber.vue'
import WikiPreview from '@/components/study/WikiPreview.vue'
import { useCurrentUser } from '@/composables/useCurrentUser'

const router = useRouter()
const { username } = useCurrentUser()
const PY_BASE = import.meta.env.VITE_PYTHON_BASE ?? ''

// ========== 学习路径数据（每条知识点绑定百科词条） ==========
interface StudyItem {
  name: string
  wikiSlug: string
  prompt: string
  difficulty: string
  estimatedMinutes: number
  prerequisites?: string[]
}
interface Chapter {
  id: string; name: string; description: string; items: StudyItem[]
}
interface StudyPath {
  id: string; name: string; desc: string; color: string; icon: string; chapters: Chapter[]
}

const paths: StudyPath[] = [
  {
    id: 'ds', name: '数据结构入门', desc: '从线性表到高级树结构，逐个生成动画直观理解', color: '#7c3aed', icon: 'DataAnalysis',
    chapters: [
      { id: 'ch1', name: '线性表', description: '最基础的数据组织方式',
        items: [
          { name: '栈 (Stack)', wikiSlug: 'stack', prompt: '栈的 push 和 pop 操作动画演示，展示后进先出特性', difficulty: '入门', estimatedMinutes: 15 },
          { name: '队列 (Queue)', wikiSlug: 'queue', prompt: '队列的入队出队操作可视化动画', difficulty: '入门', estimatedMinutes: 15 },
          { name: '链表 (Linked List)', wikiSlug: 'linked-list', prompt: '链表插入删除节点的动画演示，展示指针操作', difficulty: '入门', estimatedMinutes: 20 },
          { name: '哈希表 (Hash Table)', wikiSlug: 'hash-table', prompt: '哈希表存储和冲突解决的可视化动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['链表 (Linked List)'] },
        ],
      },
      { id: 'ch2', name: '树结构', description: '层次化数据模型',
        items: [
          { name: '二叉树 (Binary Tree)', wikiSlug: 'binary-tree', prompt: '二叉树三种遍历方式的可视化对比动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['栈 (Stack)', '队列 (Queue)'] },
          { name: '二叉搜索树 (BST)', wikiSlug: 'binary-search-tree', prompt: '二叉搜索树插入查找删除操作的动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['二叉树 (Binary Tree)'] },
          { name: '堆 (Heap)', wikiSlug: 'heap', prompt: '堆的建堆和调整过程动画，展示优先队列原理', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['二叉树 (Binary Tree)'] },
        ],
      },
      { id: 'ch3', name: '高级树结构', description: '高效查找与存储',
        items: [
          { name: 'AVL 树', wikiSlug: 'avl-tree', prompt: 'AVL 树自平衡旋转操作的动画演示', difficulty: '困难', estimatedMinutes: 30, prerequisites: ['二叉搜索树 (BST)'] },
          { name: '线段树 (Segment Tree)', wikiSlug: 'segment-tree', prompt: '线段树构建和区间查询的可视化动画', difficulty: '困难', estimatedMinutes: 30, prerequisites: ['二叉树 (Binary Tree)'] },
          { name: '字典树 (Trie)', wikiSlug: 'trie', prompt: 'Trie 树插入和前缀搜索的动画演示', difficulty: '中等', estimatedMinutes: 20 },
        ],
      },
    ],
  },
  {
    id: 'algo', name: '算法基础', desc: '从排序到分治，掌握经典算法设计思想', color: '#f59e0b', icon: 'Operation',
    chapters: [
      { id: 'ch1', name: '查找与二分', description: '高效查找的基石',
        items: [
          { name: '二分查找', wikiSlug: 'binary-search', prompt: '二分查找算法的执行过程动画，展示分治思想', difficulty: '入门', estimatedMinutes: 15 },
          { name: '滑动窗口', wikiSlug: 'sliding-window', prompt: '滑动窗口算法解决子数组问题的动画演示', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['二分查找'] },
          { name: '双指针', wikiSlug: 'two-pointers', prompt: '双指针技巧解决数组问题的可视化动画', difficulty: '中等', estimatedMinutes: 20 },
        ],
      },
      { id: 'ch2', name: '排序算法', description: '经典的排序策略对比',
        items: [
          { name: '冒泡排序', wikiSlug: 'bubble-sort', prompt: '冒泡排序算法执行过程可视化动画', difficulty: '入门', estimatedMinutes: 15 },
          { name: '归并排序', wikiSlug: 'merge-sort', prompt: '归并排序分治合并过程动画演示', difficulty: '中等', estimatedMinutes: 25 },
          { name: '快速排序', wikiSlug: 'quick-sort', prompt: '快速排序算法分治过程动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['归并排序'] },
          { name: '堆排序', wikiSlug: 'heap-sort', prompt: '堆排序建堆和排序过程动画演示', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['堆 (Heap)'] },
        ],
      },
      { id: 'ch3', name: '算法设计思想', description: '通用的问题求解策略',
        items: [
          { name: '贪心算法', wikiSlug: 'greedy', prompt: '贪心算法求解问题的动画演示', difficulty: '中等', estimatedMinutes: 25 },
          { name: '分治算法', wikiSlug: 'divide-and-conquer', prompt: '分治算法分解合并过程的可视化动画', difficulty: '中等', estimatedMinutes: 25 },
          { name: '回溯算法', wikiSlug: 'backtracking', prompt: '回溯算法搜索解空间的可视化动画', difficulty: '困难', estimatedMinutes: 30, prerequisites: ['分治算法'] },
        ],
      },
    ],
  },
  {
    id: 'graph', name: '图论基础', desc: '理解图的结构、遍历和最短路算法', color: '#06b6d4', icon: 'Connection',
    chapters: [
      { id: 'ch1', name: '图的遍历', description: '探索图的基础方法',
        items: [
          { name: '广度优先搜索 (BFS)', wikiSlug: 'bfs', prompt: 'BFS 逐层探索图的动画演示，展示最短路径性质', difficulty: '中等', estimatedMinutes: 25 },
          { name: '深度优先搜索 (DFS)', wikiSlug: 'dfs', prompt: 'DFS 递归探索图的动画演示', difficulty: '中等', estimatedMinutes: 25 },
          { name: '拓扑排序', wikiSlug: 'topological-sort', prompt: '拓扑排序的 Kahn 算法动画演示', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['深度优先搜索 (DFS)'] },
        ],
      },
      { id: 'ch2', name: '最短路径', description: '找到最优路径',
        items: [
          { name: 'Dijkstra 算法', wikiSlug: 'dijkstra算法', prompt: 'Dijkstra 最短路径算法的动画演示', difficulty: '中等', estimatedMinutes: 30, prerequisites: ['广度优先搜索 (BFS)'] },
          { name: 'Bellman-Ford 算法', wikiSlug: 'bellman-ford算法', prompt: 'Bellman-Ford 算法处理负权边的动画演示', difficulty: '困难', estimatedMinutes: 30, prerequisites: ['Dijkstra 算法'] },
          { name: 'Floyd-Warshall 算法', wikiSlug: 'floyd-warshall算法', prompt: 'Floyd-Warshall 全源最短路径动画演示', difficulty: '困难', estimatedMinutes: 25, prerequisites: ['Dijkstra 算法'] },
        ],
      },
      { id: 'ch3', name: '图的高级主题', description: '更深入的图论应用',
        items: [
          { name: '最小生成树', wikiSlug: 'minimum-spanning-tree', prompt: 'Prim/Kruskal 最小生成树算法动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['Dijkstra 算法'] },
          { name: '网络流', wikiSlug: 'network-flow', prompt: '最大流 Ford-Fulkerson 算法动画演示', difficulty: '困难', estimatedMinutes: 35, prerequisites: ['广度优先搜索 (BFS)'] },
          { name: '最短路径总览', wikiSlug: 'shortest-path', prompt: '多种最短路径算法对比可视化动画', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['Dijkstra 算法'] },
        ],
      },
    ],
  },
  {
    id: 'dp', name: '动态规划', desc: '掌握状态转移的思维方式', color: '#10b981', icon: 'Histogram',
    chapters: [
      { id: 'ch1', name: '基础概念', description: '理解 DP 的核心思想',
        items: [
          { name: '动态规划入门', wikiSlug: 'dynamic-programming', prompt: '动态规划核心思想：状态转移的可视化动画', difficulty: '中等', estimatedMinutes: 30 },
          { name: '编辑距离', wikiSlug: 'edit-distance', prompt: '编辑距离 DP 填表过程动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['动态规划入门'] },
        ],
      },
      { id: 'ch2', name: '经典问题', description: 'DP 的经典应用场景',
        items: [
          { name: '背包问题', wikiSlug: 'knapsack', prompt: '0-1 背包问题 DP 求解过程动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['动态规划入门'] },
          { name: '最长公共子序列 (LCS)', wikiSlug: 'lcs', prompt: 'LCS 动态规划填表回溯过程动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['动态规划入门'] },
          { name: '最长递增子序列 (LIS)', wikiSlug: 'lis', prompt: 'LIS 动态规划求解过程可视化动画', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['最长公共子序列 (LCS)'] },
        ],
      },
      { id: 'ch3', name: '进阶技巧', description: '高级 DP 技术',
        items: [
          { name: '状态压缩 DP', wikiSlug: '状态压缩动态规划', prompt: '状态压缩动态规划的位运算技巧动画', difficulty: '困难', estimatedMinutes: 35, prerequisites: ['背包问题'] },
        ],
      },
    ],
  },
  {
    id: 'math', name: '高等数学', desc: '用动画理解极限、微积分的几何意义', color: '#3b82f6', icon: 'TrendCharts',
    chapters: [
      { id: 'ch1', name: '极限与连续', description: '微积分的基石',
        items: [
          { name: '极限 (Limit)', wikiSlug: 'limit', prompt: '函数趋近于某点时极限的可视化动画', difficulty: '中等', estimatedMinutes: 20 },
          { name: '级数 (Series)', wikiSlug: 'series', prompt: '数列级数收敛发散的动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['极限 (Limit)'] },
        ],
      },
      { id: 'ch2', name: '微分学', description: '变化率与优化',
        items: [
          { name: '导数', wikiSlug: 'derivative', prompt: '导数的切线斜率几何意义动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['极限 (Limit)'] },
          { name: '偏导数', wikiSlug: 'partial-derivative', prompt: '多元函数偏导数的几何解释动画', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['导数'] },
          { name: '泰勒级数', wikiSlug: 'taylor-series', prompt: '泰勒级数多项式逼近函数的动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['导数'] },
          { name: '梯度下降', wikiSlug: 'gradient-descent', prompt: '梯度下降法寻找最小值的迭代过程动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['偏导数'] },
        ],
      },
      { id: 'ch3', name: '积分学与进阶', description: '面积、体积与变换',
        items: [
          { name: '定积分', wikiSlug: 'integral', prompt: '定积分黎曼和逼近过程动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['极限 (Limit)'] },
          { name: '傅里叶级数', wikiSlug: 'fourier-series', prompt: '傅里叶级数逼近方波的可视化动画', difficulty: '中等', estimatedMinutes: 30, prerequisites: ['泰勒级数'] },
        ],
      },
    ],
  },
  {
    id: 'algebra', name: '线性代数', desc: '矩阵变换、特征值的几何直观理解', color: '#8b5cf6', icon: 'Grid',
    chapters: [
      { id: 'ch1', name: '矩阵与变换', description: '线性代数的基本对象',
        items: [
          { name: '矩阵运算', wikiSlug: 'matrix', prompt: '矩阵乘法行列对应计算过程动画', difficulty: '入门', estimatedMinutes: 20 },
          { name: '行列式', wikiSlug: 'determinant', prompt: '行列式的几何意义：面积/体积变换动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['矩阵运算'] },
        ],
      },
      { id: 'ch2', name: '线性变换', description: '空间变换的几何直观',
        items: [
          { name: '线性变换', wikiSlug: 'linear-transformation', prompt: '线性变换对空间形变影响的可视化动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['矩阵运算'] },
          { name: '向量空间', wikiSlug: 'vector-space', prompt: '向量空间基变换的动画演示', difficulty: '中等', estimatedMinutes: 25 },
          { name: '正交基', wikiSlug: 'orthogonal-basis', prompt: 'Gram-Schmidt 正交化过程动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['向量空间'] },
        ],
      },
      { id: 'ch3', name: '特征分解', description: '矩阵的核心不变量',
        items: [
          { name: '特征值与特征向量', wikiSlug: 'eigenvalue', prompt: '特征向量和特征值的几何直观动画', difficulty: '中等', estimatedMinutes: 30, prerequisites: ['线性变换'] },
          { name: '矩阵对角化', wikiSlug: 'diagonalization', prompt: '矩阵对角化分解过程可视化', difficulty: '困难', estimatedMinutes: 30, prerequisites: ['特征值与特征向量'] },
        ],
      },
    ],
  },
  {
    id: 'prob', name: '概率统计', desc: '从随机变量到统计推断', color: '#ec4899', icon: 'PieChart',
    chapters: [
      { id: 'ch1', name: '概率基础', description: '理解随机性',
        items: [
          { name: '概率论基础', wikiSlug: 'probability-theory', prompt: '概率基本概念和公理的可视化动画', difficulty: '入门', estimatedMinutes: 20 },
          { name: '贝叶斯定理', wikiSlug: 'bayes-theorem', prompt: '贝叶斯定理条件概率更新的动画演示', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['概率论基础'] },
        ],
      },
      { id: 'ch2', name: '概率分布', description: '描述随机变量的行为',
        items: [
          { name: '正态分布', wikiSlug: 'normal-distribution', prompt: '正态分布的概率密度函数和性质动画', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['概率论基础'] },
          { name: '中心极限定理', wikiSlug: 'central-limit-theorem', prompt: '中心极限定理的采样分布收敛动画', difficulty: '中等', estimatedMinutes: 25, prerequisites: ['正态分布'] },
          { name: '大数定律', wikiSlug: 'law-of-large-numbers', prompt: '大数定律样本均值收敛过程动画', difficulty: '中等', estimatedMinutes: 20, prerequisites: ['概率论基础'] },
        ],
      },
      { id: 'ch3', name: '随机过程', description: '随时间演化的随机系统',
        items: [
          { name: '马尔可夫链', wikiSlug: 'markov-chain', prompt: '马尔可夫链状态转移的可视化动画', difficulty: '困难', estimatedMinutes: 30, prerequisites: ['概率论基础'] },
        ],
      },
    ],
  },
]

// ========== 状态管理 ==========
const activePathId = ref<string | null>(null)
const learned = ref<Record<string, boolean>>({})
// 扩展进度：记录学习时长和完成时间
const learnMeta = ref<Record<string, { seconds: number; completedAt: string }>>({})
// Wiki 内联面板 — 用 item key 追踪当前展开的是哪个知识点
const activeWikiKey = ref('')
const activeWikiSlug = ref('')
const activeWikiPrompt = ref('')
// 学习报告
const showReport = ref(false)
const reportData = ref<any>(null)
const reportLoading = ref(false)

const storageKey = computed(() => `cs:learn:${username.value || 'anon'}`)
const metaKey = computed(() => `cs:learn-meta:${username.value || 'anon'}`)

// ========== 进度持久化 ==========
async function loadProgress() {
  try {
    const res = await fetch(`${PY_BASE}/api/study/progress?username=${encodeURIComponent(username.value || 'anon')}`)
    if (res.ok) {
      const data = await res.json()
      if (data.data?.progress && Object.keys(data.data.progress).length > 0) {
        learned.value = data.data.progress
        localStorage.setItem(storageKey.value, JSON.stringify(data.data.progress))
      } else {
        _loadFromLocal()
      }
      return
    }
  } catch { /* ignore */ }
  _loadFromLocal()
}
function _loadFromLocal() {
  try {
    const saved = localStorage.getItem(storageKey.value)
    if (saved) learned.value = JSON.parse(saved)
  } catch { /* ignore */ }
  try {
    const saved = localStorage.getItem(metaKey.value)
    if (saved) learnMeta.value = JSON.parse(saved)
  } catch { /* ignore */ }
}
function saveProgress(durationSec = 0) {
  const json = JSON.stringify(learned.value)
  localStorage.setItem(storageKey.value, json)
  localStorage.setItem(metaKey.value, JSON.stringify(learnMeta.value))
  const now = new Date().toISOString()
  const params = new URLSearchParams({ username: username.value || 'anon', progress: json })
  if (durationSec > 0) {
    params.set('duration', String(durationSec))
    params.set('timestamp', now)
  }
  fetch(`${PY_BASE}/api/study/progress?${params.toString()}`, { method: 'POST' }).catch(() => {})
}

onMounted(loadProgress)
watch(learned, () => saveProgress(), { deep: true })

// ========== 计算属性 ==========
const activePath = computed(() => paths.find(p => p.id === activePathId.value))
const totalItems = computed(() => {
  let total = 0; paths.forEach(p => p.chapters.forEach(ch => total += ch.items.length)); return total
})
const learnedItems = computed(() => Object.values(learned.value).filter(Boolean).length)

function getItemKey(pathId: string, chId: string, itemName: string) { return `${pathId}:${chId}:${itemName}` }
function isLearned(pathId: string, chId: string, itemName: string) { return !!learned.value[getItemKey(pathId, chId, itemName)] }
function isLocked(item: StudyItem, pathId: string, chId: string): boolean {
  if (!item.prerequisites?.length) return false
  // 查找同路径下所有 item 中 name 匹配前置条件的
  const path = paths.find(p => p.id === pathId)
  if (!path) return false
  const allItems = path.chapters.flatMap(c => c.items)
  return item.prerequisites.some(pre => {
    const preItem = allItems.find(i => i.name === pre)
    if (!preItem) return false
    // 找到前置 item 的 chapter
    for (const ch of path.chapters) {
      if (ch.items.some(i => i.name === pre)) {
        return !isLearned(pathId, ch.id, pre)
      }
    }
    return !isLearned(pathId, chId, pre)
  })
}

function getPathProgress(pathId: string): number {
  const path = paths.find(p => p.id === pathId); if (!path) return 0
  let total = 0, done = 0
  path.chapters.forEach(ch => {
    ch.items.forEach(item => { total++; if (isLearned(pathId, ch.id, item.name)) done++ })
  })
  return total === 0 ? 0 : Math.round((done / total) * 100)
}

function getChapterProgress(pathId: string, chId: string): number {
  const path = paths.find(p => p.id === pathId); if (!path) return 0
  const ch = path.chapters.find(c => c.id === chId); if (!ch) return 0
  let total = ch.items.length, done = 0
  ch.items.forEach(item => { if (isLearned(pathId, chId, item.name)) done++ })
  return total === 0 ? 0 : Math.round((done / total) * 100)
}

// Wiki inline panel ref for scroll-into-view
const wikiRef = ref<InstanceType<typeof WikiPreview> | null>(null)

// ========== Wiki 内联面板 ==========
function openWiki(item: StudyItem, pathId: string, chId: string) {
  const key = getItemKey(pathId, chId, item.name)
  if (activeWikiKey.value === key) {
    // 再次点击同一个 → 收起
    activeWikiKey.value = ''
    return
  }
  activeWikiKey.value = key
  activeWikiSlug.value = item.wikiSlug
  activeWikiPrompt.value = item.prompt
  // 展开后等待动画完成，滚动到最底部再往上收一个滚轮距离
  nextTick(() => {
    setTimeout(() => {
      const maxScroll = Math.max(0, document.documentElement.scrollHeight - window.innerHeight)
      window.scrollTo({ top: maxScroll - 200, behavior: 'smooth' })
    }, 400)
  })
}

function onWikiReadingSeconds(seconds: number) {
  if (seconds > 0 && activeWikiKey.value) {
    learnMeta.value[activeWikiKey.value] = {
      seconds: (learnMeta.value[activeWikiKey.value]?.seconds || 0) + seconds,
      completedAt: new Date().toISOString(),
    }
  }
}

function onWikiGenerate(_promptTitle: string) {
  if (activeWikiKey.value) {
    learned.value[activeWikiKey.value] = true
  }
  const prompt = activeWikiPrompt.value
  activeWikiKey.value = ''
  ElMessage.success('开始生成动画...')
  router.push({ path: '/sandbox', query: { prompt } })
}

function onWikiMarkLearned() {
  if (activeWikiKey.value) {
    learned.value[activeWikiKey.value] = true
  }
  activeWikiKey.value = ''
  ElMessage.success('已标记为已学习')
}

function toggleLearned(pathId: string, chId: string, itemName: string) {
  const key = getItemKey(pathId, chId, itemName)
  const newVal = !learned.value[key]
  learned.value[key] = newVal

  // 取消打卡 → 级联取消所有后置依赖项
  if (!newVal) {
    _unlearnDependents(pathId, itemName)
  }
}

function _unlearnDependents(pathId: string, itemName: string) {
  const path = paths.find(p => p.id === pathId)
  if (!path) return

  // 找到所有依赖 itemName 的知识点
  const dependents: { chId: string; itemName: string }[] = []
  for (const ch of path.chapters) {
    for (const item of ch.items) {
      if (item.prerequisites?.includes(itemName)) {
        dependents.push({ chId: ch.id, itemName: item.name })
      }
    }
  }

  // 递归取消打卡
  for (const dep of dependents) {
    const depKey = getItemKey(pathId, dep.chId, dep.itemName)
    if (learned.value[depKey]) {
      learned.value[depKey] = false
      _unlearnDependents(pathId, dep.itemName) // 继续递归
    }
  }
}

// ========== 学习报告 ==========
async function loadReport() {
  reportLoading.value = true
  showReport.value = true
  try {
    const res = await fetch(`${PY_BASE}/api/study/report?username=${encodeURIComponent(username.value || 'anon')}`)
    if (res.ok) {
      const data = await res.json()
      reportData.value = data.data
    }
  } catch { /* ignore */ }
  finally { reportLoading.value = false }
}

// ========== 继续学习 ==========
function continueLearning(pathId: string) {
  openPath(pathId)
  nextTick(() => {
    const path = paths.find(p => p.id === pathId); if (!path) return
    for (const ch of path.chapters) {
      for (const item of ch.items) {
        if (!isLearned(pathId, ch.id, item.name) && !isLocked(item, pathId, ch.id)) {
          openWiki(item, pathId, ch.id)
          return
        }
      }
    }
  })
}

// ========== 路径切换 ==========
function openPath(id: string) { activePathId.value = id }
function backToList() { activePathId.value = null; activeWikiKey.value = '' }

function getDifficultyColor(d: string): string {
  if (['入门', '初级'].includes(d)) return 'var(--accent-green)'
  if (d === '中等') return 'var(--accent-orange)'
  return 'var(--accent-red)'
}
</script>

<template>
  <div class="study-page">
    <PageHeader title="学习路径" description="按路线逐个学习百科词条，理解后再生成动画巩固" icon="Guide" />

    <!-- 学习统计 + 报告入口 -->
    <RevealOnScroll>
      <div class="stats-row">
        <div class="stat-card glass-card" @click="loadReport" style="cursor:pointer" title="点击查看详细报告">
          <div class="stat-num">
            <CountNumber :value="learnedItems" :duration="1000" />
            <span class="stat-total">/{{ totalItems }}</span>
          </div>
          <div class="stat-label">已完成知识点 <el-icon style="font-size:12px"><ArrowRight /></el-icon></div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-num"><CountNumber :value="paths.length" :duration="800" /></div>
          <div class="stat-label">学习路线</div>
        </div>
        <div class="stat-card glass-card">
          <div class="stat-num">
            <CountNumber :value="Math.round(learnedItems / Math.max(totalItems, 1) * 100)" :duration="1000" />
            <span class="stat-percent">%</span>
          </div>
          <div class="stat-label">总体进度</div>
        </div>
        <div class="stat-card glass-card" v-if="reportData?.streak_days">
          <div class="stat-num streak">
            🔥 <CountNumber :value="reportData.streak_days" :duration="600" />
          </div>
          <div class="stat-label">连续学习天数</div>
        </div>
      </div>
    </RevealOnScroll>

    <!-- 学习报告面板 -->
    <Transition name="report-fade">
      <div v-if="showReport" class="report-panel glass-card">
        <div class="report-header">
          <h3><el-icon><DataAnalysis /></el-icon> 学习报告</h3>
          <el-button link @click="showReport = false"><el-icon><Close /></el-icon></el-button>
        </div>
        <div class="report-body" v-loading="reportLoading">
          <template v-if="reportData">
            <div class="report-stats">
              <div class="rs-item">
                <span class="rs-num">{{ reportData.total_minutes || 0 }}</span>
                <span class="rs-label">总学习分钟</span>
              </div>
              <div class="rs-item">
                <span class="rs-num">{{ reportData.streak_days || 0 }}</span>
                <span class="rs-label">连续打卡天数</span>
              </div>
              <div class="rs-item">
                <span class="rs-num">{{ learnedItems }}</span>
                <span class="rs-label">已完成知识点</span>
              </div>
              <div class="rs-item">
                <span class="rs-num">{{ reportData.daily?.length || 0 }}</span>
                <span class="rs-label">活跃天数</span>
              </div>
            </div>
            <!-- 每日学习热力 -->
            <div class="daily-heatmap" v-if="reportData.daily?.length">
              <div class="heatmap-title">最近学习记录</div>
              <div class="heatmap-row">
                <div v-for="d in reportData.daily.slice(-14)" :key="d.date"
                  class="heat-cell"
                  :title="`${d.date}: ${d.count} 个知识点, ${Math.round(d.seconds / 60)} 分钟`"
                  :style="{ '--intensity': Math.min(d.count / 5, 1) }"
                >
                  <div class="heat-dot"></div>
                  <span class="heat-date">{{ d.date.slice(5) }}</span>
                </div>
              </div>
            </div>
            <!-- 各路径进度 -->
            <div class="path-progress-list">
              <div class="heatmap-title">各路线进度</div>
              <div v-for="p in paths" :key="p.id" class="pp-item">
                <span class="pp-name" :style="{ color: p.color }">{{ p.name }}</span>
                <el-progress :percentage="getPathProgress(p.id)" :stroke-width="6" :color="p.color" style="flex:1;margin:0 12px" />
                <span class="pp-pct">{{ getPathProgress(p.id) }}%</span>
              </div>
            </div>
          </template>
          <div v-else class="report-empty">
            <p>还没有学习记录，开始你的第一条学习路径吧！</p>
          </div>
        </div>
      </div>
    </Transition>

    <!-- 路径列表 -->
    <template v-if="!activePath">
      <div class="path-grid">
        <RevealOnScroll v-for="(path, i) in paths" :key="path.id" :delay="i * 80">
          <div class="path-card glass-card" @click="openPath(path.id)">
            <div class="path-icon" :style="{ background: path.color + '20', color: path.color }">
              <el-icon :size="28"><component :is="path.icon" /></el-icon>
            </div>
            <h3>{{ path.name }}</h3>
            <p>{{ path.desc }}</p>
            <el-progress :percentage="getPathProgress(path.id)" :stroke-width="6" :color="path.color" />
            <div class="path-footer">
              <span class="chapter-count">{{ path.chapters.length }} 章 · {{ path.chapters.reduce((s, c) => s + c.items.length, 0) }} 个知识点</span>
              <span class="enter-btn" v-if="getPathProgress(path.id) > 0 && getPathProgress(path.id) < 100" @click.stop="continueLearning(path.id)">继续学习 →</span>
              <span class="enter-btn" v-else>开始学习 →</span>
            </div>
          </div>
        </RevealOnScroll>
      </div>
    </template>

    <!-- 路径详情 -->
    <template v-else>
      <div class="path-detail">
        <button class="back-btn" @click="backToList">← 返回路径列表</button>

        <div class="detail-header glass-card">
          <div class="path-icon large" :style="{ background: activePath!.color + '20', color: activePath!.color }">
            <el-icon :size="36"><component :is="activePath!.icon" /></el-icon>
          </div>
          <div class="detail-info">
            <h2>{{ activePath!.name }}</h2>
            <p>{{ activePath!.desc }}</p>
            <div style="display:flex;align-items:center;gap:12px">
              <el-progress :percentage="getPathProgress(activePath!.id)" :stroke-width="8" :color="activePath!.color" style="flex:1" />
              <el-button v-if="getPathProgress(activePath!.id) > 0 && getPathProgress(activePath!.id) < 100" size="small" type="primary" round @click="continueLearning(activePath!.id)">
                继续学习
              </el-button>
            </div>
          </div>
        </div>

        <!-- 章节列表 -->
        <div class="chapters">
          <RevealOnScroll v-for="(ch, i) in activePath!.chapters" :key="ch.id" :delay="i * 60">
            <div class="chapter-card glass-card">
              <div class="chapter-header">
                <div class="chapter-title-row">
                  <h4>{{ ch.name }}</h4>
                  <span class="chapter-desc">{{ ch.description }}</span>
                </div>
                <span class="chapter-stat">
                  {{ ch.items.filter(item => isLearned(activePath!.id, ch.id, item.name)).length }}/{{ ch.items.length }}
                  <span class="chapter-pct">({{ getChapterProgress(activePath!.id, ch.id) }}%)</span>
                </span>
              </div>
              <div class="item-list">
                <div
                  v-for="item in ch.items"
                  :key="item.name"
                  class="study-item"
                  :class="{
                    done: isLearned(activePath!.id, ch.id, item.name),
                    locked: isLocked(item, activePath!.id, ch.id)
                  }"
                >
                  <div
                    class="item-left"
                    :class="{ 'no-toggle': isLocked(item, activePath!.id, ch.id) }"
                    @click="!isLocked(item, activePath!.id, ch.id) && toggleLearned(activePath!.id, ch.id, item.name)"
                  >
                    <el-icon v-if="isLocked(item, activePath!.id, ch.id)" class="check-icon"><Lock /></el-icon>
                    <el-icon v-else-if="isLearned(activePath!.id, ch.id, item.name)" class="check-icon"><CircleCheckFilled /></el-icon>
                    <span v-else class="check-circle"></span>
                    <div class="item-info">
                      <span class="item-name">{{ item.name }}</span>
                      <span class="item-meta">
                        <el-tag :style="{ color: getDifficultyColor(item.difficulty), borderColor: getDifficultyColor(item.difficulty) + '40' }" size="small" effect="plain">
                          {{ item.difficulty }}
                        </el-tag>
                        <span class="item-time">~{{ item.estimatedMinutes }} 分钟</span>
                      </span>
                    </div>
                  </div>
                  <el-button
                    v-if="!isLocked(item, activePath!.id, ch.id)"
                    size="small"
                    :type="isLearned(activePath!.id, ch.id, item.name) ? 'default' : 'primary'"
                    round
                    @click="openWiki(item, activePath!.id, ch.id)"
                    v-ripple
                  >
                    <el-icon><Reading /></el-icon>
                    {{ isLearned(activePath!.id, ch.id, item.name) ? '复习' : '学习' }}
                  </el-button>
                  <el-tooltip v-else content="需先完成前置知识点" placement="top">
                    <el-button size="small" type="info" round disabled>
                      <el-icon><Lock /></el-icon> 未解锁
                    </el-button>
                  </el-tooltip>
                </div>
              </div>

            </div>
          </RevealOnScroll>
        </div>

        <!-- Wiki 内联预览 — 展示在章节列表下方，用 activeWikiSlug 驱动 -->
        <WikiPreview
          ref="wikiRef"
          v-if="activeWikiKey"
          :wiki-slug="activeWikiSlug"
          :visible="true"
          @close="activeWikiKey = ''"
          @generate="onWikiGenerate"
          @mark-learned="onWikiMarkLearned"
          @reading-seconds="onWikiReadingSeconds"
        />
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
  grid-template-columns: repeat(4, 1fr);
  gap: var(--space-md);
}
.stat-card { text-align: center; padding: var(--space-lg); }
.stat-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-md); }
.stat-num { font-size: 2rem; font-weight: 800; color: var(--text-primary); font-variant-numeric: tabular-nums; }
.stat-num.streak { font-size: 1.8rem; }
.stat-total, .stat-percent { font-size: 0.95rem; font-weight: 500; color: var(--text-tertiary); }
.stat-label {
  font-size: 0.8rem; color: var(--text-secondary); margin-top: var(--space-xs);
  display: flex; align-items: center; justify-content: center; gap: 4px;
}

/* 报告面板 */
.report-panel {
  max-width: var(--max-content-width); margin: 0 auto var(--space-xl); padding: 0; overflow: hidden;
}
.report-header {
  display: flex; justify-content: space-between; align-items: center;
  padding: var(--space-md) var(--space-lg); border-bottom: 1px solid var(--border-color);
  background: linear-gradient(135deg, rgba(124,58,237,0.06), rgba(6,182,212,0.04));
}
.report-header h3 { margin: 0; font-size: 1rem; font-weight: 700; display: flex; align-items: center; gap: 8px; }
.report-body { padding: var(--space-lg); }
.report-stats {
  display: grid; grid-template-columns: repeat(4, 1fr); gap: var(--space-md); margin-bottom: var(--space-xl);
}
.rs-item { text-align: center; }
.rs-num { font-size: 1.6rem; font-weight: 800; color: var(--accent-purple); display: block; }
.rs-label { font-size: 0.75rem; color: var(--text-tertiary); margin-top: 2px; }

.heatmap-title { font-size: 0.8rem; font-weight: 600; color: var(--text-secondary); margin-bottom: var(--space-sm); }
.heatmap-row { display: flex; gap: 6px; flex-wrap: wrap; margin-bottom: var(--space-lg); }
.heat-cell { display: flex; flex-direction: column; align-items: center; gap: 2px; }
.heat-dot {
  width: 14px; height: 14px; border-radius: 3px;
  background: color-mix(in srgb, var(--accent-purple) calc(var(--intensity, 0) * 100%), transparent);
  min-background: rgba(124, 58, 237, calc(var(--intensity, 0) * 0.8 + 0.05));
  background: rgba(124, 58, 237, calc(var(--intensity, 0) * 0.8 + 0.05));
}
.heat-date { font-size: 0.6rem; color: var(--text-tertiary); }

.path-progress-list { display: flex; flex-direction: column; gap: 8px; }
.pp-item { display: flex; align-items: center; }
.pp-name { font-size: 0.82rem; font-weight: 600; min-width: 90px; }
.pp-pct { font-size: 0.78rem; color: var(--text-tertiary); min-width: 36px; text-align: right; }
.report-empty { text-align: center; color: var(--text-tertiary); padding: var(--space-xl); }

/* 动画 */
.report-fade-enter-active { transition: all 0.3s ease; }
.report-fade-leave-active { transition: all 0.2s ease; }
.report-fade-enter-from, .report-fade-leave-to { opacity: 0; transform: translateY(-10px); }

/* 路径卡片 */
.path-grid {
  max-width: var(--max-content-width); margin: 0 auto; padding: 0 var(--space-xl);
  display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: var(--space-lg);
}
.path-card { padding: var(--space-xl); cursor: pointer; }
.path-icon {
  width: 52px; height: 52px; border-radius: var(--radius-md);
  display: flex; align-items: center; justify-content: center; margin-bottom: var(--space-md);
}
.path-icon.large { width: 64px; height: 64px; flex-shrink: 0; }
.path-card h3 { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); }
.path-card p { font-size: 0.82rem; color: var(--text-tertiary); margin: var(--space-sm) 0 var(--space-lg); line-height: 1.6; }
.path-footer { display: flex; justify-content: space-between; align-items: center; margin-top: var(--space-md); }
.chapter-count { font-size: 0.72rem; color: var(--text-tertiary); background: var(--bg-card); padding: 2px 10px; border-radius: var(--radius-full); }
.enter-btn { font-size: 0.82rem; color: var(--accent-purple); font-weight: 500; }

/* 路径详情 */
.path-detail { max-width: var(--max-content-width); margin: 0 auto; padding: 0 var(--space-xl); }
.back-btn { background: none; border: none; color: var(--text-secondary); cursor: pointer; font-size: 0.9rem; margin-bottom: var(--space-md); padding: 4px 0; }
.back-btn:hover { color: var(--accent-purple); }
.detail-header { display: flex; gap: var(--space-lg); align-items: center; padding: var(--space-xl); margin-bottom: var(--space-lg); }
.detail-info { flex: 1; }
.detail-info h2 { font-size: 1.4rem; font-weight: 700; color: var(--text-primary); margin-bottom: 4px; }
.detail-info p { font-size: 0.88rem; color: var(--text-tertiary); margin-bottom: var(--space-md); }

/* 章节 */
.chapters { display: flex; flex-direction: column; gap: var(--space-md); }
.chapter-card { padding: var(--space-lg); }
.chapter-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: var(--space-md); }
.chapter-title-row { display: flex; flex-direction: column; gap: 2px; }
.chapter-title-row h4 { font-size: 1rem; font-weight: 600; color: var(--text-primary); margin: 0; }
.chapter-desc { font-size: 0.78rem; color: var(--text-tertiary); }
.chapter-stat { font-size: 0.78rem; color: var(--text-tertiary); white-space: nowrap; }
.chapter-pct { color: var(--accent-purple); }

/* 学习项 */
.item-list { display: flex; flex-direction: column; gap: 6px; }
.study-item {
  display: flex; align-items: center; justify-content: space-between; gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md); border-radius: var(--radius-sm);
  transition: background var(--transition-fast);
}
.study-item:hover { background: var(--bg-card-hover); }
.study-item.done { opacity: 0.7; }
.study-item.locked { opacity: 0.5; }
.item-left { display: flex; align-items: center; gap: var(--space-sm); cursor: pointer; flex: 1; min-width: 0; }
.item-left.no-toggle { cursor: default; }
.check-icon { font-size: 18px; flex-shrink: 0; color: var(--text-tertiary); }
.study-item.done .check-icon { color: var(--accent-purple); }
.study-item.locked .check-icon { color: var(--text-tertiary); }
.check-circle {
  width: 18px; height: 18px; flex-shrink: 0;
  border-radius: 50%; border: 2px solid var(--text-tertiary);
  opacity: 0.5;
}
.item-info { display: flex; flex-direction: column; gap: 2px; min-width: 0; }
.item-name { font-size: 0.9rem; color: var(--text-secondary); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.study-item.done .item-name { color: var(--text-tertiary); text-decoration: line-through; }
.item-meta { display: flex; align-items: center; gap: 8px; }
.item-time { font-size: 0.7rem; color: var(--text-tertiary); }

@media (max-width: 900px) {
  .stats-row { grid-template-columns: repeat(2, 1fr); }
  .report-stats { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 640px) {
  .stats-row { grid-template-columns: 1fr; }
  .report-stats { grid-template-columns: 1fr 1fr; }
  .detail-header { flex-direction: column; text-align: center; }
}
</style>

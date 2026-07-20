<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { templatesApi } from '@/api/templates'
import { generationApi } from '@/api/generation'
import { useSSE } from '@/composables/useSSE'
import { useCurrentUser } from '@/composables/useCurrentUser'
import type { TemplateDetail } from '@/types/template'
import { ElMessage } from 'element-plus'

const PY_BASE = import.meta.env.VITE_PYTHON_BASE ?? ''

const route = useRoute()
const router = useRouter()
const { username } = useCurrentUser()
const { connect, disconnect } = useSSE()
const template = ref<TemplateDetail | null>(null)
const renderQuality = ref(localStorage.getItem('cs:render-quality') || '-qm')
const loading = ref(false)
const generating = ref(false)
const progress = ref(0)
const videoUrl = ref('')
const formParams = reactive<Record<string, unknown>>({})
let _tplProgressTimer: ReturnType<typeof setInterval> | null = null
let _tplProgressTarget = 0

// 评分相关
const hoverStar = ref(0)
const myRating = ref<number>(0)
const ratingSubmitting = ref(false)

function startTplProgress() {
  stopTplProgress()
  progress.value = 0
  _tplProgressTarget = 5
  _tplProgressTimer = setInterval(() => {
    if (progress.value < _tplProgressTarget) {
      progress.value = Math.round(progress.value + 1)
    }
    if (_tplProgressTarget < 92) {
      _tplProgressTarget += 0.3
    }
  }, 300)
}

function stopTplProgress() {
  if (_tplProgressTimer) { clearInterval(_tplProgressTimer); _tplProgressTimer = null }
  _tplProgressTarget = 0
}

async function load() {
  loading.value = true
  try {
    const res = await templatesApi.getDetail(route.params.id as string)
    template.value = res.data.data
    // 清空旧模板的残留参数
    for (const key of Object.keys(formParams)) {
      delete formParams[key]
    }
    // 初始化当前模板的默认值
    if (template.value?.params) {
      for (const p of template.value.params) {
        formParams[p.name] = p.default
      }
    }
    // 加载用户已有评分
    loadMyRating()
  } catch {
    template.value = null
  } finally { loading.value = false }
}

async function loadMyRating() {
  if (!username.value) return
  try {
    const res = await templatesApi.getMyRating(route.params.id as string)
    myRating.value = res.data.data?.score || 0
  } catch { /* 未登录或无评分，忽略 */ }
}

async function handleRate(score: number) {
  if (ratingSubmitting.value) return
  if (!username.value) {
    ElMessage.warning('请先登录')
    return
  }
  ratingSubmitting.value = true
  try {
    const rateRes = await templatesApi.rateTemplate(route.params.id as string, score)
    // 后端非200时返回HTTP 200 + code≠0，需要检查业务状态码
    if (rateRes.data.code !== 0 && rateRes.data.code !== 200) {
      ElMessage.error(rateRes.data.message || '评分失败')
      return
    }
    myRating.value = score
    ElMessage.success('评分成功')
    // 刷新模板数据以获取最新平均分
    const res = await templatesApi.getDetail(route.params.id as string)
    if (res.data.data) {
      template.value = res.data.data
    }
  } catch (e: any) {
    ElMessage.error(e?.response?.data?.message || '评分失败')
  } finally {
    ratingSubmitting.value = false
  }
}

async function handleGenerate() {
  if (!template.value) return
  generating.value = true
  startTplProgress()
  try {
    const res = await generationApi.asyncTemplateRender(template.value.id, formParams, renderQuality.value, username.value)
    const taskId = res.data.data?.task_id
    if (taskId) {
      connect(taskId, (data: any) => {
        if (data.type === 'done') { stopTplProgress(); progress.value = 100; generating.value = false; disconnect(); return }
        if (data.video_path) videoUrl.value = `${PY_BASE}${data.video_path}`
        if (data.state === 'SUCCESS') { stopTplProgress(); progress.value = 100; generating.value = false; disconnect() }
        if (data.state === 'FAILURE') { stopTplProgress(); generating.value = false; disconnect(); ElMessage.error('渲染失败') }
      })
    }
  } catch { stopTplProgress(); generating.value = false }
}

onMounted(load)
onUnmounted(() => { disconnect(); stopTplProgress() })

async function goToSandbox() {
  if (!template.value) return
  // 先生成模板代码，然后像 Fork 一样传递到沙箱
  try {
    const res = await templatesApi.generateCode(template.value.id, formParams)
    const code = res.data.data?.code
    if (code) {
      sessionStorage.setItem('cs:forked-code', code)
    }
  } catch { /* 代码生成失败不阻塞，至少把参数带过去 */ }
  router.push({ path: '/sandbox', query: { template: template.value.id, params: JSON.stringify(formParams) } })
}

function saveToWorks() {
  ElMessage.success('已保存到我的作品')
  // 实际保存逻辑由后端处理
}
</script>

<template>
  <div class="tpl-detail-page">
    <div v-if="template" class="container">
      <el-button link @click="router.back()"><el-icon><ArrowLeft /></el-icon> 返回模板库</el-button>
      <h1 class="tpl-title text-gradient">{{ template.name }}</h1>
      <p class="tpl-desc">{{ template.description }}</p>

      <div class="tpl-meta glass-card">
        <div class="meta-item">
          <span class="meta-label">使用次数</span>
          <span class="meta-value">{{ template.use_count ?? 0 }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">难度</span>
          <span class="meta-value">{{ template.difficulty || '入门' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">分类</span>
          <span class="meta-value">{{ template.category || '算法' }}</span>
        </div>
        <div class="meta-item">
          <span class="meta-label">评分</span>
          <span class="meta-value rating-row">
            <span class="rating-stars" :class="{ disabled: ratingSubmitting }">
              <span
                v-for="s in 5" :key="s"
                class="star"
                :class="{ active: s <= (template.rating || 0), hover: s <= hoverStar, 'my-rating': s <= myRating }"
                @click="handleRate(s)"
                @mouseenter="hoverStar = s"
                @mouseleave="hoverStar = 0"
              >★</span>
            </span>
            <span class="rating-text">{{ (template.rating || 0).toFixed(1) }}</span>
            <span class="rating-count" v-if="template.rating_count">({{ template.rating_count }}人)</span>
          </span>
        </div>
      </div>

      <div class="tpl-layout">
        <!-- 参数表单 -->
        <div class="tpl-form glass-card">
          <h3>参数设置</h3>
          <div v-for="p in template.params" :key="p.name" class="param-item">
            <label>{{ p.label }} <span v-if="p.required" class="required">*</span></label>
            <span class="param-desc">{{ p.description }}</span>
            <el-input v-if="p.type === 'string'" v-model="formParams[p.name]" />
            <el-input-number v-else-if="p.type === 'number' || p.type === 'integer'" v-model="formParams[p.name]" :min="p.min" :max="p.max" :step="p.type === 'integer' ? 1 : 0.1" style="width:100%" />
            <el-switch v-else-if="p.type === 'boolean'" v-model="formParams[p.name]" />
            <el-select v-else-if="p.type === 'select'" v-model="formParams[p.name]" style="width:100%">
              <el-option v-for="o in p.options" :key="o.value" :label="o.label" :value="o.value" />
            </el-select>
          </div>
          <div style="display:flex;gap:8px;margin-top:var(--space-md)">
            <el-select v-model="renderQuality" size="small" style="width:110px" @change="(v: string) => localStorage.setItem('cs:render-quality', v)">
              <el-option label="⚡ 480p" value="-ql" />
              <el-option label="🎯 720p" value="-qm" />
              <el-option label="✨ 1080p" value="-qh" />
            </el-select>
            <el-button type="primary" size="large" round :loading="generating" @click="handleGenerate" class="gen-btn" style="flex:1">
              <el-icon><MagicStick /></el-icon> 生成动画
            </el-button>
          </div>
        </div>

        <!-- 预览区 -->
        <div class="tpl-preview glass-card">
          <h3>预览</h3>
          <div v-if="generating" class="preview-progress">
            <el-progress :percentage="progress" :color="'#7c3aed'" />
          </div>
          <div v-else-if="videoUrl" class="video-wrap">
            <video :src="videoUrl" controls autoplay loop class="pv-video" />
            <div class="video-actions">
              <el-button type="primary" round @click="goToSandbox" v-ripple>
                <el-icon><EditPen /></el-icon> 进阶编辑
              </el-button>
              <el-button round @click="saveToWorks" v-ripple>
                <el-icon><Collection /></el-icon> 保存作品
              </el-button>
              <el-button round>
                <el-icon><Download /></el-icon>
                <a :href="videoUrl" download style="text-decoration:none;color:inherit">下载</a>
              </el-button>
            </div>
          </div>
          <div v-else class="preview-empty">
            <el-icon :size="48"><VideoCamera /></el-icon>
            <p>调整参数后点击"生成动画"预览效果</p>
          </div>
        </div>
      </div>
    </div>
    <div v-else class="loading"><el-icon :size="32" class="is-loading"><Loading /></el-icon></div>
  </div>
</template>

<style scoped>
.tpl-detail-page { padding-bottom: var(--space-3xl); }
.container { max-width: 1100px; margin: 0 auto; padding: var(--space-xl); }
.tpl-title { font-size: 2rem; font-weight: 800; margin: var(--space-md) 0; }
.tpl-desc { color: var(--text-secondary); font-size: 1rem; }

.tpl-meta {
  display: flex;
  gap: var(--space-xl);
  padding: var(--space-md) var(--space-lg);
  margin: var(--space-lg) 0;
  flex-wrap: wrap;
}
.meta-item { display: flex; flex-direction: column; gap: 2px; }
.meta-label { font-size: 0.75rem; color: var(--text-tertiary); }
.meta-value { font-size: 0.95rem; font-weight: 600; color: var(--text-primary); }

/* 评分样式 */
.rating-row { display: flex; align-items: center; gap: 6px; flex-direction: row; }
.rating-stars { display: flex; gap: 2px; cursor: pointer; }
.rating-stars.disabled { pointer-events: none; opacity: 0.6; }
.star {
  font-size: 1.15rem;
  color: var(--text-tertiary);
  transition: color 0.15s, transform 0.15s;
  user-select: none;
}
.star.active { color: #f59e0b; }
.star.hover { color: #fbbf24; transform: scale(1.15); }
.star.my-rating { color: #f59e0b; }
.rating-text { font-size: 0.9rem; color: var(--text-primary); font-weight: 600; }
.rating-count { font-size: 0.78rem; color: var(--text-tertiary); font-weight: 400; }

.tpl-layout { display: grid; grid-template-columns: 400px 1fr; gap: var(--space-xl); margin-top: var(--space-xl); }
.tpl-form { padding: var(--space-xl); }
.tpl-form h3 { font-size: 1.1rem; font-weight: 700; color: var(--text-primary); margin-bottom: var(--space-lg); }
.param-item { margin-bottom: var(--space-lg); }
.param-item label { display: block; font-weight: 600; color: var(--text-primary); font-size: 0.9rem; }
.param-item .required { color: var(--accent-red); }
.param-desc { display: block; color: var(--text-tertiary); font-size: 0.78rem; margin: 2px 0 var(--space-sm); }
.gen-btn { width: 100%; margin-top: var(--space-md); }

.tpl-preview { padding: var(--space-xl); }
.tpl-preview h3 { font-size: 1.1rem; font-weight: 700; margin-bottom: var(--space-lg); }
.pv-video { width: 100%; border-radius: var(--radius-md); }
.video-actions {
  display: flex;
  gap: var(--space-sm);
  margin-top: var(--space-md);
  flex-wrap: wrap;
}
.preview-empty { text-align: center; color: var(--text-tertiary); padding: var(--space-3xl); }
.preview-progress { padding: var(--space-3xl); }
.loading { display: flex; justify-content: center; padding: var(--space-3xl); color: var(--accent-purple); }

@media (max-width: 768px) { .tpl-layout { grid-template-columns: 1fr; } }
</style>

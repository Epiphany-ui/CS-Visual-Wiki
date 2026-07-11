<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { templatesApi } from '@/api/templates'
import { generationApi } from '@/api/generation'
import { useSSE } from '@/composables/useSSE'
import type { TemplateDetail } from '@/types/template'
import { ElMessage } from 'element-plus'

const route = useRoute()
const router = useRouter()
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
  } catch {
    template.value = null
  } finally { loading.value = false }
}

async function handleGenerate() {
  if (!template.value) return
  generating.value = true
  startTplProgress()
  try {
    const res = await generationApi.asyncTemplateRender(template.value.id, formParams, renderQuality.value)
    const taskId = res.data.data?.task_id
    if (taskId) {
      connect(taskId, (data: any) => {
        if (data.type === 'done') { stopTplProgress(); progress.value = 100; generating.value = false; disconnect(); return }
        if (data.video_path) videoUrl.value = `http://localhost:8000${data.video_path}`
        if (data.state === 'SUCCESS') { stopTplProgress(); progress.value = 100; generating.value = false; disconnect() }
        if (data.state === 'FAILURE') { stopTplProgress(); generating.value = false; disconnect(); ElMessage.error('渲染失败') }
      })
    }
  } catch { stopTplProgress(); generating.value = false }
}

onMounted(load)
onUnmounted(() => { disconnect(); stopTplProgress() })
</script>

<template>
  <div class="tpl-detail-page">
    <div v-if="template" class="container">
      <el-button link @click="router.back()"><el-icon><ArrowLeft /></el-icon> 返回模板库</el-button>
      <h1 class="tpl-title text-gradient">{{ template.name }}</h1>
      <p class="tpl-desc">{{ template.description }}</p>

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
.preview-empty { text-align: center; color: var(--text-tertiary); padding: var(--space-3xl); }
.preview-progress { padding: var(--space-3xl); }
.loading { display: flex; justify-content: center; padding: var(--space-3xl); color: var(--accent-purple); }

@media (max-width: 768px) { .tpl-layout { grid-template-columns: 1fr; } }
</style>

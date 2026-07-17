<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'

interface ParamItem {
  name: string
  type: 'number' | 'integer' | 'float' | 'string' | 'boolean' | 'color'
  value: any
  min?: number
  max?: number
  step?: number
}

const props = defineProps<{
  code: string
}>()

const emit = defineEmits<{
  (e: 'update:code', code: string): void
  (e: 'render'): void
}>()

const params = ref<ParamItem[]>([])
const collapsed = ref(false)

// ========== 从代码中提取参数 ==========
function extractParams(code: string): ParamItem[] {
  const results: ParamItem[] = []
  const lines = code.split('\n')
  const found = new Set<string>()

  for (const line of lines) {
    // 匹配变量定义：name = value
    const match = line.match(/^\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*=\s*(.+?)\s*(#.*)?$/)
    if (!match) continue

    const name = match[1]
    const rawValue = match[2].trim()

    // 跳过私有变量和常见非参数变量
    if (name.startsWith('_') || ['self', 'config', 'class', 'def'].includes(name)) continue
    if (found.has(name)) continue

    let param: ParamItem | null = null

    // 布尔值
    if (rawValue === 'True' || rawValue === 'False') {
      param = { name, type: 'boolean', value: rawValue === 'True' }
    }
    // 整数
    else if (/^-?\d+$/.test(rawValue)) {
      const val = parseInt(rawValue)
      param = {
        name,
        type: 'integer',
        value: val,
        min: val > 0 ? 1 : -1000,
        max: Math.max(val * 3, 100),
        step: 1,
      }
    }
    // 浮点数
    else if (/^-?\d+\.\d+$/.test(rawValue)) {
      const val = parseFloat(rawValue)
      param = {
        name,
        type: 'float',
        value: val,
        min: val > 0 ? 0 : -10,
        max: Math.max(val * 3, 10),
        step: 0.1,
      }
    }
    // 字符串（带引号）
    else if (/^['"].*['"]$/.test(rawValue)) {
      const val = rawValue.slice(1, -1)
      // 颜色值检测
      if (/^#[0-9a-fA-F]{6}$/.test(val) || /^#[0-9a-fA-F]{3}$/.test(val)) {
        param = { name, type: 'color', value: val }
      } else {
        param = { name, type: 'string', value: val }
      }
    }

    if (param) {
      results.push(param)
      found.add(name)
    }
  }

  return results.slice(0, 20) // 最多显示20个参数
}

// 监听代码变化，重新提取参数
watch(
  () => props.code,
  (newCode) => {
    params.value = extractParams(newCode)
  },
  { immediate: true }
)

// ========== 修改参数 ==========
function updateParam(paramName: string, newValue: any) {
  const param = params.value.find(p => p.name === paramName)
  if (!param) return

  // 防护：数字输入清空时 newValue 为 undefined，不更新
  if ((param.type === 'integer' || param.type === 'float') && newValue === undefined) return

  param.value = newValue

  // 格式化新值
  let strValue: string
  if (param.type === 'boolean') {
    strValue = newValue ? 'True' : 'False'
  } else if (param.type === 'string' || param.type === 'color') {
    // 转义字符串中的单引号，避免破坏 Python 语法
    const escaped = String(newValue).replace(/'/g, "\\'")
    strValue = `'${escaped}'`
  } else if (param.type === 'float') {
    // 浮点数限制精度，避免超长小数写入代码
    strValue = Number(newValue).toFixed(3).replace(/\.?0+$/, '')
  } else {
    strValue = String(newValue)
  }

  // 替换代码中的对应行（变量名做正则转义，防止特殊字符注入）
  const lines = props.code.split('\n')
  let updated = false
  const escapedName = paramName.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
  for (let i = 0; i < lines.length; i++) {
    const regex = new RegExp(`^(\\s*)${escapedName}\\s*=\\s*.+$`)
    if (regex.test(lines[i])) {
      const indent = lines[i].match(/^\s*/)?.[0] || ''
      const comment = lines[i].match(/#.+$/)?.[0] || ''
      lines[i] = `${indent}${paramName} = ${strValue} ${comment}`.trimEnd()
      updated = true
      break
    }
  }

  if (updated) {
    emit('update:code', lines.join('\n'))
  }
}

// 一键渲染
function handleRender() {
  emit('render')
  ElMessage.success('开始渲染...')
}

const hasParams = computed(() => params.value.length > 0)
</script>

<template>
  <div class="param-panel glass-card" :class="{ collapsed }">
    <div class="panel-header" @click="collapsed = !collapsed">
      <h4>
        <el-icon><Setting /></el-icon>
        参数面板
      </h4>
      <el-icon :class="{ rotate: collapsed }"><ArrowUp /></el-icon>
    </div>

    <div v-show="!collapsed" class="panel-body">
      <div v-if="!hasParams" class="empty-tip">
        <el-icon :size="24"><InfoFilled /></el-icon>
        <p>代码中未检测到可调参数</p>
        <p class="hint">定义顶层变量即可自动识别：<code>n = 10</code></p>
      </div>

      <div v-else class="param-list">
        <div v-for="p in params" :key="p.name" class="param-item">
          <div class="param-label">
            <span class="param-name">{{ p.name }}</span>
            <span class="param-type">{{ p.type }}</span>
          </div>

          <!-- 整数/浮点：滑块 + 数字 -->
          <div v-if="p.type === 'integer' || p.type === 'float'" class="param-control">
            <el-slider
              :model-value="p.value"
              :min="p.min"
              :max="p.max"
              :step="p.step"
              :show-tooltip="false"
              @update:model-value="(v: number) => updateParam(p.name, v)"
            />
            <el-input-number
              size="small"
              :model-value="p.value"
              :min="p.min"
              :max="p.max"
              :step="p.step"
              controls-position="right"
              @update:model-value="(v: number) => updateParam(p.name, v)"
            />
          </div>

          <!-- 布尔：开关 -->
          <div v-else-if="p.type === 'boolean'" class="param-control">
            <el-switch
              :model-value="p.value"
              @update:model-value="(v: boolean) => updateParam(p.name, v)"
            />
          </div>

          <!-- 字符串：输入框 -->
          <div v-else-if="p.type === 'string'" class="param-control">
            <el-input
              size="small"
              :model-value="p.value"
              @update:model-value="(v: string) => updateParam(p.name, v)"
            />
          </div>

          <!-- 颜色：选择器 -->
          <div v-else-if="p.type === 'color'" class="param-control">
            <el-color-picker
              :model-value="p.value"
              size="small"
              @update:model-value="(v: string) => updateParam(p.name, v)"
            />
          </div>
        </div>
      </div>

      <el-button
        v-if="hasParams"
        type="primary"
        round
        full
        class="render-btn"
        @click="handleRender"
        v-ripple
      >
        <el-icon><VideoPlay /></el-icon>
        用当前参数渲染
      </el-button>
    </div>
  </div>
</template>

<style scoped>
.param-panel {
  padding: 0;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
.param-panel.collapsed .panel-body {
  display: none;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: var(--space-md) var(--space-lg);
  cursor: pointer;
  border-bottom: 1px solid var(--border-color);
  user-select: none;
}
.panel-header h4 {
  margin: 0;
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--text-primary);
  display: flex;
  align-items: center;
  gap: 6px;
}
.panel-header .el-icon {
  color: var(--text-tertiary);
  transition: transform var(--transition-normal);
}
.panel-header .el-icon.rotate {
  transform: rotate(180deg);
}

.panel-body {
  padding: var(--space-md) var(--space-lg) var(--space-lg);
  flex: 1;
  overflow-y: auto;
}

.empty-tip {
  text-align: center;
  padding: var(--space-lg) 0;
  color: var(--text-tertiary);
}
.empty-tip p {
  margin: var(--space-sm) 0 0;
  font-size: 0.85rem;
}
.empty-tip .hint {
  font-size: 0.75rem;
  color: var(--text-tertiary);
  margin-top: 4px;
}
.empty-tip code {
  background: var(--bg-secondary);
  padding: 1px 6px;
  border-radius: 4px;
  font-size: 0.8rem;
}

.param-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}

.param-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.param-label {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.param-name {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--text-primary);
  font-family: 'JetBrains Mono', Consolas, monospace;
}
.param-type {
  font-size: 0.7rem;
  color: var(--text-tertiary);
  background: var(--bg-secondary);
  padding: 1px 6px;
  border-radius: 4px;
  text-transform: lowercase;
}

.param-control {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}
.param-control .el-slider {
  flex: 1;
}
.param-control .el-input-number {
  width: 90px;
}

.render-btn {
  margin-top: var(--space-lg);
}
</style>

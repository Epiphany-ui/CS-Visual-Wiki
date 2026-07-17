import { createApp } from 'vue'
import { createPinia } from 'pinia'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import 'element-plus/theme-chalk/dark/css-vars.css'
import * as ElementPlusIconsVue from '@element-plus/icons-vue'

import App from './App.vue'
import router from './router'
import { useAppStore } from './stores/app'
import { vRipple } from './directives/ripple'
import { vTilt } from './directives/tilt'

import './styles/global.scss'
import './styles/transitions.css'

const app = createApp(App)

// 注册所有 Element Plus 图标
for (const [key, component] of Object.entries(ElementPlusIconsVue)) {
  app.component(key, component)
}

// 全局指令
app.directive('ripple', vRipple)
app.directive('tilt', vTilt)

app.use(createPinia())
app.use(router)
app.use(ElementPlus)

// 全局统一 ElMessage 提示时长（默认 3 秒 → 1.2 秒）
import { ElMessage } from 'element-plus'
const _origSuccess = ElMessage.success
const _origError = ElMessage.error
const _origWarning = ElMessage.warning
const _origInfo = ElMessage.info
function _patchMsg(orig: Function) {
  return (opts: any) => {
    if (typeof opts === 'string') return orig({ message: opts, duration: 1200 })
    return orig({ ...opts, duration: opts.duration ?? 1200 })
  }
}
ElMessage.success = _patchMsg(_origSuccess) as any
ElMessage.error = _patchMsg(_origError) as any
ElMessage.warning = _patchMsg(_origWarning) as any
ElMessage.info = _patchMsg(_origInfo) as any

// 初始化主题
const appStore = useAppStore()
appStore.initTheme()

app.mount('#app')

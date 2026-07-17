import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

/**
 * 从 localStorage 读取当前用户信息的统一入口。
 * 消除各组件中重复的 localStorage.getItem('username') / 'token' / 'cs:nickname:…' 等模式。
 *
 * 注意：displayName / avatar 依赖 localStorage，而 localStorage 本身不是响应式的，
 * 因此在同一会话内修改昵称/头像后，调用方应调用 refresh() 强制刷新。
 */

function migrateLegacy(userKey: (base: string) => string) {
  const oldAvatar = localStorage.getItem('cs:avatar')
  const oldNick = localStorage.getItem('cs:nickname')
  if (oldAvatar && !localStorage.getItem(userKey('avatar'))) {
    localStorage.setItem(userKey('avatar'), oldAvatar)
  }
  if (oldNick && !localStorage.getItem(userKey('nickname'))) {
    localStorage.setItem(userKey('nickname'), oldNick)
  }
  // 不删除旧 key — 其他用户登录时也能迁移
}

export function useCurrentUser() {
  const userStore = useUserStore()

  /** 依当前用户隔离的 localStorage key */
  function userKey(base: string): string {
    const u = userStore.username || 'default'
    return `cs:${base}:${u}`
  }

  // 首次调用时迁移旧的全局 key
  migrateLegacy(userKey)

  // ---- 响应式属性 ----

  const username = computed(() => userStore.username)
  const userId = computed(() => userStore.userId)
  const token = computed(() => userStore.token)
  const isLoggedIn = computed(() => userStore.isLoggedIn)

  // displayName / avatar 依赖 localStorage，不是原生响应式的。
  // 用 _version 作为手动缓存失效标记。
  const _version = ref(0)
  function refresh() { _version.value++ }

  const displayName = computed(() => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const _ = _version.value // 读取以建立依赖
    try {
      const perUser = localStorage.getItem(userKey('nickname'))
      if (perUser) return perUser
    } catch { /* ignore */ }
    return username.value || '匿名用户'
  })

  const avatar = computed(() => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const _ = _version.value // 读取以建立依赖
    try {
      const perUser = localStorage.getItem(userKey('avatar'))
      if (perUser) return perUser
    } catch { /* ignore */ }
    return ''
  })

  return {
    username,
    userId,
    displayName,
    avatar,
    token,
    isLoggedIn,
    userKey,
    refresh,
  }
}

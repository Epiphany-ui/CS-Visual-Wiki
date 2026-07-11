import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

function isTokenExpired(token: string): boolean {
  try {
    const payload = JSON.parse(atob(token.split('.')[1]))
    return payload.exp * 1000 < Date.now()
  } catch {
    return true
  }
}

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || 0)

  const isLoggedIn = computed(() => {
    if (!token.value || !username.value) return false
    return !isTokenExpired(token.value)
  })

  // 登录/注册时将服务端返回的头像和昵称写入 per-user localStorage
  function _saveProfileToLocal(u: string, nickname?: string, avatar?: string) {
    if (nickname) localStorage.setItem(`cs:nickname:${u}`, nickname)
    if (avatar) localStorage.setItem(`cs:avatar:${u}`, avatar)
  }

  async function login(name: string, pwd: string) {
    const res = await authApi.login(name, pwd)
    const data = res.data.data
    if (data && data.token) {
      token.value = data.token
      username.value = data.username
      userId.value = data.userId
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('userId', String(data.userId))
      _saveProfileToLocal(data.username, data.nickname, data.avatar)
    }
    return res.data
  }

  async function register(name: string, pwd: string) {
    const res = await authApi.register(name, pwd)
    const data = res.data.data
    if (data && data.token) {
      token.value = data.token
      username.value = data.username
      userId.value = data.userId
      localStorage.setItem('token', data.token)
      localStorage.setItem('username', data.username)
      localStorage.setItem('userId', String(data.userId))
      _saveProfileToLocal(data.username, data.nickname, data.avatar)
    }
    return res.data
  }

  function logout() {
    token.value = ''
    username.value = ''
    userId.value = 0
    localStorage.removeItem('token')
    localStorage.removeItem('username')
    localStorage.removeItem('userId')
    // 不清除 per-user 头像/昵称 — 下次同账号登录时自动恢复
  }

  return { token, username, userId, isLoggedIn, login, register, logout }
})

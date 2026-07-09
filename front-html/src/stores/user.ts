import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { authApi } from '@/api/auth'

export const useUserStore = defineStore('user', () => {
  const token = ref(localStorage.getItem('token') || '')
  const username = ref(localStorage.getItem('username') || '')
  const userId = ref(Number(localStorage.getItem('userId')) || 0)

  const isLoggedIn = computed(() => !!token.value && !!username.value)

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
  }

  return { token, username, userId, isLoggedIn, login, register, logout }
})

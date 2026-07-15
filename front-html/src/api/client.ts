import axios from 'axios'
import { ElMessage } from 'element-plus'

// 后端地址通过环境变量配置（生产环境可设为同域空字符串走 Nginx 反代）
const JAVA_BASE = import.meta.env.VITE_JAVA_BASE ?? ''
const PYTHON_BASE = import.meta.env.VITE_PYTHON_BASE ?? ''

// Java 业务后端
export const javaClient = axios.create({
  baseURL: JAVA_BASE,
  timeout: 15000,
  headers: { 'Content-Type': 'application/json' },
})

// Python AI 引擎
export const pythonClient = axios.create({
  baseURL: PYTHON_BASE,
  timeout: 120000,
  headers: { 'Content-Type': 'application/json' },
})

// 请求拦截器：自动注入 JWT
javaClient.interceptors.request.use(config => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器：统一错误提示
const responseInterceptor = (response: any) => {
  const data = response.data
  if (data && data.code != null && data.code !== 0 && data.code !== 200) {
    ElMessage.error(data.message || data.msg || '服务器错误')
  }
  return response
}

const errorInterceptor = (error: any) => {
  if (error.response) {
    const { status, data } = error.response
    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('username')
      localStorage.removeItem('userId')
      window.location.hash = '#/login'
    } else if (status === 429) {
      ElMessage.warning('请求过于频繁，请稍后重试')
    } else if (status >= 500) {
      ElMessage.error(data?.detail || data?.message || '服务器内部错误')
    }
  } else {
    ElMessage.error('网络连接失败，请检查后端服务')
    console.error(error.message)
  }
  return Promise.reject(error)
}

javaClient.interceptors.response.use(responseInterceptor, errorInterceptor)
pythonClient.interceptors.response.use(responseInterceptor, errorInterceptor)

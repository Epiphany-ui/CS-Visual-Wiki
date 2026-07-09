import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': resolve(__dirname, 'src'),
    },
  },
  css: {
    preprocessorOptions: {
      scss: {
        additionalData: '',
      },
    },
  },
  server: {
    port: 5173,
    proxy: {
      // Java 后端（仅认证 + 任务）
      '/api/register': { target: 'http://localhost:8080', changeOrigin: true },
      '/api/login': { target: 'http://localhost:8080', changeOrigin: true },
      '/api/submit': { target: 'http://localhost:8080', changeOrigin: true },
      '/api/task/status': { target: 'http://localhost:8080', changeOrigin: true },
      '/api/task/list': { target: 'http://localhost:8080', changeOrigin: true },
      // Python AI 引擎（默认：百科/模板/生成/视频/调试/SSE 等）
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/videos': { target: 'http://localhost:8000', changeOrigin: true },
      '/frames': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})

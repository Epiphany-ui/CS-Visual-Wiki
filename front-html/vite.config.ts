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
    host: '0.0.0.0',
    allowedHosts: true,
    proxy: {
      // Java 后端 — 作品/用户中心等
      '/api/v1': { target: 'http://localhost:8080', changeOrigin: true },
      '/work': { target: 'http://localhost:8080', changeOrigin: true },
      '/user': { target: 'http://localhost:8080', changeOrigin: true },
      // Python AI 引擎 — 百科/模板/生成/视频/调试/SSE 等
      '/api': { target: 'http://localhost:8000', changeOrigin: true },
      '/videos': { target: 'http://localhost:8000', changeOrigin: true },
      '/frames': { target: 'http://localhost:8000', changeOrigin: true },
      '/avatars': { target: 'http://localhost:8000', changeOrigin: true },
    },
  },
})

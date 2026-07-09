<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { ElMessage } from 'element-plus'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const isLogin = ref(true)
const username = ref('')
const password = ref('')
const loading = ref(false)

async function handleSubmit() {
  if (!username.value || !password.value) {
    ElMessage.warning('请填写用户名和密码')
    return
  }
  loading.value = true
  try {
    const res = isLogin.value
      ? await userStore.login(username.value, password.value)
      : await userStore.register(username.value, password.value)

    if (res.code === 0 || res.code === 200) {
      ElMessage.success(isLogin.value ? '登录成功！' : '注册成功！')
      const redirect = (route.query.redirect as string) || '/'
      router.push(redirect)
    } else {
      ElMessage.error(res.message || res.msg || '操作失败')
    }
  } catch (e: any) {
    const msg = e?.response?.data?.message || e?.response?.data?.msg || '网络错误，请检查后端服务'
    ElMessage.error(msg)
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-page">
    <!-- 装饰背景 -->
    <div class="hero-bg">
      <div class="gradient-blob" style="top: -80px; left: -80px; width: 400px; height: 400px; background: var(--accent-purple);"></div>
      <div class="gradient-blob" style="bottom: -60px; right: -60px; width: 350px; height: 350px; background: var(--accent-blue);"></div>
    </div>

    <div class="login-card glass-card">
      <div class="login-header">
        <span class="logo-icon">◆</span>
        <h2>{{ isLogin ? '欢迎回来' : '创建账号' }}</h2>
        <p>{{ isLogin ? '登录后开始你的可视化学习之旅' : '注册即表示同意服务条款' }}</p>
      </div>

      <el-form @submit.prevent="handleSubmit" size="large" class="login-form">
        <el-form-item>
          <el-input
            v-model="username"
            placeholder="用户名"
            prefix-icon="User"
            autocomplete="username"
          />
        </el-form-item>
        <el-form-item>
          <el-input
            v-model="password"
            type="password"
            placeholder="密码"
            prefix-icon="Lock"
            show-password
            autocomplete="current-password"
          />
        </el-form-item>
        <el-button
          type="primary"
          native-type="submit"
          :loading="loading"
          round
          class="submit-btn"
        >
          {{ isLogin ? '登录' : '注册' }}
        </el-button>
      </el-form>

      <div class="login-footer">
        <span>{{ isLogin ? '还没有账号？' : '已有账号？' }}</span>
        <el-button link type="primary" @click="isLogin = !isLogin">
          {{ isLogin ? '立即注册' : '去登录' }}
        </el-button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.login-page {
  min-height: calc(100vh - var(--header-height));
  display: flex;
  align-items: center;
  justify-content: center;
  position: relative;
  overflow: hidden;
  padding: var(--space-xl);
}
.hero-bg {
  position: absolute;
  inset: 0;
  pointer-events: none;
}

.login-card {
  position: relative; z-index: 2; width: 100%; max-width: 420px;
  padding: var(--space-2xl); animation: scale-in 0.5s var(--ease-bounce) both;
}
.login-header {
  text-align: center;
  margin-bottom: var(--space-xl);
}
.logo-icon {
  font-size: 2.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.login-header h2 {
  margin-top: var(--space-md);
  font-size: 1.5rem;
  font-weight: 700;
  color: var(--text-primary);
}
.login-header p {
  margin-top: var(--space-xs);
  color: var(--text-tertiary);
  font-size: 0.9rem;
}
.submit-btn {
  width: 100%;
  margin-top: var(--space-md);
  height: 44px;
}
.login-footer {
  margin-top: var(--space-lg);
  text-align: center;
  color: var(--text-tertiary);
  font-size: 0.9rem;
}
</style>

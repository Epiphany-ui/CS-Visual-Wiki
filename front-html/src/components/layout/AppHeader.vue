<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useUserStore } from '@/stores/user'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import AvatarIcon from '@/components/common/AvatarIcon.vue'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()
const appStore = useAppStore()
const searchKeyword = ref('')
const searchFocused = ref(false)
const themeSpinning = ref(false)
const avatarUrl = ref('')
const displayName = ref(userStore.username)

function refreshProfile() {
  try {
    avatarUrl.value = localStorage.getItem('cs:avatar') || ''
    displayName.value = localStorage.getItem('cs:nickname') || userStore.username
  } catch { /* ignore */ }
}
refreshProfile()

// 从 Profile 页返回时自动刷新头像和昵称
watch(() => route.fullPath, () => refreshProfile())

function handleSearch() {
  if (searchKeyword.value.trim()) {
    router.push({ path: '/wiki', query: { q: searchKeyword.value.trim() } })
    searchKeyword.value = ''
  }
}

function handleLogout() {
  userStore.logout()
  ElMessage.success('已退出登录')
  router.push('/')
}
</script>

<template>
  <header class="app-header">
    <div class="header-inner">
      <!-- Logo -->
      <router-link to="/" class="logo">
        <span class="logo-icon">◆</span>
        <span class="logo-text">CS Visual Learn</span>
      </router-link>

      <!-- 导航 -->
      <nav class="nav-links">
        <router-link to="/wiki" class="nav-link" active-class="nav-active">
          <el-icon><Collection /></el-icon> 百科
        </router-link>
        <router-link to="/sandbox" class="nav-link" active-class="nav-active">
          <el-icon><EditPen /></el-icon> 沙箱
        </router-link>
        <router-link to="/templates" class="nav-link" active-class="nav-active">
          <el-icon><Tickets /></el-icon> 模板库
        </router-link>
        <router-link to="/gallery" class="nav-link" active-class="nav-active">
          <el-icon><PictureFilled /></el-icon> 画廊
        </router-link>
        <router-link to="/community" class="nav-link" active-class="nav-active">
          <el-icon><User /></el-icon> 社区
        </router-link>
        <router-link to="/study" class="nav-link" active-class="nav-active">
          <el-icon><School /></el-icon> 备考
        </router-link>
      </nav>

      <div class="header-actions">
        <!-- 搜索 -->
        <div class="search-box" :class="{ 'search-expanded': searchFocused }">
          <el-input
            v-model="searchKeyword"
            placeholder="搜索知识点、动画、模板..."
            size="default"
            prefix-icon="Search"
            @keyup.enter="handleSearch"
            @focus="searchFocused = true"
            @blur="searchFocused = false"
            class="search-input"
          />
        </div>

        <!-- 主题切换 -->
        <el-button
          :icon="appStore.theme === 'dark' ? 'Sunny' : 'Moon'"
          circle
          size="default"
          @click="appStore.toggleTheme"
          class="theme-btn"
          :class="{ 'theme-spin': themeSpinning }"
          @click.once="themeSpinning = true; setTimeout(() => themeSpinning = false, 600)"
        />

        <!-- 用户 -->
        <template v-if="userStore.isLoggedIn">
          <el-dropdown trigger="click">
            <div class="user-avatar">
              <AvatarIcon :name="displayName" :size="32" :avatar-url="avatarUrl" />
              <span class="username">{{ displayName }}</span>
            </div>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="router.push('/profile')">
                  <el-icon><User /></el-icon> 个人中心
                </el-dropdown-item>
                <el-dropdown-item @click="router.push('/sandbox')">
                  <el-icon><EditPen /></el-icon> 创作工坊
                </el-dropdown-item>
                <el-dropdown-item divided @click="handleLogout">
                  <el-icon><SwitchButton /></el-icon> 退出登录
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
        <template v-else>
          <el-button type="primary" size="default" @click="router.push('/login')" round>
            登录 / 注册
          </el-button>
        </template>
      </div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 100;
  height: var(--header-height);
  background: rgba(10, 10, 15, 0.85);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-bottom: 1px solid var(--border-color);
  transition: background var(--transition-base);
}

[data-theme="light"] .app-header {
  background: rgba(255, 255, 255, 0.85);
}

.header-inner {
  max-width: var(--max-content-width);
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  gap: var(--space-lg);
  padding: 0 var(--space-xl);
}

/* Logo */
.logo {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  text-decoration: none;
  flex-shrink: 0;
}
.logo-icon {
  font-size: 1.5rem;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}
.logo-text {
  font-size: 1.05rem;
  font-weight: 700;
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  white-space: nowrap;
}

/* 导航 */
.nav-links {
  display: flex;
  gap: var(--space-xs);
  flex: 1;
  justify-content: center;
}
.nav-link {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 6px 14px;
  border-radius: var(--radius-md);
  text-decoration: none;
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
  transition: all var(--transition-fast);
  white-space: nowrap;
}
.nav-link:hover {
  color: var(--text-primary);
  background: var(--bg-card-hover);
}
.nav-link.nav-active {
  color: var(--accent-purple-light);
  background: rgba(124, 58, 237, 0.1);
  position: relative;
}
.nav-link.nav-active::after {
  content: '';
  position: absolute;
  bottom: 2px;
  left: 50%;
  transform: translateX(-50%);
  width: 16px;
  height: 2px;
  border-radius: 1px;
  background: var(--accent-purple-light);
  animation: nav-indicator-in var(--duration-normal) var(--ease-bounce);
}
@keyframes nav-indicator-in {
  from { width: 0; opacity: 0; }
  to { width: 16px; opacity: 1; }
}

/* 操作区 */
.header-actions {
  display: flex;
  align-items: center;
  gap: var(--space-md);
  flex-shrink: 0;
}

.search-box {
  width: 200px;
  transition: width var(--transition-base);
}
.search-box.search-expanded {
  width: 260px;
}
.search-input :deep(.el-input__wrapper) {
  background: var(--bg-card);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-full);
  box-shadow: none;
  transition: border-color var(--transition-fast), box-shadow var(--transition-fast);
}
.search-input :deep(.el-input__wrapper:hover) {
  border-color: var(--border-color-light);
}
.search-input :deep(.el-input__wrapper.is-focus) {
  border-color: var(--accent-purple);
  box-shadow: 0 0 0 2px rgba(124, 58, 237, 0.15);
}

.theme-btn {
  background: var(--bg-card) !important;
  border: 1px solid var(--border-color) !important;
  color: var(--text-secondary) !important;
  transition: all var(--transition-base) !important;
}
.theme-btn:hover {
  color: var(--text-primary) !important;
  border-color: var(--accent-purple) !important;
}
.theme-btn.theme-spin :deep(i) {
  animation: theme-spin 0.6s var(--ease-spring);
}
@keyframes theme-spin {
  0% { transform: rotate(0deg) scale(1); }
  50% { transform: rotate(180deg) scale(1.2); }
  100% { transform: rotate(360deg) scale(1); }
}

/* 用户 */
.user-avatar {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  cursor: pointer;
  color: var(--text-secondary);
}
.user-avatar:hover {
  color: var(--text-primary);
}
.username {
  font-size: 0.9rem;
  font-weight: 500;
}
</style>

import { createRouter, createWebHashHistory } from 'vue-router'
import { useUserStore } from '@/stores/user'

const router = createRouter({
  history: createWebHashHistory(),
  routes: [
    {
      path: '/',
      name: 'home',
      component: () => import('@/views/Home.vue'),
      meta: { title: '首页' },
    },
    {
      path: '/login',
      name: 'login',
      component: () => import('@/views/Login.vue'),
      meta: { title: '登录', guest: true },
    },
    {
      path: '/wiki',
      name: 'wiki',
      component: () => import('@/views/Wiki/WikiList.vue'),
      meta: { title: '知识百科' },
    },
    {
      path: '/wiki/:slug',
      name: 'wiki-detail',
      component: () => import('@/views/Wiki/WikiDetail.vue'),
      meta: { title: '词条详情' },
    },
    {
      path: '/sandbox',
      name: 'sandbox',
      component: () => import('@/views/Sandbox.vue'),
      meta: { title: '动画沙箱', auth: true },
    },
    {
      path: '/templates',
      name: 'templates',
      component: () => import('@/views/Templates/TemplateList.vue'),
      meta: { title: '模板库' },
    },
    {
      path: '/templates/:id',
      name: 'template-detail',
      component: () => import('@/views/Templates/TemplateDetail.vue'),
      meta: { title: '模板详情' },
    },
    {
      path: '/gallery',
      name: 'gallery',
      component: () => import('@/views/Gallery/GalleryList.vue'),
      meta: { title: '精选画廊' },
    },
    {
      path: '/gallery/:filename',
      name: 'gallery-detail',
      component: () => import('@/views/Gallery/GalleryDetail.vue'),
      meta: { title: '作品详情' },
    },
    {
      path: '/community',
      name: 'community',
      component: () => import('@/views/Community/CommunityFeed.vue'),
      meta: { title: '社区' },
    },
    {
      path: '/study',
      name: 'study',
      component: () => import('@/views/Study/StudyPath.vue'),
      meta: { title: '备考学习' },
    },
    {
      path: '/profile',
      name: 'profile',
      component: () => import('@/views/Profile.vue'),
      meta: { title: '个人中心', auth: true },
    },
    {
      path: '/user/:username',
      name: 'user-profile',
      component: () => import('@/views/UserProfile.vue'),
      meta: { title: '用户主页' },
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'not-found',
      component: () => import('@/views/NotFound.vue'),
      meta: { title: '404' },
    },
  ],
})

// 路由守卫
router.beforeEach((to) => {
  const userStore = useUserStore()

  // 需要登录的页面 → 跳转登录页，携带目标地址
  if (to.meta.auth) {
    if (!userStore.isLoggedIn) {
      return { name: 'login', query: { redirect: to.fullPath } }
    }
  }

  // 已登录用户访问游客页面（如登录页） → 跳转首页
  if (to.meta.guest && userStore.isLoggedIn) {
    return { name: 'home' }
  }
})

export default router

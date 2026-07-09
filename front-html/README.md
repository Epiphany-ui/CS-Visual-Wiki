# CS Visual Learn — 前端

基于 Vue 3 + TypeScript + Vite + Element Plus 构建的交互式知识可视化学习平台前端。

## 技术栈

| 技术 | 用途 |
|------|------|
| Vue 3 + Composition API | 组件框架 |
| TypeScript | 类型安全 |
| Vite 5 | 构建工具 |
| Element Plus | UI 组件库 |
| Pinia | 状态管理 |
| Vue Router (Hash) | 路由 |
| Axios | HTTP 客户端 |
| CodeMirror 6 | 代码编辑器（Python 语法高亮） |
| KaTeX + marked | LaTeX 数学公式渲染 |
| @vueuse/core | 工具 composables（IntersectionObserver 等） |

## 页面结构

| 路由 | 页面 | 说明 |
|------|------|------|
| `/` | 首页 | Hero + 分类导航 + 平台数据 |
| `/wiki` | 知识百科 | 111 个词条，7 大分类，搜索筛选 |
| `/wiki/:slug` | 词条详情 | Markdown + LaTeX 渲染，文本选中即生成动画 |
| `/sandbox` | 动画沙箱 | AI 对话 + CodeMirror 编辑器 + 视频预览，SSE 实时进度 |
| `/templates` | 模板库 | 10 个参数化模板，零代码创作 |
| `/templates/:id` | 模板详情 | 动态参数表单 + 一键生成 |
| `/gallery` | 画廊 | 全部作品 / 我的作品 / 我的收藏，三标签页 |
| `/gallery/:filename` | 作品详情 | 视频播放 + 标题编辑 + 收藏 + GIF 转换 |
| `/community` | 社区 | 即将上线 |
| `/study` | 备考学习 | 即将上线 |
| `/login` | 登录注册 | JWT 认证 |
| `/profile` | 个人中心 | 统计数据 + 快捷入口 |

## 开发

```bash
npm install
npm run dev       # http://localhost:5173
npm run build     # 生产构建
```

## 架构

```
src/
├── api/           # Axios 客户端 + 7 个 API 模块
├── components/    # 共享组件（AnimatedBackground, RevealOnScroll, CodeEditor 等）
├── composables/   # useSSE（SSE 自动重连）
├── router/        # 路由配置 + 导航守卫
├── stores/        # Pinia（app/user/task）
├── styles/        # CSS 变量 + 全局样式 + 动画关键帧
├── types/         # TypeScript 类型定义
└── views/         # 13 个页面组件
```

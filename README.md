# CS-Visual-Learn — 让抽象概念，动起来

> 基于 Manim + DeepSeek 大语言模型的交互式知识可视化学习平台

## 项目简介

将教材中抽象的算法、数据结构、数学定理转化为直观可交互的动画，提供"百科学习 → AI 生成 → 模板创作 → 画廊分享"的完整闭环。

- **学习者**：通过动画直观理解抽象概念，111 个百科词条覆盖 7 大知识领域
- **创作者**：自然语言描述需求，AI 自动生成 Manim 代码并渲染为动画
- **模板使用者**：10 个参数化模板，零代码生成专业教学动画

## 技术架构

```
┌──────────────────────────────────────────────────┐
│               前端 (front-html/)                   │
│  Vue 3 + TypeScript + Vite + Element Plus         │
│  CodeMirror 6 + KaTeX + marked + Pinia            │
│  13 个页面：首页/百科/沙箱/模板/画廊/社区/备考/登录   │
└────────────────────┬─────────────────────────────┘
                     │ HTTP + SSE
┌────────────────────▼─────────────────────────────┐
│           业务服务层 (java-web/)                    │
│  Spring Boot 2.7 + MyBatis-Plus + MySQL           │
│  JWT 认证 + 用户系统 + 14 张表                      │
└────────────────────┬─────────────────────────────┘
                     │ HTTP
┌────────────────────▼─────────────────────────────┐
│           核心引擎层 (ai-service/)                  │
│  FastAPI + DeepSeek + Manim Community             │
│  ChromaDB + Celery + Redis + SSE 实时推送          │
│  30+ REST API + 异步任务队列 + 画廊收藏              │
└──────────────────────────────────────────────────┘
```

## 项目结构

```
cs-visual-learn/
├── start.bat              # Windows 一键启动脚本
├── README.md
│
├── front-html/            # Vue 3 前端 — 13 个页面
│   └── src/
│       ├── views/         # 页面组件
│       ├── components/    # 共享组件（AnimatedBackground 等）
│       ├── api/           # API 客户端层
│       ├── stores/        # Pinia 状态管理
│       ├── composables/   # SSR / useSSE
│       ├── styles/        # CSS 变量 + 全局样式 + 动画
│       └── router/        # Vue Router 路由
│
├── ai-service/            # Python AI 引擎 — 30+ API
│   ├── main.py            # FastAPI 入口
│   ├── ai_engine.py       # 核心引擎
│   ├── services/          # 扩展服务
│   ├── workers/           # Celery 异步任务
│   ├── wiki_data/         # 111 个百科词条（7 大分类）
│   ├── templates/         # 10 个参数化模板
│   └── outputs/           # 渲染产物（代码 + 视频）
│
└── java-web/              # Spring Boot 业务层
    └── src/main/java/com/manim/
```

## 快速启动

```bash
# Windows 一键启动（推荐）
双击 start.bat

# 或手动启动各服务：
# 1. Redis
"C:\Program Files\Redis\redis-server.exe"

# 2. API 服务
cd ai-service
python main.py  # → http://localhost:8000

# 3. Celery Worker
celery -A workers.celery_app worker --loglevel=info -P solo

# 4. 前端
cd front-html
npm run dev  # → http://localhost:5173
```

## 环境要求

- Python ≥ 3.10 + Manim Community + FFmpeg
- Node.js 18+ + npm 9+
- DeepSeek API Key（必需）
- Redis（异步任务 + 画廊数据）
- MySQL 8.0（Java 业务层）
- Ollama（RAG 向量检索，可选）

## 许可证

MIT License

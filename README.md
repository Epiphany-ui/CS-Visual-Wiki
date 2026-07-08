# CS-Visual-Learn — 让抽象概念，动起来

> 基于 Manim + 大语言模型的交互式知识可视化学习平台，面向计算机科学与数学领域。

[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

## 项目简介

CS-Visual-Learn 将教材中抽象的算法、数据结构、数学定理转化为直观可交互的动画，同时提供零代码/低代码的动画创作能力，打造"学习-理解-创作-分享"的完整闭环。

- **对学习者**：告别"看书就懂，做题就废"，通过动画直观理解抽象概念
- **对创作者**：不需要掌握复杂的 Manim 语法，通过自然语言或模板参数快速生成专业级教学动画
- **对教育者**：一键生成可视化教学素材，降低课件制作成本

## 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    前端展示层 (front-html/)               │
│    Vue 3 + TypeScript + Vite + Element Plus             │
│    Monaco Editor  │  Video.js  │  Pinia  │  Vue Router  │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP + SSE
┌───────────────────────────▼─────────────────────────────┐
│                    业务服务层 (java-web/)                 │
│    Spring Boot 2.7 + MyBatis-Plus + MySQL 8.0           │
│    Spring Security + JWT  │  Redis  │  MinIO             │
└───────────────────────────┬─────────────────────────────┘
                            │ HTTP
┌───────────────────────────▼─────────────────────────────┐
│                    核心引擎层 (ai-service/)               │
│    FastAPI + DeepSeek API + Manim Community             │
│    ChromaDB + Ollama  │  Celery + Redis  │  Jinja2      │
│    SSE 实时推送  │  Wiki 自动超链接  │  GIF 转换          │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│                    数据存储层                             │
│    MySQL 8.0  │  ChromaDB  │  Redis  │  本地文件存储      │
└─────────────────────────────────────────────────────────┘
```

## 项目结构

```
cs-visual-learn/
├── PRODUCT.md                  # 产品业务文档
├── README.md                   # 本文件
│
├── ai-service/                 # 核心引擎层 — 23 个 REST API，95% 成品
│   ├── ai_engine.py            # 🔴 核心引擎（代码生成/渲染/修复/RAG），禁止修改
│   ├── main.py                 # FastAPI 入口，全部 REST 接口
│   ├── Dockerfile              # Docker 镜像
│   ├── docker-compose.yml      # 一键部署：Redis + API + Worker
│   ├── services/               # 扩展服务（模板/日志/Prompt/进度追踪）
│   ├── workers/                # Celery 异步任务（3 个 Task + 进度上报）
│   ├── templates/              # 10 个参数化模板（零代码创作）
│   ├── prompts/                # Prompt 模板（热重载）
│   ├── wiki_data/              # 百科词条（80+ 关键词就绪，6 大分类）
│   ├── kb_data/                # 知识库素材（Manim API 文档 + 示例代码）
│   ├── scripts/                # 工具脚本（知识库构建/百科生成/功能测试）
│   ├── outputs/                # 渲染产物（代码 + 视频）
│   └── logs/                   # 运行日志（自动轮转）
│
├── java-web/                   # 业务服务层 (Spring Boot) — 基础骨架
│   └── src/main/java/com/manim/
│
├── front-html/                 # 前端展示层 (Vue 3) — 待初始化
├── docs/                       # 项目文档
└── scripts/                    # 全局脚本
```

## 核心功能模块

| 模块 | 说明 | 状态 |
|------|------|------|
| 百科知识库 | 结构化词条，五段式内容，Wikipedia 风格自动超链接 + 相关推荐 | ✅ 已完成 |
| AI 代码生成 | 自然语言 → Manim 代码，RAG 增强，自动修复重试（最多 3 次） | ✅ 已完成 |
| 模板库 | 10 个官方模板，覆盖算法/数学/图论/ML/数据结构，零代码生成 | ✅ 已完成 |
| 异步任务队列 | Celery + Redis，3 个异步 Task，SSE 实时进度推送 | ✅ 已完成 |
| Prompt 管理 | 模板化 Prompt，热重载，文件即改即生效 | ✅ 已完成 |
| 视频管理 | 列表/下载/GIF 转换/删除 | ✅ 已完成 |
| Docker 部署 | Dockerfile + docker-compose 一键启动全套 | ✅ 已完成 |
| 结构化日志 | 控制台 + 文件双输出，RotatingFileHandler 自动轮转 | ✅ 已完成 |
| 动画沙箱 | AI 对话 + 代码编辑 + 实时预览，三栏式布局 | ⏳ 待前端 |
| 精选画廊 | 高质量作品展示，排行榜，Fork 机制 | ⏳ 待前端 |
| 社区交流 | 评论、点赞、Fork 二次创作、创作者主页 | ⏳ 规划中 |
| 备考学习 | 408/考研数学学习路径，打卡，进度跟踪 | ⏳ 规划中 |

## 版本路线图

| 版本 | 核心内容 | 状态 |
|------|---------|------|
| v0.1 MVP | 百科 + AI 生成 + 基础沙箱 + RAG | ✅ 完成 |
| v0.2 模板画廊 | 10 个官方模板 + 异步任务 + SSE + Wiki 超链接 + Docker | ✅ 引擎完成 |
| v0.3 社区 | 评论 + Fork + 用户主页 | ⏳ 待开始 |
| v1.0 正式版 | 学习路径 + 单步调试 + 参数面板 + 导出 | ⏳ 待开始 |
| v2.0 生态 | 创作者分成 + 开放 API + 多语言 | ⏳ 待开始 |

## 开发原则

1. **核心引擎零修改** — `ai_engine.py` 为稳定核心，新功能仅在外层封装
2. **三层解耦** — 前端 → Java 业务层 → Python 引擎层，仅通过 HTTP 通信
3. **异步优先** — 渲染/生成任务走 Celery 队列，SSE 实时推送进度
4. **渐进式复杂度** — 看动画 → 调参数 → 改模板 → 写代码
5. **缓存优先** — 相同需求 MD5 缓存，减少重复渲染

## 快速启动

### 核心引擎层 (ai-service)

```bash
cd ai-service
pip install -r requirements.txt
python build_kb.py          # 构建知识库（可选）
python main.py              # 启动 API → http://localhost:8000/docs
# 异步 Worker（需 Redis）：
celery -A workers.celery_app worker --loglevel=info -P solo
```

### Docker 部署

```bash
cd ai-service
docker compose up -d        # 一键启动 Redis + API + Worker
```

### 业务服务层 (java-web)

```bash
cd java-web && mvn spring-boot:run
```

## 环境要求

- Python ≥ 3.10，Manim Community v0.19.x，FFmpeg
- DeepSeek API Key（必需）
- Redis 7.x（异步任务需要，可选）
- Ollama（RAG 向量检索需要，可选）
- Java 11+ / Maven 3.6+ / MySQL 8.0（业务层需要）
- Docker Desktop（容器部署，可选）

## 许可证

本项目采用 [MIT License](LICENSE) 开源。

## 致谢

- [Manim Community](https://www.manim.community/) — 数学动画引擎
- [DeepSeek](https://www.deepseek.com/) — 大语言模型 API
- [ChromaDB](https://www.trychroma.com/) — 向量数据库

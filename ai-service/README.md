# AI Service — Manim 智能动画生成引擎

## 模块简介

本模块是 CS-Visual-Learn 的核心 AI 能力层，基于 DeepSeek 大语言模型 + RAG 检索增强技术，实现从自然语言需求到 Manim 动画视频的全自动化生成。具备代码自动修复、参数化模板、百科词条管理、异步任务队列等完整能力，通过 FastAPI 向外暴露标准 REST 接口。

## 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 大模型 | DeepSeek API (v4-flash) | 代码生成、错误修复、多轮对话 |
| 向量检索 | ChromaDB + Ollama (nomic-embed-text) | RAG 知识库，提升生成准确率 |
| 动画渲染 | Manim Community v0.19.x | 数学动画核心引擎 |
| API 框架 | FastAPI + Uvicorn | 高性能异步 HTTP 服务 |
| 异步任务 | Celery + Redis | 渲染任务队列，失败重试 |
| 模板引擎 | Jinja2 | 参数化模板渲染（零代码创作） |
| 运行环境 | Python 3.10+ | |

## 目录结构

```
ai-service/
├── ai_engine.py             # 🔴 核心引擎（代码生成/渲染/修复/RAG），禁止修改
├── main.py                  # FastAPI 入口，封装全部 REST 接口
├── requirements.txt         # Python 依赖清单
├── .env / .env.example      # 环境变量配置（API Key 等）
│
├── services/                # 引擎扩展服务
│   └── template_service.py  # 参数模板引擎（Jinja2 + 参数校验）
│
├── workers/                 # 异步任务
│   └── celery_app.py        # Celery 配置 + 3 个异步 Task
│
├── templates/               # 官方参数化模板（零代码创作）
│   ├── sort-algorithm/      # 排序算法可视化（5 种算法可切换）
│   ├── function-plot/       # 一元函数图像绘制
│   ├── binary-tree-traversal/ # 二叉树遍历（4 种遍历方式）
│   ├── central-limit-theorem/ # 正态分布与中心极限定理
│   └── fourier-series-square/ # 傅里叶级数方波分解
│
├── prompts/                 # Prompt 模板
├── wiki_data/               # 百科词条 Markdown
│   ├── algorithm/           # 算法类词条（排序、搜索、树、图等）
│   └── math/                # 数学类词条（微积分、线性代数、概率论等）
├── kb_data/                 # 知识库原始素材
│   └── api_docs/            # Manim API 参考文档
│
├── scripts/                 # 工具脚本
│   ├── build_kb.py          # 构建向量知识库
│   └── test_celery.py       # Celery 测试脚本
│
├── chroma_db/               # 向量库持久化（自动生成）
├── outputs/                 # 渲染产物（自动生成）
│   ├── code/                # 生成的 Manim 代码
│   └── videos/              # 渲染完成的 MP4 视频
├── media/                   # Manim 渲染临时文件
└── cache/                   # 生成结果缓存
```

## 环境搭建

### 软件要求

- Python ≥ 3.10
- Manim Community v0.19.x
- DeepSeek API Key
- FFmpeg（Manim 渲染依赖）
- Redis（Celery 异步任务需要，可选）
- Ollama（RAG 向量检索需要，可选）

### 安装步骤

```bash
# 1. 创建虚拟环境
conda create -n manim_ai python=3.10 -y
conda activate manim_ai

# 2. 安装依赖
cd ai-service
pip install -r requirements.txt

# 3. 安装 FFmpeg
conda install -c conda-forge ffmpeg -y

# 4. 配置环境变量
cp .env.example .env
# 编辑 .env，填入 DEEPSEEK_API_KEY=你的密钥

# 5. （可选）拉取 Ollama 嵌入模型
ollama pull nomic-embed-text

# 6. 构建向量知识库
python build_kb.py
```

## 快速启动

### 启动 API 服务

```bash
cd ai-service
python main.py
# 服务运行在 http://localhost:8000
# API 文档：http://localhost:8000/docs
```

### 启动异步 Worker（需要 Redis）

```bash
cd ai-service
celery -A workers.celery_app worker --loglevel=info -P solo
```

## 核心工作原理

系统采用「生成 → 执行 → 反馈 → 修复」的闭环流水线：

1. **RAG 检索** — 用户需求向量化，从知识库召回相关示例与 API 说明
2. **代码生成** — DeepSeek 基于参考资料 + System Prompt 生成 Manim 代码
3. **安全校验** — 预检代码语法、LaTeX 合法性、常见易错点
4. **渲染执行** — 调用 Manim 渲染，超时 120s 自动终止
5. **自动修复** — 渲染失败则提取错误日志，让 AI 修复代码后重试（最多 3 次）
6. **缓存返回** — 相同需求命中 MD5 缓存，秒级返回

## API 接口文档

> 完整交互文档：启动服务后访问 `http://localhost:8000/docs`

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 服务健康检查 |

### 核心流水线

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | **完整流水线**：需求 → 生成代码 → 渲染 → 自动修复 → 返回视频 |
| POST | `/api/ai/generate-code` | 仅生成 Manim 代码，不渲染 |
| POST | `/api/render` | 提交已有代码执行渲染 |
| POST | `/api/ai/fix-code` | AI 根据报错信息自动修复代码 |
| POST | `/api/rag/retrieve` | RAG 向量检索参考资料 |

### 百科词条

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/wiki/categories` | 获取所有词条分类 |
| GET | `/api/wiki/list?category=` | 词条列表（支持按分类筛选） |
| GET | `/api/wiki/search?q=` | 关键词搜索词条 |
| GET | `/api/wiki/{slug}` | 获取单个词条完整内容 |

### 模板库（零代码创作）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/templates/categories` | 获取模板分类 |
| GET | `/api/templates/list?category=` | 模板列表（支持按分类筛选） |
| GET | `/api/templates/{id}` | 模板详情（含参数说明） |
| POST | `/api/templates/generate-code` | 根据参数生成代码 |
| POST | `/api/templates/render` | 根据参数生成代码并渲染视频 |
| POST | `/api/templates/reload` | 热重载模板（开发用） |

### 请求/响应格式

所有接口统一响应格式：

```json
{
  "code": 0,
  "message": "ok",
  "data": { ... }
}
```

- `code: 0` 成功，`code: 1` 失败
- `data` 为具体业务数据，失败时为 `null`

## 5 个官方模板

| 模板 ID | 名称 | 分类 | 可调参数 |
|---------|------|------|----------|
| `sort-algorithm` | 排序算法可视化 | 算法 | 算法类型、数组大小、动画速度、显示数值 |
| `function-plot` | 一元函数图像绘制 | 数学 | 函数表达式、坐标范围 |
| `binary-tree-traversal` | 二叉树遍历 | 数据结构 | 遍历方式、树深度、速度 |
| `central-limit-theorem` | 正态分布与中心极限定理 | 概率论 | 样本量、分布参数 |
| `fourier-series-square` | 傅里叶级数方波分解 | 数学 | 傅里叶项数 |

## 异步任务

| 任务名 | 说明 |
|--------|------|
| `generate_full_task` | 异步完整生成流水线（需求 → 代码 → 渲染 → 修复） |
| `render_code_task` | 异步渲染已有 Manim 代码 |
| `render_template_task` | 异步模板渲染（参数生成代码 + 渲染） |

## 测试

```bash
# 仅测试导入（不需要 Redis）
python scripts/test_celery.py --import-only

# 测试同步调用（不需要 Redis，会实际渲染一段动画）
python scripts/test_celery.py --sync

# 完整测试（需要 Redis + Celery Worker 运行中）
python scripts/test_celery.py --all
```

## 设计原则

1. **核心引擎零修改** — `ai_engine.py` 为稳定核心，所有新功能仅在外层封装
2. **异步优先** — 渲染任务走 Celery 队列，避免同步阻塞
3. **缓存优先** — 相同需求 MD5 缓存，减少重复生成和渲染
4. **渐进式复杂度** — 模板零代码 → AI 对话生成 → 手动代码编辑

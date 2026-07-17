# AI Service — Manim 智能动画生成引擎

## 模块简介

CS-Visual-Learn 的核心 AI 能力层，基于 **DeepSeek 大语言模型 + RAG 检索增强**技术，实现从自然语言需求到 Manim 动画视频的全自动化生成。提供参数化模板、百科词条管理、异步任务队列、SSE 实时进度推送等完整能力，通过 **23 个 REST API** 向外暴露服务。

## 技术栈

| 组件 | 技术选型 | 说明 |
|------|----------|------|
| 大模型 | DeepSeek API (v4-flash) | 代码生成、错误修复 |
| 向量检索 | ChromaDB + Ollama (nomic-embed-text) | kb_data + wiki_data 双源 RAG |
| 动画渲染 | Manim Community v0.19.x | 数学动画核心引擎 |
| API 框架 | FastAPI + Uvicorn | 高性能异步 HTTP，自动生成 /docs |
| 异步任务 | Celery 5.x + Redis | 3 个异步 Task，带进度上报 |
| 实时推送 | SSE (Server-Sent Events) | 渲染进度流，前端 EventSource 直连 |
| 模板引擎 | Jinja2 | 10 个参数化模板（零代码创作） |
| 日志 | logging + RotatingFileHandler | 控制台 + 文件双输出，自动轮转 |
| 运行环境 | Python 3.10+ | |

## 目录结构

```
ai-service/
├── ai_engine.py             # 🔴 核心引擎 — 代码生成/渲染/修复/RAG/缓存（禁止修改）
├── main.py                  # FastAPI 入口 — 23 个 REST 接口
├── build_kb.py              # 知识库构建脚本（kb_data + wiki_data 双源）
├── requirements.txt         # Python 依赖
├── .env / .env.example      # 环境变量（API Key 等）
│
├── services/                # 引擎扩展服务（外层封装，不修改核心）
│   ├── template_service.py  # 参数模板引擎（Jinja2 + 参数校验）
│   ├── prompt_service.py    # Prompt 管理（热重载 + 自动回退）
│   ├── progress_service.py  # 进度追踪（Redis + Pub/Sub + SSE）
│   └── logging_config.py    # 统一日志配置
│
├── workers/                 # Celery 异步任务
│   └── celery_app.py        # 3 个 Task：渲染/生成/模板，均带进度上报
│
├── templates/               # 10 个官方参数化模板（零代码创作）
│   ├── sort-algorithm/      # 排序算法可视化（5 种算法可切换）
│   ├── function-plot/       # 一元函数图像绘制
│   ├── binary-tree-traversal/  # 二叉树遍历（4 种遍历方式）
│   ├── binary-search-visual/   # 二分查找可视化
│   ├── central-limit-theorem/  # 正态分布与中心极限定理
│   ├── fourier-series-square/  # 傅里叶级数方波分解
│   ├── dijkstra-shortest-path/ # Dijkstra 最短路径
│   ├── gradient-descent/       # 梯度下降可视化
│   ├── kmp-string-match/       # KMP 字符串匹配
│   └── convolution-demo/       # 卷积运算演示
│
├── prompts/                 # Prompt 模板（热重载）
│   ├── code_generation.j2   # 代码生成 System Prompt
│   └── code_fix.j2          # 代码修复 System Prompt
│
├── wiki_data/               # 百科词条（Wikipedia 风格自动超链接）
│   ├── algorithm/           # 排序、搜索、分治、贪心等
│   ├── data-structures/     # 树、图、堆、哈希等
│   ├── graph-theory/        # 最短路径、生成树、网络流等
│   ├── dynamic-programming/ # 背包、LCS、编辑距离等
│   ├── math/                # 微积分、级数、傅里叶等
│   ├── linear-algebra/      # 矩阵、特征值、SVD 等
│   └── probability/         # 正态分布、贝叶斯、马尔可夫链等
│
├── kb_data/                 # 知识库素材（进入 ChromaDB RAG 索引）
│   ├── api_docs/            # Manim API 参考文档（组员贡献）
│   └── examples/            # 高质量示例代码
│
├── scripts/                 # 工具脚本
│   ├── build_kb.py          # 构建 ChromaDB 向量知识库
│   ├── fetch_wiki.py        # Wikipedia 批量抓取 + AI 整理
│   ├── keywords.txt         # 80+ 词条关键词列表
│   ├── test_celery.py       # Celery 功能测试
│   └── test_full.py         # 全功能冒烟测试
│
├── chroma_db/               # 向量库持久化目录（自动生成）
├── outputs/                 # 渲染产物（自动生成）
│   ├── code/                # 生成的 Manim Python 代码
│   └── videos/              # 渲染完成的 MP4 视频
├── media/                   # Manim 渲染临时文件
├── cache/                   # 生成结果 MD5 缓存
└── logs/                    # 运行日志（自动轮转，10MB × 3）
```

## 环境搭建

### 软件要求

- Python ≥ 3.10
- Manim Community v0.19.x
- DeepSeek API Key（必需）
- FFmpeg（Manim 渲染 + GIF 转换依赖）
- Redis（Celery 异步任务，可选）
- Ollama（RAG 向量检索，可选）

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

# 4. 配置密钥
cp .env.example .env
# 编辑 .env：DEEPSEEK_API_KEY=你的密钥

# 5. 拉取嵌入模型（可选）
ollama pull nomic-embed-text

# 6. 构建知识库（可选，但推荐）
python build_kb.py
```

## 快速启动

```bash
# 启动 API 服务
python main.py
# → http://localhost:8000
# → API 文档 http://localhost:8000/docs

# 异步 Worker（需 Redis，Windows 加 -P solo）
redis-server &
celery -A workers.celery_app worker --loglevel=info -P solo
```

## 核心工作原理

「生成 → 执行 → 反馈 → 修复」闭环流水线：

1. **RAG 检索** — kb_data + wiki_data 双源向量库召回参考资料
2. **代码生成** — DeepSeek 基于 Prompt 模板 + RAG 上下文生成 Manim 代码
3. **安全预检** — 语法校验、LaTeX 合法性检查
4. **渲染执行** — Popen 实时输出，progress_callback 逐行上报进度
5. **自动修复** — 渲染失败提取错误日志，AI 修复 → 重试（最多 3 次）
6. **缓存返回** — MD5 缓存，相同需求秒级返回

## API 接口文档

> 交互文档：`http://localhost:8000/docs`

### 健康检查

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/health` | 服务运行状态 |

### 核心流水线（5 个端点）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/generate` | **完整流水线**：需求 → 代码 → 渲染 → 修复 → 视频 |
| POST | `/api/ai/generate-code` | 仅生成 Manim 代码 |
| POST | `/api/render` | 提交代码执行渲染 |
| POST | `/api/ai/fix-code` | AI 根据报错修复代码 |
| POST | `/api/rag/retrieve` | RAG 向量检索 |

### 百科词条（5 个端点）— Wikipedia 风格自动超链接

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/wiki/categories` | 获取所有分类 |
| GET | `/api/wiki/list?category=` | 词条列表（按分类筛选） |
| GET | `/api/wiki/search?q=` | 关键词搜索 |
| GET | `/api/wiki/{slug}` | 词条详情（含自动超链接 + 相关推荐） |
| POST | `/api/wiki/reload-index` | 重建词条索引（新增词条后） |

### 模板库（6 个端点）— 10 个模板

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/templates/categories` | 获取模板分类 |
| GET | `/api/templates/list?category=` | 模板列表 |
| GET | `/api/templates/{id}` | 模板详情（含参数定义） |
| POST | `/api/templates/generate-code` | 参数 → 代码 |
| POST | `/api/templates/render` | 参数 → 代码 → 渲染 → 视频 |
| POST | `/api/templates/reload` | 热重载全部模板 |

### Prompt 管理（3 个端点）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/prompts/list` | 列出所有 Prompt 模板 |
| GET | `/api/prompts/{name}` | 预览 Prompt 内容 |
| POST | `/api/prompts/reload` | 热重载 Prompt |

### 任务进度（2 个端点）— SSE 实时推送

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/tasks/{task_id}` | 查询 Celery 任务状态与结果 |
| GET | `/api/tasks/{task_id}/stream` | **SSE 实时流**，前端 EventSource 直连 |

### 视频管理 & 画廊（7 个端点）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/videos/list` | 列出所有视频（合并标题元数据） |
| GET | `/api/videos/list?gallery=true` | 仅列出已收藏视频 |
| GET | `/api/videos/{name}/download` | 直链下载 MP4 |
| POST | `/api/videos/{name}/convert/gif?fps=10&width=480` | MP4 → GIF 转换 |
| POST | `/api/videos/{name}/save` | Toggle 画廊收藏 |
| PATCH | `/api/videos/{name}/title?title=...` | 修改视频标题 |
| DELETE | `/api/videos/{name}` | 删除视频及源码 |

### 统一响应格式

```json
{"code": 0, "message": "ok", "data": {...}}
```

## 10 个官方模板

| # | 模板 ID | 名称 | 分类 | 可调参数 |
|---|---------|------|------|----------|
| 1 | `sort-algorithm` | 排序算法可视化 | 算法 | 算法类型、数组大小、速度、显示数值 |
| 2 | `function-plot` | 一元函数图像绘制 | 数学 | 函数表达式、坐标范围 |
| 3 | `binary-tree-traversal` | 二叉树遍历 | 数据结构 | 遍历方式、树深度、速度 |
| 4 | `binary-search-visual` | 二分查找可视化 | 算法 | 数组大小、目标值、速度、显示指针 |
| 5 | `central-limit-theorem` | 正态分布与中心极限定理 | 概率论 | 样本量、分布参数 |
| 6 | `fourier-series-square` | 傅里叶级数方波分解 | 数学 | 傅里叶项数 |
| 7 | `dijkstra-shortest-path` | Dijkstra 最短路径 | 图论 | 图类型、起点、速度、显示距离 |
| 8 | `gradient-descent` | 梯度下降可视化 | 机器学习 | 函数类型、学习率、迭代次数、速度 |
| 9 | `kmp-string-match` | KMP 字符串匹配 | 算法 | 文本串、模式串、速度 |
| 10 | `convolution-demo` | 卷积运算演示 | 数学 | 信号类型、卷积核、速度 |

## 异步任务

| 任务名 | 进度状态 | 说明 |
|--------|----------|------|
| `generate_full_task` | STARTED → RENDERING → SUCCESS/FAILURE | 异步完整流水线 |
| `render_code_task` | STARTED → RENDERING → SUCCESS/FAILURE | 异步渲染 |
| `render_template_task` | STARTED（代码生成）→ RENDERING（渲染）→ SUCCESS/FAILURE | 异步模板渲染 |

## 测试

```bash
# 全功能冒烟测试（不需要 Redis，推荐）
python scripts/test_full.py

# 仅测试导入（不需要 Redis）
python scripts/test_celery.py --import-only

# 同步渲染 + 模板测试（不需要 Redis）
python scripts/test_celery.py --sync

# 完整异步测试（需 Redis + Celery Worker 运行中）
python scripts/test_celery.py --all
```

## 百科词条批量生成

```bash
# 纯 AI 生成（推荐，不需要代理）
python scripts/fetch_wiki.py -b scripts/keywords.txt --ai

# 单条测试
python scripts/fetch_wiki.py 归并排序 --ai

# 重建知识库（新词条进入 RAG）
python build_kb.py

# 刷新词条索引（无需重启服务）
curl -X POST http://localhost:8000/api/wiki/reload-index
```

## 设计原则

1. **核心引擎零修改** — `ai_engine.py` 为稳定核心，新功能仅在外层 services/、workers/ 封装
2. **异步优先** — 渲染任务走 Celery，SSE 实时推送进度
3. **缓存优先** — MD5 缓存，减少重复生成
4. **渐进式复杂度** — 模板零代码 → AI 对话生成 → 手动代码编辑
5. **热重载** — 模板、Prompt 文件修改即生效，无需重启

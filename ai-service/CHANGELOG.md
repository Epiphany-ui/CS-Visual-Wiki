# ai-service CHANGELOG

## v1.0.0 (2026-07-08)

### 新增功能

#### 异步任务 API（Celery 驱动）
- `POST /api/async/generate` — 异步全流程生成（需求→代码→渲染→修复）
- `POST /api/async/render` — 异步纯渲染（带代码预检）
- `POST /api/async/template-render` — 异步模板渲染
- `GET /api/tasks` — 任务列表查询（支持分页和状态筛选）
- `DELETE /api/tasks/{task_id}` — 取消/删除任务

#### 逐帧调试 API（v1.0 核心功能）
- `GET /api/debug/video/{filename}/info` — 视频元数据查询
- `GET /api/debug/video/{filename}/frames` — 帧范围提取
- `GET /api/debug/video/{filename}/frame/{frame_index}` — 单帧获取
- `GET /api/debug/video/{filename}/frame-at-time` — 时间点截图
- `GET /api/debug/video/{filename}/thumbnail-sheet` — 缩略图网格

#### 生产加固
- **统一配置管理** (`services/config.py`) — pydantic-settings 驱动
- **结构化健康检查** (`GET /health`) — Redis、ChromaDB、DeepSeek、Celery、Ollama、磁盘
- **请求追踪中间件** — X-Request-ID 全链路追踪
- **请求日志中间件** — 结构化记录 method/path/status/duration
- **API Key 认证** — 服务间调用认证（可选启用）
- **速率限制** — Redis 滑动窗口，分级限流
- **统一异常处理** — AppException 体系 + 全局 handler
- **增强代码预检** (`services/code_validator.py`) — 6 项检查

#### 兼容性
- `POST /generate` — 兼容旧 Java 后端（映射到 `/api/generate`）

### 变更

- `GET /health` — 响应格式扩展，新增依赖状态检测
- `GET /api/videos/list` — 保持兼容
- CORS 配置 — 从硬编码 `*` 改为可配置
- Celery Worker — 增加 ack_late、prefetch_multiplier、result_expires 配置
- `services/progress_service.py` — 新增 `list_tasks`、`delete_task`、`get_task_count`

### 文件结构

```
services/
├── config.py          [NEW] 统一配置管理
├── middleware.py      [NEW] 请求追踪 + 日志 + 认证 + 限流
├── exceptions.py      [NEW] 统一异常类
├── rate_limiter.py    [NEW] 速率限制器
├── code_validator.py  [NEW] 增强代码预检
├── debug_service.py   [NEW] 逐帧调试服务
├── __init__.py        [UPDATED] 导出新服务
└── progress_service.py [UPDATED] 新增任务管理
```

### 测试

- `tests/conftest.py` — pytest fixtures
- `tests/test_health.py`
- `tests/test_async_tasks.py`
- `tests/test_debug_api.py`
- `tests/test_rate_limiter.py`
- `tests/test_middleware.py`
- `tests/test_error_handling.py`
- `tests/test_config.py`

---

## v0.2.0 (2026-06)

### 新增功能

- 10 个参数化模板（零代码动画创作）
- SSE 实时进度推送
- Celery 异步任务队列
- Prompt 热重载
- 视频 GIF 转换

---

## v0.1.0 (2026-05)

### 初始版本

- Manim 代码生成 + 渲染 + 自动修复
- RAG 知识库检索
- 百科词条 API（80+ 条目）
- 基础视频管理

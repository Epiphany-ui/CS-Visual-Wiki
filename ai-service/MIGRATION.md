# ai-service v0.x → v1.0 迁移指南

## 概述

v1.0 是一个**向后兼容**的升级。所有 v0.x API 端点保持不变，新增端点通过新路径提供。

## 快速检查清单

- [ ] 更新 `.env` 配置（新增变量见下方）
- [ ] 安装新增 Python 依赖（`pip install -r requirements.txt`）
- [ ] 确保 Redis 运行（Celery 依赖）
- [ ] 确认 ffmpeg 已安装（逐帧调试功能需要）
- [ ] 更新 Java 后端调用地址（如需迁移到 `/api/generate`）

## 破坏性变更

**无。** v1.0 对 v0.x 完全向后兼容。

唯一行为变更：
- `GET /health` 响应格式已扩展（新增 `checks` 和 `version` 字段），但保留了 `{"status": "running"}` 语义（现在包装在 data.checks 中）

## 新增环境变量

```ini
# Redis
REDIS_URL=redis://localhost:6379/0

# CORS
CORS_ORIGINS=*

# 安全（留空则关闭认证）
# API_KEY=your_shared_secret_key

# 速率限制
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_GENERATE_PER_MINUTE=20

# 日志
LOG_LEVEL=INFO

# 视频管理
MAX_VIDEO_AGE_DAYS=30
```

## API 使用变更

### 推荐：从同步迁移到异步

```bash
# v0.x (同步，阻塞 2+ 分钟)
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"requirement": "冒泡排序动画"}'

# v1.0 (异步，立即返回 task_id)
curl -X POST http://localhost:8000/api/async/generate \
  -H "Content-Type: application/json" \
  -d '{"requirement": "冒泡排序动画"}'
# → {"code": 0, "data": {"task_id": "xxx-xxx"}}

# 然后通过 SSE 获取实时进度
curl -N http://localhost:8000/api/tasks/xxx-xxx/stream
```

### 新增：逐帧调试

```bash
# 1. 获取视频信息
curl http://localhost:8000/api/debug/video/xxx.mp4/info

# 2. 提取前 10 帧
curl "http://localhost:8000/api/debug/video/xxx.mp4/frames?start_frame=0&end_frame=10"

# 3. 访问单帧图片
# /frames/xxx/frame_0000.jpg
```

### 兼容：Java 后端无需改动

Java `TaskServiceImpl` 仍可调用 `POST /generate`（自动映射到 `/api/generate`）。
建议后续更新 Java 配置 `manim.ai.generate-endpoint` 为 `/api/generate`。

## 部署

```bash
# Docker Compose 一键部署
cd ai-service
docker-compose up -d

# 验证
curl http://localhost:8000/health | jq .
```

## 降级

如需回退到 v0.x，只需：
1. 停止使用新增的 `/api/async/*` 和 `/api/debug/*` 端点
2. 删除新增的 `.env` 变量（或保留——v0.x 会忽略它们）
3. 可选：恢复旧的 `main.py`（v0.x 版本）

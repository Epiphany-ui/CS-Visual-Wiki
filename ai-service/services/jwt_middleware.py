#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""JWT 认证中间件 —— 从 Authorization header 提取用户名并注入 request.state"""
import jwt as _jwt
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .logging_config import get_logger

logger = get_logger("jwt")

# 无需认证的公开路径前缀
PUBLIC_PREFIXES = (
    "/health", "/docs", "/openapi.json", "/redoc",
    "/videos/", "/frames/", "/avatars/",
    "/api/videos/list",        # 公开视频列表
    "/api/wiki/",              # 百科
    "/api/templates/list", "/api/templates/",  # 模板浏览
    "/api/tasks/",             # SSE 进度推送（task-specific）
)


class JwtUserMiddleware(BaseHTTPMiddleware):
    """从 JWT token 提取用户名注入 request.state.username。

    无 token 的公开请求不受影响；需要身份的端点应检查
    request.state.username 是否存在。
    """

    async def dispatch(self, request: Request, call_next: Response) -> Response:
        path = request.url.path

        # 公开路径跳过
        if any(path.startswith(p) for p in PUBLIC_PREFIXES):
            return await call_next(request)

        # 提取 JWT
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            token = auth[7:]
            try:
                payload = _jwt.decode(token, settings.jwt_secret, algorithms=["HS256"])
                request.state.username = payload.get("username", "")
            except Exception:
                pass  # token 无效，继续处理（端点自行决定是否拒绝）

        return await call_next(request)

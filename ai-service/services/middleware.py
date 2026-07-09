#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
FastAPI 中间件集合
- RequestIDMiddleware: 为每个请求生成唯一 ID
- RequestLoggingMiddleware: 结构化请求日志
- ApiKeyMiddleware: API Key 认证（服务间调用）
- RateLimitMiddleware: 速率限制
"""
import secrets
import time
import uuid

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from .config import settings
from .exceptions import RateLimitError, UnauthorizedError
from .rate_limiter import rate_limiter
from .logging_config import get_logger

logger = get_logger("middleware")


class RequestIDMiddleware(BaseHTTPMiddleware):
    """为每个请求注入 X-Request-ID 头，便于全链路追踪"""

    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        request.state.request_id = request_id

        response: Response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """结构化请求日志：方法、路径、状态码、耗时"""

    async def dispatch(self, request: Request, call_next):
        # 跳过健康检查和静态文件
        if request.url.path in ("/health",) or request.url.path.startswith("/videos/"):
            return await call_next(request)

        start = time.time()
        response: Response = await call_next(request)
        duration_ms = round((time.time() - start) * 1000, 2)
        request_id = getattr(request.state, "request_id", "-")

        logger.info(
            "[%s] %s %s → %s | %.2fms",
            request_id,
            request.method,
            request.url.path,
            response.status_code,
            duration_ms,
        )
        return response


class ApiKeyMiddleware(BaseHTTPMiddleware):
    """服务间 API Key 认证中间件
    仅当 settings.api_key 被设置时启用。
    跳过 /health 和 /videos/ 路径。
    """

    async def dispatch(self, request: Request, call_next):
        if not settings.is_auth_enabled:
            return await call_next(request)

        # 公开路径白名单
        public_paths = {"/health", "/docs", "/openapi.json", "/redoc"}
        if request.url.path in public_paths or request.url.path.startswith("/videos/"):
            return await call_next(request)

        api_key = request.headers.get("X-API-Key", "")
        if not api_key:
            return JSONResponse(
                status_code=401,
                content={"code": 40101, "message": "未授权：缺少 X-API-Key 请求头", "data": None},
            )

        if not secrets.compare_digest(api_key, settings.api_key):
            return JSONResponse(
                status_code=401,
                content={"code": 40101, "message": "未授权：API Key 无效", "data": None},
            )

        return await call_next(request)


class RateLimitMiddleware(BaseHTTPMiddleware):
    """速率限制中间件
    对生成类端点使用更严格的限制。
    静态文件（/videos/ /frames/）不做限流。
    """

    # 无需限流的路径（静态资源、文档、调试接口）
    EXEMPT_PATHS = {"/videos", "/frames", "/docs", "/openapi.json", "/redoc", "/api/debug", "/health"}

    # 生成类路径前缀（更严格的限制）
    GENERATE_PATHS = {"/api/generate", "/api/async", "/api/render", "/api/ai/fix-code"}

    async def dispatch(self, request: Request, call_next):
        if not settings.rate_limit_enabled:
            return await call_next(request)

        path = request.url.path

        # 静态资源和文档不做限流
        if any(path.startswith(p) for p in self.EXEMPT_PATHS):
            return await call_next(request)

        key = rate_limiter.get_rate_limit_key(request)

        # 为生成类端点设置更严格的限制
        if any(path.startswith(p) for p in self.GENERATE_PATHS):
            max_req = settings.rate_limit_generate_per_minute
        else:
            max_req = settings.rate_limit_per_minute

        allowed, remaining = rate_limiter.is_allowed(key, max_requests=max_req)

        if not allowed:
            return JSONResponse(
                status_code=429,
                content={"code": 42901, "message": "请求过于频繁，请稍后重试", "data": None},
                headers={"X-RateLimit-Remaining": "0", "Retry-After": "60"},
            )

        response: Response = await call_next(request)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        return response

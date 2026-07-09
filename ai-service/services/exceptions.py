#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一异常类定义
所有 API 层抛出的异常使用本模块的异常类，
通过 FastAPI exception_handler 统一捕获并返回标准格式响应。
"""
from typing import Optional, Any


class AppException(Exception):
    """应用统一异常基类"""

    def __init__(self, message: str, code: int = 1, status_code: int = 500, data: Any = None):
        self.message = message
        self.code = code
        self.status_code = status_code
        self.data = data
        super().__init__(message)


# ===================== 业务异常 =====================

class ValidationError(AppException):
    """参数校验失败"""
    def __init__(self, message: str = "参数校验失败"):
        super().__init__(message=message, code=40001, status_code=400)


class TaskNotFoundError(AppException):
    """任务不存在"""
    def __init__(self, task_id: str = ""):
        msg = f"任务 {task_id} 不存在或已过期" if task_id else "任务不存在或已过期"
        super().__init__(message=msg, code=40401, status_code=404)


class RenderTimeoutError(AppException):
    """渲染超时"""
    def __init__(self, message: str = "渲染超时，请简化动画或降低质量后重试"):
        super().__init__(message=message, code=50001, status_code=500)


class AIServiceError(AppException):
    """AI 服务调用失败"""
    def __init__(self, message: str = "AI 服务暂时不可用，请稍后重试"):
        super().__init__(message=message, code=50002, status_code=502)


class RateLimitError(AppException):
    """请求频率超限"""
    def __init__(self, message: str = "请求过于频繁，请稍后重试"):
        super().__init__(message=message, code=42901, status_code=429)


class UnauthorizedError(AppException):
    """未授权访问"""
    def __init__(self, message: str = "未授权：缺少或无效的 API Key"):
        super().__init__(message=message, code=40101, status_code=401)


class ResourceNotFoundError(AppException):
    """资源不存在"""
    def __init__(self, message: str = "请求的资源不存在"):
        super().__init__(message=message, code=40402, status_code=404)

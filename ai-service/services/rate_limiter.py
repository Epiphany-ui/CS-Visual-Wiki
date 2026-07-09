#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
基于 Redis 滑动窗口的速率限制器
使用有序集合 (Sorted Set) 实现精确的滑动窗口计数。
"""
import time
from typing import Tuple

import redis

from .config import settings


class RateLimiter:
    """Redis 滑动窗口速率限制器"""

    def __init__(self, redis_client: redis.Redis = None):
        self._redis = redis_client

    @property
    def redis(self) -> redis.Redis:
        if self._redis is None:
            self._redis = redis.Redis.from_url(settings.redis_url, decode_responses=True)
        return self._redis

    def is_allowed(
        self,
        key: str,
        max_requests: int = None,
        window_seconds: int = 60,
    ) -> Tuple[bool, int]:
        """
        检查请求是否被允许（滑动窗口算法）。

        :param key: 限流键（如 IP 地址或 API Key）
        :param max_requests: 窗口内最大请求数，默认使用 settings.rate_limit_per_minute
        :param window_seconds: 滑动窗口大小（秒）
        :return: (allowed: bool, remaining: int)
        """
        if max_requests is None:
            max_requests = settings.rate_limit_per_minute

        if not settings.rate_limit_enabled:
            return True, max_requests

        redis_key = f"cs:ratelimit:{key}"
        now = time.time()
        window_start = now - window_seconds

        try:
            pipe = self.redis.pipeline()
            # 移除窗口之外的旧记录
            pipe.zremrangebyscore(redis_key, 0, window_start)
            # 统计当前窗口内的请求数
            pipe.zcard(redis_key)
            # 添加当前请求（使用纳秒级时间戳 + 随机后缀确保唯一性）
            pipe.zadd(redis_key, {f"{now}:{time.time_ns() % 1000000}": now})
            # 设置过期时间
            pipe.expire(redis_key, window_seconds + 10)

            _, current_count, _, _ = pipe.execute()

            allowed = current_count < max_requests
            remaining = max(0, max_requests - current_count - (1 if allowed else 0))
            return allowed, remaining
        except Exception:
            # Redis 故障时降级——放行请求
            return True, max_requests

    def get_rate_limit_key(self, request) -> str:
        """从请求中提取限流键：优先使用 API Key，其次使用客户端 IP"""
        api_key = request.headers.get("X-API-Key", "")
        if api_key:
            return f"apikey:{api_key[:16]}"
        # 获取客户端 IP（支持代理）
        forwarded = request.headers.get("X-Forwarded-For", "")
        if forwarded:
            return forwarded.split(",")[0].strip()
        client = request.client
        if client:
            return client.host
        return "unknown"


# 全局单例
rate_limiter = RateLimiter()

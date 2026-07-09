#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试速率限制器"""
import pytest
import time


class TestRateLimiter:
    """速率限制器单元测试"""

    def test_is_allowed_first_request(self, mock_redis):
        """第一个请求应该被允许"""
        from services.rate_limiter import RateLimiter
        limiter = RateLimiter(mock_redis)
        allowed, remaining = limiter.is_allowed("test-key", max_requests=10)
        assert allowed is True
        assert remaining >= 0

    def test_rate_limiting_blocks_when_full(self, mock_redis):
        """超过限制后的请求应该被阻止"""
        from services.rate_limiter import RateLimiter
        limiter = RateLimiter(mock_redis)
        max_req = 3
        # 先用完配额
        for i in range(max_req):
            allowed, _ = limiter.is_allowed("block-test", max_requests=max_req)
            assert allowed is True, f"Request {i+1} should be allowed"
        # 下一次应该被阻止
        allowed, remaining = limiter.is_allowed("block-test", max_requests=max_req)
        assert allowed is False
        assert remaining == 0

    def test_disabled_rate_limiter(self, monkeypatch):
        """禁用速率限制时所有请求都放行"""
        from services.config import settings
        monkeypatch.setattr(settings, "rate_limit_enabled", False)
        from services.rate_limiter import RateLimiter
        limiter = RateLimiter()
        allowed, remaining = limiter.is_allowed("any-key", max_requests=1)
        assert allowed is True
        monkeypatch.setattr(settings, "rate_limit_enabled", True)

    def test_get_rate_limit_key_from_ip(self, mock_redis):
        """从客户端 IP 提取限流键"""
        from services.rate_limiter import RateLimiter

        class MockRequest:
            headers = {}
            class client:
                host = "192.168.1.1"

        limiter = RateLimiter(mock_redis)
        key = limiter.get_rate_limit_key(MockRequest())
        assert key == "192.168.1.1"

    def test_get_rate_limit_key_from_api_key(self, mock_redis):
        """优先从 API Key 提取限流键"""
        from services.rate_limiter import RateLimiter

        class MockRequest:
            headers = {"X-API-Key": "sk-secret-key-12345"}
            class client:
                host = "192.168.1.1"

        limiter = RateLimiter(mock_redis)
        key = limiter.get_rate_limit_key(MockRequest())
        assert "apikey:" in key

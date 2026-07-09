#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试中间件（请求追踪、日志、认证）"""
import pytest
import uuid


class TestRequestIDMiddleware:
    """X-Request-ID 中间件测试"""

    def test_response_has_request_id(self, client):
        """每个响应都应该包含 X-Request-ID 头"""
        response = client.get("/health")
        assert "X-Request-ID" in response.headers
        request_id = response.headers["X-Request-ID"]
        # 验证 UUID 格式
        parts = request_id.split("-")
        assert len(parts) == 5

    def test_request_id_passthrough(self, client):
        """如果客户端发送 X-Request-ID，服务端应该传递它"""
        custom_id = str(uuid.uuid4())
        response = client.get("/health", headers={"X-Request-ID": custom_id})
        # 服务端可以选择保留或替换
        assert "X-Request-ID" in response.headers
        # 当客户端发送时，中间件会使用客户端的值
        assert response.headers["X-Request-ID"] == custom_id


class TestApiKeyMiddleware:
    """API Key 认证中间件测试"""

    def test_health_is_public(self, client):
        """/health 端点不需要 API Key"""
        response = client.get("/health")
        assert response.status_code == 200

    def test_videos_is_public(self, client):
        """/videos/ 路径不需要 API Key"""
        response = client.get("/videos/nonexistent.mp4")
        # 404 表示通过了认证层（被开放路径放行）
        assert response.status_code in (404, 200)

    def test_api_endpoints_public_when_auth_disabled(self, client):
        """当 API Key 未配置时，API 端点公开访问"""
        response = client.get("/api/wiki/categories")
        assert response.status_code == 200
        response2 = client.get("/api/templates/list")
        assert response2.status_code == 200

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试 health check 端点"""
import pytest


class TestHealthCheck:
    """GET /health 端点测试"""

    def test_health_returns_200(self, client):
        """健康检查端点返回 200"""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "data" in data

    def test_health_contains_status(self, client):
        """健康检查响应包含状态字段"""
        response = client.get("/health")
        data = response.json()["data"]
        assert "status" in data
        assert data["status"] in ("healthy", "degraded", "unhealthy")

    def test_health_contains_version(self, client):
        """健康检查响应包含版本号"""
        response = client.get("/health")
        data = response.json()["data"]
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_contains_checks(self, client):
        """健康检查响应包含依赖检测结果"""
        response = client.get("/health")
        data = response.json()["data"]
        assert "checks" in data
        checks = data["checks"]
        assert "redis" in checks
        assert "chromadb" in checks

    def test_health_contains_uptime(self, client):
        """健康检查响应包含运行时长"""
        response = client.get("/health")
        data = response.json()["data"]
        assert "uptime_seconds" in data
        assert data["uptime_seconds"] >= 0

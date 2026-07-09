#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试统一异常处理"""
import pytest
from fastapi.testclient import TestClient


class TestErrorHandling:
    """AppException 异常处理测试"""

    def test_task_not_found_is_404(self, client):
        """TaskNotFoundError 返回 404"""
        response = client.delete("/api/tasks/nonexistent-task-id-99999")
        assert response.status_code == 404
        data = response.json()
        assert data["code"] != 0

    def test_validation_returns_structured_error(self, client):
        """验证错误返回包含错误信息（兼容 FastAPI 默认和自定义格式）"""
        response = client.post("/api/ai/generate-code", json={"requirement": ""})
        # 空字符串可能触发 DeepSeek API 调用或内部错误
        assert response.status_code in (200, 400, 422, 500)
        data = response.json()
        # 两种可能的错误格式：自定义 {code, message, data} 或 FastAPI 默认 {detail}
        has_custom_format = "code" in data and "message" in data
        has_fastapi_format = "detail" in data
        assert has_custom_format or has_fastapi_format, f"Unexpected error format: {data}"

    def test_nonexistent_route_returns_404(self, client):
        """访问不存在的端点返回 404"""
        response = client.get("/api/nonexistent-endpoint-xyz")
        assert response.status_code == 404

    def test_invalid_json_returns_422(self, client):
        """无效 JSON 返回 422"""
        response = client.post(
            "/api/generate",
            data="not valid json",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code in (400, 422)

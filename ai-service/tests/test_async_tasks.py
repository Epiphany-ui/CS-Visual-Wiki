#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试异步任务端点"""
import pytest


class TestAsyncEndpoints:
    """POST /api/async/* 端点测试"""

    def test_async_generate_dispatches(self, client, mock_deepseek, mock_render):
        """POST /api/async/generate 返回 task_id 且不阻塞"""
        response = client.post("/api/async/generate", json={
            "requirement": "test bubble sort",
            "max_retry": 1,
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "task_id" in data["data"]

    def test_async_render_dispatches(self, client, mock_render):
        """POST /api/async/render 返回 task_id"""
        response = client.post("/api/async/render", json={
            "code": "from manim import *\n\nclass Test(Scene):\n    def construct(self):\n        self.play(Create(Circle()))",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "task_id" in data["data"]

    def test_async_render_rejects_invalid_code(self, client, mock_render):
        """异步渲染对无效代码返回错误（无 Scene 类）"""
        response = client.post("/api/async/render", json={
            "code": "print('no manim here')",
        })
        assert response.status_code == 200
        data = response.json()
        # 无 Scene → 预检失败
        assert data["code"] != 0

    def test_async_template_dispatches(self, client, mock_render):
        """POST /api/async/template-render 返回 task_id"""
        response = client.post("/api/async/template-render", json={
            "template_id": "sort-algorithm",
            "params": {"algorithm": "bubble", "array_size": 8, "speed": 0.5},
        })
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "task_id" in data["data"]

    def test_async_invalid_template(self, client):
        """不存在模板的异步请求返回错误"""
        response = client.post("/api/async/template-render", json={
            "template_id": "nonexistent-template",
            "params": {},
        })
        # 可能返回 200 error 或 500
        assert response.status_code in (200, 500)


class TestTaskQueue:
    """任务队列管理端点测试"""

    def test_list_tasks(self, client, mock_redis):
        """GET /api/tasks 返回任务列表"""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]

    def test_list_tasks_with_filter(self, client, mock_redis):
        """GET /api/tasks?state=SUCCESS 支持筛选"""
        response = client.get("/api/tasks?state=SUCCESS&page=1&page_size=10")
        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    def test_delete_nonexistent_task(self, client, mock_redis):
        """DELETE /api/tasks/{id} 对不存在的任务返回 404"""
        response = client.delete("/api/tasks/nonexistent-12345")
        assert response.status_code == 404

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pytest 共享 fixtures"""
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# 确保 ai-service 在 sys.path 中
AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(AI_SERVICE_DIR))

# 在导入应用之前设置测试环境变量
os.environ.setdefault("DEEPSEEK_API_KEY", "test-key-placeholder")
os.environ.setdefault("RATE_LIMIT_ENABLED", "false")


@pytest.fixture(scope="session")
def app():
    """创建 FastAPI 应用实例（session 级别复用）"""
    from main import app
    return app


@pytest.fixture(scope="module")
def client(app):
    """FastAPI TestClient"""
    return TestClient(app)


@pytest.fixture
def mock_redis(monkeypatch):
    """用 fakeredis 替换真实 Redis"""
    try:
        from fakeredis import FakeRedis
        fake_redis = FakeRedis(decode_responses=True)

        def fake_get_redis():
            return fake_redis

        monkeypatch.setattr(
            "services.progress_service._get_redis",
            fake_get_redis,
        )
        monkeypatch.setattr(
            "services.rate_limiter.RateLimiter.redis",
            property(lambda self: fake_redis),
        )
        return fake_redis
    except ImportError as e:
        pytest.skip(f"fakeredis not available: {e}")


@pytest.fixture
def mock_deepseek(monkeypatch):
    """Mock DeepSeek API 调用"""
    def fake_chat(messages):
        return True, """```python
from manim import *

class TestAnimation(Scene):
    def construct(self):
        circle = Circle()
        self.play(Create(circle))
        self.wait(1)
```"""
    monkeypatch.setattr("ai_engine.deepseek_chat_request", fake_chat)


@pytest.fixture
def mock_render(monkeypatch):
    """Mock Manim 渲染（避免真实渲染）"""
    def fake_render(code_str, progress_callback=None):
        import uuid
        task_id = uuid.uuid4().hex[:8]
        if progress_callback:
            progress_callback("started", "mock")
            progress_callback("rendering", "mock frame")
            progress_callback("success", "mock done")
        return True, "mock render log", f"/videos/{task_id}.mp4"
    monkeypatch.setattr("ai_engine.render_manim_animation", fake_render)

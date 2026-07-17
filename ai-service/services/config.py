#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统一配置管理
基于 pydantic-settings，从 .env 文件和环境变量加载配置。
所有新增代码通过本模块获取配置，ai_engine.py 保持独立不变。
"""
import os
from pathlib import Path
from typing import List, Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置单例，自动从 .env 和环境变量加载"""

    # ==================== DeepSeek 大模型配置 ====================
    deepseek_api_key: str = ""
    deepseek_model_name: str = "deepseek-v4-flash"

    # ==================== Ollama 本地嵌入服务 ====================
    ollama_base_url: str = "http://localhost:11434"
    embedding_model_name: str = "nomic-embed-text"

    # ==================== 渲染配置 ====================
    render_quality_flag: str = "-qm"  # -ql(480p) -qm(720p) -qh(1080p) -qk(4K)
    render_timeout: int = 120  # 秒

    # ==================== Redis 配置 ====================
    redis_url: str = "redis://localhost:6379/0"

    # ==================== CORS 配置 ====================
    cors_origins: str = "*"  # 逗号分隔，或 "*"

    # ==================== 安全配置 ====================
    api_key: Optional[str] = None  # 若设置，则所有 /api/* 请求需携带 X-API-Key 头
    jwt_secret: str = "ManimAI2024SecretKeyForJWTTokenGenerationMustBe256BitsLong!!"  # 与 Java 后端一致

    # ==================== 速率限制 ====================
    rate_limit_enabled: bool = True
    rate_limit_per_minute: int = 300
    rate_limit_generate_per_minute: int = 60  # 生成类端点更严格的限制

    # ==================== 日志配置 ====================
    log_level: str = "INFO"

    # ==================== 视频管理 ====================
    max_video_age_days: int = 30  # 自动清理超过此天数的旧视频

    # ==================== 应用元信息 ====================
    app_version: str = "1.0.0"
    app_name: str = "CS Visual Wiki AI Service"

    # ==================== 代理配置 ====================
    http_proxy: Optional[str] = None

    model_config = {
        "env_file": str(Path(__file__).resolve().parent.parent / ".env"),
        "env_file_encoding": "utf-8",
        "extra": "ignore",  # 忽略 .env 中未定义的变量
    }

    @property
    def cors_origin_list(self) -> List[str]:
        """将逗号分隔的字符串转为列表"""
        if self.cors_origins == "*":
            return ["*"]
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_auth_enabled(self) -> bool:
        """API Key 认证是否启用"""
        return self.api_key is not None and len(self.api_key) > 0


# 全局单例
settings = Settings()

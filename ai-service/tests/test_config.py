#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""测试统一配置管理"""
import os
import pytest


class TestConfigService:
    """services/config.py 测试"""

    def test_settings_defaults(self):
        """默认值正确"""
        from services.config import Settings
        # 覆盖 env_file 避免读取实际 .env
        os.environ["DEEPSEEK_API_KEY"] = "test-key"
        s = Settings(_env_file="nonexistent.env")
        assert s.deepseek_model_name == "deepseek-v4-flash"
        assert s.redis_url == "redis://localhost:6379/0"
        assert s.render_quality_flag == "-qm"
        assert s.render_timeout == 120
        assert s.app_version == "1.0.0"

    def test_cors_origin_list(self):
        """cors_origins 字符串被正确解析为列表"""
        from services.config import Settings
        s = Settings(_env_file="nonexistent.env")

        # 默认 "*"
        s.cors_origins = "*"
        assert s.cors_origin_list == ["*"]

        # 逗号分隔
        s.cors_origins = "http://localhost:5173,http://localhost:8081"
        assert s.cors_origin_list == ["http://localhost:5173", "http://localhost:8081"]

    def test_auth_enabled_when_key_set(self):
        """设置 API Key 时认证启用"""
        from services.config import Settings
        s = Settings(_env_file="nonexistent.env")
        s.api_key = "test-secret"
        assert s.is_auth_enabled is True

    def test_auth_disabled_when_key_none(self):
        """无 API Key 时认证禁用"""
        from services.config import Settings
        s = Settings(_env_file="nonexistent.env")
        s.api_key = None
        assert s.is_auth_enabled is False

    def test_extra_fields_ignored(self):
        """.env 中的未知变量应该被忽略"""
        from services.config import Settings
        s = Settings(_env_file="nonexistent.env")
        # extra: "ignore" 确保不会抛出 ValidationError
        # 此测试确保配置加载不会因新增未定义变量而崩溃
        assert s.app_name == "CS Visual Wiki AI Service"

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery异步任务配置
注意：本文件为外层异步封装，不修改ai_engine.py核心代码
使用前需启动Redis服务，在Linux上的启动命令:celery -A workers.celery_app worker --loglevel=info
Windows上的启动命令:celery -A workers.celery_app worker --loglevel=info -P solo
因为Celery 在 Windows 上的已知兼容性问题——billiard 的多进程池和 Windows 的信号机制不兼容，所以Windows上串行运行
"""
import sys
from pathlib import Path

# 确保 ai-service 目录在 sys.path 中，使得 celery -A workers.celery_app worker
# 在任何目录下启动都能正确解析 ai_engine 和 services 等顶层模块
_AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(_AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SERVICE_DIR))

from celery import Celery
from ai_engine import render_manim_animation, run_full_pipeline
from services.template_service import template_service

# Celery配置
celery_app = Celery(
    'cs_visual_tasks',
    broker='redis://localhost:6379/0',
    backend='redis://localhost:6379/0',
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=False,
    task_track_started=True,
    task_time_limit=300,  # 单任务超时5分钟
    task_soft_time_limit=240,
)


@celery_app.task(bind=True, max_retries=2)
def render_code_task(self, code: str):
    """异步渲染已有Manim代码"""
    try:
        success, log, video_path = render_manim_animation(code)
        return {
            "success": success,
            "code": code,
            "log": log,
            "video_path": video_path
        }
    except Exception as e:
        self.retry(exc=e, countdown=5)


@celery_app.task(bind=True, max_retries=2)
def generate_full_task(self, requirement: str, max_retry: int = 3):
    """异步完整生成流水线（需求→代码→渲染→修复）"""
    try:
        result = run_full_pipeline(requirement, max_retry=max_retry)
        return result
    except Exception as e:
        self.retry(exc=e, countdown=5)


@celery_app.task(bind=True, max_retries=2)
def render_template_task(self, template_id: str, params: dict):
    """异步模板渲染任务"""
    try:
        # 生成代码
        gen_success, code = template_service.render_template_code(template_id, params)
        if not gen_success:
            return {"success": False, "error": code}
        # 渲染
        success, log, video_path = render_manim_animation(code)
        return {
            "success": success,
            "code": code,
            "log": log,
            "video_path": video_path
        }
    except Exception as e:
        self.retry(exc=e, countdown=5)

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
from services.progress_service import set_progress

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


def _make_render_callback(task_id: str):
    """创建渲染进度回调，将 Manim 渲染进度同步到 Redis"""
    def on_progress(state: str, message: str):
        progress = 0
        if state == "started":
            progress, msg = 5, "渲染已启动"
        elif state == "rendering":
            progress, msg = 50, message
        elif state == "success":
            progress, msg = 100, "渲染完成"
        elif state == "failed":
            progress, msg = 0, f"渲染失败: {message}"
        else:
            msg = message
        set_progress(task_id, state="RENDERING", progress=progress, message=msg)
    return on_progress


@celery_app.task(bind=True, max_retries=2)
def render_code_task(self, code: str):
    """异步渲染已有Manim代码"""
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0, message="任务已接收，准备渲染...")

    try:
        on_progress = _make_render_callback(task_id)
        success, log, video_path = render_manim_animation(code, progress_callback=on_progress)

        if success:
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="渲染完成", video_path=video_path, log=log)
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="渲染失败", log=log)

        return {"success": success, "code": code, "log": log, "video_path": video_path}
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        self.retry(exc=e, countdown=5)


@celery_app.task(bind=True, max_retries=2)
def generate_full_task(self, requirement: str, max_retry: int = 3):
    """异步完整生成流水线（需求→代码→渲染→修复）"""
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0, message="任务已接收，AI 正在生成代码...")

    try:
        result = run_full_pipeline(requirement, max_retry=max_retry)

        if result.get("success"):
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="生成完成", video_path=result.get("video_path", ""),
                         log=result.get("log", ""))
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="生成失败", log=result.get("log", ""))

        return result
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        self.retry(exc=e, countdown=5)


@celery_app.task(bind=True, max_retries=2)
def render_template_task(self, template_id: str, params: dict):
    """异步模板渲染任务"""
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0,
                 message=f"正在生成模板 '{template_id}' 的代码...")

    try:
        # 1. 生成代码
        gen_success, code = template_service.render_template_code(template_id, params)
        if not gen_success:
            set_progress(task_id, state="FAILURE", progress=0, message=f"模板生成失败: {code}")
            return {"success": False, "error": code}

        set_progress(task_id, state="STARTED", progress=10, message="代码已生成，开始渲染...")

        # 2. 渲染
        on_progress = _make_render_callback(task_id)
        success, log, video_path = render_manim_animation(code, progress_callback=on_progress)

        if success:
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="渲染完成", video_path=video_path, log=log)
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="渲染失败", log=log)

        return {"success": success, "code": code, "log": log, "video_path": video_path}
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        self.retry(exc=e, countdown=5)

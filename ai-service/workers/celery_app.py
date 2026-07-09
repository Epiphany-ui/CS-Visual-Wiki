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
from services.config import settings
from services.template_service import template_service
from services.progress_service import set_progress, save_video_meta
from services.logging_config import get_logger

logger = get_logger("celery")

# Celery 配置 — Redis 地址从统一配置读取
celery_app = Celery(
    'cs_visual_tasks',
    broker=settings.redis_url,
    backend=settings.redis_url,
    task_serializer='json',
    result_serializer='json',
    accept_content=['json'],
    timezone='Asia/Shanghai',
    enable_utc=False,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    result_expires=3600,
)

# 可重试的异常类型（网络/Redis 瞬时错误，非代码逻辑错误）
RETRYABLE_EXCEPTIONS = (ConnectionError, TimeoutError, OSError)


def _make_render_callback(task_id: str):
    """创建渲染进度回调，将 Manim 渲染进度同步到 Redis"""
    def on_progress(state: str, message: str, percent: int = 0):
        if state == "started":
            progress, msg = 5, "渲染已启动"
        elif state == "rendering":
            # message 来自 tqdm stderr 解析，percent 为实际百分比
            progress, msg = percent if percent > 0 else 50, message or "渲染中..."
        elif state == "success":
            progress, msg = 100, "渲染完成"
        elif state == "failed":
            progress, msg = 0, f"渲染失败: {message}"
        else:
            progress, msg = 0, message
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
            fn = video_path.replace("/videos/", "") if video_path else ""
            if fn:
                save_video_meta(fn, title=f"Manim 渲染 {fn[:8]}")
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="渲染完成", video_path=video_path, log=log)
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="渲染失败", log=log)

        return {"success": success, "code": code, "log": log, "video_path": video_path}
    except RETRYABLE_EXCEPTIONS as e:
        set_progress(task_id, state="FAILURE", progress=0, message=f"瞬时错误: {e}")
        self.retry(exc=e, countdown=5)
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        logger.exception("render_code_task 不可重试错误: %s", e)


@celery_app.task(bind=True, max_retries=2)
def generate_full_task(self, requirement: str, max_retry: int = 3):
    """异步完整生成流水线（需求→代码→渲染→修复）"""
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0, message="任务已接收，AI 正在生成代码...")

    try:
        on_progress = _make_render_callback(task_id)
        result = run_full_pipeline(requirement, max_retry=max_retry, progress_callback=on_progress)

        if result.get("success"):
            vp = result.get("video_path", "")
            fn = vp.replace("/videos/", "") if vp else ""
            if fn:
                save_video_meta(fn, title=requirement[:80])
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="生成完成", video_path=vp,
                         log=result.get("log", ""), code=result.get("code", ""))
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="生成失败", log=result.get("log", ""))

        return result
    except RETRYABLE_EXCEPTIONS as e:
        set_progress(task_id, state="FAILURE", progress=0, message=f"瞬时错误: {e}")
        self.retry(exc=e, countdown=5)
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        logger.exception("render_code_task 不可重试错误: %s", e)


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
    except RETRYABLE_EXCEPTIONS as e:
        set_progress(task_id, state="FAILURE", progress=0, message=f"瞬时错误: {e}")
        self.retry(exc=e, countdown=5)
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        logger.exception("render_code_task 不可重试错误: %s", e)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery异步任务配置
注意：本文件为外层异步封装，不修改ai_engine.py核心代码
使用前需启动Redis服务，在Linux上的启动命令:celery -A workers.celery_app worker --loglevel=info
Windows上的启动命令:celery -A workers.celery_app worker --loglevel=info -P solo
因为Celery 在 Windows 上的已知兼容性问题——billiard 的多进程池和 Windows 的信号机制不兼容，所以Windows上串行运行
"""
import subprocess
import sys
from pathlib import Path

# 确保 ai-service 目录在 sys.path 中，使得 celery -A workers.celery_app worker
# 在任何目录下启动都能正确解析 ai_engine 和 services 等顶层模块
_AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
if str(_AI_SERVICE_DIR) not in sys.path:
    sys.path.insert(0, str(_AI_SERVICE_DIR))

from celery import Celery
from ai_engine import render_manim_animation, run_full_pipeline, extract_scene_class_name, generate_video_poster
from services.config import settings
from services.template_service import template_service
from services.progress_service import set_progress, get_progress, save_video_meta, add_to_user_works, is_task_cancelled
from pathlib import Path as _Path
from services.logging_config import get_logger

logger = get_logger("celery")

_VIDEO_DIR = _Path(__file__).resolve().parent.parent / "outputs" / "videos"


def _cleanup_if_cancelled(task_id: str, video_path: str):
    """如果任务已被用户取消，删除已生成的视频和缩略图，返回 True 表示已清理"""
    if is_task_cancelled(task_id):
        logger.info(f"[cancel] 任务 {task_id} 已被用户取消，清理: {video_path}")
        try:
            fn = video_path.replace("/videos/", "") if video_path else ""
            if fn:
                for ext in (".mp4", ".jpg"):
                    f = _VIDEO_DIR / f"{_Path(fn).stem}{ext}"
                    if f.exists():
                        f.unlink()
        except Exception:
            pass
        set_progress(task_id, state="CANCELLED", progress=0, message="用户已取消")
        return True
    return False

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
    broker_connection_retry_on_startup=True,
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
def render_code_task(self, code: str, quality: str = None, username: str = None):
    """异步渲染已有Manim代码"""
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0, message="任务已接收，准备渲染...")

    try:
        on_progress = _make_render_callback(task_id)
        success, log, video_path = render_manim_animation(code, progress_callback=on_progress, quality=quality)

        if success:
            if _cleanup_if_cancelled(task_id, video_path):
                return {"success": False, "error": "cancelled"}
            fn = video_path.replace("/videos/", "") if video_path else ""
            if fn:
                scene = extract_scene_class_name(code) or "Manim"
                save_video_meta(fn, title=f"{scene} 渲染", username=username or "")
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="渲染完成", video_path=video_path, log=log, code=code)
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="渲染失败", log=log, code=code)

        return {"success": success, "code": code, "log": log, "video_path": video_path}
    except RETRYABLE_EXCEPTIONS as e:
        set_progress(task_id, state="FAILURE", progress=0, message=f"瞬时错误: {e}")
        self.retry(exc=e, countdown=5)
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        logger.exception("celery_task 不可重试错误: %s", e)


@celery_app.task(bind=True, max_retries=2)
def generate_full_task(self, requirement: str, max_retry: int = 3, quality: str = None, username: str = None):
    """异步完整生成流水线（需求→代码→渲染→修复）"""
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0, message="任务已接收，AI 正在生成代码...")

    try:
        on_progress = _make_render_callback(task_id)
        result = run_full_pipeline(requirement, max_retry=max_retry, progress_callback=on_progress, quality=quality)

        vp = result.get("video_path", "")
        code_str = result.get("code", "")
        if result.get("success"):
            if _cleanup_if_cancelled(task_id, vp):
                return {"success": False, "error": "cancelled"}
            fn = vp.replace("/videos/", "") if vp else ""
            if fn:
                save_video_meta(fn, title=requirement[:80], username=username or "")
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="生成完成", video_path=vp,
                         log=result.get("log", ""), code=code_str)
        else:
            # 失败时也传递代码，让用户可以在沙箱中手动修复
            set_progress(task_id, state="FAILURE", progress=0,
                         message="生成失败", log=result.get("log", ""),
                         code=code_str)

        return result
    except RETRYABLE_EXCEPTIONS as e:
        set_progress(task_id, state="FAILURE", progress=0, message=f"瞬时错误: {e}")
        self.retry(exc=e, countdown=5)
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        logger.exception("celery_task 不可重试错误: %s", e)


@celery_app.task(bind=True, max_retries=2)
def render_template_task(self, template_id: str, params: dict, quality: str = None, username: str = None):
    """异步模板渲染任务（带代码缓存：相同代码跳过渲染）"""
    import hashlib
    task_id = self.request.id
    set_progress(task_id, state="STARTED", progress=0,
                 message=f"正在生成模板 '{template_id}' 的代码...")

    try:
        # 1. 生成代码
        gen_success, code = template_service.render_template_code(template_id, params)
        if not gen_success:
            set_progress(task_id, state="FAILURE", progress=0, message=f"模板生成失败: {code}")
            return {"success": False, "error": code}

        # 2. 缓存检查：相同模板+参数 → 跳过渲染
        import json
        cache_key = hashlib.md5(f"{template_id}:{json.dumps(params, sort_keys=True)}".encode()).hexdigest()[:16]
        cached = get_progress(f"tpl:{cache_key}")
        if cached.get("video_path"):
            if _cleanup_if_cancelled(task_id, cached["video_path"]):
                return {"success": False, "error": "cancelled"}
            vp = cached["video_path"]
            # 缓存命中时也关联到当前用户
            if username:
                fn = vp.replace("/videos/", "") if vp else ""
                if fn:
                    add_to_user_works(username, fn)
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="渲染完成（缓存命中）", video_path=vp, log="", code=code)
            return {"success": True, "code": code, "log": "缓存命中", "video_path": vp}

        set_progress(task_id, state="STARTED", progress=10, message="代码已生成，开始渲染...")

        # 2. 渲染
        on_progress = _make_render_callback(task_id)
        success, log, video_path = render_manim_animation(code, progress_callback=on_progress, quality=quality)

        if success:
            if _cleanup_if_cancelled(task_id, video_path):
                return {"success": False, "error": "cancelled"}
            fn = video_path.replace("/videos/", "") if video_path else ""
            if fn:
                tpl = template_service.get_template_detail(template_id)
                tpl_name = tpl[1].get("name", template_id) if tpl[0] else template_id
                save_video_meta(fn, title=f"{tpl_name}", username=username or "")
            # 缓存结果：相同模板+参数下次秒级返回
            set_progress(f"tpl:{cache_key}", state="SUCCESS", progress=100,
                         message="模板缓存", video_path=video_path, log=log, code=code)
            set_progress(task_id, state="SUCCESS", progress=100,
                         message="渲染完成", video_path=video_path, log=log, code=code)
        else:
            set_progress(task_id, state="FAILURE", progress=0,
                         message="渲染失败", log=log, code=code)

        return {"success": success, "code": code, "log": log, "video_path": video_path}
    except RETRYABLE_EXCEPTIONS as e:
        set_progress(task_id, state="FAILURE", progress=0, message=f"瞬时错误: {e}")
        self.retry(exc=e, countdown=5)
    except Exception as e:
        set_progress(task_id, state="FAILURE", progress=0, message=str(e))
        logger.exception("celery_task 不可重试错误: %s", e)

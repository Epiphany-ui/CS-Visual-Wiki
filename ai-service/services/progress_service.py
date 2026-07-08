#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
异步任务进度追踪服务
基于 Redis 存储任务状态，通过 Pub/Sub 实现实时进度推送。
配合 Celery Worker + SSE 端点使用，为前端提供"渲染中→完成"的实时反馈。
"""
import json
import time
from datetime import datetime
from typing import Optional, Dict, Generator

import redis

# Redis 连接（复用 Celery 的 Redis，默认本地）
REDIS_URL = "redis://localhost:6379/0"
_redis_client: Optional[redis.Redis] = None

# 常量
TASK_KEY_PREFIX = "cs:task"
TASK_CHANNEL_PREFIX = "cs:task"
TASK_TTL = 3600  # 任务状态 1 小时后自动过期


def _get_redis() -> redis.Redis:
    """延迟初始化 Redis 连接"""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(REDIS_URL, decode_responses=True)
    return _redis_client


# ===================== 任务进度管理 =====================

def set_progress(
    task_id: str,
    state: str,
    progress: int = 0,
    message: str = "",
    video_path: str = "",
    log: str = "",
):
    """
    更新任务进度并发布到 Pub/Sub
    :param task_id: 任务 ID
    :param state: PENDING | STARTED | RENDERING | SUCCESS | FAILURE
    :param progress: 进度百分比 0-100
    :param message: 当前状态描述
    :param video_path: 成功时返回的视频路径
    :param log: 日志信息
    """
    r = _get_redis()
    key = f"{TASK_KEY_PREFIX}:{task_id}"
    channel = f"{TASK_CHANNEL_PREFIX}:{task_id}:progress"

    data = {
        "task_id": task_id,
        "state": state,
        "progress": progress,
        "message": message,
        "video_path": video_path,
        "log": log[-2000:] if log else "",  # 截断日志，避免 Redis 存储过大
        "updated_at": datetime.now().isoformat(),
    }

    # 存储状态
    r.setex(key, TASK_TTL, json.dumps(data, ensure_ascii=False))
    # 发布事件
    r.publish(channel, json.dumps(data, ensure_ascii=False))


def get_progress(task_id: str) -> Dict:
    """查询任务进度"""
    r = _get_redis()
    key = f"{TASK_KEY_PREFIX}:{task_id}"
    raw = r.get(key)
    if raw:
        return json.loads(raw)
    return {"task_id": task_id, "state": "UNKNOWN", "progress": 0, "message": "任务不存在或已过期"}


def subscribe_progress(task_id: str):
    """
    订阅任务进度更新（返回生成器，供 SSE 使用）
    使用 Redis Pub/Sub 订阅，阻塞式迭代
    """
    r = _get_redis()
    channel = f"{TASK_CHANNEL_PREFIX}:{task_id}:progress"
    pubsub = r.pubsub()
    pubsub.subscribe(channel)
    return pubsub


def unsubscribe_progress(pubsub):
    """取消订阅"""
    try:
        pubsub.unsubscribe()
        pubsub.close()
    except Exception:
        pass


# ===================== 视频文件管理 =====================

def list_videos() -> list:
    """列出 outputs/videos/ 下所有视频文件信息"""
    from pathlib import Path

    video_dir = Path(__file__).resolve().parent.parent / "outputs" / "videos"
    if not video_dir.exists():
        return []

    videos = []
    for f in sorted(video_dir.glob("*.mp4"), key=lambda x: x.stat().st_mtime, reverse=True):
        stat = f.stat()
        videos.append({
            "filename": f.name,
            "task_id": f.stem,
            "size_bytes": stat.st_size,
            "size_mb": round(stat.st_size / (1024 * 1024), 2),
            "created_at": datetime.fromtimestamp(stat.st_ctime).isoformat(),
            "url": f"/videos/{f.name}",
        })
    return videos


def delete_video(filename: str) -> bool:
    """删除指定视频文件及对应的代码文件"""
    from pathlib import Path

    base = Path(__file__).resolve().parent.parent / "outputs"
    video_path = base / "videos" / filename
    code_path = base / "code" / f"{Path(filename).stem}.py"

    deleted = False
    if video_path.exists():
        video_path.unlink()
        deleted = True
    if code_path.exists():
        code_path.unlink()
        deleted = True
    return deleted

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""社区互动服务：评论、点赞、浏览量（基于 Redis）"""
import json
import time
import uuid
from typing import List, Dict, Optional

from services.progress_service import _get_redis, _maybe_bgsave


# ==================== 点赞 ====================

def toggle_like(work_id: int, username: str) -> dict:
    """Toggle 点赞：已点赞则取消，未点赞则添加。返回 {liked: bool, count: int}"""
    r = _get_redis()
    key = f"cs:work_likes:{work_id}"
    if r.sismember(key, username):
        r.srem(key, username)
        liked = False
    else:
        r.sadd(key, username)
        liked = True
    _maybe_bgsave()
    count = r.scard(key)
    return {"liked": liked, "count": count}


def is_liked(work_id: int, username: str) -> bool:
    """检查用户是否已点赞"""
    try:
        return bool(_get_redis().sismember(f"cs:work_likes:{work_id}", username))
    except Exception:
        return False


def get_like_counts(work_ids: List[int]) -> Dict[int, int]:
    """批量获取多个作品的点赞数"""
    r = _get_redis()
    result = {}
    for wid in work_ids:
        result[wid] = r.scard(f"cs:work_likes:{wid}")
    return result


def check_user_likes(work_ids: List[int], username: str) -> Dict[int, bool]:
    """批量查询用户是否已点赞"""
    r = _get_redis()
    result = {}
    for wid in work_ids:
        result[wid] = bool(r.sismember(f"cs:work_likes:{wid}", username))
    return result


# ==================== 浏览量 ====================

def increment_view(work_id: int) -> int:
    """递增浏览量，返回最新值"""
    r = _get_redis()
    val = r.incr(f"cs:work_views:{work_id}")
    _maybe_bgsave()
    return val


def get_view_counts(work_ids: List[int]) -> Dict[int, int]:
    """批量获取浏览量"""
    r = _get_redis()
    result = {}
    for wid in work_ids:
        v = r.get(f"cs:work_views:{wid}")
        result[wid] = int(v) if v else 0
    return result


# ==================== 评论 ====================

def add_comment(work_id: int, username: str, text: str, avatar: str = "", user_id: str = "") -> dict:
    """添加评论，返回评论对象"""
    r = _get_redis()
    comment = {
        "id": uuid.uuid4().hex[:12],
        "workId": work_id,
        "username": username,
        "text": text.strip(),
        "likes": 0,
        "avatar": avatar or "",
        "userId": user_id or "",
    }
    # 用 sorted set 存储，score = 点赞数，方便按热度排序
    r.zadd(f"cs:comments:{work_id}", {json.dumps(comment, ensure_ascii=False): 0})
    _maybe_bgsave()
    return comment


def get_comments(work_id: int, limit: int = 3, sort_by: str = "likes") -> List[dict]:
    """获取评论列表（默认按点赞数降序，返回前 N 条）"""
    r = _get_redis()
    key = f"cs:comments:{work_id}"
    if sort_by == "likes":
        raw = r.zrevrange(key, 0, limit - 1)
    else:
        raw = r.zrange(key, 0, limit - 1)  # 按时间（score=0 时按插入顺序）
    comments = []
    for item in raw:
        try:
            comments.append(json.loads(item))
        except Exception:
            continue
    return comments


def get_comment_count(work_id: int) -> int:
    """获取评论总数"""
    return _get_redis().zcard(f"cs:comments:{work_id}")


def like_comment(comment_id: str, work_id: int, username: str = "") -> dict:
    """给评论点赞/取消点赞，返回 {liked: bool, likes: int}"""
    r = _get_redis()
    like_key = f"cs:comment_like:{comment_id}"
    # 检查是否已点赞
    if r.sismember(like_key, username):
        r.srem(like_key, username)
        delta = -1
        liked = False
    else:
        r.sadd(like_key, username)
        delta = 1
        liked = True

    key = f"cs:comments:{work_id}"
    raw = r.zrange(key, 0, -1)
    for item in raw:
        try:
            c = json.loads(item)
            if c.get("id") == comment_id:
                r.zrem(key, item)
                c["likes"] = max(0, c.get("likes", 0) + delta)
                r.zadd(key, {json.dumps(c, ensure_ascii=False): c["likes"]})
                _maybe_bgsave()
                return {"liked": liked, "likes": c["likes"]}
        except Exception:
            continue
    return {"liked": False, "likes": 0}

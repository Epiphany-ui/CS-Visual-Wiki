#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
逐帧调试服务 v1.0
基于 FFmpeg 从已渲染的视频中提取帧图片，支持：
- 视频元数据查询（分辨率、帧率、时长）
- 逐帧提取（PNG/JPEG）
- 时间点截图
- 缩略图网格生成
- 帧缓存管理
"""
import json
import subprocess
import time
from pathlib import Path
from typing import Optional, List, Dict, Tuple

from .logging_config import get_logger

logger = get_logger("debug_service")

# 基础路径
_BASE_DIR = Path(__file__).resolve().parent.parent
VIDEO_DIR = _BASE_DIR / "outputs" / "videos"
FRAME_CACHE_DIR = _BASE_DIR / "outputs" / "frames"


def _ensure_frame_dir(video_stem: str) -> Path:
    """确保帧缓存目录存在"""
    d = FRAME_CACHE_DIR / video_stem
    d.mkdir(parents=True, exist_ok=True)
    return d


def _run_ffprobe(video_path: Path) -> Optional[Dict]:
    """运行 ffprobe 获取视频元数据"""
    try:
        result = subprocess.run(
            [
                "ffprobe", "-v", "quiet",
                "-print_format", "json",
                "-show_format", "-show_streams",
                str(video_path),
            ],
            capture_output=True, text=True, timeout=15,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0:
            return json.loads(result.stdout)
        logger.error("ffprobe failed: %s", result.stderr[:200])
        return None
    except FileNotFoundError:
        logger.error("ffprobe not found - ffmpeg required")
        return None
    except subprocess.TimeoutExpired:
        logger.error("ffprobe timeout for %s", video_path.name)
        return None
    except Exception as e:
        logger.error("ffprobe error: %s", e)
        return None


def get_video_info(filename: str) -> Tuple[bool, Dict]:
    """
    获取视频元数据（用于帧调试的入口）。

    :param filename: 视频文件名（如 abc123.mp4）
    :return: (found: bool, info: dict)
    """
    video_path = VIDEO_DIR / filename
    if not video_path.exists():
        return False, {"error": f"视频 {filename} 不存在"}

    probe = _run_ffprobe(video_path)
    if not probe:
        return True, {
            "filename": filename,
            "error": "无法解析视频信息",
        }

    # 提取视频流信息
    video_stream = None
    for s in probe.get("streams", []):
        if s.get("codec_type") == "video":
            video_stream = s
            break

    fmt = probe.get("format", {})

    if video_stream:
        # 计算总帧数
        nb_frames = video_stream.get("nb_frames")
        if not nb_frames:
            duration = float(fmt.get("duration", 0))
            fps_parts = video_stream.get("r_frame_rate", "30/1").split("/")
            fps = float(fps_parts[0]) / float(fps_parts[1]) if len(fps_parts) == 2 else 30.0
            nb_frames = int(duration * fps) if duration and fps else 0

        info = {
            "filename": filename,
            "duration_seconds": float(fmt.get("duration", 0)),
            "fps": _parse_fps(video_stream.get("r_frame_rate", "30/1")),
            "total_frames": int(nb_frames) if nb_frames else 0,
            "resolution": f"{video_stream.get('width', 0)}x{video_stream.get('height', 0)}",
            "codec": video_stream.get("codec_name", "unknown"),
            "size_bytes": int(fmt.get("size", 0)),
            "size_mb": round(int(fmt.get("size", 0)) / (1024 * 1024), 2),
        }
    else:
        info = {
            "filename": filename,
            "duration_seconds": float(fmt.get("duration", 0)),
            "size_bytes": int(fmt.get("size", 0)),
            "error": "未找到视频流",
        }

    return True, info


def _parse_fps(fps_str: str) -> float:
    """解析 ffprobe 的帧率字符串 (如 '30/1' 或 '29.97')"""
    if "/" in fps_str:
        parts = fps_str.split("/")
        return round(float(parts[0]) / float(parts[1]), 2)
    return float(fps_str)


def extract_frames(
    filename: str,
    start_frame: int = 0,
    end_frame: int = 10,
    format: str = "jpg",
    quality: int = 85,
) -> Tuple[bool, Dict]:
    """
    提取指定范围的帧为图片。

    :param filename: 视频文件名
    :param start_frame: 起始帧编号
    :param end_frame: 结束帧编号（不含）
    :param format: 输出格式 (jpg/png)
    :param quality: JPEG 质量 (1-100)
    :return: (success, result_dict)
    """
    video_path = VIDEO_DIR / filename
    if not video_path.exists():
        return False, {"error": f"视频 {filename} 不存在"}

    video_stem = Path(filename).stem
    frame_dir = _ensure_frame_dir(video_stem)

    # 限制每次提取最多 100 帧，避免磁盘耗尽
    frame_count = end_frame - start_frame
    if frame_count > 100:
        end_frame = start_frame + 100

    output_pattern = str(frame_dir / f"frame_%04d.{format}")

    try:
        # 使用 ffmpeg select filter 提取指定帧范围
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-vf", f"select=between(n\\,{start_frame}\\,{end_frame - 1}),setpts=N/FRAME_RATE/TB",
                "-vsync", "0",
                "-q:v", str(min(31 - quality // 4, 31)),  # 映射 quality 到 ffmpeg q:v
                "-frame_pts", "1",
                output_pattern,
            ],
            capture_output=True, text=True, timeout=60,
            encoding="utf-8", errors="replace",
        )

        # 查找实际生成的文件
        extracted = sorted(frame_dir.glob(f"frame_*.{format}"))
        frames = []
        for i, fpath in enumerate(extracted):
            frame_num = start_frame + i
            frames.append({
                "frame_index": frame_num,
                "time_seconds": round(frame_num / 30.0, 3),  # 近似值，假设 30fps
                "url": f"/frames/{video_stem}/{fpath.name}",
                "size_bytes": fpath.stat().st_size,
            })

        return True, {
            "frames": frames,
            "total_extracted": len(frames),
            "requested_range": [start_frame, end_frame - 1],
            "format": format,
        }

    except FileNotFoundError:
        return False, {"error": "ffmpeg 未安装"}
    except subprocess.TimeoutExpired:
        return False, {"error": "帧提取超时（60s）"}
    except Exception as e:
        logger.error("Frame extraction error: %s", e)
        return False, {"error": str(e)}


def extract_frame_at_time(filename: str, time_seconds: float) -> Tuple[bool, Dict]:
    """
    提取指定时间点的单帧。

    :param filename: 视频文件名
    :param time_seconds: 时间点（秒）
    :return: (success, result_dict with url)
    """
    video_path = VIDEO_DIR / filename
    if not video_path.exists():
        return False, {"error": f"视频 {filename} 不存在"}

    video_stem = Path(filename).stem
    frame_dir = _ensure_frame_dir(video_stem)
    output_path = frame_dir / f"time_{time_seconds:.3f}s.jpg"

    if output_path.exists() and output_path.stat().st_mtime >= video_path.stat().st_mtime:
        return True, {
            "frame_path": str(output_path),
            "url": f"/frames/{video_stem}/{output_path.name}",
            "time_seconds": time_seconds,
            "cached": True,
        }

    try:
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-ss", str(time_seconds),
                "-i", str(video_path),
                "-vframes", "1",
                "-q:v", "2",
                str(output_path),
            ],
            capture_output=True, text=True, timeout=30,
            encoding="utf-8", errors="replace",
        )

        if result.returncode == 0 and output_path.exists():
            return True, {
                "url": f"/frames/{video_stem}/{output_path.name}",
                "time_seconds": time_seconds,
                "size_bytes": output_path.stat().st_size,
                "cached": False,
            }
        return False, {"error": f"截图失败: {result.stderr[:200]}"}

    except FileNotFoundError:
        return False, {"error": "ffmpeg 未安装"}
    except subprocess.TimeoutExpired:
        return False, {"error": "截图超时（30s）"}


def generate_thumbnail_sheet(
    filename: str,
    cols: int = 5,
    rows: int = 4,
    width: int = 320,
) -> Tuple[bool, Dict]:
    """
    生成缩略图网格（contact sheet），均匀采样视频的关键帧。

    :param filename: 视频文件名
    :param cols: 列数
    :param rows: 行数
    :param width: 每个缩略图宽度
    :return: (success, result_dict with composite image url)
    """
    video_path = VIDEO_DIR / filename
    if not video_path.exists():
        return False, {"error": f"视频 {filename} 不存在"}

    video_stem = Path(filename).stem
    frame_dir = _ensure_frame_dir(video_stem)
    output_path = frame_dir / f"sheet_{cols}x{rows}.jpg"

    if output_path.exists() and output_path.stat().st_mtime >= video_path.stat().st_mtime:
        return True, {
            "url": f"/frames/{video_stem}/{output_path.name}",
            "cols": cols, "rows": rows,
            "cached": True,
        }

    try:
        # ffmpeg thumbnail tile filter
        total_tiles = cols * rows
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-vf", (
                    f"fps=1/10,"  # 每10秒一个样本
                    f"scale={width}:-1,"
                    f"tile={cols}x{rows}:padding=4:color=black"
                ),
                "-frames:v", "1",
                "-q:v", "3",
                str(output_path),
            ],
            capture_output=True, text=True, timeout=60,
            encoding="utf-8", errors="replace",
        )

        if result.returncode == 0 and output_path.exists():
            return True, {
                "url": f"/frames/{video_stem}/{output_path.name}",
                "cols": cols, "rows": rows,
                "size_bytes": output_path.stat().st_size,
                "cached": False,
            }
        return False, {"error": f"缩略图生成失败: {result.stderr[:200]}"}

    except FileNotFoundError:
        return False, {"error": "ffmpeg 未安装"}
    except subprocess.TimeoutExpired:
        return False, {"error": "缩略图生成超时（60s）"}


def clean_frame_cache(video_stem: str = None):
    """清理帧缓存"""
    if video_stem:
        import shutil
        target = FRAME_CACHE_DIR / video_stem
        if target.exists():
            shutil.rmtree(target, ignore_errors=True)
    else:
        import shutil
        if FRAME_CACHE_DIR.exists():
            shutil.rmtree(FRAME_CACHE_DIR, ignore_errors=True)
            FRAME_CACHE_DIR.mkdir(exist_ok=True)

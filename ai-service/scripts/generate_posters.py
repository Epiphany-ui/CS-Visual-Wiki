#!/usr/bin/env python3
"""批量为已有视频生成缩略图（独立脚本，无内部依赖，仅需 ffmpeg）"""
import subprocess
import sys
from pathlib import Path

VIDEO_DIR = Path(__file__).resolve().parent.parent / "outputs" / "videos"


def generate_poster(mp4_path: Path) -> bool:
    """用 ffmpeg 截取第 2 秒帧保存为同名 .jpg"""
    poster_path = mp4_path.with_suffix(".jpg")
    if poster_path.exists():
        return True  # 已存在，跳过
    try:
        result = subprocess.run(
            ["ffmpeg", "-y", "-i", str(mp4_path), "-ss", "2", "-vframes", "1",
             "-q:v", "3", str(poster_path)],
            capture_output=True, timeout=15,
            encoding="utf-8", errors="replace",
        )
        return poster_path.exists()
    except Exception as e:
        print(f"  FAIL {mp4_path.name}: {e}")
        return False


def main():
    if not VIDEO_DIR.exists():
        print(f"视频目录不存在: {VIDEO_DIR}")
        sys.exit(1)

    mp4s = sorted(VIDEO_DIR.glob("*.mp4"))
    missing = [m for m in mp4s if not m.with_suffix(".jpg").exists()]

    print(f"总视频数: {len(mp4s)}")
    print(f"已有缩略图: {len(mp4s) - len(missing)}")
    print(f"缺少缩略图: {len(missing)}")

    if not missing:
        print("所有视频已有缩略图，无需操作。")
        return

    ok = 0
    for i, m in enumerate(missing):
        if generate_poster(m):
            ok += 1
        if (i + 1) % 10 == 0:
            print(f"  进度: {i + 1}/{len(missing)} (成功 {ok})")

    print(f"\n完成! 成功生成 {ok}/{len(missing)} 个缩略图。")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""批量从 .py 代码文件中提取场景类名，恢复视频标题到 Redis。

运行方式: E:\anaconda\envs\manim_ai\python.exe scripts/restore_titles.py
"""
import sys
from pathlib import Path

# 确保 ai-service 在 sys.path 中
_AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_SERVICE_DIR))

from services.progress_service import save_video_meta, get_all_video_metas
from services.logging_config import get_logger

logger = get_logger("restore_titles")

VIDEO_DIR = _AI_SERVICE_DIR / "outputs" / "videos"
CODE_DIR = _AI_SERVICE_DIR / "outputs" / "code"

SCENE_CLASS_RE = __import__('re').compile(r"class\s+(\w+)\s*\(\s*Scene\s*\)")


def extract_scene_name(code: str) -> str | None:
    m = SCENE_CLASS_RE.search(code)
    return m.group(1) if m else None


def main():
    mp4s = sorted(VIDEO_DIR.glob("*.mp4"))
    metas = get_all_video_metas()

    restored = 0
    skipped = 0
    no_code = 0

    for mp4 in mp4s:
        stem = mp4.stem
        fn = mp4.name

        # 检查是否已有标题
        existing = metas.get(fn, {})
        current_title = existing.get("title", "") if existing else ""
        if current_title and current_title != fn:
            # print(f"  SKIP {fn}: already has title '{current_title}'")
            skipped += 1
            continue

        # 查找对应的代码文件
        code_file = CODE_DIR / f"{stem}.py"
        if not code_file.exists():
            no_code += 1
            continue

        try:
            code = code_file.read_text(encoding="utf-8")
            scene = extract_scene_name(code)
            title = f"{scene} 渲染" if scene else f"动画 {stem[:6]}"
            save_video_meta(fn, title=title)
            restored += 1
            if restored % 20 == 0:
                print(f"  进度: {restored} 个标题已恢复...")
        except Exception as e:
            print(f"  ERROR {fn}: {e}")

    print(f"\n完成！")
    print(f"  已恢复: {restored}")
    print(f"  已有标题跳过: {skipped}")
    print(f"  无代码文件: {no_code}")
    print(f"  总视频数: {len(mp4s)}")


if __name__ == "__main__":
    main()

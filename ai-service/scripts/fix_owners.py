#!/usr/bin/env python3
"""扫描 Redis cs:video:user-works:* 键，将 cs:video:{filename} 元数据中
username 为"匿名"的条目修正为实际拥有者。

运行方式: E:\anaconda\envs\manim_ai\python.exe scripts/fix_owners.py
"""
import sys
from pathlib import Path

# 确保 ai-service 在 sys.path 中
_AI_SERVICE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_AI_SERVICE_DIR))

from services.progress_service import _get_redis, _maybe_bgsave, VIDEO_META_PREFIX
from services.logging_config import get_logger

logger = get_logger("fix_owners")


def main(dry_run: bool = False):
    """主逻辑：扫描 user-works set，修复匿名拥有者的视频元数据。

    :param dry_run: True 时只打印差异，不实际写入 Redis。
    """
    r = _get_redis()

    # 1. 扫描所有 cs:video:user-works:* 键
    cursor = 0
    user_keys: list[str] = []
    while True:
        cursor, keys = r.scan(cursor, match=f"{VIDEO_META_PREFIX}:user-works:*", count=200)
        for k in keys:
            ks = k.decode("utf-8") if isinstance(k, bytes) else k
            user_keys.append(ks)
        if cursor == 0:
            break

    if not user_keys:
        print("未找到任何 cs:video:user-works:* 键，无需修复。")
        return

    print(f"找到 {len(user_keys)} 个 user-works set，开始扫描...\n")

    total_fixed = 0
    total_checked = 0
    total_errors = 0

    for uk in user_keys:
        # 从 key 中提取用户名: cs:video:user-works:alice → alice
        prefix_len = len(f"{VIDEO_META_PREFIX}:user-works:")
        username = uk[prefix_len:]
        if not username:
            print(f"  跳过无效 key: {uk}")
            continue

        # 获取该用户的所有作品文件名
        filenames = r.smembers(uk)
        if not filenames:
            continue

        for fn_bytes in filenames:
            fn = fn_bytes.decode("utf-8") if isinstance(fn_bytes, bytes) else fn_bytes
            total_checked += 1

            meta_key = f"{VIDEO_META_PREFIX}:{fn}"
            meta = r.hgetall(meta_key)
            if not meta:
                continue

            # 解码 bytes key
            meta = {
                (k.decode("utf-8") if isinstance(k, bytes) else k): (
                    v.decode("utf-8") if isinstance(v, bytes) else v
                )
                for k, v in meta.items()
            }

            current_owner = meta.get("username", "")
            if current_owner != "匿名":
                continue

            # 需要修复
            print(f"  修复: {fn}  匿名 → {username}")
            if not dry_run:
                try:
                    r.hset(meta_key, "username", username)
                    total_fixed += 1
                except Exception as e:
                    print(f"    ERROR 写入失败: {e}")
                    total_errors += 1
            else:
                total_fixed += 1

    if not dry_run and total_fixed > 0:
        _maybe_bgsave()

    print(f"\n{'[DRY-RUN] ' if dry_run else ''}完成！")
    print(f"  已扫描 user-works set: {len(user_keys)}")
    print(f"  已检查视频元数据:    {total_checked}")
    print(f"  已修复拥有者:        {total_fixed}")
    if total_errors:
        print(f"  写入错误:            {total_errors}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="修复 Redis 中匿名视频的拥有者信息")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="仅打印差异，不实际写入 Redis",
    )
    args = parser.parse_args()
    main(dry_run=args.dry_run)

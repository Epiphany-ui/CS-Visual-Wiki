#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery 任务测试脚本
用法：
  1. 导入测试（不需要Redis）：python scripts/test_celery.py --import-only
  2. 同步调用测试（不需要Redis）：python scripts/test_celery.py --sync
  3. 异步调用测试（需要先启动Redis + Celery Worker）：
     - 终端1：redis-server
     - 终端2：cd ai-service && celery -A workers.celery_app worker --loglevel=info
     - 终端3：python scripts/test_celery.py
"""
import sys
import os
from pathlib import Path

# 确保 ai-service 在 sys.path 中
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))


def test_import():
    """测试1：验证 celery_app 能否正常导入（不依赖Redis）"""
    print("=" * 50)
    print("测试1：导入 celery_app 模块...")
    try:
        from workers.celery_app import celery_app
        print("✅ celery_app 导入成功")
        print(f"   broker: {celery_app.conf.broker_url}")
        print(f"   backend: {celery_app.conf.result_backend}")
        print(f"   已注册任务: {list(celery_app.tasks.keys())}")
        return True
    except Exception as e:
        print(f"❌ 导入失败: {e}")
        return False


def test_sync_direct():
    """测试2：直接调用核心函数（不经过Celery，不需要Redis）"""
    print("\n" + "=" * 50)
    print("测试2：直接调用 ai_engine 核心函数（同步，无Celery）")
    try:
        from ai_engine import render_manim_animation

        # 用一段最简单的 Manim 代码测试渲染
        test_code = """
from manim import *

class TestScene(Scene):
    def construct(self):
        circle = Circle(radius=1, color=BLUE)
        text = Text("Hello CS Visual!", font_size=36)
        text.next_to(circle, DOWN)
        self.play(Create(circle), Write(text))
        self.wait(1)
"""
        print("   正在渲染测试动画...")
        success, log, video_path = render_manim_animation(test_code)
        if success:
            print(f"✅ 渲染成功！视频路径: {video_path}")
            return True
        else:
            print(f"⚠️  渲染失败（可能是Manim环境问题）:\n{log[:500]}")
            return False
    except Exception as e:
        print(f"❌ 直接调用失败: {e}")
        return False


def test_celery_async():
    """测试3：通过 Celery 异步调用任务（需要 Redis + Worker）"""
    print("\n" + "=" * 50)
    print("测试3：Celery 异步任务调用...")
    try:
        from workers.celery_app import celery_app, render_code_task

        # 发送简单渲染任务
        test_code = """
from manim import *

class QuickTest(Scene):
    def construct(self):
        square = Square(side_length=1, color=RED)
        self.play(Create(square))
        self.wait(0.5)
"""
        print("   提交异步渲染任务...")
        result = render_code_task.delay(test_code)

        print(f"   任务ID: {result.task_id}")
        print(f"   任务状态: {result.status}")

        # 等待结果（超时60秒）
        print("   等待任务完成（最多等待60秒）...")
        try:
            task_result = result.get(timeout=60)
            if task_result.get("success"):
                print(f"✅ 异步渲染成功！视频: {task_result.get('video_path')}")
                return True
            else:
                print(f"⚠️  异步渲染失败:\n{task_result.get('log', '')[:500]}")
                return False
        except Exception as e:
            print(f"⚠️  等待结果超时或失败: {e}")
            print(f"   提示: 请确认 Redis 已启动且 Celery Worker 正在运行")
            print(f"   启动命令: celery -A workers.celery_app worker --loglevel=info")
            return False
    except Exception as e:
        print(f"❌ Celery 异步调用失败: {e}")
        return False


def test_template_task():
    """测试4：测试模板渲染任务"""
    print("\n" + "=" * 50)
    print("测试4：模板渲染任务...")
    try:
        from services.template_service import template_service

        # 先列出可用模板
        templates = template_service.get_template_list()
        if not templates:
            print("⚠️  没有找到任何模板")
            return False

        print(f"   找到 {len(templates)} 个模板:")
        for t in templates:
            print(f"     - {t['id']}: {t['name']} [{t['category']}]")

        # 取第一个模板渲染代码（不执行渲染）
        first_tpl = templates[0]
        template_id = first_tpl["id"]
        detail = template_service.get_template_detail(template_id)
        if detail[0]:
            params = {}
            for p in detail[1]["params"]:
                if p.get("default") is not None:
                    params[p["name"]] = p["default"]
            print(f"\n   用默认参数测试模板 '{template_id}': {params}")
            success, code = template_service.render_template_code(template_id, params)
            if success:
                print(f"✅ 模板代码生成成功！代码长度: {len(code)} 字符")
                print(f"   代码预览:\n{code[:300]}...")
                return True
            else:
                print(f"❌ 模板代码生成失败: {code}")
                return False
    except Exception as e:
        print(f"❌ 模板测试失败: {e}")
        return False


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Celery 任务测试")
    parser.add_argument("--import-only", action="store_true", help="仅测试导入")
    parser.add_argument("--sync", action="store_true", help="测试同步直接调用（不需要Redis）")
    parser.add_argument("--all", action="store_true", help="运行所有测试")
    args = parser.parse_args()

    results = []

    if args.import_only or args.all or (not args.sync):
        results.append(("导入测试", test_import()))

    if args.sync or args.all:
        results.append(("同步渲染测试", test_sync_direct()))
        results.append(("模板渲染测试", test_template_task()))

    if args.all:
        results.append(("Celery异步测试", test_celery_async()))

    if not results:
        parser.print_help()
        sys.exit(0)

    print("\n" + "=" * 50)
    print("测试结果汇总:")
    all_pass = True
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"  {status} - {name}")
        if not passed:
            all_pass = False

    sys.exit(0 if all_pass else 1)

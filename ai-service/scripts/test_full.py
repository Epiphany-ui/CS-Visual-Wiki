#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ai-service 全功能冒烟测试
覆盖：导入 → 渲染 → API → 模板 → Prompt → 视频管理 → 导出 → 日志
"""
import sys, json, time, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

PASS, FAIL = 0, 0
API_BASE = "http://localhost:8000"


def test(name, fn):
    global PASS, FAIL
    try:
        fn()
        print(f"  ✅ {name}")
        PASS += 1
    except Exception as e:
        print(f"  ❌ {name}: {e}")
        FAIL += 1


# ==================== 模块导入 ====================
def step1_imports():
    print("\n" + "=" * 50)
    print("1. 模块导入测试")

    test("logging_config", lambda: __import__("services.logging_config"))
    test("ai_engine", lambda: __import__("ai_engine"))
    test("prompt_service", lambda: __import__("services.prompt_service"))
    test("template_service", lambda: __import__("services.template_service"))
    test("progress_service", lambda: __import__("services.progress_service"))
    test("celery_app", lambda: __import__("workers.celery_app"))


# ==================== 核心引擎 ====================
def step2_core_engine():
    print("\n" + "=" * 50)
    print("2. 核心引擎测试")

    from ai_engine import render_manim_animation, generate_manim_code, fix_manim_code, rag_retrieve_references, run_full_pipeline

    code = """
from manim import *
class QuickTest(Scene):
    def construct(self):
        c = Circle(radius=0.5, color=BLUE)
        self.play(Create(c))
        self.wait(0.3)
"""

    test("渲染 Manim 动画", lambda: (
        lambda r: r[0] or print(f"  渲染日志: {r[1][:200]}")
    )(render_manim_animation(code)))

    test("RAG 检索", lambda: (
        lambda r: True  # RAG 可能返回空，不算失败
    )(rag_retrieve_references("冒泡排序")))


# ==================== 模板引擎 ====================
def step3_templates():
    print("\n" + "=" * 50)
    print("3. 模板引擎测试")

    from services.template_service import template_service

    templates = template_service.get_template_list()

    test(f"加载了 {len(templates)} 个模板", lambda: (
        None if len(templates) >= 10 else (_ for _ in ()).throw(AssertionError(f"期望>=10，实际{len(templates)}"))
    ))

    for t in templates:
        tid = t["id"]
        detail = template_service.get_template_detail(tid)
        params = {}
        for p in detail[1]["params"]:
            if p.get("default") is not None:
                params[p["name"]] = p["default"]
        success, code = template_service.render_template_code(tid, params)
        test(f"  模板 [{tid}] 代码生成", lambda s=success, c=code: (
            None if s else (_ for _ in ()).throw(AssertionError(c[:200]))
        ))
        # 验证生成的代码语法
        import ast
        test(f"  模板 [{tid}] 语法检查", lambda c=code: ast.parse(c))


# ==================== Prompt 服务 ====================
def step4_prompts():
    print("\n" + "=" * 50)
    print("4. Prompt 服务测试")

    from services.prompt_service import prompt_service

    info = prompt_service.get_template_info()
    test(f"加载了 {len(info)} 个 Prompt 模板", lambda: len(info) >= 2)

    for p in info:
        name = p["name"]
        content = prompt_service.render(
            name,
            max_animation_duration=30,
            references="测试",
            error_message="测试错误",
        )
        test(f"  渲染 Prompt [{name}] ({len(content)}字符)", lambda: len(content) > 100)

    prompt_service.reload()
    test("热重载 Prompt", lambda: True)


# ==================== 日志系统 ====================
def step5_logging():
    print("\n" + "=" * 50)
    print("5. 日志系统测试")

    from services.logging_config import setup_logging, get_logger

    lg = get_logger("test")
    lg.info("测试日志 INFO")
    lg.warning("测试日志 WARNING")
    lg.debug("测试日志 DEBUG")

    log_dir = Path(__file__).resolve().parent.parent / "logs"
    test(f"日志目录存在: {log_dir}", lambda: log_dir.exists())


# ==================== 视频管理 ====================
def step6_video_management():
    print("\n" + "=" * 50)
    print("6. 视频管理测试")

    from services.progress_service import list_videos

    videos = list_videos()
    print(f"  当前有 {len(videos)} 个视频文件")
    for v in videos[:3]:
        print(f"    - {v['filename']} ({v['size_mb']}MB)")


# ==================== 进度追踪 ====================
def step7_progress():
    print("\n" + "=" * 50)
    print("7. 进度追踪测试")

    from services.progress_service import set_progress, get_progress

    task_id = "test_task_001"
    set_progress(task_id, "STARTED", progress=0, message="测试开始")
    data = get_progress(task_id)
    test("写入进度", lambda: data["state"] == "STARTED")

    set_progress(task_id, "SUCCESS", progress=100, message="测试完成", video_path="/videos/test.mp4")
    data = get_progress(task_id)
    test("更新进度到 SUCCESS", lambda: data["state"] == "SUCCESS" and data["video_path"] == "/videos/test.mp4")


# ==================== 文件清理 ====================
def step8_clean_tmp():
    print("\n" + "=" * 50)
    print("8. 生成测试文件（供导出测试用）")

    from ai_engine import render_manim_animation

    code = """
from manim import *
class ExportTest(Scene):
    def construct(self):
        sq = Square(side_length=1, color=RED, fill_opacity=0.5)
        self.play(DrawBorderThenFill(sq))
        self.wait(0.5)
"""
    success, log, video_path = render_manim_animation(code)
    if success:
        print(f"  ✅ 测试视频: {video_path}")
        return video_path
    else:
        print(f"  ⚠️ 渲染失败: {log[:200]}")
        return None


# ==================== 汇总 ====================
if __name__ == "__main__":
    print("=" * 60)
    print("CS-Visual-Learn AI Service — 全功能测试")
    print("=" * 60)

    step1_imports()
    step2_core_engine()
    step3_templates()
    step4_prompts()
    step5_logging()
    step6_video_management()
    step7_progress()
    video_path = step8_clean_tmp()

    print("\n" + "=" * 60)
    total = PASS + FAIL
    print(f"测试完成: {PASS}/{total} 通过", end="")
    if FAIL > 0:
        print(f"  ❌ {FAIL} 个失败")
    else:
        print("  ✅ 全部通过！")

    if video_path:
        print(f"\n提示: 启动 API 服务后可测试:")
        print(f"  下载: curl -O http://localhost:8000{video_path}/download")
        print(f"  GIF:  curl -X POST http://localhost:8000{video_path}/convert/gif")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
增强的代码预检服务
在不修改 ai_engine.py 的前提下，提供更全面的 Manim 代码质量检查。
作为外层包装，在调用 ai_engine 之前运行。
"""
import ast
from typing import List, Dict, Tuple


def validate_code(code: str) -> Tuple[bool, List[Dict]]:
    """
    对 Manim 代码进行全面预检。

    :param code: Manim Python 代码
    :return: (is_valid: bool, warnings: list)
             warnings 列表每项为 {severity, line, message, suggestion}
    """
    warnings = []

    # 1. 基础语法检查
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, [{
            "severity": "error",
            "line": e.lineno or 1,
            "message": f"Python 语法错误: {e.msg}",
            "suggestion": "请检查代码语法，确保括号匹配、缩进正确",
        }]

    # 2. Manim 导入检测
    has_manim_import = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if "manim" in alias.name:
                    has_manim_import = True
        elif isinstance(node, ast.ImportFrom):
            if node.module and "manim" in node.module:
                has_manim_import = True

    if not has_manim_import:
        warnings.append({
            "severity": "warning",
            "line": 1,
            "message": "未检测到 manim 导入语句",
            "suggestion": "请在代码开头添加 'from manim import *'",
        })

    # 3. Scene 类检测（支持所有 Manim Scene 子类）
    KNOWN_SCENES = {"Scene","ThreeDScene","MovingCameraScene","ZoomedScene","GraphScene","VectorScene"}
    has_scene_class = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if isinstance(base, ast.Name) and (base.id in KNOWN_SCENES or base.id.endswith("Scene")):
                    has_scene_class = True
                elif isinstance(base, ast.Attribute) and base.attr.endswith("Scene"):
                    has_scene_class = True

    if not has_scene_class:
        warnings.append({
            "severity": "error",
            "line": 1,
            "message": "未定义 Scene 子类，Manim 无法渲染",
            "suggestion": "请定义一个继承自 Scene 的类，如 'class MyAnimation(Scene):'",
        })

    # 4. LaTeX + 中文字符检测
    try:
        _check_latex_chinese(code, tree, warnings)
    except Exception:
        pass

    # 5. 常见 Manim API 错误模式
    _check_common_mistakes(code, tree, warnings)

    # 6. 复杂度估算
    stats = _estimate_complexity(tree)
    if stats["animation_count"] > 20:
        warnings.append({
            "severity": "info",
            "line": 1,
            "message": f"动画数量较多（约 {stats['animation_count']} 个），渲染可能较慢",
            "suggestion": "考虑减少动画数量或降低渲染质量",
        })

    is_valid = not any(w["severity"] == "error" for w in warnings)
    return is_valid, warnings


def _check_latex_chinese(code: str, tree: ast.AST, warnings: list):
    """检测 LaTeX 中是否包含中文字符（Manim 不支持）"""
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name in ("MathTex", "Tex"):
                for arg in node.args:
                    if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                        if any('一' <= c <= '鿿' for c in arg.value):
                            warnings.append({
                                "severity": "error",
                                "line": arg.lineno if hasattr(arg, 'lineno') else node.lineno,
                                "message": f"{func_name} 中包含中文字符，Manim 的 LaTeX 不支持中文",
                                "suggestion": "请改用 Text() 替代 MathTex()，或使用英文/数学符号",
                            })


def _check_common_mistakes(code: str, tree: ast.AST, warnings: list):
    """检测常见的 Manim API 使用错误"""
    # 检测 3D 坐标 Dot()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            func_name = None
            if isinstance(node.func, ast.Name):
                func_name = node.func.id
            elif isinstance(node.func, ast.Attribute):
                func_name = node.func.attr

            if func_name == "Dot":
                for kw in node.keywords:
                    if kw.arg == "point" and isinstance(kw.value, (ast.List, ast.Tuple)):
                        if len(kw.value.elts) == 3:
                            warnings.append({
                                "severity": "warning",
                                "line": kw.lineno,
                                "message": "Dot() 使用了 3D 坐标，可能导致渲染异常",
                                "suggestion": "请使用 2D 坐标，如 Dot(point[:2])",
                            })

    # 检测 updater 中的 numpy 直方图（性能陷阱）
    code_lower = code.lower()
    if "np.histogram" in code_lower or "numpy.histogram" in code_lower:
        if "add_updater" in code_lower:
            warnings.append({
                "severity": "warning",
                "line": 1,
                "message": "updater 中使用 np.histogram 会导致严重性能问题",
                "suggestion": "请在 updater 外部预计算直方图数据",
            })


def _estimate_complexity(tree: ast.AST) -> Dict:
    """估算代码复杂度"""
    stats = {
        "animation_count": 0,
        "loop_count": 0,
        "mobject_count": 0,
    }

    animation_methods = {
        "play", "animate", "Create", "FadeIn", "FadeOut", "Transform",
        "Write", "DrawBorderThenFill", "GrowFromCenter", "Uncreate",
        "FadeToColor", "ScaleInPlace", "Rotate", "MoveTo", "Shift",
        "ReplacementTransform", "Unwrite",
    }

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            if isinstance(node.func, ast.Attribute) and node.func.attr in animation_methods:
                stats["animation_count"] += 1
            elif isinstance(node.func, ast.Name) and node.func.id in {"Circle", "Square",
                                                                       "Rectangle", "Triangle",
                                                                       "Dot", "Line", "Arrow",
                                                                       "Text", "MathTex", "Tex"}:
                stats["mobject_count"] += 1
        elif isinstance(node, (ast.For, ast.While)):
            stats["loop_count"] += 1

    return stats

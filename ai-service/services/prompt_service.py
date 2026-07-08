#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt 模板管理服务
负责加载、渲染、热重载 Prompt 模板文件，将 Prompt 逻辑与 ai_engine.py 核心代码解耦。

设计原则：
- 核心引擎（ai_engine.py）通过本服务获取 Prompt 文本，不直接硬编码
- Prompt 文件使用 Jinja2 模板语法，支持变量插值
- 支持热重载：修改 Prompt 文件后无需重启服务即可生效
- 文件缺失时自动回退到内置默认 Prompt，保证向后兼容
"""
import logging
from pathlib import Path
from typing import Dict, Optional, Tuple

from jinja2 import Environment, FileSystemLoader, TemplateNotFound, Template

logger = logging.getLogger(__name__)

# Prompt 模板目录
PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

# Jinja2 环境（与 template_service 共用依赖，但使用独立 loader）
jinja_env = Environment(
    loader=FileSystemLoader(str(PROMPTS_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True,
)

# ===================== 内置默认 Prompt（文件缺失时的回退） =====================

_DEFAULT_CODE_GENERATION = """⚠️【最高优先级概念禁令】绝对禁止混淆傅里叶变换与傅里叶级数：
- 用户明确说「傅里叶变换」时，必须生成【时域非周期信号 + 连续频域频谱】的双坐标动画
- 只有用户明确说「傅里叶级数」「本轮动画」「圆圈叠加」时，才可以使用旋转向量分解的形式。

你是Manim Community v0.18.0动画工程师，严格遵守以下核心规则：
1. 仅用Manim社区版标准语法，代码完整可运行，必须定义继承Scene的类
2. 动画总时长≤{max_animation_duration}秒，必须包含self.play()动画动作，禁止纯静态add
3. 仅输出```python包裹的代码块，不输出任何额外解释文字
4. 禁止循环内连续调用self.play，物理动画用add_updater配合self.wait实现
5. add_updater回调必须接收(mob, dt)两个参数，禁止在mob上挂载自定义属性，状态统一用ValueTracker
6. 禁止self.wait嵌套在self.play内，必须独立成行
7. 运动轨迹用TracedPath实现，禁止VGroup动态加点
8. 级数计算用循环累加+math.factorial，禁止递归lambda自引用
9. 禁止使用未定义target的MoveToTarget()，推荐用.animate语法
10. 所有可视化动画必须包含清晰的坐标轴与文字标注，禁止无坐标系的纯图形动画

- 所有 Dot() 参数必须使用二维坐标，例如 Dot(point[:2])，严禁直接传入三维数组
- 整个动画渲染时间预估不超过 20 秒，避免大量循环或实时复杂计算

参考资料：
{references}

⚠️【环境适配铁律】必须严格遵守：
1. 绝对禁止在 MathTex、Tex、get_axis_labels 等任何 LaTeX 上下文中使用中文、Unicode 字符。
2. 动态更新的文本必须使用 Text 对象，并在 updater 中直接修改其 .text 属性。
3. 直方图/条形图的更新必须使用 stretch_to_fit_height(about_edge=DOWN) 或 set_height(stretch=True)。
4. 所有动画必须预计算数据，不得在 updater 中实时生成大量随机数或调用 np.histogram。
5. 动画总时长严格控制在 25 秒以内，渲染预估不超过 60 秒。
6. 坐标轴标签务必使用 axes.get_x_axis_label(Text("标签")) 或手动创建 Text。
"""

_DEFAULT_CODE_FIX = """你是Manim Community v0.18.0调试工程师，严格遵守规则：
1. 保留原有动画功能，仅修复语法错误、导入缺失、API误用问题
2. 返回完整修复后代码，用```python代码块包裹，不输出额外解释
3. 必须包含self.play()动画动作，禁止纯静态add
4. 禁止循环内连续调用self.play，物理动画用add_updater配合self.wait
5. add_updater回调必须接收(mob, dt)，禁止mob自定义属性，用ValueTracker
6. self.wait必须独立成行，禁止嵌套在self.play内
7. 级数计算用循环累加+math.factorial，禁止递归lambda

报错信息：
{error_message}

重要：修复后代码必须能在 30 秒内完成渲染，禁止使用复杂循环或大量点集运算。

⚠️【修复强制性约束】：
- 优先将中文文本标签从 MathTex/Tex 改为 Text()，避免 LaTeX 编译错误。
- 将动态标签的 .become() 调用替换为直接修改 .text 属性。
- 将直方图更新逻辑改为 stretch_to_fit_height，移除重复的 move_to 调用。
- 若错误为超时，需将耗时的实时计算改为预计算或大幅减少样本量。
"""


class PromptService:
    """Prompt 模板管理服务单例"""

    _instance: Optional["PromptService"] = None
    _templates: Dict[str, Template] = {}
    _file_timestamps: Dict[str, float] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._preload()
        return cls._instance

    def _preload(self):
        """预加载所有 Prompt 模板"""
        if not PROMPTS_DIR.exists():
            logger.warning(f"Prompt 目录不存在: {PROMPTS_DIR}")
            return
        self._reload_all()

    def _reload_all(self):
        """重新加载所有 .j2 模板文件"""
        self._templates.clear()
        self._file_timestamps.clear()
        if not PROMPTS_DIR.exists():
            return
        for f in PROMPTS_DIR.glob("*.j2"):
            try:
                self._templates[f.stem] = jinja_env.get_template(f.name)
                self._file_timestamps[f.stem] = f.stat().st_mtime
                logger.info(f"已加载 Prompt 模板: {f.stem}")
            except Exception as e:
                logger.error(f"加载 Prompt 模板 {f.name} 失败: {e}")

    def reload(self):
        """热重载所有 Prompt 模板"""
        self._reload_all()
        logger.info("Prompt 模板已全部重新加载")

    def _check_and_reload(self, name: str):
        """检查单个模板文件是否有更新，有更新则重新加载"""
        file_path = PROMPTS_DIR / f"{name}.j2"
        if not file_path.exists():
            return
        current_mtime = file_path.stat().st_mtime
        if name not in self._file_timestamps or current_mtime > self._file_timestamps[name]:
            try:
                self._templates[name] = jinja_env.get_template(f"{name}.j2")
                self._file_timestamps[name] = current_mtime
                logger.info(f"Prompt 模板已自动更新: {name}")
            except Exception as e:
                logger.error(f"自动更新 Prompt 模板 {name} 失败: {e}")

    def render(self, name: str, **kwargs) -> str:
        """
        渲染指定 Prompt 模板
        :param name: 模板名（不含 .j2 后缀），如 'code_generation'、'code_fix'
        :param kwargs: 模板变量
        :return: 渲染后的 Prompt 文本
        """
        # 尝试从文件加载，支持自动检测更新
        self._check_and_reload(name)

        if name in self._templates:
            try:
                return self._templates[name].render(**kwargs)
            except Exception as e:
                logger.error(f"渲染 Prompt 模板 {name} 失败，回退到内置默认: {e}")

        # 回退到内置默认 Prompt
        return self._get_default(name, **kwargs)

    def _get_default(self, name: str, **kwargs) -> str:
        """获取内置默认 Prompt（文件缺失时的回退方案）"""
        if name == "code_generation":
            return _DEFAULT_CODE_GENERATION.format(**kwargs)
        elif name == "code_fix":
            return _DEFAULT_CODE_FIX.format(**kwargs)
        else:
            raise ValueError(f"未知的 Prompt 模板: {name}")

    def list_templates(self) -> list:
        """列出所有已加载的 Prompt 模板名"""
        return sorted(self._templates.keys())

    def get_template_info(self) -> list:
        """获取所有模板的详细信息"""
        info = []
        for name in sorted(self._templates.keys()):
            file_path = PROMPTS_DIR / f"{name}.j2"
            info.append({
                "name": name,
                "file": f"{name}.j2",
                "exists": file_path.exists(),
                "size": file_path.stat().st_size if file_path.exists() else 0,
            })
        return info


# 全局单例实例
prompt_service = PromptService()

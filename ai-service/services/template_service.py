#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数模板引擎服务
零代码创作核心：加载官方模板、参数校验、占位符替换生成可渲染Manim代码
注意：本文件为外层服务，不修改ai_engine.py核心代码
"""
import json
from pathlib import Path
from typing import List, Dict, Tuple, Any
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

# 模板根目录
TEMPLATES_DIR = Path(__file__).resolve().parent.parent / "templates"

# Jinja2环境初始化
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATES_DIR)),
    autoescape=False,
    trim_blocks=True,
    lstrip_blocks=True
)


class TemplateInfo:
    """模板元信息"""
    def __init__(self, template_id: str, meta: dict):
        self.id = template_id
        self.name = meta.get("name", "")
        self.description = meta.get("description", "")
        self.category = meta.get("category", "其他")
        self.tags = meta.get("tags", [])
        self.difficulty = meta.get("difficulty", "入门")
        self.cover = meta.get("cover", "")
        self.params = meta.get("params", [])  # 参数列表：[{name, label, type, default, required, description, min, max, options}]
        self.use_count = meta.get("use_count", 0)

    def to_dict(self, include_params: bool = True) -> dict:
        data = {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "tags": self.tags,
            "difficulty": self.difficulty,
            "cover": self.cover,
            "use_count": self.use_count
        }
        if include_params:
            data["params"] = self.params
        return data


class TemplateService:
    """模板服务单例"""
    _instance = None
    _templates: Dict[str, TemplateInfo] = {}

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._load_templates()
        return cls._instance

    def _load_templates(self):
        """加载所有模板元信息"""
        self._templates.clear()
        if not TEMPLATES_DIR.exists():
            TEMPLATES_DIR.mkdir(parents=True, exist_ok=True)
            return

        for template_dir in TEMPLATES_DIR.iterdir():
            if not template_dir.is_dir():
                continue
            meta_file = template_dir / "meta.json"
            if not meta_file.exists():
                continue
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                template_id = template_dir.name
                self._templates[template_id] = TemplateInfo(template_id, meta)
            except Exception as e:
                print(f"⚠️ 加载模板 {template_dir.name} 失败：{str(e)}")

    def reload_templates(self):
        """重新加载所有模板（热更新用）"""
        self._load_templates()

    def _refresh_use_counts(self):
        """从磁盘重新同步 use_count（跨进程可见：Celery 写入 → FastAPI 可读，反之亦然）"""
        for template_id, tpl_info in self._templates.items():
            try:
                meta_file = TEMPLATES_DIR / template_id / "meta.json"
                if meta_file.exists():
                    meta = json.loads(meta_file.read_text(encoding="utf-8"))
                    tpl_info.use_count = max(tpl_info.use_count, meta.get("use_count", 0))
            except Exception:
                pass

    def get_template_list(self, category: str = None) -> List[dict]:
        """获取模板列表，可按分类筛选"""
        self._refresh_use_counts()  # 同步 Celery 或其他进程的写入
        items = []
        for tpl in self._templates.values():
            if category and tpl.category != category:
                continue
            items.append(tpl.to_dict(include_params=False))
        # 按使用次数倒序
        items.sort(key=lambda x: x["use_count"], reverse=True)
        return items

    def get_template_detail(self, template_id: str) -> Tuple[bool, Any]:
        """获取模板详情"""
        if template_id not in self._templates:
            return False, f"模板 {template_id} 不存在"
        return True, self._templates[template_id].to_dict(include_params=True)

    def _increment_use_count(self, template_id: str):
        """递增模板使用次数并持久化到 meta.json"""
        if template_id not in self._templates:
            return
        tpl_info = self._templates[template_id]
        tpl_info.use_count += 1
        # 持久化到 meta.json（静默失败）
        try:
            meta_file = TEMPLATES_DIR / template_id / "meta.json"
            if meta_file.exists():
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                meta["use_count"] = tpl_info.use_count
                meta_file.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        except Exception:
            pass

    def render_template_code(self, template_id: str, params: dict) -> Tuple[bool, str]:
        """
        根据参数渲染模板代码，返回可直接渲染的Manim代码
        :param template_id: 模板ID
        :param params: 用户传入的参数字典
        :return: (是否成功, 代码/错误信息)
        """
        if template_id not in self._templates:
            return False, f"模板 {template_id} 不存在"

        tpl_info = self._templates[template_id]
        # 参数校验与默认值填充
        processed_params = {}
        for param in tpl_info.params:
            param_name = param["name"]
            required = param.get("required", True)
            default = param.get("default", None)
            param_type = param.get("type", "string")

            if param_name not in params or params[param_name] is None:
                if required and default is None:
                    return False, f"缺少必填参数：{param.get('label', param_name)}"
                processed_params[param_name] = default
            else:
                value = params[param_name]
                # 类型转换
                try:
                    if param_type == "number":
                        value = float(value)
                        # 范围校验
                        if "min" in param and value < param["min"]:
                            return False, f"参数 {param.get('label', param_name)} 不能小于 {param['min']}"
                        if "max" in param and value > param["max"]:
                            return False, f"参数 {param.get('label', param_name)} 不能大于 {param['max']}"
                    elif param_type == "integer":
                        value = int(value)
                        if "min" in param and value < param["min"]:
                            return False, f"参数 {param.get('label', param_name)} 不能小于 {param['min']}"
                        if "max" in param and value > param["max"]:
                            return False, f"参数 {param.get('label', param_name)} 不能大于 {param['max']}"
                    elif param_type == "boolean":
                        value = bool(value)
                    elif param_type == "select":
                        options = param.get("options", [])
                        if options and value not in [opt["value"] for opt in options]:
                            return False, f"参数 {param.get('label', param_name)} 取值不合法"
                except Exception as e:
                    return False, f"参数 {param.get('label', param_name)} 类型错误：{str(e)}"
                processed_params[param_name] = value

        # 渲染Jinja2模板
        try:
            template = jinja_env.get_template(f"{template_id}/template.py.j2")
            rendered_code = template.render(**processed_params)
            self._increment_use_count(template_id)
            return True, rendered_code
        except TemplateNotFound:
            return False, f"模板文件 {template_id}/template.py.j2 不存在"
        except Exception as e:
            return False, f"模板渲染失败：{str(e)}"

    def get_categories(self) -> List[str]:
        """获取所有模板分类"""
        categories = set()
        for tpl in self._templates.values():
            categories.add(tpl.category)
        return sorted(list(categories))


# 全局单例实例
template_service = TemplateService()

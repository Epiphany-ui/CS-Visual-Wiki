#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS Visual Wiki - AI 服务入口
直接复用 ai_engine 核心能力，外层封装 FastAPI 接口
"""
import os
import uuid
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

# 导入核心引擎（所有业务逻辑都在 ai_engine.py）
from ai_engine import (
    run_full_pipeline,
    generate_manim_code,
    render_manim_animation,
    fix_manim_code,
    rag_retrieve_references,
    VIDEO_OUTPUT_SUBDIR,
    CODE_OUTPUT_SUBDIR,
)

# 导入外层扩展服务（不修改核心引擎）
from services.template_service import template_service

# ===================== FastAPI 应用初始化 =====================
app = FastAPI(
    title="CS Visual Wiki AI Service",
    description="基于 DeepSeek + Manim 的可视化动画生成后端服务",
    version="0.1.0",
)

# CORS 跨域配置，适配前端开发
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载视频静态目录，前端可直接通过 URL 播放
app.mount("/videos", StaticFiles(directory=str(VIDEO_OUTPUT_SUBDIR)), name="videos")

# ===================== 请求响应模型 =====================
class GenerateRequest(BaseModel):
    """生成动画请求：输入需求描述，走完整流水线（生成→渲染→自动修复）"""
    requirement: str
    max_retry: int = 3
    context: Optional[str] = None  # 百科词条上下文，可选

class GenerateCodeRequest(BaseModel):
    """仅生成 Manim 代码，不渲染"""
    requirement: str
    context: Optional[str] = None

class RenderRequest(BaseModel):
    """提交已有代码进行渲染"""
    code: str

class FixCodeRequest(BaseModel):
    """AI 修复代码"""
    code: str
    error_message: str

class RetrieveRequest(BaseModel):
    """RAG 检索参考资料"""
    query: str
    top_k: int = 2

class TemplateGenerateCodeRequest(BaseModel):
    """模板生成代码请求"""
    template_id: str
    params: dict = {}

class TemplateRenderRequest(BaseModel):
    """模板渲染请求：生成代码+渲染视频"""
    template_id: str
    params: dict = {}

# ===================== 统一响应格式 =====================
def success_response(data: dict, message: str = "ok") -> dict:
    return {"code": 0, "message": message, "data": data}

def error_response(message: str, code: int = 1) -> dict:
    return {"code": code, "message": message, "data": None}

# ===================== 健康检查 =====================
@app.get("/health")
async def health_check():
    return success_response({"status": "running"}, "服务运行正常")

# ===================== 核心接口：完整流水线 =====================
@app.post("/api/generate")
async def api_generate_animation(req: GenerateRequest):
    """
    完整流水线：输入知识点描述 → AI 生成代码 → 自动渲染 → 失败自动修复重试
    返回生成的代码、视频地址、尝试次数、日志
    """
    try:
        result = run_full_pipeline(req.requirement, max_retry=req.max_retry)
        return success_response(result, "任务执行完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 拆分接口：仅生成代码 =====================
@app.post("/api/ai/generate-code")
async def api_generate_code(req: GenerateCodeRequest):
    """只生成 Manim 代码，不执行渲染"""
    try:
        success, result = generate_manim_code(req.requirement)
        if not success:
            return error_response(result)
        return success_response({"code": result}, "代码生成成功")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 拆分接口：仅渲染代码 =====================
@app.post("/api/render")
async def api_render_code(req: RenderRequest):
    """传入 Manim 代码，执行渲染，返回视频地址"""
    try:
        success, log, video_path = render_manim_animation(req.code)
        data = {
            "success": success,
            "log": log,
            "video_path": video_path,
        }
        return success_response(data, "渲染任务执行完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 拆分接口：AI 修复代码 =====================
@app.post("/api/ai/fix-code")
async def api_fix_code(req: FixCodeRequest):
    """根据报错信息，AI 自动修复代码"""
    try:
        success, result = fix_manim_code(req.code, req.error_message)
        if not success:
            return error_response(result)
        return success_response({"code": result}, "代码修复完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 拆分接口：RAG 检索参考 =====================
@app.post("/api/rag/retrieve")
async def api_rag_retrieve(req: RetrieveRequest):
    """向量检索相关知识库参考资料"""
    try:
        references = rag_retrieve_references(req.query)
        return success_response({"references": references}, "检索完成")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===================== 百科词条接口 =====================
WIKI_DATA_DIR = Path(__file__).resolve().parent / "wiki_data"


def _parse_wiki_meta(file_path: Path) -> dict:
    """轻量解析词条 meta 信息（只解析头部，不读全文）"""
    meta = {
        "slug": file_path.stem,
        "title": file_path.stem,
        "category": "未分类",
        "tags": "",
        "difficulty": "未知",
    }
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            head = f.read(1024)  # 只读前 1KB 足够解析 meta
        if head.startswith("<!-- meta"):
            end_idx = head.find("-->")
            if end_idx != -1:
                for line in head[len("<!-- meta"):end_idx].strip().split("\n"):
                    line = line.strip()
                    if ":" in line:
                        key, value = line.split(":", 1)
                        key, value = key.strip(), value.strip()
                        if key in meta:
                            meta[key] = value
        # 从相对路径推断分类
        rel = file_path.relative_to(WIKI_DATA_DIR)
        if len(rel.parts) > 1:
            meta["category"] = rel.parts[0]
            meta["path"] = str(rel)
    except Exception:
        pass
    return meta


@app.get("/api/wiki/categories")
async def api_wiki_categories():
    """获取所有词条分类"""
    if not WIKI_DATA_DIR.exists():
        return success_response({"categories": []})
    categories = [d.name for d in WIKI_DATA_DIR.iterdir() if d.is_dir()]
    return success_response({"categories": sorted(categories)})


@app.get("/api/wiki/list")
async def api_wiki_list(category: Optional[str] = None):
    """获取词条列表，可按分类筛选"""
    if not WIKI_DATA_DIR.exists():
        return success_response({"items": [], "total": 0})

    md_files = list(WIKI_DATA_DIR.rglob("*.md"))
    items = []
    for f in md_files:
        meta = _parse_wiki_meta(f)
        if category and meta["category"] != category:
            continue
        items.append(meta)

    items.sort(key=lambda x: x["title"])
    return success_response({"items": items, "total": len(items)})


@app.get("/api/wiki/search")
async def api_wiki_search(q: str, limit: int = 10):
    """关键词搜索词条（标题匹配）"""
    if not WIKI_DATA_DIR.exists() or not q:
        return success_response({"items": [], "total": 0})

    q_lower = q.lower()
    md_files = list(WIKI_DATA_DIR.rglob("*.md"))
    items = []
    for f in md_files:
        meta = _parse_wiki_meta(f)
        # 标题或标签包含关键词就匹配
        if q_lower in meta["title"].lower() or q_lower in meta.get("tags", "").lower():
            items.append(meta)
        if len(items) >= limit:
            break

    return success_response({"items": items, "total": len(items), "keyword": q})


@app.get("/api/wiki/{slug}")
async def api_wiki_detail(slug: str):
    """获取单个词条详情（完整 Markdown 内容）"""
    if not WIKI_DATA_DIR.exists():
        raise HTTPException(status_code=404, detail="词条目录不存在")

    # 递归查找匹配的 md 文件
    matched = list(WIKI_DATA_DIR.rglob(f"{slug}.md"))
    if not matched:
        raise HTTPException(status_code=404, detail=f"词条 {slug} 不存在")

    file_path = matched[0]
    meta = _parse_wiki_meta(file_path)
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 去掉 meta 块，只返回正文
    if content.startswith("<!-- meta"):
        end_idx = content.find("-->")
        if end_idx != -1:
            content = content[end_idx + 3:].strip()

    return success_response({
        "slug": slug,
        "meta": meta,
        "content": content,
    })

# ===================== 模板相关接口（零代码创作） =====================
@app.get("/api/templates/categories")
async def api_template_categories():
    """获取所有模板分类"""
    categories = template_service.get_categories()
    return success_response({"categories": categories})


@app.get("/api/templates/list")
async def api_template_list(category: Optional[str] = None):
    """获取模板列表，可按分类筛选"""
    items = template_service.get_template_list(category=category)
    return success_response({"items": items, "total": len(items)})


@app.get("/api/templates/{template_id}")
async def api_template_detail(template_id: str):
    """获取模板详情（包含参数说明）"""
    success, data = template_service.get_template_detail(template_id)
    if not success:
        return error_response(data)
    return success_response(data)


@app.post("/api/templates/generate-code")
async def api_template_generate_code(req: TemplateGenerateCodeRequest):
    """根据模板参数生成Manim代码，不执行渲染"""
    success, result = template_service.render_template_code(req.template_id, req.params)
    if not success:
        return error_response(result)
    return success_response({"code": result}, "代码生成成功")


@app.post("/api/templates/render")
async def api_template_render(req: TemplateRenderRequest):
    """根据模板参数生成代码并直接渲染视频（零代码入口）"""
    # 1. 模板渲染生成代码
    gen_success, code = template_service.render_template_code(req.template_id, req.params)
    if not gen_success:
        return error_response(f"模板生成代码失败：{code}")
    # 2. 调用核心引擎渲染
    render_success, log, video_path = render_manim_animation(code)
    data = {
        "success": render_success,
        "code": code,
        "log": log,
        "video_path": video_path,
    }
    return success_response(data, "渲染完成" if render_success else "渲染失败")


@app.post("/api/templates/reload")
async def api_template_reload():
    """开发用：热重载所有模板，无需重启服务"""
    template_service.reload_templates()
    return success_response(None, "模板重载完成")

# ===================== 启动入口 =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

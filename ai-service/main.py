#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS Visual Learn - AI 服务入口
直接复用 ai_engine 核心能力，外层封装 FastAPI 接口
"""
import os
import uuid
from pathlib import Path
from typing import Optional

import asyncio
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse

from services.logging_config import setup_logging, get_logger

# 初始化日志（在所有导入之后，确保所有模块受益）
setup_logging()
logger = get_logger("main")
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
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
from services.prompt_service import prompt_service
from services.progress_service import get_progress, subscribe_progress, unsubscribe_progress, list_videos, delete_video

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

# 全局词条索引（标题→slug），用于自动生成超链接和相关推荐
_wiki_title_index: dict = {}
_index_loaded: bool = False


def _load_wiki_index():
    """构建全局词条索引：{标题: slug} + {slug: meta}"""
    global _wiki_title_index, _index_loaded
    if _index_loaded:
        return
    if not WIKI_DATA_DIR.exists():
        _index_loaded = True
        return
    for f in WIKI_DATA_DIR.rglob("*.md"):
        meta = _parse_wiki_meta(f)
        title = meta.get("title", "")
        slug = meta.get("slug", "")
        if title and slug:
            _wiki_title_index[title] = slug
            # 也加入拼音/英文别名（从 tags 中提取）
            tags = meta.get("tags", "")
            for tag in tags.split(","):
                tag = tag.strip()
                if tag and tag != title:
                    _wiki_title_index[tag] = slug
    _index_loaded = True


def _auto_link_content(content: str, current_slug: str) -> str:
    """将正文中提到的其他词条标题自动替换为 Markdown 超链接"""
    _load_wiki_index()
    # 按标题长度降序排序，优先匹配长标题（避免 "排序" 误匹配 "快速排序"）
    titles = sorted(_wiki_title_index.keys(), key=len, reverse=True)
    for title in titles:
        target_slug = _wiki_title_index[title]
        if target_slug == current_slug:
            continue  # 不链接到自己
        if title in content:
            # 只在正文段落中替换，不在已有的链接或代码块中替换
            # 简单策略：替换第一个出现
            link = f"[{title}](/api/wiki/{target_slug})"
            content = content.replace(title, link, 1)  # 每篇最多链接一次
    return content


def _get_related_articles(current_slug: str, current_tags: str, limit: int = 5) -> list:
    """基于标签重叠获取相关词条推荐"""
    _load_wiki_index()
    if not current_tags:
        return []

    current_tag_set = set(t.strip().lower() for t in current_tags.split(",") if t.strip())
    scored = []

    for f in WIKI_DATA_DIR.rglob("*.md"):
        if f.stem == current_slug:
            continue
        meta = _parse_wiki_meta(f)
        other_tags = set(t.strip().lower() for t in meta.get("tags", "").split(",") if t.strip())
        overlap = len(current_tag_set & other_tags)
        if overlap > 0:
            scored.append((overlap, {
                "slug": meta["slug"],
                "title": meta["title"],
                "category": meta["category"],
                "difficulty": meta["difficulty"],
            }))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [item for _, item in scored[:limit]]


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
    """获取单个词条详情（含自动超链接 + 相关词条推荐）"""
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

    # 去掉 meta 块
    if content.startswith("<!-- meta"):
        end_idx = content.find("-->")
        if end_idx != -1:
            content = content[end_idx + 3:].strip()

    # 自动生成文中其他词条的超链接（Wikipedia 风格）
    content = _auto_link_content(content, slug)

    # 基于标签重叠获取相关词条推荐
    related = _get_related_articles(slug, meta.get("tags", ""))

    return success_response({
        "slug": slug,
        "meta": meta,
        "content": content,
        "related": related,
    })

@app.post("/api/wiki/reload-index")
async def api_wiki_reload_index():
    """重建词条索引（新增词条后调用，无需重启服务）"""
    global _index_loaded
    _wiki_title_index.clear()
    _index_loaded = False
    _load_wiki_index()
    return success_response({"index_size": len(_wiki_title_index)}, "索引已重建")


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


# ===================== Prompt 管理接口 =====================

@app.get("/api/prompts/list")
async def api_prompts_list():
    """获取所有可用的 Prompt 模板列表"""
    info = prompt_service.get_template_info()
    return success_response({"items": info, "total": len(info)})


@app.post("/api/prompts/reload")
async def api_prompts_reload():
    """开发用：热重载所有 Prompt 模板，修改 Prompt 文件后无需重启服务"""
    prompt_service.reload()
    return success_response(None, "Prompt 模板重载完成")


@app.get("/api/prompts/{name}")
async def api_prompts_detail(name: str):
    """查看指定 Prompt 模板的渲染预览（用于调试 Prompt 效果）"""
    try:
        # 渲染预览时使用占位变量
        preview_vars = {
            "code_generation": {"max_animation_duration": 30, "references": "（预览模式：无RAG参考资料）"},
            "code_fix": {"error_message": "（预览模式：模拟报错信息）"},
        }
        kwargs = preview_vars.get(name, {})
        content = prompt_service.render(name, **kwargs)
        return success_response({"name": name, "content": content})
    except ValueError as e:
        return error_response(str(e))


# ===================== 任务进度与视频管理接口 =====================

@app.get("/api/tasks/{task_id}")
async def api_task_status(task_id: str):
    """查询异步任务状态和结果"""
    progress = get_progress(task_id)
    # 如果 Redis 中找不到，尝试从 Celery 后端查询
    if progress.get("state") == "UNKNOWN":
        try:
            from workers.celery_app import celery_app
            result = celery_app.AsyncResult(task_id)
            if result:
                progress = {
                    "task_id": task_id,
                    "state": result.state,
                    "progress": 100 if result.state == "SUCCESS" else 0,
                    "message": "",
                    "video_path": result.result.get("video_path", "") if result.result and isinstance(result.result, dict) else "",
                    "log": result.result.get("log", "") if result.result and isinstance(result.result, dict) else "",
                }
        except Exception:
            pass
    return success_response(progress)


@app.get("/api/tasks/{task_id}/stream")
async def api_task_stream(task_id: str):
    """SSE 实时进度推送，前端可用 EventSource 连接"""
    async def event_generator():
        pubsub = None
        try:
            # 先发送当前状态
            current = get_progress(task_id)
            yield f"data: {json.dumps(current, ensure_ascii=False)}\n\n"

            # 如果任务已完成，直接结束
            if current.get("state") in ("SUCCESS", "FAILURE"):
                yield f"data: {json.dumps({'type': 'done', 'state': current.get('state')}, ensure_ascii=False)}\n\n"
                return

            # 订阅 Redis Pub/Sub，实时推送更新
            pubsub = subscribe_progress(task_id)
            while True:
                message = pubsub.get_message(timeout=30)
                if message and message["type"] == "message":
                    data = message["data"]
                    yield f"data: {data}\n\n"
                    # 检查是否是终态
                    try:
                        parsed = json.loads(data)
                        if parsed.get("state") in ("SUCCESS", "FAILURE"):
                            yield f"data: {json.dumps({'type': 'done', 'state': parsed.get('state')}, ensure_ascii=False)}\n\n"
                            break
                    except Exception:
                        pass
                await asyncio.sleep(0.5)
        except asyncio.CancelledError:
            pass
        finally:
            if pubsub:
                unsubscribe_progress(pubsub)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@app.get("/api/videos/list")
async def api_videos_list():
    """列出所有已生成的视频文件"""
    videos = list_videos()
    return success_response({"items": videos, "total": len(videos)})


@app.delete("/api/videos/{filename}")
async def api_videos_delete(filename: str):
    """删除指定视频及对应代码文件"""
    if not filename.endswith(".mp4"):
        return error_response("仅支持删除 .mp4 文件")
    if ".." in filename or "/" in filename or "\\" in filename:
        return error_response("非法文件名")
    deleted = delete_video(filename)
    if deleted:
        return success_response(None, f"已删除 {filename}")
    return error_response(f"文件 {filename} 不存在")


# ===================== 导出与下载 =====================

@app.get("/api/videos/{filename}/download")
async def api_videos_download(filename: str):
    """直接下载视频文件"""
    if not filename.endswith(".mp4"):
        return error_response("仅支持下载 .mp4 文件")
    if ".." in filename or "/" in filename or "\\" in filename:
        return error_response("非法文件名")

    video_path = VIDEO_OUTPUT_SUBDIR / filename
    if not video_path.exists():
        return error_response(f"视频 {filename} 不存在")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=filename,
    )


@app.post("/api/videos/{filename}/convert/gif")
async def api_videos_convert_gif(filename: str, fps: int = 10, width: int = 480):
    """将视频转换为 GIF（需要 ffmpeg）"""
    if not filename.endswith(".mp4"):
        return error_response("仅支持转换 .mp4 文件")
    if ".." in filename or "/" in filename or "\\" in filename:
        return error_response("非法文件名")

    video_path = VIDEO_OUTPUT_SUBDIR / filename
    if not video_path.exists():
        return error_response(f"视频 {filename} 不存在")

    gif_name = filename.replace(".mp4", ".gif")
    gif_path = VIDEO_OUTPUT_SUBDIR / gif_name

    try:
        import subprocess
        # ffmpeg -i input.mp4 -vf "fps=10,scale=480:-1" output.gif
        result = subprocess.run(
            [
                "ffmpeg", "-y",
                "-i", str(video_path),
                "-vf", f"fps={fps},scale={width}:-1:flags=lanczos",
                "-loop", "0",
                str(gif_path),
            ],
            capture_output=True, text=True, timeout=60,
            encoding="utf-8", errors="replace",
        )
        if result.returncode == 0 and gif_path.exists():
            size = round(gif_path.stat().st_size / 1024, 1)
            return success_response({
                "filename": gif_name,
                "url": f"/videos/{gif_name}",
                "size_kb": size,
            }, f"GIF 转换完成（{size}KB）")
        else:
            logger.error(f"GIF 转换失败: {result.stderr[:500]}")
            return error_response(f"GIF 转换失败: {result.stderr[:300]}")
    except FileNotFoundError:
        return error_response("未找到 ffmpeg，请先安装 ffmpeg")
    except subprocess.TimeoutExpired:
        return error_response("GIF 转换超时（60s）")


# ===================== 启动入口 =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CS Visual Learn - AI 服务入口 v1.0
直接复用 ai_engine 核心能力，外层封装 FastAPI 接口
"""
import asyncio
import json
import os
import threading
import uuid
import time as _time
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from services.logging_config import setup_logging, get_logger

# 初始化日志
setup_logging()
logger = get_logger("main")

# 导入核心引擎（所有业务逻辑都在 ai_engine.py）
from ai_engine import (
    run_full_pipeline,
    generate_manim_code,
    render_manim_animation,
    fix_manim_code,
    rag_retrieve_references,
    generate_video_poster,
    VIDEO_OUTPUT_SUBDIR,
    CODE_OUTPUT_SUBDIR,
)

# 导入外层扩展服务（不修改核心引擎）
from services.template_service import template_service
from services.prompt_service import prompt_service
from services.progress_service import (
    get_progress, set_progress, subscribe_progress, unsubscribe_progress,
    list_videos, delete_video, list_tasks, delete_task, get_task_count,
    save_to_gallery, is_in_gallery, get_gallery_filenames,
    save_video_meta, get_video_meta, get_all_video_metas, update_video_title,
    add_to_user_works, get_user_works, mark_task_cancelled,
)
from services.comment_service import (
    toggle_like, is_liked, get_like_counts, check_user_likes,
    increment_view, get_view_counts,
    add_comment, get_comments, get_comment_count, like_comment,
)
from services.config import settings
from services.exceptions import (
    AppException, TaskNotFoundError, RateLimitError, ValidationError,
)
from services.middleware import (
    RequestIDMiddleware, RequestLoggingMiddleware,
    ApiKeyMiddleware, RateLimitMiddleware,
)
from services.code_validator import validate_code

# ===================== FastAPI 应用初始化 =====================
app = FastAPI(
    title=settings.app_name,
    description="基于 DeepSeek + Manim 的可视化动画生成后端服务",
    version=settings.app_version,
)

# --- 中间件注册（顺序重要：先添加的后执行） ---
# 1. 请求追踪（最先注册，最后执行，确保所有响应都有 X-Request-ID）
app.add_middleware(RequestIDMiddleware)
# 2. 结构化请求日志
app.add_middleware(RequestLoggingMiddleware)
# 3. API Key 认证（安全层）
app.add_middleware(ApiKeyMiddleware)
# 4. 速率限制
app.add_middleware(RateLimitMiddleware)
# 5. CORS 跨域配置（可配置化）
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 全局异常处理 ---
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """统一处理应用异常，返回标准格式"""
    request_id = getattr(request.state, "request_id", "-")
    return JSONResponse(
        status_code=exc.status_code,
        content={"code": exc.code, "message": exc.message, "data": exc.data},
        headers={"X-Request-ID": request_id},
    )

# 挂载视频静态目录，前端可直接通过 URL 播放
app.mount("/videos", StaticFiles(directory=str(VIDEO_OUTPUT_SUBDIR)), name="videos")

# v1.0: 挂载帧缓存目录（逐帧调试功能）
FRAME_CACHE_DIR = Path(__file__).resolve().parent / "outputs" / "frames"
FRAME_CACHE_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/frames", StaticFiles(directory=str(FRAME_CACHE_DIR)), name="frames")

# 头像上传目录
AVATAR_DIR = Path(__file__).resolve().parent / "outputs" / "avatars"
AVATAR_DIR.mkdir(parents=True, exist_ok=True)
app.mount("/avatars", StaticFiles(directory=str(AVATAR_DIR)), name="avatars")

# 服务器启动时间
_START_TIME = _time.time()


# ===================== 启动事件：预热缓存 =====================
@app.on_event("startup")
async def startup_event():
    """服务启动时预加载 wiki 元数据缓存，避免第一个用户请求触发 111 次文件 I/O"""
    logger.info("[startup] 正在构建 wiki 元数据缓存...")
    _build_wiki_cache()
    _load_wiki_index()
    logger.info(
        "[startup] wiki 缓存就绪: %d 个词条, %d 个分类, %d 个索引条目",
        len(_wiki_meta_cache), len(_wiki_categories_cache), len(_wiki_title_index),
    )

    # 自动修复 Windows Redis 常见问题：
    # 1. RDB 目录无写权限 → 重定向到项目目录
    # 2. stop-writes-on-bgsave-error=yes → 持久化失败时拒绝写操作
    # 3. save 配置 → 确保自动持久化生效
    try:
        import redis as _redis_lib
        r = _redis_lib.Redis.from_url(settings.redis_url, decode_responses=True, socket_connect_timeout=3)
        _project_dir = str(Path(__file__).resolve().parent)
        r.config_set("dir", _project_dir)
        r.config_set("stop-writes-on-bgsave-error", "no")
        r.config_set("save", "")  # Windows 上禁用自动 BGSAVE（fork 会断连 Celery），改为手动触发
        try:
            r.config_rewrite()  # 持久化到 redis.conf，重启后生效
        except Exception:
            pass
        logger.info("[startup] Redis 配置已自动修复并持久化 (dir=%s)", _project_dir)
    except Exception as _e:
        logger.warning("[startup] 无法自动配置 Redis: %s（如 Redis 未安装请忽略）", _e)

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
    context: Optional[str] = None  # 原始需求描述，帮助 AI 理解用户意图

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
    """
    结构化健康检查：逐一验证所有依赖服务的连接状态。
    返回 healthy / degraded / unhealthy 三种状态。
    """
    checks = {}
    overall = "healthy"

    # 1. Redis 检测
    try:
        t0 = _time.time()
        from services.progress_service import _get_redis
        r = _get_redis()
        r.ping()
        checks["redis"] = {"status": "up", "latency_ms": round((_time.time() - t0) * 1000, 1)}
    except Exception as e:
        checks["redis"] = {"status": "down", "error": str(e)[:200]}
        overall = "degraded"

    # 2. ChromaDB 检测
    try:
        from ai_engine import kb_collection
        if kb_collection is not None:
            count = kb_collection.count()
            checks["chromadb"] = {"status": "up", "collection_count": count}
        else:
            checks["chromadb"] = {"status": "down", "error": "kb_collection 未初始化"}
            overall = "degraded"
    except Exception as e:
        checks["chromadb"] = {"status": "down", "error": str(e)[:200]}
        overall = "degraded"

    # 3. DeepSeek API 检测
    try:
        import requests as req_lib
        t0 = _time.time()
        resp = req_lib.get(
            "https://api.deepseek.com/v1/models",
            headers={"Authorization": f"Bearer {os.environ.get('DEEPSEEK_API_KEY', '')}"},
            timeout=5,
        )
        latency = round((_time.time() - t0) * 1000)
        if resp.status_code == 200:
            checks["deepseek_api"] = {"status": "up", "latency_ms": latency}
        else:
            checks["deepseek_api"] = {"status": "down", "status_code": resp.status_code}
            overall = "degraded"
    except Exception as e:
        checks["deepseek_api"] = {"status": "down", "error": str(e)[:200]}
        overall = "degraded"

    # 4. Celery Worker 检测
    try:
        from workers.celery_app import celery_app
        t0 = _time.time()
        result = celery_app.control.ping(timeout=3)
        worker_count = len([w for w in result if w])
        checks["celery"] = {
            "status": "up" if worker_count > 0 else "down",
            "worker_count": worker_count,
            "latency_ms": round((_time.time() - t0) * 1000, 1),
        }
        if worker_count == 0:
            overall = "degraded"
    except Exception as e:
        checks["celery"] = {"status": "unknown", "error": str(e)[:200]}

    # 5. Ollama 检测
    try:
        import requests as req_lib
        t0 = _time.time()
        ollama_url = settings.ollama_base_url
        resp = req_lib.get(f"{ollama_url}/api/tags", timeout=5)
        if resp.status_code == 200:
            checks["ollama"] = {"status": "up", "latency_ms": round((_time.time() - t0) * 1000, 1)}
        else:
            checks["ollama"] = {"status": "down", "status_code": resp.status_code}
    except Exception:
        checks["ollama"] = {"status": "down", "error": "无法连接到 Ollama"}
        # Ollama 不可用不影响核心功能，不降低整体状态

    # 6. 磁盘使用检测
    try:
        import shutil
        usage = shutil.disk_usage(VIDEO_OUTPUT_SUBDIR)
        percent = round(usage.used / usage.total * 100, 1)
        checks["disk"] = {"status": "ok" if percent < 90 else "warning", "used_percent": percent}
    except Exception:
        pass

    return JSONResponse(content={
        "code": 0,
        "message": "ok",
        "data": {
            "status": overall,
            "version": settings.app_version,
            "uptime_seconds": round(_time.time() - _START_TIME),
            "checks": checks,
        },
    })


# ===================== 兼容层：Java 后端调用 /generate 不带 /api 前缀 =====================
@app.post("/generate")
async def legacy_generate_animation(req: GenerateRequest):
    """
     [DEPRECATED] 兼容旧 Java 后端（TaskServiceImpl 调用 /generate 而非 /api/generate）
    请迁移到 POST /api/generate 或 POST /api/async/generate
    """
    return await api_generate_animation(req)

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
    """根据报错信息和原始需求，AI 自动修复代码"""
    try:
        success, result = fix_manim_code(req.code, req.error_message, req.context)
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

# ===================== 工具函数 =====================

def _is_safe_filename(filename: str) -> bool:
    """防止路径穿越攻击：文件名不得包含 .. 或路径分隔符"""
    return ".." not in filename and "/" not in filename and "\\" not in filename

# ===================== 百科词条接口 =====================
WIKI_DATA_DIR = Path(__file__).resolve().parent / "wiki_data"

# 全局词条索引（标题→slug），用于自动生成超链接和相关推荐
_wiki_title_index: dict = {}
_index_loaded: bool = False

# v1.0.1: 全量元数据缓存，避免每次请求扫描 111 个文件
_wiki_meta_cache: list = []        # 所有词条的 meta 列表（已排序）
_wiki_categories_cache: list = []  # 分类列表
_cache_loaded: bool = False
_wiki_cache_lock = threading.Lock()


def _build_wiki_cache():
    """一次性扫描 wiki_data 目录，构建全量元数据缓存。
    避免每个 /api/wiki/list 请求打开 111 个文件。
    线程安全：使用 Lock 防止并发构建。
    """
    global _wiki_meta_cache, _wiki_categories_cache, _cache_loaded
    if _cache_loaded:
        return
    with _wiki_cache_lock:
        if _cache_loaded:
            return
        if not WIKI_DATA_DIR.exists():
            _cache_loaded = True
            return

        categories_set = set()
        meta_list = []
        for f in WIKI_DATA_DIR.rglob("*.md"):
            meta = _parse_wiki_meta(f)
            meta_list.append(meta)
            categories_set.add(meta.get("category", "未分类"))

        meta_list.sort(key=lambda x: x.get("title", ""))
        _wiki_meta_cache = meta_list
        _wiki_categories_cache = sorted(categories_set)
        _cache_loaded = True


def _load_wiki_index():
    """构建全局词条索引：{标题: slug} + {slug: meta}"""
    global _wiki_title_index, _index_loaded
    if _index_loaded:
        return
    # 依赖缓存：确保 meta 缓存已构建（内部有锁）
    _build_wiki_cache()
    with _wiki_cache_lock:
        if _index_loaded:
            return
        if not WIKI_DATA_DIR.exists():
            _index_loaded = True
            return
        for meta in _wiki_meta_cache:
            title = meta.get("title", "")
            slug = meta.get("slug", "")
            if title and slug:
                _wiki_title_index[title] = slug
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
    """基于标签重叠获取相关词条推荐（从内存缓存读取）"""
    _load_wiki_index()
    _build_wiki_cache()
    if not current_tags:
        return []

    current_tag_set = set(t.strip().lower() for t in current_tags.split(",") if t.strip())
    scored = []

    for meta in _wiki_meta_cache:
        if meta.get("slug") == current_slug:
            continue
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
    """获取所有词条分类（从内存缓存读取，不触碰磁盘）"""
    _build_wiki_cache()
    return success_response({"categories": _wiki_categories_cache})


@app.get("/api/wiki/list")
async def api_wiki_list(category: Optional[str] = None):
    """获取词条列表，可按分类筛选（从内存缓存读取）"""
    _build_wiki_cache()

    if category:
        items = [m for m in _wiki_meta_cache if m.get("category") == category]
    else:
        items = list(_wiki_meta_cache)

    return success_response({"items": items, "total": len(items)})


@app.get("/api/wiki/search")
async def api_wiki_search(q: str, limit: int = 10):
    """关键词搜索词条（标题匹配，从内存缓存读取）"""
    _build_wiki_cache()
    if not q:
        return success_response({"items": [], "total": 0})

    q_lower = q.lower()
    items = []
    for meta in _wiki_meta_cache:
        # 标题或标签包含关键词就匹配
        if q_lower in meta.get("title", "").lower() or q_lower in meta.get("tags", "").lower():
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
    """重建词条索引 + 元数据缓存（新增词条后调用，无需重启服务）"""
    global _index_loaded, _cache_loaded
    _wiki_title_index.clear()
    _wiki_meta_cache.clear()
    _wiki_categories_cache.clear()
    _index_loaded = False
    _cache_loaded = False
    _build_wiki_cache()
    _load_wiki_index()
    return success_response({
        "index_size": len(_wiki_title_index),
        "cached_items": len(_wiki_meta_cache),
    }, "索引与缓存已重建")


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
async def api_videos_list(gallery: bool = False, my_works: bool = False, username: str = ""):
    """
    列出所有已生成的视频文件。
    ?gallery=true 时仅返回已收藏到画廊的视频。
    ?my_works=true&username=xxx 时仅返回该用户的作品（服务端持久化）。
    每条记录会合并视频元数据（标题等）。
    """
    videos = list_videos()
    metas = get_all_video_metas()
    # 合并元数据
    for v in videos:
        fn = v.get("filename", "")
        meta = metas.get(fn, {})
        v["title"] = (meta.get("title") or b"").decode("utf-8") if isinstance(meta.get("title"), bytes) else (meta.get("title") or fn)
        v["username"] = (meta.get("username") or b"").decode("utf-8") if isinstance(meta.get("username"), bytes) else (meta.get("username") or "匿名")
        v["created_by"] = v.get("username", "匿名")
    if gallery:
        saved = get_gallery_filenames(username)
        videos = [v for v in videos if v.get("filename") in saved]
    if my_works and username:
        # 优先用 Redis user-works set，fallback 到视频元数据 username 字段
        works = get_user_works(username)
        if works:
            videos = [v for v in videos if v.get("filename") in works]
        else:
            # user-works 为空时，直接按视频元数据的 username 过滤
            videos = [v for v in videos if v.get("username") == username or v.get("created_by") == username]
    return success_response({"items": videos, "total": len(videos)})


@app.post("/api/videos/{filename}/save")
async def api_videos_save(filename: str, username: str = ""):
    """
    Toggle 画廊收藏：已收藏则取消，未收藏则添加。
    同时加入用户作品列表（服务端持久化）。
    返回 {saved: true/false}。
    """
    if not _is_safe_filename(filename):
        return error_response("非法文件名")
    saved = save_to_gallery(filename, username)
    # 同步到用户作品列表
    if saved and username:
        add_to_user_works(username, filename)
    return success_response({"filename": filename, "saved": saved}, "已收藏" if saved else "已取消收藏")


@app.post("/api/user/works/sync")
async def api_user_works_sync(username: str = "", works: str = ""):
    """
    将前端的本地作品列表同步到服务端 Redis。
    POST body: { username: "xxx", works: "file1.mp4,file2.mp4" }
    """
    if not username:
        return error_response("用户名不能为空")
    filenames = [f.strip() for f in works.split(",") if f.strip().endswith(".mp4")]
    for fn in filenames:
        add_to_user_works(username, fn)
    server_works = get_user_works(username)
    return success_response({
        "username": username,
        "synced_count": len(filenames),
        "total": len(server_works),
    }, "同步完成")


@app.patch("/api/videos/{filename}/title")
async def api_videos_rename(filename: str, title: str = ""):
    """修改视频标题（用户自定义命名）"""
    if not _is_safe_filename(filename):
        return error_response("非法文件名")
    if not title or not title.strip():
        return error_response("标题不能为空")
    ok = update_video_title(filename, title.strip())
    return success_response({"filename": filename, "title": title.strip()}, "标题已更新" if ok else "更新失败")


@app.delete("/api/videos/{filename}")
async def api_videos_delete(filename: str):
    """删除指定视频及对应代码文件"""
    if not filename.endswith(".mp4"):
        return error_response("仅支持删除 .mp4 文件")
    if not _is_safe_filename(filename):
        return error_response("非法文件名")
    deleted = delete_video(filename)
    if deleted:
        return success_response(None, f"已删除 {filename}")
    return error_response(f"文件 {filename} 不存在")


# ===================== v1.0 异步任务端点（Celery 驱动） =====================

class AsyncGenerateRequest(BaseModel):
    """异步生成请求"""
    requirement: str
    max_retry: int = 3
    context: Optional[str] = None
    quality: Optional[str] = None  # -ql(480p) / -qm(720p) / -qh(1080p)
    username: Optional[str] = None  # 视频所有者（用于"我的作品"）


class AsyncRenderRequest(BaseModel):
    """异步渲染请求"""
    code: str
    quality: Optional[str] = None
    username: Optional[str] = None


@app.post("/api/user/avatar")
async def api_upload_avatar(file: UploadFile = File(...)):
    """上传用户头像，返回可访问的 URL"""
    ALLOWED_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
    if file.content_type not in ALLOWED_TYPES:
        return error_response("仅支持 JPG/PNG/GIF/WebP 格式")
    # 限制 2MB
    contents = await file.read()
    if len(contents) > 2 * 1024 * 1024:
        return error_response("头像文件不能超过 2MB")
    # 用时间戳 + 原始扩展名生成文件名
    ext = file.filename.split(".")[-1] if "." in (file.filename or "") else "png"
    safe_ext = ext if ext.lower() in ("jpg", "jpeg", "png", "gif", "webp") else "png"
    avatar_name = f"avatar_{int(_time.time())}_{uuid.uuid4().hex[:6]}.{safe_ext}"
    avatar_path = AVATAR_DIR / avatar_name
    with open(avatar_path, "wb") as f:
        f.write(contents)
    url = f"/avatars/{avatar_name}"
    return success_response({"url": url}, "头像上传成功")


class AsyncTemplateRequest(BaseModel):
    """异步模板渲染请求"""
    template_id: str
    params: dict = {}
    quality: Optional[str] = None


@app.post("/api/async/generate")
async def api_async_generate(req: AsyncGenerateRequest):
    """
     异步全流程生成：提交需求 → 立即返回 task_id → Celery Worker 后台处理。
    前端通过 GET /api/tasks/{task_id}/stream (SSE) 获取实时进度。
    """
    try:
        from workers.celery_app import generate_full_task
        task = generate_full_task.delay(req.requirement, req.max_retry, req.quality, req.username)
        logger.info("[async] generate task dispatched: %s", task.id)
        return success_response({"task_id": task.id}, "任务已提交")
    except Exception as e:
        logger.error("[async] generate dispatch failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/async/render")
async def api_async_render(req: AsyncRenderRequest):
    """
     异步纯渲染：提交代码 → 立即返回 task_id。
    """
    # 渲染前进行代码预检
    is_valid, warnings_list = validate_code(req.code)
    if not is_valid:
        errors = [w for w in warnings_list if w["severity"] == "error"]
        return error_response(f"代码预检失败: {errors[0]['message']}" if errors else "代码校验未通过")

    try:
        from workers.celery_app import render_code_task
        task = render_code_task.delay(req.code, req.quality, req.username)
        logger.info("[async] render task dispatched: %s", task.id)
        return success_response({
            "task_id": task.id,
            "warnings": [w for w in warnings_list if w["severity"] != "error"],
        }, "渲染任务已提交")
    except Exception as e:
        logger.error("[async] render dispatch failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/async/template-render")
async def api_async_template_render(req: AsyncTemplateRequest):
    """
     异步模板渲染：提交模板ID+参数 → 立即返回 task_id。
    """
    try:
        from workers.celery_app import render_template_task
        task = render_template_task.delay(req.template_id, req.params, req.quality)
        logger.info("[async] template task dispatched: %s (template=%s)", task.id, req.template_id)
        return success_response({"task_id": task.id}, "模板渲染任务已提交")
    except Exception as e:
        logger.error("[async] template dispatch failed: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


# ===================== v1.0 任务队列管理 =====================

@app.get("/api/tasks")
async def api_tasks_list(
    state: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
):
    """
    列出所有任务（支持按状态筛选和分页）。
    任务数据来源于 Redis cs:task:* 键。
    """
    try:
        result = list_tasks(state_filter=state, page=page, page_size=page_size)
        return success_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/tasks/{task_id}")
async def api_task_cancel(task_id: str):
    """
    取消/删除一个任务。
    调用 Celery revoke 并清理 Redis 进度数据。
    """
    try:
        existed = delete_task(task_id)
        if existed:
            return success_response(None, f"任务 {task_id} 已取消")
        else:
            raise TaskNotFoundError(task_id)
    except AppException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== 任务进度查询（已有端点，增强） =====================

@app.get("/api/videos/{filename}/download")
async def api_videos_download(filename: str):
    """直接下载视频文件"""
    if not filename.endswith(".mp4"):
        return error_response("仅支持下载 .mp4 文件")
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    video_path = VIDEO_OUTPUT_SUBDIR / filename
    if not video_path.exists():
        return error_response(f"视频 {filename} 不存在")

    return FileResponse(
        path=str(video_path),
        media_type="video/mp4",
        filename=filename,
    )


@app.get("/api/videos/{filename}/thumbnail")
async def api_videos_thumbnail(filename: str):
    """获取视频缩略图（不存在则用 ffmpeg 懒生成并缓存为 .jpg）"""
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    stem = Path(filename).stem
    poster_file = VIDEO_OUTPUT_SUBDIR / f"{stem}.jpg"
    video_file = VIDEO_OUTPUT_SUBDIR / filename

    if not video_file.exists() and not poster_file.exists():
        return error_response(f"视频 {filename} 不存在")

    # 缩略图不存在则即时生成
    if not poster_file.exists():
        generate_video_poster(filename)

    if poster_file.exists():
        return FileResponse(
            path=str(poster_file),
            media_type="image/jpeg",
        )
    return error_response("缩略图生成失败，请确认 ffmpeg 已安装")


@app.post("/api/videos/{filename}/convert/gif")
async def api_videos_convert_gif(filename: str, fps: int = 10, width: int = 480):
    """将视频转换为 GIF（需要 ffmpeg）"""
    if not filename.endswith(".mp4"):
        return error_response("仅支持转换 .mp4 文件")
    if not _is_safe_filename(filename):
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


# ===================== v1.0 社区互动 API（评论、点赞、浏览） =====================

@app.post("/api/community/like/{work_id}")
async def api_toggle_like(work_id: int, username: str = ""):
    """Toggle 点赞"""
    if not username:
        return error_response("用户名不能为空")
    result = toggle_like(work_id, username)
    return success_response(result, "已点赞" if result["liked"] else "已取消")


@app.get("/api/community/likes")
async def api_get_likes(ids: str = ""):
    """批量获取点赞数 ?ids=1,2,3"""
    try:
        work_ids = [int(x) for x in ids.split(",") if x.strip()]
        counts = get_like_counts(work_ids)
        return success_response({"counts": counts})
    except Exception:
        return error_response("参数格式错误")


@app.get("/api/community/likes/check")
async def api_check_likes(ids: str = "", username: str = ""):
    """查询用户是否已点赞 ?ids=1,2,3&username=xxx"""
    try:
        work_ids = [int(x) for x in ids.split(",") if x.strip()]
        liked = check_user_likes(work_ids, username)
        return success_response({"liked": liked})
    except Exception:
        return error_response("参数格式错误")


@app.get("/api/community/views")
async def api_get_views(ids: str = ""):
    """批量获取浏览量 & 递增"""
    try:
        work_ids = [int(x) for x in ids.split(",") if x.strip()]
        counts = get_view_counts(work_ids)
        return success_response({"counts": counts})
    except Exception:
        return error_response("参数格式错误")


@app.post("/api/community/view/{work_id}")
async def api_increment_view(work_id: int):
    """递增浏览量（播放视频时调用）"""
    count = increment_view(work_id)
    return success_response({"count": count})


@app.get("/api/community/comments/{work_id}")
async def api_get_comments(work_id: int, limit: int = 3, sort: str = "likes"):
    """获取评论列表"""
    comments = get_comments(work_id, limit=limit, sort_by=sort)
    total = get_comment_count(work_id)
    return success_response({"comments": comments, "total": total})


@app.post("/api/community/comments/{work_id}")
async def api_add_comment(work_id: int, username: str = "", text: str = "", avatar: str = ""):
    """发表评论"""
    if not username or not text:
        return error_response("用户名和评论内容不能为空")
    if len(text) > 500:
        return error_response("评论不能超过500字")
    comment = add_comment(work_id, username, text, avatar)
    return success_response({"comment": comment}, "评论发表成功")


@app.post("/api/community/comments/{work_id}/like/{comment_id}")
async def api_like_comment(work_id: int, comment_id: str, username: str = ""):
    """给评论点赞/取消点赞"""
    result = like_comment(comment_id, work_id, username)
    return success_response({"commentId": comment_id, "liked": result["liked"], "likes": result["likes"]})


# ===================== v1.0 逐帧调试 API =====================

@app.get("/api/debug/video/{filename}/info")
async def api_debug_video_info(filename: str):
    """
    获取视频元数据——时长、帧率、总帧数、分辨率等。
    这是逐帧调试的入口端点。
    """
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    try:
        from services.debug_service import get_video_info
        found, info = get_video_info(filename)
        if not found:
            return error_response(info.get("error", "视频不存在"))
        return success_response(info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debug/video/{filename}/frames")
async def api_debug_extract_frames(
    filename: str,
    start_frame: int = 0,
    end_frame: int = 10,
    format: str = "jpg",
    quality: int = 85,
):
    """
    提取视频指定帧范围的图片。
    每次最多 100 帧，返回帧列表及访问 URL。
    """
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    try:
        from services.debug_service import extract_frames
        success, result = extract_frames(
            filename, start_frame=start_frame, end_frame=end_frame,
            format=format, quality=quality,
        )
        if not success:
            return error_response(result.get("error", "帧提取失败"))
        return success_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debug/video/{filename}/frame/{frame_index}")
async def api_debug_single_frame(filename: str, frame_index: int):
    """
    获取指定编号的单帧图片（便捷端点）。
    自动定位缓存目录中的 frame_{idx:04d}.jpg 或 .png。
    """
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    video_stem = Path(filename).stem
    frame_dir = FRAME_CACHE_DIR / video_stem

    # 按常见格式查找帧文件
    for ext in ("jpg", "png"):
        frame_path = frame_dir / f"frame_{frame_index:04d}.{ext}"
        if frame_path.exists():
            return FileResponse(
                path=str(frame_path),
                media_type=f"image/{'jpeg' if ext == 'jpg' else ext}",
            )
        # 也尝试不带前导零的文件名
        alt_path = frame_dir / f"frame_{frame_index}.{ext}"
        if alt_path.exists():
            return FileResponse(
                path=str(alt_path),
                media_type=f"image/{'jpeg' if ext == 'jpg' else ext}",
            )

    return error_response(f"帧 #{frame_index} 不存在，请先调用 /api/debug/video/{filename}/frames 提取")


@app.get("/api/debug/video/{filename}/frame-at-time")
async def api_debug_frame_at_time(filename: str, time: float = 0.0):
    """
    获取指定时间点的单帧截图。
    """
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    try:
        from services.debug_service import extract_frame_at_time
        success, result = extract_frame_at_time(filename, time)
        if not success:
            return error_response(result.get("error", "截图失败"))

        # 返回图片文件
        video_stem = Path(filename).stem
        frame_name = f"time_{time:.3f}s.jpg"
        frame_path = FRAME_CACHE_DIR / video_stem / frame_name
        if frame_path.exists():
            return FileResponse(path=str(frame_path), media_type="image/jpeg")
        return success_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/debug/video/{filename}/thumbnail-sheet")
async def api_debug_thumbnail_sheet(
    filename: str,
    cols: int = 5,
    rows: int = 4,
    width: int = 320,
):
    """
    生成缩略图网格（contact sheet），均匀采样视频帧。
    返回一张拼接后的网格图 URL。
    """
    if not _is_safe_filename(filename):
        return error_response("非法文件名")

    try:
        from services.debug_service import generate_thumbnail_sheet
        success, result = generate_thumbnail_sheet(
            filename, cols=cols, rows=rows, width=width,
        )
        if not success:
            return error_response(result.get("error", "缩略图生成失败"))
        return success_response(result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ===================== 启动入口 =====================
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=[
            "outputs/**",       # 渲染产物：Celery 写入代码/视频会触发重载
            "outputs\\**",      # Windows 路径兼容
            "logs/**",          # 日志文件
            "logs\\**",
            "chroma_db/**",     # 向量库：build_kb 会修改
            "chroma_db\\**",
            "cache/**",         # 缓存目录
            "cache\\**",
            "__pycache__/**",
            "__pycache__\\**",
            "**/*.pyc",
            "**/*.log",
            "media/**",         # Manim 渲染中间文件
            "media\\**",
        ],
    )

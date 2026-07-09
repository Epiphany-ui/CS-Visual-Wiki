#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import ast
import hashlib
import json
import logging
import os
import re
import subprocess
import sys
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import chromadb
import requests

from services.logging_config import get_logger

logger = get_logger("ai_engine")

# ===================== LaTeX 环境配置（跨平台） =====================
_miktex_env = os.environ.get("MIKTEX_BIN_PATH", "")
if _miktex_env and os.path.isdir(_miktex_env) and _miktex_env not in os.environ["PATH"]:
    os.environ["PATH"] = _miktex_env + os.pathsep + os.environ["PATH"]

# ===================== 模型与 API 全局配置 =====================
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("未设置环境变量 DEEPSEEK_API_KEY，请检查 .env 文件或系统环境变量")

CODER_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
LLM_TEMPERATURE: float = 0.1
LLM_TOP_P: float = 0.85
API_REQUEST_TIMEOUT: tuple = (10, 120)  # (连接超时10s, 读取超时120s)

# --- Ollama 本地服务 ---
OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL_NAME: str = os.getenv("EMBEDDING_MODEL_NAME", "nomic-embed-text")

# ===================== 业务常量配置 =====================
CHROMA_PERSIST_DIR: str = "chroma_db"
CHROMA_COLLECTION_NAME: str = "manim_animation_kb"
RAG_TOP_K: int = 2

MAX_ANIMATION_DURATION: int = 30
DEFAULT_RETRY_TIMES: int = 3

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_DIR = BASE_DIR / "outputs"
CODE_OUTPUT_SUBDIR = OUTPUT_DIR / "code"
VIDEO_OUTPUT_SUBDIR = OUTPUT_DIR / "videos"
CACHE_DIR = BASE_DIR / "cache"
RENDER_QUALITY_FLAG: str = os.getenv("RENDER_QUALITY_FLAG", "-qm")
RENDER_TIMEOUT: int = int(os.getenv("RENDER_TIMEOUT", "120"))

CODE_BLOCK_PATTERN: str = r"```python\s*(.*?)\s*```|```\s*(.*?)\s*```"
SCENE_CLASS_PATTERN: str = r"class\s+(\w+)\s*\(\s*Scene\s*\)"

# 延迟导入 Prompt 服务，避免循环依赖和启动顺序问题
_prompt_service = None

def _get_prompt_service():
    global _prompt_service
    if _prompt_service is None:
        from services.prompt_service import prompt_service
        _prompt_service = prompt_service
    return _prompt_service

# ===================== 全局资源初始化 =====================
try:
    chroma_client = chromadb.PersistentClient(path=str(BASE_DIR / CHROMA_PERSIST_DIR))
    kb_collection = chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)
except Exception as e:
    kb_collection = None
    logger.critical(f"严重警告：向量库初始化失败，请检查是否已执行 build_kb.py。错误：{str(e)}")

CODE_OUTPUT_SUBDIR.mkdir(parents=True, exist_ok=True)
VIDEO_OUTPUT_SUBDIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)


# ===================== 通用工具函数 =====================
def generate_embedding(text: str) -> List[float]:
    try:
        response = requests.post(
            url=f"{OLLAMA_BASE_URL}/api/embed",
            json={
                "model": EMBEDDING_MODEL_NAME,
                "input": text
            },
            timeout=API_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json().get("embeddings", [[]])[0]
    except requests.exceptions.RequestException as e:
        logger.error(f"向量生成失败：{str(e)}")
        return []


def extract_manim_code(model_response: str) -> str:
    matches = re.findall(CODE_BLOCK_PATTERN, model_response, re.DOTALL)
    if not matches:
        return ""
    for match in matches:
        code = match[0] if match[0] else match[1]
        if code.strip():
            return code.strip()
    return ""


def extract_scene_class_name(code: str) -> Optional[str]:
    match = re.search(SCENE_CLASS_PATTERN, code)
    if match:
        return match.group(1)
    return None


# ===================== 缓存工具函数 =====================
def get_cached_result(user_input: str) -> Optional[Dict]:
    input_hash = hashlib.md5(user_input.strip().encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{input_hash}.json"
    if cache_file.exists():
        try:
            with open(cache_file, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return None
    return None


def save_to_cache(user_input: str, result: Dict):
    input_hash = hashlib.md5(user_input.strip().encode("utf-8")).hexdigest()
    cache_file = CACHE_DIR / f"{input_hash}.json"
    try:
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.warning(f"缓存写入失败：{str(e)}")


# ===================== DeepSeek API 统一封装（调试版）=====================
def deepseek_chat_request(messages: List[Dict]) -> Tuple[bool, str]:
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}"
    }
    payload = {
        "model": CODER_MODEL_NAME,
        "messages": messages,
        "temperature": LLM_TEMPERATURE,
        "top_p": LLM_TOP_P,
        "stream": False
    }

    max_retry = 2
    for attempt in range(max_retry):
        try:
            response = requests.post(
                url=DEEPSEEK_API_URL,
                headers=headers,
                json=payload,
                timeout=API_REQUEST_TIMEOUT
            )
            response.raise_for_status()
            resp_json = response.json()

            # ====== 调试：打印完整响应，控制台可直接看到返回内容 ======
            logger.debug("DeepSeek完整响应：%s", json.dumps(resp_json, ensure_ascii=False, indent=2))

            choices = resp_json.get("choices")
            if not choices:
                return False, "❌ 模型返回异常：choices 为空"
            content = choices[0].get("message", {}).get("content", "")
            if not content or not content.strip():
                return False, "❌ 模型返回空内容，请检查模型名或提示词"
            return True, content
        except (requests.exceptions.Timeout, requests.exceptions.ConnectionError, ConnectionError, TimeoutError) as e:
            if attempt < max_retry - 1:
                wait_time = 2 ** attempt
                logger.warning("DeepSeek API超时/连接失败 (attempt %d/%d)，等待%d秒后重试...", attempt + 1, max_retry, wait_time)
                time.sleep(wait_time)
                continue
            return False, f"❌ DeepSeek API连续{max_retry}次超时/连接失败，请稍后重试"
        except Exception as e:
            return False, f"❌ DeepSeek API调用失败：{str(e)}"
    return False, "❌ DeepSeek API达到最大重试次数"


# ===================== 核心业务逻辑 =====================
def rag_retrieve_references(user_query: str) -> str:
    if not kb_collection:
        return "知识库未就绪，使用纯大模型能力生成。"

    query_embedding = generate_embedding(user_query)
    if not query_embedding:
        return "未获取到参考资料（向量生成失败）"

    try:
        results = kb_collection.query(
            query_embeddings=[query_embedding],
            n_results=RAG_TOP_K
        )
        if not results.get("documents") or not results["documents"][0]:
            return "未找到相关参考资料"

        references = []
        for idx, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            ref = f"【参考资料{idx + 1} | 文件：{meta.get('file_name', '未知')}】\n{doc}\n"
            references.append(ref)
        return "\n".join(references)
    except Exception as e:
        logger.error(f"RAG检索失败：{str(e)}")
        return "参考资料检索失败"


def generate_manim_code(user_requirement: str) -> Tuple[bool, str]:
    references = rag_retrieve_references(user_requirement)
    # 从外部 Prompt 模板文件加载 System Prompt（支持热重载，修改即生效）
    system_prompt = _get_prompt_service().render(
        "code_generation",
        max_animation_duration=MAX_ANIMATION_DURATION,
        references=references,
    )
    user_prompt = f"请根据需求生成Manim动画代码：{user_requirement}"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    success, result = deepseek_chat_request(messages)
    if not success:
        return False, result

    manim_code = extract_manim_code(result)
    if not manim_code:
        return False, f"❌ 未提取到有效Manim代码。原始回复：\n{result}"
    return True, manim_code


def check_latex_violation(code_str: str) -> bool:
    """检测代码中是否使用了 LaTeX（MathTex/Tex），Windows 下可能因缺少 LaTeX 渲染失败"""
    try:
        root = ast.parse(code_str)
        for node in ast.walk(root):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ("MathTex", "Tex"):
                    return True
        return False
    except SyntaxError:
        return True  # 语法有误时保守返回 True，交由后续处理


def preflight_code_check(code: str) -> Tuple[bool, str]:
    """渲染前快速检查常见易错点，不通过则返回错误信息，避免无效渲染"""
    # 1. 基础语法检查
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"代码语法错误（第 {e.lineno or '?'} 行）: {e.msg}"

    # 2. 检查是否有 Scene 子类
    has_scene = False
    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                if (isinstance(base, ast.Name) and base.id == "Scene") or \
                   (isinstance(base, ast.Attribute) and base.attr == "Scene"):
                    has_scene = True
                    break
    if not has_scene:
        return False, "代码中未找到继承自 Scene 的类，Manim 无法渲染"

    # 3. 检查 Manim 导入
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
        return False, "代码中未导入 manim 模块"

    # 4. 检查 3D Dot 坐标（常见错误）
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "Dot":
            for kw in node.keywords:
                if kw.arg == "point":
                    if isinstance(kw.value, (ast.List, ast.Tuple)) and len(kw.value.elts) == 3:
                        return False, (
                            "Dot() 使用了 3D 坐标，可能导致渲染异常。"
                            "请使用 2D 坐标，如 Dot(point[:2])"
                        )
            for arg in node.args:
                if isinstance(arg, (ast.List, ast.Tuple)) and len(arg.elts) == 3:
                    return False, (
                        "Dot() 使用了 3D 坐标，可能导致渲染异常。"
                        "请使用 2D 坐标，如 Dot(point[:2])"
                    )

    return True, ""


def render_manim_animation(code_str: str, progress_callback=None) -> Tuple[bool, str, str]:
    """
    渲染 Manim 动画代码，返回 (成功, 日志, 视频路径)
    :param code_str: Manim Python 代码
    :param progress_callback: 可选进度回调，签名为 callback(state, message)
           state: 'started' | 'rendering' | 'success' | 'failed'
    """
    task_id = uuid.uuid4().hex[:8]
    code_file_path = CODE_OUTPUT_SUBDIR / f"{task_id}.py"
    video_output_path = VIDEO_OUTPUT_SUBDIR / f"{task_id}.mp4"

    try:
        with open(code_file_path, "w", encoding="utf-8") as f:
            f.write(code_str)

        scene_name = extract_scene_class_name(code_str)
        if not scene_name:
            return False, "❌ 渲染失败：代码中未找到继承Scene的场景类", ""

        render_command = [
            sys.executable,
            "-m", "manim",
            RENDER_QUALITY_FLAG,
            str(code_file_path.absolute()),
            scene_name,
            "-o", str(video_output_path.absolute())
        ]

        if progress_callback:
            progress_callback("started", "Manim 渲染已启动...")

        # 使用 Popen + 线程读取 stderr（避免缓冲区满导致死锁）
        import threading

        process = subprocess.Popen(
            render_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        stdout_lines: List[str] = []
        stderr_lines: List[str] = []

        def _read_stderr():
            """独立线程读取 stderr，防止缓冲区满导致死锁 + 解析 tqdm 进度"""
            for line in iter(process.stderr.readline, ""):
                if line:
                    stderr_lines.append(line)
                    if progress_callback:
                        m = _tqdm_pct.search(line)
                        if m:
                            pct = int(m.group(1))
                            progress_callback("rendering", line.strip(), percent=pct)

        stderr_thread = threading.Thread(target=_read_stderr, daemon=True)
        stderr_thread.start()

        try:
            # 逐行读取 stdout，非阻塞式获取渲染进度
            import re as _re
            _tqdm_pct = _re.compile(r'(\d+)%')  # 解析 tqdm 进度条: " 40%|####"
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                stdout_lines.append(line)
                if progress_callback:
                    # 尝试从 tqdm 输出中提取实际百分比
                    m = _tqdm_pct.search(line)
                    if m:
                        pct = int(m.group(1))
                        progress_callback("rendering", line.strip(), percent=pct)
                    elif "Rendering" in line or "Writing" in line or "File ready" in line:
                        progress_callback("rendering", line.strip())

            process.wait(timeout=RENDER_TIMEOUT)
            stderr_thread.join(timeout=5)

        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
            if progress_callback:
                progress_callback("failed", f"渲染超时（超过{RENDER_TIMEOUT}秒）")
            return False, f"❌ 渲染超时（超过{RENDER_TIMEOUT}秒），进程已强制终止", ""

        full_stdout = "".join(stdout_lines)
        full_stderr = "".join(stderr_lines)
        full_log = f"=== 标准输出 ===\n{full_stdout}\n=== 错误输出 ===\n{full_stderr}"

        if process.returncode == 0 and video_output_path.exists():
            web_accessible_url = f"/videos/{task_id}.mp4"
            if progress_callback:
                progress_callback("success", web_accessible_url)
            return True, f"✅ 渲染成功\n{full_log}", web_accessible_url
        else:
            if progress_callback:
                progress_callback("failed", f"进程返回码：{process.returncode}")
            return False, f"❌ 渲染失败，进程返回码：{process.returncode}\n{full_log}", ""

    except Exception as e:
        if progress_callback:
            progress_callback("failed", str(e))
        return False, f"❌ 渲染执行异常：{str(e)}", ""


def fix_manim_code(original_code: str, error_message: str) -> Tuple[bool, str]:
    # 从外部 Prompt 模板文件加载 System Prompt（支持热重载，修改即生效）
    system_prompt = _get_prompt_service().render(
        "code_fix",
        error_message=error_message,
    )
    user_prompt = f"请修复以下Manim代码：\n```python\n{original_code}\n```"

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
    success, result = deepseek_chat_request(messages)
    if not success:
        return False, result

    fixed_code = extract_manim_code(result)
    if not fixed_code:
        return False, "❌ 未提取到修复后的有效代码"
    return True, fixed_code


def run_full_pipeline(user_requirement: str, max_retry: int = DEFAULT_RETRY_TIMES, progress_callback=None) -> Dict:
    result = {"success": False, "code": "", "video_path": "", "try_count": 0, "log": ""}
    current_code = ""
    all_logs = []

    def _report(state, msg, pct=0):
        if progress_callback:
            progress_callback(state, msg, percent=pct)

    try:
        # 优先命中缓存
        cached = get_cached_result(user_requirement)
        if cached:
            cached["log"] = "✅ 命中本地缓存，极速返回\n" + cached["log"]
            _report("rendering", "命中缓存", 100)
            return cached

        _report("rendering", "AI 正在生成 Manim 代码...", 10)
        gen_success, gen_result = generate_manim_code(user_requirement)
        result["try_count"] = 1
        if not gen_success:
            all_logs.append(f"第1次尝试生成失败：{gen_result}")
            result["log"] = "\n".join(all_logs)
            return result

        current_code = gen_result
        result["code"] = current_code
        _report("rendering", "代码生成完成，开始渲染动画...", 20)
        render_success, render_log, video_path = render_manim_animation(current_code, progress_callback=progress_callback)
        all_logs.append(f"第1次渲染：\n{render_log}")

        if render_success:
            result.update({"success": True, "video_path": video_path, "log": "\n".join(all_logs)})
            save_to_cache(user_requirement, result)
            return result

        for retry_index in range(1, max_retry + 1):
            current_try = retry_index + 1
            result["try_count"] = current_try

            _report("rendering", f"第{current_try}次修复中...", 30 + retry_index * 20)
            fix_success, fix_result = fix_manim_code(current_code, render_log)
            if not fix_success:
                all_logs.append(f"第{current_try}次修复失败：{fix_result}")
                break
            if fix_result.strip() == current_code.strip():
                all_logs.append(f"第{current_try}次修复后代码无变化，终止重试以防死循环。")
                break

            current_code = fix_result
            result["code"] = current_code

            _report("rendering", f"第{current_try}次渲染中...", 40 + retry_index * 20)
            render_success, render_log, video_path = render_manim_animation(current_code, progress_callback=progress_callback)
            all_logs.append(f"第{current_try}次渲染：\n{render_log}")

            if render_success:
                result.update({"success": True, "video_path": video_path, "log": "\n".join(all_logs)})
                save_to_cache(user_requirement, result)
                return result

        all_logs.append(f"❌ 达到最大重试次数 {max_retry}，任务终止。")
        result["log"] = "\n".join(all_logs)
        return result
    except Exception as e:
        result["log"] = f"❌ 流水线全局异常：{str(e)}"
        return result
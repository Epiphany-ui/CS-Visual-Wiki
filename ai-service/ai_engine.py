#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import re
import sys
import ast
import time
import uuid
import json
import hashlib
import requests
import subprocess
import chromadb
from typing import List, Dict, Optional, Tuple
from pathlib import Path

# ===================== 环境安全与路径配置 =====================
miktex_path = fr"C:\Users\{os.getlogin()}\AppData\Local\Programs\MiKTeX\miktex\bin\x64"
if os.path.exists(miktex_path) and miktex_path not in os.environ["PATH"]:
    os.environ["PATH"] = miktex_path + os.pathsep + os.environ["PATH"]

# ===================== 模型与 API 全局配置 =====================
import os
from dotenv import load_dotenv

# 加载 .env 文件中的环境变量（优先级：已存在的系统环境变量 > .env 文件）
load_dotenv()

# 密钥从环境变量读取，如果未设置则报错退出（避免静默失败）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
if not DEEPSEEK_API_KEY:
    raise RuntimeError("未设置环境变量 DEEPSEEK_API_KEY，请检查 .env 文件或系统环境变量")

CODER_MODEL_NAME = os.getenv("DEEPSEEK_MODEL_NAME", "deepseek-v4-flash")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
LLM_TEMPERATURE: float = 0.1
LLM_TOP_P: float = 0.85
API_REQUEST_TIMEOUT: int = 180

# --- Ollama 本地服务 ---
OLLAMA_BASE_URL: str = "http://localhost:11434"
EMBEDDING_MODEL_NAME: str = "nomic-embed-text"

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
RENDER_QUALITY_FLAG: str = "-qm"
RENDER_TIMEOUT: int = 120

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
    print(f"⚠️ 严重警告：向量库初始化失败，请检查是否已执行 build_kb.py。错误：{str(e)}")

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
        print(f"❌ 向量生成失败：{str(e)}")
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
        print(f"⚠️ 缓存写入失败：{str(e)}")


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
            print("🔍 DeepSeek完整响应：", json.dumps(resp_json, ensure_ascii=False, indent=2))

            content = resp_json["choices"][0]["message"]["content"]
            if not content or not content.strip():
                return False, "❌ 模型返回空内容，请检查模型名或提示词"
            return True, content
        except requests.exceptions.Timeout:
            if attempt < max_retry - 1:
                wait_time = 2 ** attempt
                print(f"⚠️ DeepSeek API超时，第{attempt + 1}次重试，等待{wait_time}秒...")
                time.sleep(wait_time)
                continue
            return False, f"❌ DeepSeek API连续{max_retry}次读取超时，请稍后重试"
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
        print(f"❌ RAG检索失败：{str(e)}")
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
    try:
        root = ast.parse(code_str)
        for node in ast.walk(root):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
                if node.func.id in ["MathTex", "Tex"]:
                    return True
        return False
    except:
        return True

import ast
import numpy as np

def preflight_code_check(code: str) -> bool:
    """快速检查常见易错点，不通过则直接返回错误信息，避免无效渲染"""
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return False, f"代码语法错误: {e}"

    # 检查是否有 Dot(point) 且 point 是三维数组
    # 简单正则匹配可能误判，用 AST 遍历更可靠
    for node in ast.walk(tree):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id == 'Dot':
                # 检查参数是否可能是三维坐标（比如 np.array 或直接列表）
                for arg in node.args:
                    # 如果参数是列表或数组，可进一步分析维度（复杂，可先简单规则）
                    pass
    # 可以添加更多检查，如 MathTex/Tex 是否存在（如果你环境 LaTeX 不稳定）
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

        # 使用 Popen 逐行读取输出，支持进度回调
        process = subprocess.Popen(
            render_command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        stdout_lines = []
        stderr_lines = []

        try:
            # 逐行读取 stdout，非阻塞式获取渲染进度
            for line in iter(process.stdout.readline, ""):
                if not line:
                    break
                stdout_lines.append(line)
                # Manim 每渲染一帧会输出类似 "Rendering xxx" 的行
                if progress_callback and "Rendering" in line:
                    progress_callback("rendering", line.strip())

            # 读取剩余 stderr
            stderr_text = process.stderr.read()
            if stderr_text:
                stderr_lines.append(stderr_text)

            process.wait(timeout=RENDER_TIMEOUT)

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


def run_full_pipeline(user_requirement: str, max_retry: int = DEFAULT_RETRY_TIMES) -> Dict:
    result = {"success": False, "code": "", "video_path": "", "try_count": 0, "log": ""}
    current_code = ""
    all_logs = []

    try:
        # 优先命中缓存
        cached = get_cached_result(user_requirement)
        if cached:
            cached["log"] = "✅ 命中本地缓存，极速返回\n" + cached["log"]
            return cached

        gen_success, gen_result = generate_manim_code(user_requirement)
        result["try_count"] = 1
        if not gen_success:
            all_logs.append(f"第1次尝试生成失败：{gen_result}")
            result["log"] = "\n".join(all_logs)
            return result

        current_code = gen_result
        result["code"] = current_code
        render_success, render_log, video_path = render_manim_animation(current_code)
        all_logs.append(f"第1次渲染：\n{render_log}")

        if render_success:
            result.update({"success": True, "video_path": video_path, "log": "\n".join(all_logs)})
            save_to_cache(user_requirement, result)
            return result

        for retry_index in range(1, max_retry + 1):
            current_try = retry_index + 1
            result["try_count"] = current_try

            fix_success, fix_result = fix_manim_code(current_code, render_log)
            if not fix_success:
                all_logs.append(f"第{current_try}次修复失败：{fix_result}")
                break
            if fix_result.strip() == current_code.strip():
                all_logs.append(f"第{current_try}次修复后代码无变化，终止重试以防死循环。")
                break

            current_code = fix_result
            result["code"] = current_code

            render_success, render_log, video_path = render_manim_animation(current_code)
            all_logs.append(f"第{current_try}次渲染：\n{render_log}")

            if render_success:
                result.update({"success": True, "video_path": video_path, "log": "\n".join(all_logs)})
                if result["success"]:
                    save_to_cache(user_requirement, result)
                return result

        all_logs.append(f"❌ 达到最大重试次数 {max_retry}，任务终止。")
        result["log"] = "\n".join(all_logs)
        return result
    except Exception as e:
        result["log"] = f"❌ 流水线全局异常：{str(e)}"
        return result
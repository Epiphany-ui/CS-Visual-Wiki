#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI核心引擎模块（完整版）
功能：包含全局配置、工具函数、RAG检索、代码生成、渲染执行、Bug修复、完整流水线
依赖：chromadb, requests, subprocess, uuid, typing
创建日期：2026/7/6
"""
import os
import re
import uuid
import requests
import subprocess
import chromadb
from typing import List, Dict, Optional, Tuple
# 顶部新增导入，用于提示词格式化
import textwrap

# ===================== 全局配置常量（可根据环境修改）=====================
# === Ollama 大模型配置 ===
OLLAMA_BASE_URL: str = "http://localhost:11434"
# 代码生成模型（约束要求）
CODER_MODEL_NAME: str = "qwen2.5-coder:3b-instruct-q4_K_M"
# 向量嵌入模型（约束要求）
EMBEDDING_MODEL_NAME: str = "nomic-embed-text"
# 生成温度：0.2保证输出稳定（约束要求）
LLM_TEMPERATURE: float = 0.2
# HTTP请求超时时间
API_REQUEST_TIMEOUT: int = 60

# === ChromaDB 向量库配置 ===
CHROMA_PERSIST_DIR: str = "chroma_db"
CHROMA_COLLECTION_NAME: str = "manim_animation_kb"
# RAG检索Top2（约束要求）
RAG_TOP_K: int = 2

# === Manim 渲染配置 ===
# 动画最大时长：30秒以内（约束要求）
MAX_ANIMATION_DURATION: int = 30
# 默认重试次数
DEFAULT_RETRY_TIMES: int = 3
# 根输出目录
OUTPUT_DIR: str = "outputs"
# 代码文件存放子目录
CODE_OUTPUT_SUBDIR: str = f"{OUTPUT_DIR}/code"
# 视频文件存放子目录
VIDEO_OUTPUT_SUBDIR: str = f"{OUTPUT_DIR}/videos"
# Manim渲染质量参数：-ql 低质量（快速渲染）
RENDER_QUALITY_FLAG: str = "-ql"
# 渲染超时时间（秒），防止进程卡死
RENDER_TIMEOUT: int = 120

# === 正则配置 ===
# 匹配Python代码块的正则（兼容```python / ```标记）
CODE_BLOCK_PATTERN: str = r"```python\s*(.*?)\s*```|```\s*(.*?)\s*```"
# 匹配Scene子类名的正则
SCENE_CLASS_PATTERN: str = r"class\s+(\w+)\s*\(\s*Scene\s*\)"

# ===================== 全局资源初始化（复用连接）=====================
# 初始化Chroma持久化客户端（全局唯一，避免重复创建）
try:
    chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)
    # 获取已构建的知识库集合
    kb_collection = chroma_client.get_collection(
        name=CHROMA_COLLECTION_NAME
    )
except Exception as e:
    raise RuntimeError(f"向量库初始化失败，请先执行build_kb.py构建知识库！错误：{str(e)}")

# 确保各级输出目录存在
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(CODE_OUTPUT_SUBDIR, exist_ok=True)
os.makedirs(VIDEO_OUTPUT_SUBDIR, exist_ok=True)


# ===================== 通用工具函数 =====================
def generate_embedding(text: str) -> List[float]:
    """
    调用Ollama嵌入模型生成文本向量
    :param text: 待向量化的文本内容
    :return: 浮点型向量数组，失败返回空列表
    """
    try:
        response = requests.post(
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
            json={
                "model": EMBEDDING_MODEL_NAME,
                "prompt": text
            },
            timeout=API_REQUEST_TIMEOUT
        )
        response.raise_for_status()
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"❌ 向量生成失败：{str(e)}")
        return []


def extract_manim_code(model_response: str) -> str:
    """
    从大模型返回的文本中，使用正则提取纯Manim Python代码
    :param model_response: 大模型原始回复
    :return: 纯净的Python代码，无Markdown标记
    """
    # 执行正则匹配，提取代码块内容
    matches = re.findall(CODE_BLOCK_PATTERN, model_response, re.DOTALL)
    if not matches:
        return ""

    # 遍历匹配结果，取第一个非空的代码内容
    for match in matches:
        code = match[0] if match[0] else match[1]
        if code.strip():
            return code.strip()
    return ""


def extract_scene_class_name(code: str) -> Optional[str]:
    """
    从Manim代码中提取继承自Scene的场景类名，用于渲染命令指定场景
    :param code: Manim代码字符串
    :return: 场景类名，未找到返回None
    """
    match = re.search(SCENE_CLASS_PATTERN, code)
    if match:
        return match.group(1)
    return None


# ===================== RAG检索核心函数 =====================
def rag_retrieve_references(user_query: str) -> str:
    """
    RAG检索：根据用户需求查询向量库，返回Top2相关参考资料
    :param user_query: 用户自然语言需求
    :return: 格式化的参考资料字符串，无结果返回提示信息
    """
    # 生成用户查询向量
    query_embedding = generate_embedding(user_query)
    if not query_embedding:
        return "⚠️ 未获取到参考资料（向量生成失败）"

    try:
        # 执行余弦相似度检索
        results = kb_collection.query(
            query_embeddings=[query_embedding],
            n_results=RAG_TOP_K
        )

        # 无检索结果
        if not results["documents"][0]:
            return "⚠️ 未找到相关参考资料"

        # 格式化拼接参考资料（包含文件名+内容）
        references = []
        for idx, (doc, meta) in enumerate(zip(results["documents"][0], results["metadatas"][0])):
            ref = f"【参考资料{idx + 1} | 文件：{meta['file_name']}】\n{doc}\n"
            references.append(ref)

        return "\n".join(references)
    except Exception as e:
        print(f"❌ RAG检索失败：{str(e)}")
        return "⚠️ 参考资料检索失败"


# ===================== Manim代码生成函数 =====================
def generate_manim_code(user_requirement: str) -> Tuple[bool, str]:
    """
    结合RAG参考资料+强约束系统提示词，调用大模型生成合规的Manim代码
    :param user_requirement: 用户自然语言动画需求
    :return: 元组(是否成功, 生成的代码/错误信息)
    """
    references = rag_retrieve_references(user_requirement)

    # 优化：使用dedent去除三引号缩进，提升提示词纯净度，避免干扰大模型
    system_prompt = textwrap.dedent(f"""
    你是专业的Manim Community v0.18.0动画工程师，必须严格遵守以下规则：
    1. 仅使用Manim社区版标准语法，禁止使用第三方扩展库
    2. 代码必须完整可直接运行，必须定义继承Scene的类
    3. 动画总时长严格控制在{MAX_ANIMATION_DURATION}秒以内
    4. 代码结构清晰，添加必要注释，无冗余无效代码
    5. 仅输出```python包裹的代码块，不输出任何额外解释文字

    参考资料：
    {references}
    """)

    user_prompt = f"请根据需求生成Manim动画代码：{user_requirement}"

    try:
        # 4. 调用Ollama代码大模型
        response = requests.post(
            url=f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": CODER_MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": LLM_TEMPERATURE,
                "stream": False
            },
            timeout=API_REQUEST_TIMEOUT
        )
        response.raise_for_status()

        # 5. 提取纯净代码
        model_raw_response = response.json()["message"]["content"]
        manim_code = extract_manim_code(model_raw_response)

        if not manim_code:
            return False, "❌ 未提取到有效Manim代码"

        return True, manim_code

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 大模型调用失败：{str(e)}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ 代码生成未知错误：{str(e)}"
        print(error_msg)
        return False, error_msg


# ===================== Manim渲染执行函数 =====================
def render_manim_animation(code_str: str) -> Tuple[bool, str, str]:
    """
    将Manim代码保存为本地文件，调用subprocess执行渲染，捕获完整日志
    :param code_str: Manim代码字符串
    :return: 元组(是否渲染成功, 完整日志信息, 视频文件路径)
    """
    # 生成8位唯一任务ID，避免多请求文件冲突
    task_id = uuid.uuid4().hex[:8]
    code_file_path = f"{CODE_OUTPUT_SUBDIR}/{task_id}.py"
    video_file_path = f"{VIDEO_OUTPUT_SUBDIR}/{task_id}.mp4"

    try:
        # 1. 将代码写入本地文件
        with open(code_file_path, "w", encoding="utf-8") as f:
            f.write(code_str)

        # 2. 提取场景类名，manim渲染必须指定场景
        scene_name = extract_scene_class_name(code_str)
        if not scene_name:
            error_log = "❌ 渲染失败：代码中未找到继承Scene的场景类"
            return False, error_log, ""

        # 3. 构建manim命令行参数
        render_command = [
            "manim",
            RENDER_QUALITY_FLAG,
            code_file_path,
            scene_name,
            "-o", video_file_path
        ]

        # 4. 执行渲染进程，捕获输出，设置超时
        result = subprocess.run(
            render_command,
            capture_output=True,
            text=True,
            timeout=RENDER_TIMEOUT,
            encoding="utf-8",
            errors="replace"
        )

        # 5. 合并标准输出与错误输出为完整日志
        full_log = f"=== 标准输出 ===\n{result.stdout}\n=== 错误输出 ===\n{result.stderr}"

        # 6. 校验渲染结果：返回码为0且视频文件真实存在
        if result.returncode == 0 and os.path.exists(video_file_path):
            success_msg = f"✅ 渲染成功，视频路径：{video_file_path}"
            return True, success_msg + "\n" + full_log, video_file_path
        else:
            error_msg = f"❌ 渲染失败，进程返回码：{result.returncode}"
            return False, error_msg + "\n" + full_log, ""

    except subprocess.TimeoutExpired:
        timeout_log = f"❌ 渲染超时（超过{RENDER_TIMEOUT}秒），进程已强制终止"
        return False, timeout_log, ""
    except Exception as e:
        error_log = f"❌ 渲染执行异常：{str(e)}"
        return False, error_log, ""


# ===================== Bug修复函数 =====================
def fix_manim_code(original_code: str, error_message: str) -> Tuple[bool, str]:
    """
    根据渲染报错信息，调用大模型修复代码中的Bug，返回完整修复后代码
    :param original_code: 有错误的原始Manim代码
    :param error_message: 渲染报错日志
    :return: 元组(是否修复成功, 修复后代码/错误信息)
    """
    # 构建修复专用系统提示词，约束只修Bug不改功能
    system_prompt = f"""
    你是专业的Manim Community v0.18.0调试工程师，请根据报错信息修复代码。
    严格遵守以下规则：
    1. 保留原有动画的全部功能和逻辑，仅修复语法错误、导入缺失、API误用等问题
    2. 必须使用Manim社区版标准语法，必须继承Scene类
    3. 动画时长保持在{MAX_ANIMATION_DURATION}秒以内
    4. 返回完整的修复后代码，使用```python代码块包裹，不要输出额外解释
    5. 确保修复后的代码可直接运行渲染

    报错信息：
    {error_message}
    """

    user_prompt = f"请修复以下Manim代码：\n```python\n{original_code}\n```"

    try:
        # 调用大模型执行修复
        response = requests.post(
            url=f"{OLLAMA_BASE_URL}/api/chat",
            json={
                "model": CODER_MODEL_NAME,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                "temperature": LLM_TEMPERATURE,
                "stream": False
            },
            timeout=API_REQUEST_TIMEOUT
        )
        response.raise_for_status()

        # 提取修复后的纯净代码
        model_response = response.json()["message"]["content"]
        fixed_code = extract_manim_code(model_response)

        if not fixed_code:
            return False, "❌ 未提取到修复后的有效代码"

        return True, fixed_code

    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 代码修复调用大模型失败：{str(e)}"
        print(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"❌ 代码修复未知错误：{str(e)}"
        print(error_msg)
        return False, error_msg


# ===================== 完整流水线函数 =====================
def run_full_pipeline(user_requirement: str, max_retry: int = DEFAULT_RETRY_TIMES) -> Dict:
    """
    完整的Manim动画生成闭环流水线：生成→渲染→失败自动修复重试，最多重试N次
    :param user_requirement: 用户自然语言动画需求
    :param max_retry: 最大重试次数（首次生成后，失败最多重试max_retry次）
    :return: 结构化结果字典，固定字段：success, code, video_path, try_count, log
    """
    # 初始化标准化返回结果
    result = {
        "success": False,
        "code": "",
        "video_path": "",
        "try_count": 0,
        "log": ""
    }
    current_code = ""
    all_logs = []

    try:
        # ========== 第1次：初始代码生成 ==========
        print(f"🔄 第1次尝试：生成初始Manim代码...")
        gen_success, gen_result = generate_manim_code(user_requirement)
        result["try_count"] = 1

        if not gen_success:
            all_logs.append(f"第1次尝试失败：{gen_result}")
            result["log"] = "\n".join(all_logs)
            return result

        current_code = gen_result
        result["code"] = current_code

        # 首次渲染
        render_success, render_log, video_path = render_manim_animation(current_code)
        all_logs.append(f"第1次渲染日志：\n{render_log}")

        if render_success:
            result["success"] = True
            result["video_path"] = video_path
            result["log"] = "\n".join(all_logs)
            print("✅ 首次渲染成功，流水线结束")
            return result

        # ========== 失败进入重试修复循环 ==========
        for retry_index in range(1, max_retry + 1):
            current_try = retry_index + 1
            result["try_count"] = current_try
            print(f"🔄 第{current_try}次尝试：修复代码并重试渲染...")

            # 调用Bug修复函数
            fix_success, fix_result = fix_manim_code(current_code, render_log)
            if not fix_success:
                all_logs.append(f"第{current_try}次修复失败：{fix_result}")
                break

            # 新增：修复后代码无变化，提前终止，避免无效死循环
            if fix_result.strip() == current_code.strip():
                all_logs.append(f"第{current_try}次修复后代码无变化，终止重试")
                break

            current_code = fix_result
            result["code"] = current_code

            # 重新执行渲染
            render_success, render_log, video_path = render_manim_animation(current_code)
            all_logs.append(f"第{current_try}次渲染日志：\n{render_log}")

            if render_success:
                result["success"] = True
                result["video_path"] = video_path
                result["log"] = "\n".join(all_logs)
                print(f"✅ 第{current_try}次渲染成功，流水线结束")
                return result

        # 所有重试均失败
        all_logs.append(f"❌ 已达到最大重试次数{max_retry}，生成任务失败")
        result["log"] = "\n".join(all_logs)
        return result

    except Exception as e:
        error_msg = f"❌ 流水线全局异常：{str(e)}"
        result["log"] = error_msg
        print(error_msg)
        return result
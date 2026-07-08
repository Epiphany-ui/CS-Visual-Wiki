#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库构建脚本
功能：递归读取kb_data目录下的文档，生成向量并持久化存入ChromaDB
依赖：chromadb, requests, python-dotenv
创建日期：2026/7/6
"""
import os
import time
import requests
import chromadb
from typing import List, Dict

# ===================== 配置常量（可根据实际环境修改）=====================
# 知识库根目录（相对路径），支持多个目录
KB_ROOT_DIRS: list = ["kb_data", "wiki_data"]
# ChromaDB 持久化存储目录
CHROMA_PERSIST_DIR: str = "chroma_db"
# 向量库集合名称
COLLECTION_NAME: str = "manim_animation_kb"
# 支持读取的文件类型
SUPPORTED_EXTENSIONS: tuple = (".md", ".txt", ".py", ".ipynb")
# Ollama 嵌入模型接口地址
OLLAMA_BASE_URL: str = "http://localhost:11434"
EMBEDDING_MODEL: str = "nomic-embed-text"
# 向量相似度算法（余弦相似度）
SIMILARITY_FUNCTION: str = "cosine"
# 请求超时时间（秒）
REQUEST_TIMEOUT: int = 30


def load_file_content(file_path: str) -> str:
    """
    读取单个文件的文本内容
    :param file_path: 文件绝对/相对路径
    :return: 文件文本内容
    """
    try:
        # 通用编码读取，忽略解码错误，适配各类文本文件
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read().strip()
    except Exception as e:
        print(f"❌ 文件读取失败：{file_path}，错误信息：{str(e)}")
        return ""


def traverse_kb_files(root_dir: str, start_id: int = 0) -> tuple[List[str], List[Dict], List[str]]:
    """
    递归遍历知识库目录，获取所有支持的文件
    :param root_dir: 根目录路径
    :param start_id: 起始文档 ID（多目录合并时使用）
    :return: 文档内容列表、元数据列表、文档ID列表
    """
    documents: List[str] = []
    metadatas: List[Dict] = []
    ids: List[str] = []
    doc_index: int = start_id

    # 递归遍历所有子文件夹
    for root, _, files in os.walk(root_dir):
        for file in files:
            # 筛选支持的文件类型
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file).replace("\\", "/")  # 统一正斜杠
                if file.lower().endswith(".ipynb"):
                    content = load_ipynb_content(file_path)
                else:
                    content = load_file_content(file_path)

                # 跳过空内容文件
                if not content:
                    continue

                # 组装数据
                documents.append(content)
                metadatas.append({
                    "file_path": file_path,
                    "file_name": file,
                    "source_dir": root_dir,
                })
                ids.append(f"doc_{doc_index}")
                doc_index += 1

    return documents, metadatas, ids


def get_ollama_embedding(text: str) -> List[float]:
    """
    调用Ollama本地嵌入模型生成向量
    :param text: 待嵌入的文本
    :return: 向量数组
    """
    try:
        response = requests.post(
            f"{OLLAMA_BASE_URL}/api/embed",  # 使用你顶部定义的常量
            json={
                "model": EMBEDDING_MODEL,
                "input": text
            }
        )

        # 优化：打印出真实的报错内容，不再盲猜
        if response.status_code != 200:
            print(f"❌ Ollama 返回错误详情：{response.text}")
            response.raise_for_status()

            # ✅ 关键修改：提取 "embeddings" 数组的第一个元素
        return response.json()["embeddings"][0]

    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama嵌入模型调用失败，错误信息：{str(e)}")
        return []

import json

def load_ipynb_content(file_path: str) -> str:
    """提取 Notebook 中的纯文本和代码"""
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            notebook = json.load(f)
            content_parts = []
            for cell in notebook.get("cells", []):
                # 提取源码或 Markdown 文本
                source = "".join(cell.get("source", []))
                if source.strip():
                    content_parts.append(source)
            return "\n".join(content_parts)
    except Exception as e:
        print(f"❌ Notebook 读取失败：{file_path}，错误信息：{str(e)}")
        return ""

def build_knowledge_base() -> None:
    """
    主函数：构建完整的向量知识库
    流程：初始化向量库 -> 扫描多个目录 -> 生成向量 -> 持久化存储 -> 输出统计
    """
    start_time = time.time()
    print("=" * 60)
    print("🚀 开始构建Manim动画知识库...")

    try:
        # 1. 初始化Chroma客户端（本地持久化）
        chroma_client = chromadb.PersistentClient(path=CHROMA_PERSIST_DIR)

        # 2. 重置集合：先删除旧集合，再创建新集合（保证数据最新）
        try:
            chroma_client.delete_collection(name=COLLECTION_NAME)
            print(f"✅ 已删除旧集合：{COLLECTION_NAME}")
        except Exception:
            print(f"ℹ️ 集合不存在，跳过删除：{COLLECTION_NAME}")

        # 创建新集合（指定余弦相似度）
        collection = chroma_client.create_collection(
            name=COLLECTION_NAME,
            metadata={"hnsw:space": SIMILARITY_FUNCTION}
        )

        # 3. 扫描所有文档（遍历多个目录）
        all_documents, all_metadatas, all_ids = [], [], []
        doc_index = 0

        for root_dir in KB_ROOT_DIRS:
            if not os.path.exists(root_dir):
                print(f"⚠️ 目录不存在，跳过：{root_dir}")
                continue
            print(f"🔍 扫描目录：{root_dir}")
            documents, metadatas, ids = traverse_kb_files(root_dir, start_id=doc_index)
            if documents:
                all_documents.extend(documents)
                all_metadatas.extend(metadatas)
                all_ids.extend(ids)
                doc_index += len(documents)
                print(f"   ✅ 找到 {len(documents)} 个有效文档")
            else:
                print(f"   ⚠️ 未找到有效文档")

        total_docs = len(all_documents)
        if total_docs == 0:
            print("⚠️ 所有目录均未找到有效文档，知识库构建终止")
            return

        print(f"\n✅ 扫描完成，共找到 {total_docs} 个有效文档")

        # 4. 批量生成嵌入向量
        print("🔢 开始生成向量嵌入...")

        valid_documents = []
        valid_metadatas = []
        valid_ids = []
        valid_embeddings = []

        for idx, text in enumerate(all_documents):
            embed = get_ollama_embedding(text)
            if not embed:
                print(f"⚠️ 文档 {all_ids[idx]} 向量生成失败，已跳过")
                continue

            # 只有成功生成向量的文档，才会被加入最终列表
            valid_embeddings.append(embed)
            valid_documents.append(text)
            valid_metadatas.append(all_metadatas[idx])
            valid_ids.append(all_ids[idx])

        # 5. 批量存入向量库
        print("💾 开始存入向量数据库...")
        if valid_ids:  # 确保列表不为空，否则插入会报错
            collection.add(
                documents=valid_documents,
                metadatas=valid_metadatas,
                ids=valid_ids,
                embeddings=valid_embeddings
            )
        else:
            print("⚠️ 所有文档向量化均失败，无可入库数据！")

        # 6. 统计耗时
        cost_time = round(time.time() - start_time, 2)
        print("=" * 60)
        print("🎉 知识库构建完成！")
        print(f"📊 入库文档总数：{total_docs} 个")
        print(f"   - kb_data: Manim API 文档 + 示例代码")
        print(f"   - wiki_data: 百科词条知识（已进入 RAG 检索）")
        print(f"⏱️ 总耗时：{cost_time} 秒")
        print(f"📂 向量库存储路径：{CHROMA_PERSIST_DIR}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 知识库构建全局异常：{str(e)}")




if __name__ == "__main__":
    build_knowledge_base()
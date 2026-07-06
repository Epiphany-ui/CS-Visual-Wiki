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
# 知识库根目录（相对路径）
KB_ROOT_DIR: str = "kb_data"
# ChromaDB 持久化存储目录
CHROMA_PERSIST_DIR: str = "chroma_db"
# 向量库集合名称
COLLECTION_NAME: str = "manim_animation_kb"
# 支持读取的文件类型
SUPPORTED_EXTENSIONS: tuple = (".md", ".txt", ".py")
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


def traverse_kb_files(root_dir: str) -> tuple[List[str], List[Dict], List[str]]:
    """
    递归遍历知识库目录，获取所有支持的文件
    :param root_dir: 根目录路径
    :return: 文档内容列表、元数据列表、文档ID列表
    """
    documents: List[str] = []
    metadatas: List[Dict] = []
    ids: List[str] = []
    doc_index: int = 0

    # 递归遍历所有子文件夹
    for root, _, files in os.walk(root_dir):
        for file in files:
            # 筛选支持的文件类型
            if file.lower().endswith(SUPPORTED_EXTENSIONS):
                file_path = os.path.join(root, file).replace("\\", "/")  # 统一正斜杠
                content = load_file_content(file_path)

                # 跳过空内容文件
                if not content:
                    continue

                # 组装数据
                documents.append(content)
                metadatas.append({
                    "file_path": file_path,
                    "file_name": file
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
            url=f"{OLLAMA_BASE_URL}/api/embeddings",
            json={"model": EMBEDDING_MODEL, "prompt": text},
            timeout=REQUEST_TIMEOUT
        )
        response.raise_for_status()  # 抛出HTTP异常
        return response.json()["embedding"]
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama嵌入模型调用失败，错误信息：{str(e)}")
        return []


def build_knowledge_base() -> None:
    """
    主函数：构建完整的向量知识库
    流程：初始化向量库 -> 扫描文件 -> 生成向量 -> 持久化存储 -> 输出统计
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

        # 3. 扫描所有文档
        print(f"🔍 开始扫描目录：{KB_ROOT_DIR}")
        documents, metadatas, ids = traverse_kb_files(KB_ROOT_DIR)
        total_docs = len(documents)

        if total_docs == 0:
            print("⚠️ 未找到任何有效文档，知识库构建终止")
            return

        print(f"✅ 扫描完成，共找到 {total_docs} 个有效文档")

        # 4. 批量生成嵌入向量
        print("🔢 开始生成向量嵌入...")
        embeddings = []
        for idx, text in enumerate(documents):
            embed = get_ollama_embedding(text)
            if not embed:
                print(f"⚠️ 文档 {ids[idx]} 向量生成失败，已跳过")
                continue
            embeddings.append(embed)

        # 5. 批量存入向量库
        print("💾 开始存入向量数据库...")
        collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids,
            embeddings=embeddings
        )

        # 6. 统计耗时
        cost_time = round(time.time() - start_time, 2)
        print("=" * 60)
        print("🎉 知识库构建完成！")
        print(f"📊 入库文档总数：{total_docs} 个")
        print(f"⏱️ 总耗时：{cost_time} 秒")
        print(f"📂 向量库存储路径：{CHROMA_PERSIST_DIR}")
        print("=" * 60)

    except Exception as e:
        print(f"❌ 知识库构建全局异常：{str(e)}")


if __name__ == "__main__":
    build_knowledge_base()
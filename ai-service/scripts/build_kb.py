#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
知识库构建脚本
读取 wiki_data/ 目录下的 Markdown 词条，向量化后写入 ChromaDB 持久化存储

使用方式：
    python scripts/build_kb.py          # 全量重建
    python scripts/build_kb.py --incremental  # 增量更新（仅处理新增/修改的文件）
"""
import os
import sys
import json
import hashlib
import argparse
from pathlib import Path

# 把项目根目录加入 sys.path，方便导入 ai_engine
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import chromadb
from ai_engine import (
    generate_embedding,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
    EMBEDDING_MODEL_NAME,
    OLLAMA_BASE_URL,
)

# 词条源文件目录
WIKI_DATA_DIR = BASE_DIR / "wiki_data"
# 记录文件哈希，用于增量更新
HASH_RECORD_FILE = BASE_DIR / "scripts" / ".kb_file_hashes.json"


def parse_wiki_markdown(file_path: Path) -> dict:
    """
    解析 Markdown 词条文件
    文件头部用 <!-- meta --> 包裹元信息
    格式：
        <!-- meta
        title: 冒泡排序
        category: 算法
        tags: 排序, 基础算法
        difficulty: 入门
        -->
        # 冒泡排序
        正文内容...
    """
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    meta = {
        "file_name": file_path.name,
        "title": file_path.stem,
        "category": "未分类",
        "tags": "",
        "difficulty": "未知",
    }

    # 提取 meta 块
    if content.startswith("<!-- meta"):
        end_idx = content.find("-->")
        if end_idx != -1:
            meta_block = content[len("<!-- meta"):end_idx].strip()
            for line in meta_block.split("\n"):
                line = line.strip()
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()
                    if key in meta:
                        meta[key] = value
            # 去掉 meta 块，剩下的是正文
            body = content[end_idx + 3:].strip()
        else:
            body = content
    else:
        body = content

    meta["content_length"] = len(body)
    return meta, body


def split_into_chunks(text: str, chunk_size: int = 800, overlap: int = 100) -> list:
    """
    将长文本切分为重叠片段，避免单条向量信息丢失
    按段落切分，尽量保持语义完整
    """
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks = []
    current_chunk = ""

    for para in paragraphs:
        if len(current_chunk) + len(para) < chunk_size:
            current_chunk += para + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            # 重叠：取上一段末尾 overlap 字符作为下一段开头
            if len(current_chunk) > overlap:
                current_chunk = current_chunk[-overlap:] + para + "\n\n"
            else:
                current_chunk = para + "\n\n"

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    return chunks if chunks else [text]


def load_file_hashes() -> dict:
    """加载已处理文件的哈希记录"""
    if HASH_RECORD_FILE.exists():
        with open(HASH_RECORD_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def save_file_hashes(hashes: dict):
    """保存文件哈希记录"""
    HASH_RECORD_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(HASH_RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes, f, ensure_ascii=False, indent=2)


def get_file_hash(file_path: Path) -> str:
    """计算文件内容 MD5"""
    with open(file_path, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()


def build_kb(incremental: bool = False):
    """构建知识库主流程"""
    # 检查词条目录
    if not WIKI_DATA_DIR.exists():
        print(f"⚠️  词条目录不存在：{WIKI_DATA_DIR}")
        print("请先创建 wiki_data/ 目录并放入 Markdown 词条文件")
        return

    # 初始化 ChromaDB
    chroma_client = chromadb.PersistentClient(path=str(BASE_DIR / CHROMA_PERSIST_DIR))

    # 获取或创建 collection
    try:
        collection = chroma_client.get_collection(name=CHROMA_COLLECTION_NAME)
        print(f"✅ 加载已有知识库集合：{CHROMA_COLLECTION_NAME}")
    except Exception:
        collection = chroma_client.create_collection(name=CHROMA_COLLECTION_NAME)
        print(f"🆕 创建新知识库集合：{CHROMA_COLLECTION_NAME}")

    # 扫描所有 md 文件
    md_files = list(WIKI_DATA_DIR.rglob("*.md"))
    if not md_files:
        print("⚠️  wiki_data/ 目录下没有找到任何 .md 词条文件")
        return

    print(f"\n📂 找到 {len(md_files)} 个词条文件")

    # 增量模式：加载历史哈希
    file_hashes = load_file_hashes() if incremental else {}
    skipped = 0
    total_chunks = 0

    for idx, file_path in enumerate(md_files, 1):
        file_hash = get_file_hash(file_path)
        relative_path = str(file_path.relative_to(BASE_DIR))

        # 增量模式：跳过未修改的文件
        if incremental and relative_path in file_hashes and file_hashes[relative_path] == file_hash:
            skipped += 1
            continue

        print(f"\n[{idx}/{len(md_files)}] 处理：{relative_path}")

        meta, body = parse_wiki_markdown(file_path)
        chunks = split_into_chunks(body)
        print(f"   切分为 {len(chunks)} 个文本片段")

        # 逐个生成向量并写入
        for chunk_idx, chunk in enumerate(chunks):
            chunk_id = f"{relative_path}#chunk{chunk_idx}"
            embedding = generate_embedding(chunk)

            if not embedding:
                print(f"   ⚠️  片段 {chunk_idx} 向量生成失败，跳过")
                continue

            # 元信息：每个片段都带上完整词条元数据
            chunk_meta = {
                **meta,
                "chunk_index": chunk_idx,
                "chunk_total": len(chunks),
                "relative_path": relative_path,
            }

            collection.upsert(
                ids=[chunk_id],
                embeddings=[embedding],
                documents=[chunk],
                metadatas=[chunk_meta],
            )
            total_chunks += 1

        # 记录文件哈希
        file_hashes[relative_path] = file_hash

    # 保存哈希记录
    save_file_hashes(file_hashes)

    print(f"\n🎉 知识库构建完成！")
    print(f"   处理词条：{len(md_files)} 个")
    print(f"   向量化片段：{total_chunks} 个")
    if incremental:
        print(f"   跳过未修改：{skipped} 个")
    print(f"   向量库位置：{BASE_DIR / CHROMA_PERSIST_DIR}")
    print(f"   嵌入模型：{EMBEDDING_MODEL_NAME}（Ollama: {OLLAMA_BASE_URL}）")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="构建百科向量知识库")
    parser.add_argument(
        "--incremental", "-i",
        action="store_true",
        help="增量更新模式，仅处理新增/修改的文件"
    )
    args = parser.parse_args()

    build_kb(incremental=args.incremental)

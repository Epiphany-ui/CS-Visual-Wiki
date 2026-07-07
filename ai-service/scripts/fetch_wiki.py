#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
百科词条批量生成脚本
两种模式：
  1. 维基百科模式（默认）：抓维基百科原文 + AI 提炼（需要代理，默认127.0.0.1:7890）
  2. 纯AI生成模式（--ai）：直接让 DeepSeek 生成专业词条，无需翻墙（推荐）

用法:
  python scripts/fetch_wiki.py "归并排序"              # 维基模式
  python scripts/fetch_wiki.py "归并排序" --ai         # 纯AI生成
  python scripts/fetch_wiki.py -b scripts/keywords.txt --ai   # 批量AI生成
"""
import os, sys, re, argparse, requests
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

API_KEY = os.getenv("DEEPSEEK_API_KEY")
API_URL = "https://api.deepseek.com/v1/chat/completions"
WIKI_DATA = BASE_DIR / "wiki_data"

# 代理配置：Clash/V2Ray 默认 7890 端口，不对可在 .env 设 HTTP_PROXY
PROXIES = {
    "http": os.getenv("HTTP_PROXY", "http://127.0.0.1:7890"),
    "https": os.getenv("HTTPS_PROXY", "http://127.0.0.1:7890"),
}

CAT_MAP = {
    "排序":"algorithm","算法":"algorithm","搜索":"algorithm","树":"algorithm",
    "图":"algorithm","链表":"algorithm","栈":"algorithm","队列":"algorithm",
    "哈希":"algorithm","动态规划":"algorithm","导数":"math","积分":"math",
    "极限":"math","级数":"math","傅里叶":"math","矩阵":"math","概率":"math",
    "微分":"math","函数":"math","向量":"math",
}

DIFF_MAP = {
    "冒泡排序":"入门","插入排序":"入门","选择排序":"入门","二分查找":"入门",
    "链表":"入门","栈":"入门","队列":"入门","导数":"入门","积分":"入门","极限":"入门",
    "快速排序":"中等","归并排序":"中等","堆排序":"中等","二叉树":"中等",
    "哈希表":"中等","广度优先搜索":"中等","深度优先搜索":"中等","矩阵":"中等",
    "动态规划":"困难","傅里叶变换":"进阶",
}

SLUG_MAP = {
    "冒泡排序":"bubble-sort","插入排序":"insertion-sort","选择排序":"selection-sort",
    "快速排序":"quick-sort","归并排序":"merge-sort","堆排序":"heap-sort",
    "二分查找":"binary-search","二叉树":"binary-tree","链表":"linked-list",
    "栈":"stack","队列":"queue","哈希表":"hash-table",
    "广度优先搜索":"bfs","深度优先搜索":"dfs","动态规划":"dynamic-programming",
    "导数":"derivative","积分":"integral","极限":"limit",
    "傅里叶变换":"fourier-transform","矩阵":"matrix",
}


def fetch_wiki(title):
    """从维基百科获取原文（需要代理）"""
    try:
        r = requests.get("https://zh.wikipedia.org/w/api.php",
            params={
                "action":"query","format":"json","titles":title,
                "prop":"extracts","explaintext":True,
            },
            proxies=PROXIES, timeout=30,
        )
        r.raise_for_status()
        data = r.json()
        for pid, page in data["query"]["pages"].items():
            if pid == "-1":
                return ""
            lines = []
            for line in page.get("extract","").split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith(("参考","参见","外部链接","注释","引用")):
                    break
                lines.append(line)
            return "\n\n".join(lines)
    except Exception as e:
        print(f"  维基获取失败: {e}")
        return ""


def call_llm(messages, max_tokens=2500):
    """统一调用 DeepSeek API"""
    try:
        r = requests.post(API_URL,
            headers={"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"},
            json={"model": "deepseek-chat", "messages": messages,
                  "temperature": 0.3, "max_tokens": max_tokens},
            timeout=90,
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"].strip()
    except Exception as e:
        print(f"  API调用失败: {e}")
        return ""


def refine_from_wiki(title, raw, category):
    """维基原文 + AI 提炼为五段式"""
    sys_prompt = (
        "你是CS/数学专业教材编辑。将维基百科原文整理为标准五段式词条：\n"
        f"1.定义：{title}的准确定义与核心公式\n"
        "2.核心原理：核心思想、工作机制、关键性质(3-5点)\n"
        "3.过程/示例：用具体小例子演示步骤\n"
        "4.复杂度/性质分析：时间/空间复杂度、稳定性、收敛性等\n"
        "5.常见误区：学习者最容易混淆或出错的3-5个点\n"
        "要求：专业准确，适合大学生；去掉历史、人物、争议等无关内容；"
        "800-1200字；直接输出Markdown正文，不要任何前言。"
    )
    return call_llm([
        {"role":"system","content":sys_prompt},
        {"role":"user","content":f"词条名称：{title}\n分类：{category}\n\n维基百科原文：\n{raw[:5000]}"},
    ])


def generate_direct(title, category):
    """纯AI直接生成专业词条，不依赖维基百科"""
    sys_prompt = (
        f"你是计算机科学和数学领域的资深教材编辑。请为「{title}」撰写一篇专业的百科词条，"
        f"面向大学计算机/数学专业学生。严格按照以下五段式结构输出：\n\n"
        f"## 一、定义\n"
        f"用最简洁准确的语言定义{title}是什么，给出核心数学公式或伪代码（如有）。\n\n"
        f"## 二、核心原理\n"
        f"讲解核心思想、工作机制、关键性质，分3-5个要点说明。\n\n"
        f"## 三、过程/示例\n"
        f"用一个具体的小例子（比如具体数组/数值）一步步演示{title}的执行过程，步骤清晰。\n\n"
        f"## 四、复杂度/性质分析\n"
        f"分析时间复杂度（最好/最坏/平均）、空间复杂度、稳定性、收敛性等关键性质。\n\n"
        f"## 五、常见误区\n"
        f"列出学习者最容易混淆或犯错误的3-5个点，特别是和相似概念的区别。\n\n"
        f"要求：\n"
        f"- 内容专业准确，参考国内外经典教材（如算法导论、同济高数）\n"
        f"- 总字数控制在800-1200字\n"
        f"- 使用标准Markdown格式，二级标题用##\n"
        f"- 直接输出正文，不要任何前言、说明或总结"
    )
    return call_llm([{"role":"system","content":sys_prompt}], max_tokens=2500)


def guess_cat(title):
    for k, v in CAT_MAP.items():
        if k in title:
            return v
    return "algorithm"


def process(title, category=None, use_ai=False):
    print(f"\n处理: {title}")
    cat = category or guess_cat(title)
    mode = "纯AI生成" if use_ai else "维基+AI"
    print(f"  分类: {cat}  模式: {mode}")

    source = "AI生成（基于专业教材知识）"
    if use_ai:
        content = generate_direct(title, cat)
    else:
        raw = fetch_wiki(title)
        if not raw:
            print("  维基获取失败，自动切换为纯AI生成模式")
            content = generate_direct(title, cat)
            source = "AI生成（维基获取失败，自动降级）"
        else:
            print(f"  维基原文: {len(raw)}字")
            content = refine_from_wiki(title, raw, cat)
            source = "维基百科(CC BY-SA) + AI整理"

    if not content:
        print("  ❌ 生成失败")
        return False
    print(f"  生成内容: {len(content)}字")

    slug = SLUG_MAP.get(title, re.sub(r"[^\w-]", "", title.lower().replace(" ", "-")))
    diff = DIFF_MAP.get(title, "中等")

    cat_dir = WIKI_DATA / cat
    cat_dir.mkdir(parents=True, exist_ok=True)

    # 双保险：没有标题的自动加上
    if not content.startswith("##"):
        content = "## 一、定义\n\n" + content

    file_content = (
        f"<!-- meta\n"
        f"title: {title}\n"
        f"category: {cat}\n"
        f"tags: {title}\n"
        f"difficulty: {diff}\n"
        f"source: {source}\n"
        f"-->\n\n"
        f"# {title}\n\n"
        f"{content}\n"
    )

    fp = cat_dir / f"{slug}.md"
    fp.write_text(file_content, encoding="utf-8")
    print(f"  ✅ 已保存: {fp.relative_to(BASE_DIR)}")
    return True


def batch(path, use_ai=False):
    with open(path, encoding="utf-8") as f:
        lines = [l.strip() for l in f if l.strip() and not l.startswith("#")]
    print(f"批量模式：共 {len(lines)} 个词条  模式: {'纯AI生成' if use_ai else '维基+AI'}")
    ok = sum(1 for l in lines if process(l, use_ai=use_ai))
    print(f"\n🎉 完成：成功 {ok}/{len(lines)}")


if __name__ == "__main__":
    p = argparse.ArgumentParser(description="百科词条批量生成工具")
    p.add_argument("keyword", nargs="?", help="单个词条名称")
    p.add_argument("-c", "--category", help="指定分类 algorithm/math")
    p.add_argument("-b", "--batch", help="批量文件路径（每行一个词条）")
    p.add_argument("--ai", action="store_true", help="纯AI生成模式，不依赖维基百科（推荐）")
    args = p.parse_args()

    if not API_KEY:
        print("❌ 请先在 .env 中配置 DEEPSEEK_API_KEY")
        sys.exit(1)

    if args.batch:
        batch(args.batch, use_ai=args.ai)
    elif args.keyword:
        process(args.keyword, args.category, use_ai=args.ai)
    else:
        p.print_help()
        print("\n示例：")
        print("  python scripts/fetch_wiki.py 归并排序 --ai")
        print("  python scripts/fetch_wiki.py -b scripts/keywords.txt --ai")

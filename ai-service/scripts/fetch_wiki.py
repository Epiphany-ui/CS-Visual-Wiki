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
  python scripts/fetch_wiki.py -b keywords.txt --ai   # 批量AI生成
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

# 代理配置：Clash/V2Ray 默认 7890 端口，可在 .env 中设 WIKI_PROXY 覆盖
PROXIES = {
    "http": os.getenv("WIKI_PROXY", "http://127.0.0.1:7897"),
    "https": os.getenv("WIKI_PROXY", "http://127.0.0.1:7897"),
}

CAT_MAP = {
    # 算法
    "排序":"algorithm","算法":"algorithm","搜索":"algorithm","递归":"algorithm",
    "匹配":"algorithm","贪心":"algorithm","回溯":"algorithm","分治":"algorithm",
    "指针":"algorithm","前缀":"algorithm",
    # 数据结构
    "树":"data-structures","链表":"data-structures","栈":"data-structures",
    "队列":"data-structures","哈希":"data-structures","堆":"data-structures",
    "表":"data-structures","数组":"data-structures","字符串":"data-structures",
    "并查集":"data-structures","字典树":"data-structures","布隆":"data-structures",
    # 图论
    "图":"graph-theory","网络流":"graph-theory","回路":"graph-theory",
    "路径":"graph-theory","连通":"graph-theory",
    # 动态规划
    "动态规划":"dynamic-programming","背包":"dynamic-programming",
    "子序列":"dynamic-programming",
    # 数学
    "导数":"math","积分":"math","极限":"math","级数":"math",
    "傅里叶":"math","微分":"math","函数":"math","泰勒":"math",
    "格林":"math","梯度":"math","牛顿":"math","斯托克斯":"math",
    # 线性代数
    "矩阵":"linear-algebra","特征值":"linear-algebra","奇异值":"linear-algebra",
    "行列式":"linear-algebra","线性":"linear-algebra","正交":"linear-algebra",
    "对角":"linear-algebra","向量":"linear-algebra","PCA":"linear-algebra",
    # 概率统计
    "概率":"probability","正态":"probability","贝叶斯":"probability",
    "大数":"probability","中心极限":"probability","假设检验":"probability",
    "似然":"probability","马尔可夫":"probability","泊松":"probability",
    "随机过程":"probability","协方差":"probability","蒙特卡洛":"probability",
    "分布":"probability",
}

DIFF_MAP = {
    # 入门
    "冒泡排序":"入门","插入排序":"入门","选择排序":"入门","二分查找":"入门",
    "链表":"入门","栈":"入门","队列":"入门","数组":"入门","字符串":"入门",
    "导数":"入门","积分":"入门","极限":"入门","前缀和":"入门",
    "双指针":"入门","滑动窗口":"入门","二分答案":"入门",
    # 中等
    "快速排序":"中等","归并排序":"中等","堆排序":"中等","希尔排序":"中等",
    "计数排序":"中等","桶排序":"中等","基数排序":"中等",
    "二叉树":"中等","二叉搜索树":"中等","完全二叉树":"中等",
    "哈希表":"中等","堆":"中等","优先队列":"中等","循环队列":"中等",
    "双向链表":"中等","稀疏表":"中等",
    "广度优先搜索":"中等","深度优先搜索":"中等","拓扑排序":"中等",
    "贪心算法":"中等","分治算法":"中等","回溯算法":"中等",
    "矩阵":"中等","行列式":"中等","线性变换":"中等","向量空间":"中等",
    "级数":"中等","泰勒展开":"中等","偏导数":"中等",
    "正态分布":"中等","贝叶斯定理":"中等","大数定律":"中等",
    "最小生成树":"中等","最短路径":"中等","欧拉回路":"中等",
    "KMP字符串匹配":"中等","Rabin-Karp算法":"中等",
    # 困难
    "动态规划":"困难","背包问题":"困难","编辑距离":"困难",
    "红黑树":"困难","AVL树":"困难","B树":"困难","跳表":"困难",
    "字典树":"困难","布隆过滤器":"困难",
    "并查集":"困难","树状数组":"困难","线段树":"困难",
    "Dijkstra算法":"困难","Bellman-Ford算法":"困难","Floyd-Warshall算法":"困难",
    "傅里叶变换":"进阶","拉普拉斯变换":"困难",
    "多重积分":"困难","微分方程":"困难",
    "特征值":"困难","奇异值分解":"困难","PCA主成分分析":"困难",
    "网络流":"困难","二分图匹配":"困难","强连通分量":"困难",
    "马尔可夫链":"困难","随机过程":"困难",
    "A星搜索算法":"困难","模拟退火算法":"困难","遗传算法":"困难",
    "梯度下降":"困难","牛顿法":"中等",
}

# 基于拼音/中文字符的 slug 自动生成，映射表仅维护常见词条
SLUG_MAP = {
    "冒泡排序":"bubble-sort","插入排序":"insertion-sort","选择排序":"selection-sort",
    "快速排序":"quick-sort","归并排序":"merge-sort","堆排序":"heap-sort",
    "希尔排序":"shell-sort","计数排序":"counting-sort","桶排序":"bucket-sort",
    "基数排序":"radix-sort",
    "二分查找":"binary-search","二分答案":"binary-answer",
    "链表":"linked-list","双向链表":"doubly-linked-list",
    "栈":"stack","队列":"queue","循环队列":"circular-queue",
    "哈希表":"hash-table","堆":"heap","优先队列":"priority-queue",
    "二叉树":"binary-tree","二叉搜索树":"binary-search-tree",
    "完全二叉树":"complete-binary-tree",
    "红黑树":"red-black-tree","AVL树":"avl-tree","B树":"b-tree",
    "跳表":"skip-list","布隆过滤器":"bloom-filter",
    "字典树":"trie","并查集":"union-find","树状数组":"fenwick-tree",
    "线段树":"segment-tree","稀疏表":"sparse-table",
    "广度优先搜索":"bfs","深度优先搜索":"dfs","拓扑排序":"topological-sort",
    "贪心算法":"greedy","分治算法":"divide-and-conquer","回溯算法":"backtracking",
    "动态规划":"dynamic-programming","背包问题":"knapsack",
    "最长公共子序列":"lcs","最长递增子序列":"lis","编辑距离":"edit-distance",
    "矩阵链乘法":"matrix-chain-multiplication",
    "KMP字符串匹配":"kmp","Rabin-Karp算法":"rabin-karp",
    "最短路径":"shortest-path","最小生成树":"minimum-spanning-tree",
    "网络流":"network-flow","二分图匹配":"bipartite-matching",
    "欧拉回路":"eulerian-circuit","哈密顿路径":"hamiltonian-path",
    "强连通分量":"scc","双指针":"two-pointers","滑动窗口":"sliding-window",
    "前缀和":"prefix-sum",
    "A星搜索算法":"a-star","模拟退火算法":"simulated-annealing",
    "遗传算法":"genetic-algorithm",
    "导数":"derivative","积分":"integral","极限":"limit",
    "泰勒展开":"taylor-series","偏导数":"partial-derivative",
    "多重积分":"multiple-integral","微分方程":"differential-equation",
    "傅里叶变换":"fourier-transform","傅里叶级数":"fourier-series",
    "拉普拉斯变换":"laplace-transform","级数":"series",
    "格林公式":"greens-theorem","斯托克斯定理":"stokes-theorem",
    "梯度下降":"gradient-descent","牛顿法":"newtons-method",
    "矩阵":"matrix","特征值":"eigenvalue","奇异值分解":"svd",
    "行列式":"determinant","线性变换":"linear-transformation",
    "正交基":"orthogonal-basis","最小二乘法":"least-squares",
    "PCA主成分分析":"pca","向量空间":"vector-space",
    "线性方程组":"linear-equations","对角化":"diagonalization",
    "二次型":"quadratic-form",
    "概率论":"probability-theory","正态分布":"normal-distribution",
    "贝叶斯定理":"bayes-theorem","大数定律":"law-of-large-numbers",
    "中心极限定理":"central-limit-theorem",
    "假设检验":"hypothesis-testing","最大似然估计":"mle",
    "马尔可夫链":"markov-chain","泊松分布":"poisson-distribution",
    "随机过程":"stochastic-process","协方差":"covariance",
    "蒙特卡洛方法":"monte-carlo",
}


def fetch_wiki(title, lang="zh"):
    """从维基百科获取原文
    :param title: 词条标题
    :param lang: zh=中文维基，en=英文维基
    """
    api_url = f"https://{lang}.wikipedia.org/w/api.php"
    headers = {"User-Agent": "CSVisualLearn/1.0 (educational project; contact@example.com)"}

    try:
        r = requests.get(api_url,
            params={
                "action":"query","format":"json","titles":title,
                "prop":"extracts","explaintext":True,
            },
            headers=headers,
            proxies=PROXIES, timeout=30,
        )
        # 429 限流时等待后重试一次
        if r.status_code == 429:
            import time as _time
            print(f"  {lang}维基限流(429)，等待3秒后重试...")
            _time.sleep(3)
            r = requests.get(api_url,
                params={
                    "action":"query","format":"json","titles":title,
                    "prop":"extracts","explaintext":True,
                },
                headers=headers,
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
                if line.startswith(("参考","参见","外部链接","注释","引用",
                                   "References","See also","External links","Notes","Citations")):
                    break
                lines.append(line)
            return "\n\n".join(lines)
    except Exception as e:
        print(f"  {lang}维基获取失败: {e}")
        return ""


def fetch_wiki_with_fallback(title):
    """先尝试中文维基，失败则回退到英文维基 + AI翻译"""
    # 1. 尝试中文维基
    raw = fetch_wiki(title, lang="zh")
    if raw:
        return raw, "zh"
    # 2. 回退到英文维基
    print("  中文维基无结果，尝试英文维基...")
    raw = fetch_wiki(title, lang="en")
    if raw:
        return raw, "en"
    return "", ""


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


def refine_from_wiki(title, raw, category, from_english=False):
    """维基原文 + AI 整理为五段式"""
    if from_english:
        sys_prompt = (
            "你是CS/数学专业教材编辑。将英文维基百科原文翻译并整理为标准五段式中文词条：\n"
            f"1.定义：{title}的准确定义与核心公式\n"
            "2.核心原理：核心思想、工作机制、关键性质(3-5点)\n"
            "3.过程/示例：用具体小例子演示步骤\n"
            "4.复杂度/性质分析：时间/空间复杂度、稳定性、收敛性等\n"
            "5.常见误区：学习者最容易混淆或出错的3-5个点\n"
            "要求：专业准确，适合大学生；去掉历史、人物、争议等无关内容；"
            "从英文翻译为中文；800-1200字；直接输出Markdown正文，不要任何前言。"
        )
    else:
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
        raw, lang = fetch_wiki_with_fallback(title)
        if not raw:
            print("  维基获取失败（中英文均无结果），自动切换为纯AI生成模式")
            content = generate_direct(title, cat)
            source = "AI生成（维基获取失败，自动降级）"
        elif lang == "en":
            print(f"  英文维基原文: {len(raw)}字，AI翻译整理中...")
            content = refine_from_wiki(title, raw, cat, from_english=True)
            source = "英文维基百科(CC BY-SA) + AI翻译整理"
        else:
            print(f"  中文维基原文: {len(raw)}字")
            content = refine_from_wiki(title, raw, cat)
            source = "维基百科(CC BY-SA) + AI整理"

    if not content:
        print("  ❌ 生成失败")
        return False
    print(f"  生成内容: {len(content)}字")

    # slug 生成：优先查映射表，否则自动从标题生成
    slug = SLUG_MAP.get(title)
    if not slug:
        # 尝试用中文标题生成拼音式 slug（去掉中文，保留英文/数字）
        import re as _re
        slug = _re.sub(r"[^\w-]", "", title.lower().replace(" ", "-"))
        if not slug or slug.isdigit():
            # 全中文标题，用 MD5 前8位
            import hashlib
            slug = hashlib.md5(title.encode()).hexdigest()[:8]
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

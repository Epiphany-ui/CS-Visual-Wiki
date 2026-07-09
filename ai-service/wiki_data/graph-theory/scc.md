<!-- meta
title: 强连通分量
category: graph-theory
tags: 强连通分量
difficulty: 困难
source: AI生成（基于专业教材知识）
-->

# 强连通分量

## 一、定义

强连通分量（Strongly Connected Component, SCC）是**有向图**中的一个极大子图，在该子图中，任意两个顶点 \( u \) 和 \( v \) 之间均存在双向可达路径，即既存在从 \( u \) 到 \( v \) 的路径，也存在从 \( v \) 到 \( u \) 的路径。形式化地，对于有向图 \( G = (V, E) \)，其强连通分量是顶点集 \( V \) 的一个划分，满足：对任意 \( u, v \in C \subseteq V \)，有 \( u \leadsto v \) 且 \( v \leadsto u \)，且 \( C \) 是满足该性质的最大集合。

强连通分量的核心数学性质可通过**传递闭包**或**深度优先搜索（DFS）** 来刻画。在算法实现中，常用 Tarjan 算法或 Kosaraju 算法进行求解，其核心伪代码（Tarjan 算法）如下：

```
function Tarjan(G):
    index = 0
    stack = []
    for each v in V:
        if v.index is undefined:
            strongconnect(v)

function strongconnect(v):
    v.index = index
    v.lowlink = index
    index += 1
    stack.push(v)
    for each (v, w) in E:
        if w.index is undefined:
            strongconnect(w)
            v.lowlink = min(v.lowlink, w.lowlink)
        else if w in stack:
            v.lowlink = min(v.lowlink, w.index)
    if v.lowlink == v.index:
        pop stack until v, output as SCC
```

## 二、核心原理

1. **基于深度优先搜索（DFS）**：强连通分量的发现依赖于对图进行 DFS 遍历。在遍历过程中，每个顶点被赋予一个访问次序（index）和一个回溯值（lowlink），用于检测环的存在。

2. **lowlink 值的意义**：`lowlink[v]` 表示从顶点 \( v \) 出发，通过 DFS 树中的边和至多一条回边（back edge）所能到达的最小 index 值。当 `lowlink[v] == index[v]` 时，说明 \( v \) 是其所在强连通分量的根节点。

3. **栈的维护**：Tarjan 算法使用一个栈来保存当前正在处理的顶点。当发现一个强连通分量的根节点时，从栈中弹出直到该根节点的所有顶点，这些顶点构成一个强连通分量。

4. **关键性质**：强连通分量构成一个有向无环图（DAG）。将每个 SCC 缩为一个节点后，原图变为一个 DAG，这一性质在编译原理（如循环优化）和程序分析中极为重要。

5. **等价关系**：强连通分量实际上定义了顶点集上的一个等价关系：\( u \sim v \) 当且仅当 \( u \) 和 \( v \) 互相可达。每个等价类即为一个 SCC。

## 三、过程/示例

考虑有向图 \( G \) 包含 5 个顶点：\( V = \{0, 1, 2, 3, 4\} \)，边集为：
\[
E = \{(0,1), (1,2), (2,0), (1,3), (3,4)\}
\]

**步骤演示（Tarjan 算法）：**

1. 从顶点 0 开始 DFS：设置 `index[0]=0, lowlink[0]=0`，压栈。访问邻接点 1。
2. 顶点 1：`index[1]=1, lowlink[1]=1`，压栈。访问邻接点 2。
3. 顶点 2：`index[2]=2, lowlink[2]=2`，压栈。访问邻接点 0。
4. 顶点 0 已在栈中，更新 `lowlink[2] = min(2, index[0]=0) = 0`。回溯到 1，`lowlink[1] = min(1, lowlink[2]=0) = 0`。
5. 回溯到 0，`lowlink[0] = min(0, lowlink[1]=0) = 0`。此时 `lowlink[0] == index[0]`，弹出栈中顶点直到 0：得到 SCC1 = {0, 1, 2}。
6. 继续从顶点 1 的未访问邻接点 3 开始：`index[3]=3, lowlink[3]=3`，压栈。访问 4。
7. 顶点 4：`index[4]=4, lowlink[4]=4`，压栈。无未访问邻接点，`lowlink[4]==index[4]`，弹出 4：SCC2 = {4}。
8. 回溯到 3，`lowlink[3]==index[3]`，弹出 3：SCC3 = {3}。

最终得到三个强连通分量：{0,1,2}、{3}、{4}。缩点后，SCC1 到 SCC2 有边，SCC2 到 SCC3 有边，形成 DAG。

## 四、复杂度/性质分析

- **时间复杂度**：Tarjan 算法和 Kosaraju 算法的时间复杂度均为 \( O(V + E) \)，其中 \( V \) 为顶点数，\( E \) 为边数。这是因为每条边和每个顶点恰好被访问一次。最好、最坏和平均情况均为线性时间。
- **空间复杂度**：\( O(V) \)，主要用于存储栈、index 数组、lowlink 数组以及递归调用栈（最坏情况下递归深度为 \( V \)）。
- **稳定性**：算法本身是确定性的，对于同一图结构，输出结果唯一。但若图中有多个 SCC 之间无依赖关系，输出顺序可能因遍历起点不同而变化。
- **收敛性**：算法保证在有限步内终止，不存在迭代不收敛的问题。
- **正确性**：Tarjan 算法基于 DFS 树和 lowlink 值的性质，已被严格证明能够正确找出所有强连通分量。

## 五、常见误区

1. **混淆强连通分量与连通分量**：强连通分量仅适用于有向图，要求双向可达；而连通分量（无向图）只要求存在路径即可，不要求方向。初学者常将无向图的连通分量概念直接套用到有向图上。

2. **误认为强连通分量必须包含多个顶点**：单个顶点如果无法与其他顶点形成双向可达，它本身就是一个强连通分量。例如示例中的顶点 3 和 4 各自构成一个 SCC。

3. **忽略缩点后的 DAG 性质**：将 SCC 缩点后得到的图一定是 DAG，这一性质常用于证明某些图论定理。初学者可能误以为缩点后仍可能有环。

4. **混淆 Tarjan 算法中的 lowlink 与 index**：`index` 记录访问顺序，`lowlink` 记录通过回溯能到达的最小 index。错误地将 `lowlink` 更新为 `lowlink[w]` 而非 `index[w]` 会导致算法错误。

5. **认为 Kosaraju 算法和 Tarjan 算法等价**：虽然两者都能求解 SCC，但 Kosaraju 需要两次 DFS（一次正向，一次反向图），而 Tarjan 只需一次 DFS。Kosaraju 更直观但需要额外空间存储反向图，Tarjan 更紧凑但理解难度稍高。

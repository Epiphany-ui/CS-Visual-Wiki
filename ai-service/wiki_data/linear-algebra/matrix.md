<!-- meta
title: 矩阵
category: linear-algebra
tags: 矩阵
difficulty: 中等
source: AI生成（基于专业教材知识）
-->

# 矩阵

## 一、定义

矩阵（Matrix）是一个按照矩形阵列排列的复数或实数集合，通常用大写字母表示。从数学形式化定义，一个 \( m \times n \) 的矩阵 \( \mathbf{A} \) 是一个由 \( m \) 行和 \( n \) 列元素构成的二维数组：

\[
\mathbf{A} = \begin{pmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1} & a_{m2} & \cdots & a_{mn}
\end{pmatrix}
\]

其中 \( a_{ij} \) 表示位于第 \( i \) 行、第 \( j \) 列的元素。在计算机科学中，矩阵通常以二维数组形式存储，支持索引访问 \( \mathbf{A}[i][j] \)。当 \( m = n \) 时称为方阵，当 \( m = 1 \) 或 \( n = 1 \) 时退化为行向量或列向量。

## 二、核心原理

矩阵的核心思想在于将线性变换和线性方程组系统化、结构化地表示与操作。其工作机制建立在以下关键性质之上：

1. **线性映射的代数表示**：矩阵本质上是有限维向量空间之间的线性变换的坐标表示。给定矩阵 \( \mathbf{A} \in \mathbb{R}^{m \times n} \)，它定义了从 \( \mathbb{R}^n \) 到 \( \mathbb{R}^m \) 的线性映射 \( \mathbf{x} \mapsto \mathbf{A}\mathbf{x} \)，满足加法和数乘的线性性。

2. **矩阵乘法与复合变换**：矩阵乘法 \( \mathbf{C} = \mathbf{A}\mathbf{B} \) 对应线性变换的复合。其计算规则为 \( c_{ij} = \sum_{k=1}^{p} a_{ik} b_{kj} \)，要求 \( \mathbf{A} \) 的列数等于 \( \mathbf{B} \) 的行数。乘法不满足交换律，但满足结合律和分配律。

3. **秩与线性相关性**：矩阵的秩定义为行向量组或列向量组的极大线性无关组中向量的个数，记作 \( \text{rank}(\mathbf{A}) \)。秩决定了线性方程 \( \mathbf{A}\mathbf{x} = \mathbf{b} \) 解的存在性和唯一性：当且仅当 \( \text{rank}(\mathbf{A}) = \text{rank}([\mathbf{A}|\mathbf{b}]) \) 时方程组有解。

4. **特征值与特征向量**：对于方阵 \( \mathbf{A} \)，若存在非零向量 \( \mathbf{v} \) 和标量 \( \lambda \) 使得 \( \mathbf{A}\mathbf{v} = \lambda \mathbf{v} \)，则 \( \lambda \) 为特征值，\( \mathbf{v} \) 为对应的特征向量。特征分解是理解矩阵本质结构（如对角化、谱分解）的核心工具。

## 三、过程/示例

以求解线性方程组为例，演示矩阵运算过程：

**问题**：解方程组
\[
\begin{cases}
2x + 3y = 8 \\
x - y = -1
\end{cases}
\]

**步骤1：矩阵表示**  
将方程组写为增广矩阵形式：
\[
[\mathbf{A}|\mathbf{b}] = \left[\begin{array}{cc|c}
2 & 3 & 8 \\
1 & -1 & -1
\end{array}\right]
\]

**步骤2：高斯消元（行初等变换）**  
先交换两行使主元为1（更易计算）：
\[
R_1 \leftrightarrow R_2 \Rightarrow \left[\begin{array}{cc|c}
1 & -1 & -1 \\
2 & 3 & 8
\end{array}\right]
\]

**步骤3：消去第二行第一列**  
用 \( R_2 - 2R_1 \) 消去 \( a_{21} \)：
\[
\left[\begin{array}{cc|c}
1 & -1 & -1 \\
0 & 5 & 10
\end{array}\right]
\]

**步骤4：回代求解**  
由第二行得 \( 5y = 10 \Rightarrow y = 2 \)；代入第一行得 \( x - 2 = -1 \Rightarrow x = 1 \)。

**步骤5：验证**  
矩阵形式验证：\( \mathbf{A}\mathbf{x} = \begin{pmatrix}2 & 3 \\ 1 & -1\end{pmatrix} \begin{pmatrix}1 \\ 2\end{pmatrix} = \begin{pmatrix}8 \\ -1\end{pmatrix} = \mathbf{b} \)，解正确。

## 四、复杂度/性质分析

1. **矩阵乘法时间复杂度**：标准算法为 \( O(mnp) \)（\( \mathbf{A}_{m \times p} \times \mathbf{B}_{p \times n} \)）。对于 \( n \times n \) 方阵，最优的Strassen算法可达 \( O(n^{2.807}) \)，而Coppersmith-Winograd算法理论下界约为 \( O(n^{2.376}) \)，但常数因子过大，实际中较少使用。

2. **高斯消元复杂度**：求解 \( n \) 元线性方程组的时间复杂度为 \( O(n^3) \)（前向消去 \( \frac{2}{3}n^3 \) + 回代 \( O(n^2) \)）。空间复杂度为 \( O(n^2) \) 存储增广矩阵。

3. **矩阵求逆**：使用高斯-约当消元法，复杂度同为 \( O(n^3) \)。对于稀疏矩阵，可利用迭代法（如共轭梯度法）将单次迭代降至 \( O(n) \)，但收敛速度取决于矩阵条件数。

4. **数值稳定性**：矩阵运算对舍入误差敏感。条件数 \( \kappa(\mathbf{A}) = \|\mathbf{A}\| \cdot \|\mathbf{A}^{-1}\| \) 衡量矩阵对误差的放大程度。条件数越大，矩阵越“病态”，求解结果越不可靠。部分主元消去法可显著提升稳定性。

## 五、常见误区

1. **矩阵乘法交换律混淆**：误以为 \( \mathbf{A}\mathbf{B} = \mathbf{B}\mathbf{A} \)。实际上矩阵乘法一般不满足交换律，即使两者都是方阵。例如 \( \mathbf{A} = \begin{pmatrix}0 & 1 \\ 0 & 0\end{pmatrix}, \mathbf{B} = \begin{pmatrix}0 & 0 \\ 1 & 0\end{pmatrix} \)，则 \( \mathbf{A}\mathbf{B} \neq \mathbf{B}\mathbf{A} \)。

2. **行列式与矩阵混淆**：行列式是方阵映射到标量的函数，而矩阵是数组。初学者常将 \( \det(\mathbf{A}) = 0 \) 误认为矩阵为零矩阵，实际上仅表示矩阵奇异（不可逆）。例如 \( \begin{pmatrix}1 & 1 \\ 1 & 1\end{pmatrix} \) 行列式为0但非零矩阵。

3. **矩阵乘法与逐元素乘法混淆**：矩阵乘法 \( \mathbf{C} = \mathbf{A}\mathbf{B} \) 是内积运算，而Hadamard积 \( \mathbf{A} \circ \mathbf{B} \) 是逐元素相乘。在编程实现中（如NumPy），`np.dot(A, B)` 与 `A * B` 含义完全不同。

4. **逆矩阵存在性误判**：认为所有方阵都有逆矩阵。实际上只有满秩方阵（行列式非零）可逆。非方阵（如 \( 2 \times 3 \) 矩阵）不存在逆矩阵，但可能存在左逆或右逆。

5. **特征值与特征向量的实数性假设**：实矩阵的特征值未必是实数。例如旋转矩阵 \( \begin{pmatrix}0 & -1 \\ 1 & 0\end{pmatrix} \) 的特征值为 \( \pm i \)，特征向量为复向量。这在物理和工程应用中常被忽略。

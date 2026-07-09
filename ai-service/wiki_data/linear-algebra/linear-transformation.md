<!-- meta
title: 线性变换
category: linear-algebra
tags: 线性变换
difficulty: 中等
source: AI生成（基于专业教材知识）
-->

# 线性变换

## 一、定义
线性变换（Linear Transformation）是向量空间之间保持向量加法和标量乘法运算的映射。设 \( V \) 和 \( W \) 是域 \( \mathbb{F} \) 上的向量空间，映射 \( T: V \to W \) 称为线性变换，当且仅当对任意 \( \mathbf{u}, \mathbf{v} \in V \) 和任意标量 \( c \in \mathbb{F} \)，满足：
1. **加法性**：\( T(\mathbf{u} + \mathbf{v}) = T(\mathbf{u}) + T(\mathbf{v}) \)
2. **齐次性**：\( T(c\mathbf{u}) = cT(\mathbf{u}) \)

这两个条件可合并为：\( T(a\mathbf{u} + b\mathbf{v}) = aT(\mathbf{u}) + bT(\mathbf{v}) \)，其中 \( a, b \in \mathbb{F} \)。在有限维空间中，线性变换等价于矩阵乘法：若 \( A \) 是 \( m \times n \) 矩阵，则 \( T(\mathbf{x}) = A\mathbf{x} \) 定义了一个从 \( \mathbb{F}^n \) 到 \( \mathbb{F}^m \) 的线性变换。

## 二、核心原理
线性变换的核心思想是“保持线性结构”，即变换后的结果完全由基向量的像决定。其工作机制和关键性质如下：

1. **基的确定性**：若 \( \{\mathbf{v}_1, \mathbf{v}_2, \ldots, \mathbf{v}_n\} \) 是 \( V \) 的一组基，则 \( T \) 完全由 \( T(\mathbf{v}_1), T(\mathbf{v}_2), \ldots, T(\mathbf{v}_n) \) 唯一确定。任意向量 \( \mathbf{x} = \sum c_i \mathbf{v}_i \) 的像为 \( T(\mathbf{x}) = \sum c_i T(\mathbf{v}_i) \)。

2. **零空间与值域**：零空间（核）\( \ker(T) = \{\mathbf{v} \in V \mid T(\mathbf{v}) = \mathbf{0}\} \) 和值域 \( \text{Im}(T) = \{T(\mathbf{v}) \mid \mathbf{v} \in V\} \) 都是子空间。维数定理：\( \dim(\ker(T)) + \dim(\text{Im}(T)) = \dim(V) \)。

3. **矩阵表示**：选定基后，线性变换与矩阵一一对应。变换的复合对应矩阵乘法，可逆变换对应可逆矩阵。

4. **不变子空间**：若子空间 \( U \subseteq V \) 满足 \( T(U) \subseteq U \)，则 \( U \) 是 \( T \) 的不变子空间，可用于简化变换的表示（如对角化）。

## 三、过程/示例
考虑线性变换 \( T: \mathbb{R}^2 \to \mathbb{R}^2 \)，定义为 \( T(x, y) = (2x + y, x - 3y) \)。用矩阵表示为 \( A = \begin{bmatrix} 2 & 1 \\ 1 & -3 \end{bmatrix} \)，即 \( T(\mathbf{v}) = A\mathbf{v} \)。

**步骤1：验证线性性**
- 加法性：\( T((x_1,y_1)+(x_2,y_2)) = T(x_1+x_2, y_1+y_2) = (2(x_1+x_2)+(y_1+y_2), (x_1+x_2)-3(y_1+y_2)) = (2x_1+y_1, x_1-3y_1) + (2x_2+y_2, x_2-3y_2) = T(x_1,y_1) + T(x_2,y_2) \)
- 齐次性：\( T(c(x,y)) = T(cx, cy) = (2cx+cy, cx-3cy) = c(2x+y, x-3y) = cT(x,y) \)

**步骤2：对具体向量应用**
取 \( \mathbf{v} = (3, 2) \)，计算 \( T(\mathbf{v}) \)：
- 矩阵乘法：\( \begin{bmatrix} 2 & 1 \\ 1 & -3 \end{bmatrix} \begin{bmatrix} 3 \\ 2 \end{bmatrix} = \begin{bmatrix} 2\cdot3 + 1\cdot2 \\ 1\cdot3 + (-3)\cdot2 \end{bmatrix} = \begin{bmatrix} 6+2 \\ 3-6 \end{bmatrix} = \begin{bmatrix} 8 \\ -3 \end{bmatrix} \)
- 结果：\( T(3,2) = (8, -3) \)

**步骤3：验证基的确定性**
标准基 \( \mathbf{e}_1=(1,0), \mathbf{e}_2=(0,1) \) 的像为：
- \( T(1,0) = (2,1) \)
- \( T(0,1) = (1,-3) \)
任意向量 \( (x,y) = x\mathbf{e}_1 + y\mathbf{e}_2 \) 的像为 \( x(2,1) + y(1,-3) = (2x+y, x-3y) \)，与定义一致。

## 四、复杂度/性质分析
1. **时间复杂度**：
   - 矩阵乘法实现：对 \( n \) 维输入，计算 \( T(\mathbf{x}) = A\mathbf{x} \) 需 \( O(mn) \) 次乘加运算（\( A \) 为 \( m \times n \) 矩阵）。
   - 最坏/平均/最好情况均为 \( O(mn) \)，因为每个输出分量依赖所有输入分量。

2. **空间复杂度**：
   - 存储变换需 \( O(mn) \) 空间（存储矩阵）。
   - 计算过程中需 \( O(m) \) 额外空间存储结果。

3. **可逆性**：
   - 方阵情形（\( m=n \)）：变换可逆当且仅当矩阵满秩（行列式非零）。
   - 逆变换的计算复杂度为 \( O(n^3) \)（高斯消元法）。

4. **收敛性**：
   - 迭代应用线性变换（如 \( T^k(\mathbf{x}) \)）的收敛性由特征值决定：若所有特征值模长小于1，则 \( T^k(\mathbf{x}) \to \mathbf{0} \)。
   - 幂迭代法求主特征值收敛速度为 \( O(|\lambda_2/\lambda_1|^k) \)。

## 五、常见误区
1. **混淆线性变换与仿射变换**：线性变换必须满足 \( T(\mathbf{0}) = \mathbf{0} \)，而仿射变换允许平移（形如 \( T(\mathbf{x}) = A\mathbf{x} + \mathbf{b} \)）。初学者常误将平移视为线性变换。

2. **误以为所有映射都是线性的**：非线性映射（如 \( T(x) = x^2 \) 或 \( T(x,y) = (xy, x+y) \)）不满足加法性或齐次性。验证时需检查两个条件，而非仅凭直觉。

3. **混淆线性变换与线性函数**：线性函数 \( f(x) = kx \)（\( k \) 为常数）是 \( \mathbb{R} \to \mathbb{R} \) 的线性变换，但多元线性函数（如 \( f(x,y) = ax+by \)）本质上是线性泛函（值域为标量域），而非一般线性变换。

4. **忽视基的选择对矩阵表示的影响**：同一线性变换在不同基下的矩阵不同（相似关系）。初学者常误以为矩阵唯一对应变换，而忽略基的依赖性。

5. **错误理解零空间与值域的关系**：维数定理 \( \dim(\ker) + \dim(\text{Im}) = \dim(V) \) 常被误用为 \( \dim(\ker) + \dim(\text{Im}) = \dim(W) \)。注意值域维数不超过 \( \dim(W) \)，但等式左边总和始终等于定义域维数。

<!-- meta
title: 矩阵
category: math
tags: 矩阵
difficulty: 中等
source: AI生成（维基获取失败，自动降级）
-->

# 矩阵

## 一、定义

矩阵是一个按矩形阵列排列的复数或实数集合，通常用大写字母表示。形式上，一个 \( m \times n \) 矩阵 \( \mathbf{A} \) 由 \( m \) 行 \( n \) 列元素组成，记作：

\[
\mathbf{A} = [a_{ij}]_{m \times n} = 
\begin{pmatrix}
a_{11} & a_{12} & \cdots & a_{1n} \\
a_{21} & a_{22} & \cdots & a_{2n} \\
\vdots & \vdots & \ddots & \vdots \\
a_{m1} & a_{m2} & \cdots & a_{mn}
\end{pmatrix}
\]

其中 \( a_{ij} \) 表示第 \( i \) 行第 \( j \) 列的元素。当 \( m = n \) 时，称为方阵。矩阵是线性代数中最基本的对象，用于表示线性变换、线性方程组和向量空间之间的映射。

## 二、核心原理

1. **线性变换的代数表示**：矩阵的核心思想是将线性变换（如旋转、缩放、投影）编码为有序的数字阵列。对向量 \( \mathbf{x} \) 施加变换 \( \mathbf{A} \)，结果 \( \mathbf{y} = \mathbf{Ax} \) 的每个分量是 \( \mathbf{x} \) 与 \( \mathbf{A} \) 对应行向量的内积。

2. **矩阵乘法作为复合映射**：两个矩阵 \( \mathbf{A} \)（\( m \times n \)）和 \( \mathbf{B} \)（\( n \times p \)）的乘积 \( \mathbf{C} = \mathbf{AB} \) 定义为一个 \( m \times p \) 矩阵，其中 \( c_{ij} = \sum_{k=1}^{n} a_{ik} b_{kj} \)。这对应着先应用 \( \mathbf{B} \) 再应用 \( \mathbf{A} \) 的复合线性变换。

3. **秩与维度**：矩阵的秩是线性无关的行（或列）的最大数目，它决定了矩阵所表示线性变换的像空间的维度。秩-零化度定理指出：\( \text{rank}(\mathbf{A}) + \text{nullity}(\mathbf{A}) = n \)，其中零化度是零空间的维度。

4. **特征值与特征向量**：对于方阵 \( \mathbf{A} \)，若存在非零向量 \( \mathbf{v} \) 和标量 \( \lambda \) 使得 \( \mathbf{Av} = \lambda \mathbf{v} \)，则 \( \lambda \) 为特征值，\( \mathbf{v} \) 为特征向量。这揭示了矩阵在特定方向上的缩放效应，是谱分解和主成分分析的基础。

5. **矩阵分解**：将矩阵分解为多个简单矩阵的乘积（如LU分解、QR分解、奇异值分解SVD），可以简化计算并揭示内在结构。例如，SVD将任意矩阵分解为 \( \mathbf{A} = \mathbf{U\Sigma V}^T \)，其中 \( \mathbf{U} \) 和 \( \mathbf{V} \) 是正交矩阵，\( \mathbf{\Sigma} \) 是对角矩阵。

## 三、过程/示例

考虑线性方程组：
\[
\begin{cases}
2x + 3y = 8 \\
4x - y = 2
\end{cases}
\]

**步骤1：矩阵表示**  
系数矩阵 \( \mathbf{A} = \begin{pmatrix} 2 & 3 \\ 4 & -1 \end{pmatrix} \)，未知向量 \( \mathbf{x} = \begin{pmatrix} x \\ y \end{pmatrix} \)，常数向量 \( \mathbf{b} = \begin{pmatrix} 8 \\ 2 \end{pmatrix} \)，方程组写作 \( \mathbf{Ax} = \mathbf{b} \)。

**步骤2：计算逆矩阵**  
对于 \( 2 \times 2 \) 矩阵，逆矩阵公式为：
\[
\mathbf{A}^{-1} = \frac{1}{\det(\mathbf{A})} \begin{pmatrix} d & -b \\ -c & a \end{pmatrix}
\]
其中 \( \det(\mathbf{A}) = ad - bc = 2 \times (-1) - 3 \times 4 = -2 - 12 = -14 \)。

**步骤3：代入公式**  
\[
\mathbf{A}^{-1} = \frac{1}{-14} \begin{pmatrix} -1 & -3 \\ -4 & 2 \end{pmatrix} = \begin{pmatrix} \frac{1}{14} & \frac{3}{14} \\ \frac{4}{14} & -\frac{2}{14} \end{pmatrix}
\]

**步骤4：求解未知向量**  
\[
\mathbf{x} = \mathbf{A}^{-1} \mathbf{b} = \begin{pmatrix} \frac{1}{14} & \frac{3}{14} \\ \frac{4}{14} & -\frac{2}{14} \end{pmatrix} \begin{pmatrix} 8 \\ 2 \end{pmatrix} = \begin{pmatrix} \frac{8}{14} + \frac{6}{14} \\ \frac{32}{14} - \frac{4}{14} \end{pmatrix} = \begin{pmatrix} 1 \\ 2 \end{pmatrix}
\]

**步骤5：验证**  
代入原方程：\( 2(1) + 3(2) = 2 + 6 = 8 \)，\( 4(1) - 2 = 4 - 2 = 2 \)，结果正确。

## 四、复杂度/性质分析

- **矩阵乘法时间复杂度**：标准算法为 \( O(mnp) \)（\( m \times n \) 与 \( n \times p \) 相乘）。Strassen算法将 \( n \times n \) 方阵乘法降至 \( O(n^{\log_2 7}) \approx O(n^{2.807}) \)，Coppersmith-Winograd算法进一步降至约 \( O(n^{2.376}) \)，但常数因子较大，实际中仅对超大矩阵有优势。

- **矩阵求逆复杂度**：使用高斯-约当消元法为 \( O(n^3) \)，与LU分解相同。对于稀疏矩阵，可优化至 \( O(n \cdot \text{nnz}) \)，其中nnz为非零元素个数。

- **空间复杂度**：存储一个 \( m \times n \) 矩阵需要 \( O(mn) \) 空间。稀疏矩阵可使用压缩行存储（CSR）或压缩列存储（CSC）格式，空间降至 \( O(\text{nnz} + m + n) \)。

- **数值稳定性**：矩阵运算受浮点误差影响。条件数 \( \kappa(\mathbf{A}) = \|\mathbf{A}\| \cdot \|\mathbf{A}^{-1}\| \) 衡量矩阵对误差的敏感度，条件数越大，求解线性方程组时相对误差被放大的程度越大。

- **收敛性**：在迭代法（如雅可比迭代、高斯-赛德尔迭代）中，收敛性由迭代矩阵的谱半径决定。谱半径小于1时迭代收敛，且越小收敛越快。

## 五、常见误区

1. **矩阵乘法不满足交换律**：\( \mathbf{AB} \neq \mathbf{BA} \) 在一般情况下成立。初学者常误以为乘法可交换，实际上即使两个矩阵都是方阵，交换后结果也可能不同，甚至维度不匹配。

2. **混淆行列式与矩阵**：行列式是一个标量值，仅对方阵定义；矩阵是一个数组。初学者常将 \( \det(\mathbf{A}) \) 与 \( \mathbf{A} \) 本身混为一谈，或试图对非方阵计算行列式。

3. **零矩阵与零因子误解**：两个非零矩阵的乘积可能为零矩阵（称为零因子）。例如 \( \begin{pmatrix} 1 & 0 \\ 0 & 0 \end{pmatrix} \begin{pmatrix} 0 & 0 \\ 0 & 1 \end{pmatrix} = \begin{pmatrix} 0 & 0 \\ 0 & 0 \end{pmatrix} \)，这与实数运算不同。

4. **逆矩阵存在条件**：只有方阵且行列式非零时才存在逆矩阵。初学者常认为所有方阵都可逆，或试图对非方阵求逆（实际上非方阵只有伪逆）。

5. **特征值与特征向量的实数性**：实矩阵的特征值可能为复数，且特征向量也相应为复向量。例如旋转矩阵 \( \begin{pmatrix} 0 & -1 \\ 1 & 0 \end{pmatrix} \) 的特征值为 \( \pm i \)，初学者常默认所有特征值都是实数。

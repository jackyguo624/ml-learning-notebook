# STOI (Short-Time Objective Intelligibility) 指标详解

**STOI** (Short-Time Objective Intelligibility) 是一种用于评估由于噪声或其他失真处理后的语音可懂度（Intelligibility）的客观指标。与 PESQ 等关注语音 *质量* (Quality) 的指标不同，STOI 专门设计用于通过分析语音信号在短时时频区域的相关性，来预测人类听觉对语音内容的 *理解能力*。

STOI 的取值范围通常在 **0 到 1** 之间，值越高代表可懂度越好。

---

## STOI 计算流程与数学原理

STOI 的核心思想是计算干净语音（Clean Speech）和处理后语音（Processed/Degraded Speech）在时频域上的包络相关性。虽然计算过程比较复杂，主要可以分为以下几个步骤：

### 1. 预处理与时频分解 (TF Decomposition)

首先将干净语音 $x(n)$ 和处理后语音 $y(n)$ 下采样到 **10 kHz**。
然后，对信号进行短时傅里叶变换 (STFT)。
*   **分帧**：使用 256 点（25.6 ms）的 Hanning 窗，重叠 50%。
*   **DFT**：计算每一帧的频谱。

令 $\hat{x}(k, m)$ 和 $\hat{y}(k, m)$ 分别表示第 $m$ 帧、第 $k$ 个频点的干净语音和处理后语音的 DFT 系数。

### 2. 三分之一倍频程带聚合 (One-third Octave Band Aggregation)

为了模拟人类听觉系统的频率分辨率，将 DFT 频点合并为 $J=15$ 个三分之一倍频程带（One-third octave bands）。
第 $j$ 个频带在第 $m$ 帧的能量（幅值）计算如下：

$$
X_j(m) = \sqrt{ \sum_{k \in \text{band}_j} |\hat{x}(k, m)|^2 }
$$

$$
Y_j(m) = \sqrt{ \sum_{k \in \text{band}_j} |\hat{y}(k, m)|^2 }
$$

其中 $\text{band}_j$ 表示第 $j$ 个频带所包含的 DFT 频点集合。

### 3. 短时时域包络 (Short-time Temporal Envelope)

STOI 不直接比较每一帧的能量，而是比较一段较长时间内的“包络”变化。
定义一个长度为 $N$ (通常 $N=30$，约 384 ms) 的短时分析窗。对于第 $m$ 帧和第 $j$ 个频带，提取该窗口内的包络向量：

$$
\mathbf{x}_{j,m} = [X_j(m-N+1), X_j(m-N+2), \dots, X_j(m)]^T
$$

$$
\mathbf{y}_{j,m} = [Y_j(m-N+1), Y_j(m-N+2), \dots, Y_j(m)]^T
$$

### 4. 归一化与裁剪 (Component Normalization and Clipping)

这是 STOI 的关键步骤。由于人耳对通过简单的线性增益导致的响度差异不敏感，但对非线性的失真敏感，STOI 需要对处理后的语音包络进行归一化和裁剪。

首先计算一个缩放因子 $\alpha$，使得 $\alpha \mathbf{y}_{j,m}$ 在最小二乘意义下最接近 $\mathbf{x}_{j,m}$：

$$
\alpha = \frac{\mathbf{x}_{j,m}^T \mathbf{y}_{j,m}}{||\mathbf{y}_{j,m}||^2}
$$

然后对归一化后的处理语音包络 $\alpha \mathbf{y}_{j,m}$ 进行**裁剪 (Clipping)**。如果不自然地有过高的能量（例如突发的噪声），会被限制住。裁剪阈值通常设为参考信号的 $(1 + 10^{-15/20})$ 倍 (即允许大约 15dB 的动态范围差异)：

$$
\mathbf{y}'_{j,m} = \min \left( \alpha \mathbf{y}_{j,m}, (1 + 10^{-1.5}) \mathbf{x}_{j,m} \right)
$$

这个步骤确保了如果处理信号在某些时刻能量过大（严重失真），指标会受到惩罚；但如果只是整体音量差异，则已被 $\alpha$ 消除。

### 5. 相关性计算 (Correlation)

计算干净语音包络 $\mathbf{x}_{j,m}$ 与裁剪后的处理语音包络 $\mathbf{y}'_{j,m}$ 之间的线性相关系数 $d_{j,m}$：

$$
d_{j,m} = \frac{(\mathbf{x}_{j,m} - \mu_{x}) \cdot (\mathbf{y}'_{j,m} - \mu_{y'})}{||\mathbf{x}_{j,m} - \mu_{x}|| \cdot ||\mathbf{y}'_{j,m} - \mu_{y'}||}
$$

其中 $\mu_x$ 和 $\mu_{y'}$ 分别是向量 $\mathbf{x}_{j,m}$ 和 $\mathbf{y}'_{j,m}$ 的均值。

### 6. 平均得到最终 STOI 分数

最终的 STOI 分数是对所有频带 $j$ 和所有分析帧 $m$ 的相关系数取平均值：

$$
\text{STOI} = \frac{1}{M \times J} \sum_{m} \sum_{j} d_{j,m}
$$

---

## 总结 (Summary)

*   **输入**：干净语音，带噪/处理语音。
*   **频域分析**：三分之一倍频程带。
*   **核心机制**：比较短时包络（约 400ms）的形状相似度（相关性）。
*   **特性**：包含非线性裁剪机制，对非线性处理（如谱减法、维纳滤波等降噪算法）的评估非常有效。
*   **优势**：与人类听力测试的主观可懂度分数有极高的相关性（Correlation > 0.9）。

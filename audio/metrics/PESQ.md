# Metrics


## PESQ (Perceptual Evaluation of Speech Quality)

### 简介
PESQ (ITU-T P.862) 是一种用于客观评估语音质量的算法，主要用于预测人类对语音质量的主观评价 (MOS 分)。
*   **分数范围**: -0.5 到 4.5 (4.5 为满分)。
*   **适用场景**: VoIP, 固话, 3G/4G 语音编码质量测试。

### 数学模型与核心算法 (Mathematical Model)

PESQ 算法通过比较参考信号 (Reference) 和退化信号 (Degraded) 在**感知域**的差异来评分。核心步骤如下：

#### 1. 预处理 (Preprocessing)
*   **电平对齐 (Level Alignment)**:
    将信号增益调整到标准听觉电平（通常对应 79 dB SPL）。
    $$X_{ref}(t) = G_1 \cdot x(t), \quad Y_{deg}(t) = G_2 \cdot y(t)$$
*   **滤波 (Filtering)**:
    使用 IRS (Intermediate Reference System) 滤波器模拟标准手柄频响 (300-3400Hz)。

#### 2. 时间对齐 (Time Alignment)
计算两个信号包络的互相关函数 (Cross-Correlation) 来确定并补偿延迟 $\tau$：
$$R_{xy}(\tau) = \int |X_{ref}(t)| \cdot |Y_{deg}(t+\tau)| dt$$
算法会分段进行对齐，以处理时变的抖动 (Jitter)。

#### 3. 听觉变换 (Perceptual Transform)
将信号变换到人耳感知的时频域。
*   **STFT**: 使用汉宁窗 (32ms 窗长, 50% 重叠) 进行短时傅里叶变换，得到功率谱 $P(f)_n$。
*   **Bark 域映射**: 将频率 $f$ 映射到 **Bark 频标** (模拟耳蜗临界频带)。
*   **响度变换 (Zwicker Loudness)**:
    将功率密度转换为响度 (Sone)。公式近似为：
    $$L(f)_n = S_l \cdot \left( \frac{P_0(f)_n}{0.5} \right)^{\gamma} \cdot \left[ \left( 0.5 + 0.5 \cdot \frac{P(f)_n}{P_0(f)_n} \right)^{\gamma} - 1 \right]$$
    其中 $\gamma \approx 0.23$。

#### 4. 扰动计算 (Disturbance Calculation)
计算参考信号响度 $L_{ref}$ 和退化信号响度 $L_{deg}$ 之间的差异。
*   **原始误差**: $D_{raw} = L_{ref} - L_{deg}$
*   **非对称掩蔽 (Asymmetry Effect)**:
    PESQ 区分了“信号丢失”和“加性噪声”。
    *   **对称扰动 ($D_{sym}$)**: 衡量绝对差异。
    *   **非对称扰动 ($D_{asym}$)**: 对 $L_{deg} < L_{ref}$ (丢失) 和 $L_{deg} > L_{ref}$ (噪声) 赋予不同权重 (丢失通常更难听)。

#### 5. 聚合与映射 (Aggregation & Mapping)
*   **频域聚合**: 在每个时间帧内沿 Bark 频带聚合误差 (L6 范数)。
*   **时域聚合**: 在整个时间轴上聚合 (L2 范数)，分别得到平均扰动 $D_{ind}$ 和非对称扰动 $A_{ind}$。
*   **最终得分**:
    线性组合后通过 Sigmoid 映射：
    $$y = a_0 + a_1 D_{ind} + a_2 A_{ind}$$
    $$PESQ = 4.5 - 0.1 \cdot y - 0.0303 \cdot y^2$$

### Narrowband vs Wideband PESQ

PESQ 分为两个主要版本/模式，区别在于处理的音频频带宽度和采样率要求。

#### 1. Narrowband (NB) - 窄带
*   **标准**: ITU-T P.862
*   **适用场景**: 传统 PSTN 电话、2G/3G 语音。
*   **频带范围**: **300 Hz - 3.4 kHz**。
*   **采样率**: 通常下采样到 **8 kHz**。
*   **评分**: 主要针对传统听筒的效果。

#### 2. Wideband (WB) - 宽带
*   **标准**: ITU-T P.862.2 (Wideband extension to PESQ)
*   **适用场景**: HD Voice (VoIP, VoLTE), 高品质音频编解码。
*   **频带范围**: **50 Hz - 7 kHz**。
*   **采样率**: 必须为 **16 kHz**。
*   **关键差异**:
    *   WB 能感知到高频 (3.4k - 7k) 和低频 (50 - 300) 的失真，而 NB 会直接忽略这些频段。
    *   如果在 NB 模式下评估宽带信号，高频损失不会被扣分。
    *   如果在 WB 模式下评估窄带信号，由于高频缺失，分数会非常低（通常 < 2.0），即使该窄带信号质量本身很好。

#### 总结对比

| 特性 | Narrowband (NB) | Wideband (WB) |
| :--- | :--- | :--- |
| **标准** | P.862 | P.862.2 |
| **参考采样率** | 8000 Hz | 16000 Hz |
| **有效带宽** | 300 - 3400 Hz | 50 - 7000 Hz |
| **典型应用** | 传统电话 | 高清语音 (VoLTE, Zoom) |

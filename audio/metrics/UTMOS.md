# UTMOS (UTokyo-SaruLab Mean Opinion Score)

## 概述

UTMOS (UTokyo-SaruLab Mean Opinion Score) 是由东京大学 SaruLab 开发的一种先进的**非侵入式**语音质量预测框架。它通过深度学习模型自动预测语音的平均意见分 (MOS)，无需人工主观评测，也不需要参考音频。

UTMOS 广泛应用于以下场景：
- 语音合成 (TTS) 质量评估
- 神经语音编解码器评估
- 语音增强效果评估
- 说话人匿名化评估

## 核心思想

UTMOS 的核心思想是通过**集成学习 (Ensemble Learning)** 方法，结合多个强学习器和弱学习器，来模拟人类听众对语音质量的感知判断。

## 模型架构

### 1. 强学习器 (Strong Learners)

强学习器采用深度神经网络架构，直接处理原始音频波形：

#### 特征提取

使用预训练的自监督学习 (SSL) 模型（如 wav2vec 2.0）提取帧级特征：

$$
\mathbf{h}_t = \text{SSL}(\mathbf{x}), \quad t = 1, 2, \ldots, T
$$

其中：
- $\mathbf{x}$ 是输入的原始音频波形
- $\mathbf{h}_t$ 是第 $t$ 帧的特征向量
- $T$ 是总帧数

#### 序列建模

使用双向 LSTM (BLSTM) 处理帧级特征：

$$
\mathbf{f}_t = \text{BLSTM}(\mathbf{h}_t), \quad t = 1, 2, \ldots, T
$$

#### 帧级预测

通过线性投影层得到每帧的质量分数：

$$
s_t = \mathbf{W}^\top \mathbf{f}_t + b
$$

其中：
- $\mathbf{W}$ 是权重向量
- $b$ 是偏置项
- $s_t$ 是第 $t$ 帧的预测分数

#### 话语级聚合

将帧级分数平均得到话语级 MOS 预测：

$$
\hat{y}_{\text{strong}} = \frac{1}{T} \sum_{t=1}^{T} s_t
$$

### 2. 弱学习器 (Weak Learners)

弱学习器使用传统机器学习方法，基于话语级特征进行预测：

#### 特征提取

从 SSL 模型提取话语级嵌入向量：

$$
\mathbf{e} = \text{Pooling}(\{\mathbf{h}_1, \mathbf{h}_2, \ldots, \mathbf{h}_T\})
$$

常用的池化方法包括平均池化或注意力池化。

#### 回归预测

使用多种回归器进行预测：

$$
\hat{y}_{\text{weak}}^{(i)} = f_i(\mathbf{e}), \quad i = 1, 2, \ldots, M
$$

其中 $f_i$ 可以是：
- 岭回归 (Ridge Regression)
- 支持向量回归 (SVR)
- 决策树 (Decision Tree)
- LightGBM

### 3. 集成策略 (Stacking Ensemble)

UTMOS 使用堆叠集成方法融合多个预测器的输出：

#### 第一层预测

收集所有基学习器的预测：

$$
\mathbf{p} = [\hat{y}_{\text{strong}}^{(1)}, \hat{y}_{\text{strong}}^{(2)}, \ldots, \hat{y}_{\text{strong}}^{(K)}, \hat{y}_{\text{weak}}^{(1)}, \hat{y}_{\text{weak}}^{(2)}, \ldots, \hat{y}_{\text{weak}}^{(M)}]
$$

#### 元学习器融合

使用元学习器（通常是线性回归或神经网络）进行最终预测：

$$
\hat{y}_{\text{UTMOS}} = g(\mathbf{p}) = \sum_{j=1}^{K+M} \alpha_j \hat{y}^{(j)} + \beta
$$

其中：
- $\alpha_j$ 是第 $j$ 个基学习器的权重
- $\beta$ 是偏置项
- $g(\cdot)$ 是元学习器函数

## 训练目标

### 损失函数

UTMOS 使用均方误差 (MSE) 作为主要损失函数：

$$
\mathcal{L}_{\text{MSE}} = \frac{1}{N} \sum_{i=1}^{N} (\hat{y}_i - y_i)^2
$$

其中：
- $N$ 是训练样本数量
- $\hat{y}_i$ 是模型预测的 MOS 分数
- $y_i$ 是真实的人工标注 MOS 分数

### 对比学习增强

部分强学习器还引入对比学习目标，增强模型的表征能力：

$$
\mathcal{L}_{\text{contrastive}} = -\log \frac{\exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_i^+) / \tau)}{\sum_{j=1}^{B} \exp(\text{sim}(\mathbf{z}_i, \mathbf{z}_j) / \tau)}
$$

其中：
- $\mathbf{z}_i$ 是样本 $i$ 的嵌入表示
- $\mathbf{z}_i^+$ 是正样本（同一音频的不同增强）
- $\tau$ 是温度参数
- $\text{sim}(\cdot, \cdot)$ 是相似度函数（如余弦相似度）

### 总损失

$$
\mathcal{L}_{\text{total}} = \mathcal{L}_{\text{MSE}} + \lambda \mathcal{L}_{\text{contrastive}}
$$

其中 $\lambda$ 是平衡系数。

## 评估指标

UTMOS 的性能通过以下指标衡量：

### 1. 均方误差 (MSE)

$$
\text{MSE} = \frac{1}{N} \sum_{i=1}^{N} (\hat{y}_i - y_i)^2
$$

### 2. 线性相关系数 (LCC)

$$
\text{LCC} = \frac{\sum_{i=1}^{N} (\hat{y}_i - \bar{\hat{y}})(y_i - \bar{y})}{\sqrt{\sum_{i=1}^{N} (\hat{y}_i - \bar{\hat{y}})^2} \sqrt{\sum_{i=1}^{N} (y_i - \bar{y})^2}}
$$

### 3. 斯皮尔曼等级相关系数 (SRCC)

$$
\text{SRCC} = 1 - \frac{6 \sum_{i=1}^{N} d_i^2}{N(N^2 - 1)}
$$

其中 $d_i$ 是预测排名与真实排名之间的差异。

### 4. 肯德尔 τ 系数 (KTAU)

$$
\tau = \frac{n_c - n_d}{\frac{1}{2}N(N-1)}
$$

其中：
- $n_c$ 是一致对的数量
- $n_d$ 是不一致对的数量

## 性能表现

在 VoiceMOS Challenge 2022 中，UTMOS 取得了优异成绩：

| 指标 | 分数 |
|------|------|
| MSE (话语级) | ~0.165 |
| SRCC | ~0.897 |
| LCC | ~0.92 |

## 优势与特点

1. **非侵入式**：不需要参考音频，仅需待评估音频
2. **高准确性**：与人类主观评分高度相关
3. **可扩展性**：适用于大规模语音质量评估
4. **鲁棒性**：通过集成学习提高预测稳定性
5. **泛化能力**：在域外数据上表现良好

## 使用示例

```python
import torch
import librosa

# 加载预训练模型 (通过 torch.hub)
predictor = torch.hub.load('tarepan/SpeechMOS:main', 'utmos22_strong', trust_repo=True)

# 准备音频
audio_path = 'path/to/audio.wav'
audio, sr = librosa.load(audio_path, sr=16000)

# 转换为 tensor (模型期望 (Batch, Samples) 输入)
audio_tensor = torch.from_numpy(audio).unsqueeze(0) 

# 预测评分
with torch.no_grad():
    mos_score = predictor(audio_tensor, sr)

print(f"预测的 MOS 分数: {mos_score:.2f}")
```

## 应用场景

- **TTS 系统开发**：快速评估合成语音质量
- **语音编解码器优化**：比较不同编码参数的效果
- **语音增强验证**：评估降噪或去混响效果
- **大规模基准测试**：替代耗时的人工评测

## 参考文献

1. Saeki, T., et al. (2022). "UTMOS: UTokyo-SaruLab System for VoiceMOS Challenge 2022." *Interspeech 2022*.
2. VoiceMOS Challenge 2022 官方论文
3. wav2vec 2.0: A Framework for Self-Supervised Learning of Speech Representations

## 总结

UTMOS 通过结合自监督学习、深度序列建模和集成学习，实现了对语音质量的准确自动评估。其非侵入式特性和高准确性使其成为现代语音处理系统评估的重要工具。
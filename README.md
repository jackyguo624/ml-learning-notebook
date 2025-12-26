# ML Learning Notebook (机器学习学习笔记)

本仓库用于收集机器学习相关的学习资料和实验，目前主要关注**音频处理 (Audio Processing)** 领域。

## 📂 目录 (Directory)

### 🎵 音频 (Audio)

#### [指标 (Metrics)](audio/metrics/)
音频质量评估指标与相关实验。

- **[PESQ (Perceptual Evaluation of Speech Quality)](audio/metrics/PESQ.md)**
  - 详解 PESQ 算法 (ITU-T P.862) 的原理与数学模型。
  
  **相关文件:**
  - 🐍 [`run_pesq.py`](audio/metrics/run_pesq.py): 用于计算 PESQ 分数的 Python 脚本。
  - 🔊 示例音频文件:
    - `speech_sample_v0.wav` (参考音频 Reference)
    - `speech_sample_v1.wav`
    - `speech_sample_v2.wav`

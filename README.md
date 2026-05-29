<div align="center">
  <h2><b>Kronos：金融市场语言的基础模型（中文版）</b></h2>
</div>

<div align="center">

<a href="https://huggingface.co/NeoQuasar">
<img src="https://img.shields.io/badge/🤗-Hugging_Face-yellow" alt="Hugging Face">
</a>
<a href="https://shiyu-coder.github.io/Kronos-demo/">
<img src="https://img.shields.io/badge/🚀-在线演示-brightgreen" alt="Live Demo">
</a>
<a href="https://github.com/liyong763435720/Kronos-cn/graphs/commit-activity">
<img src="https://img.shields.io/github/last-commit/liyong763435720/Kronos-cn?color=blue" alt="Last Commit">
</a>
<a href="https://github.com/liyong763435720/Kronos-cn/releases">
<img src="https://img.shields.io/github/v/release/liyong763435720/Kronos-cn?color=orange" alt="Release">
</a>
<a href="./LICENSE">
<img src="https://img.shields.io/github/license/liyong763435720/Kronos-cn?color=green" alt="License">
</a>

</div>

<p align="center">
<img src="./figures/logo.png" width="100">
</p>

> Kronos 是首个针对金融 K 线（蜡烛图）的**开源基础模型**，
> 训练数据来自全球超过 **45 家交易所**。
> 本仓库为**完整中文版**，含开箱即用的 WebUI 图形界面。

---

## 💾 下载即用（无需配置环境）

| 平台 | 下载 | 系统要求 |
|------|------|----------|
| 🪟 Windows | [KronosWebUI_Setup.exe](https://github.com/liyong763435720/Kronos-cn/releases/latest) | Windows 10 及以上 |
| 🍎 macOS | [KronosWebUI.dmg](https://github.com/liyong763435720/Kronos-cn/releases/latest) | macOS 12 及以上，支持 Apple Silicon 和 Intel |

> **首次加载模型需联网**（从 HuggingFace 自动下载，约 100-500MB）
>
> **macOS 首次运行**：右键点击应用 → 选择「打开」，绕过安全提示

---

## 🖥️ WebUI 图形界面

无需写代码，通过浏览器即可使用 Kronos 进行金融预测。

### 功能
- 📊 支持 A 股、港股、美股、数字货币等多市场数据获取
- 🔮 一键生成 K 线预测，可视化展示结果
- 📁 支持上传本地 CSV/Feather 格式数据
- 🤖 内置 Kronos-mini / Kronos-small / Kronos-base 三款模型可选

### 本地启动

```bash
cd webui
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:7070`

---

## 📰 最新动态

- 🚩 **[2025.11.10]** Kronos 已被 AAAI 2026 接收。
- 🚩 **[2025.08.17]** 微调脚本已正式发布！
- 🚩 **[2025.08.02]** 论文已在 [arXiv](https://arxiv.org/abs/2508.02739) 发布！

---

## 📜 简介

**Kronos** 是一系列仅解码器（decoder-only）基础模型，专门针对金融市场的"语言"——K 线序列进行预训练。与通用时序预测基础模型不同，Kronos 专为处理金融数据特有的高噪声特性而设计。它采用新颖的两阶段框架：

1. 专用分词器首先将连续的多维 K 线数据（OHLCV）量化为**层次化离散 token**。
2. 大型自回归 Transformer 在这些 token 上进行预训练，使其能够作为多样化量化任务的统一模型。

<p align="center">
    <img src="figures/overview.png" alt="" align="center" width="700px" />
</p>

## ✨ 在线演示

**👉 [点击访问在线演示](https://shiyu-coder.github.io/Kronos-demo/)**

## 📦 模型库

| 模型          | 分词器                                                                           | 上下文长度 | 参数量  | 开源状态 |
|--------------|---------------------------------------------------------------------------------|-----------|--------|---------|
| Kronos-mini  | [Kronos-Tokenizer-2k](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-2k)     | 2048      | 4.1M   | ✅ [NeoQuasar/Kronos-mini](https://huggingface.co/NeoQuasar/Kronos-mini)  |
| Kronos-small | [Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base) | 512       | 24.7M  | ✅ [NeoQuasar/Kronos-small](https://huggingface.co/NeoQuasar/Kronos-small) |
| Kronos-base  | [Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base) | 512       | 102.3M | ✅ [NeoQuasar/Kronos-base](https://huggingface.co/NeoQuasar/Kronos-base)   |
| Kronos-large | [Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base) | 512       | 499.2M | ❌ |

---

## 🚀 快速开始（代码调用）

### 安装

```shell
pip install -r requirements.txt
```

### 生成预测

```python
from model import Kronos, KronosTokenizer, KronosPredictor

# 加载模型
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")

# 初始化预测器
predictor = KronosPredictor(model, tokenizer, max_context=512)

# 生成预测
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9,
    sample_count=1
)
```

完整示例见 [`examples/prediction_example.py`](examples/prediction_example.py)

<p align="center">
    <img src="figures/prediction_example.png" alt="预测示例" align="center" width="600px" />
</p>

---

## 🔧 微调（A 股市场示例）

> **免责声明**：本流程仅用于演示微调过程，并非可投入生产的量化交易系统。

微调过程分为四步：配置 → 数据准备 → 模型微调 → 回测评估。

```shell
# 数据预处理
python finetune/qlib_data_preprocess.py

# 微调分词器
torchrun --standalone --nproc_per_node=NUM_GPUS finetune/train_tokenizer.py

# 微调预测器
torchrun --standalone --nproc_per_node=NUM_GPUS finetune/train_predictor.py

# 回测评估
python finetune/qlib_test.py --device cuda:0
```

<p align="center">
    <img src="figures/backtest_result_example.png" alt="回测示例" align="center" width="700px" />
</p>

详细说明见 [微调文档](finetune_csv/README.md)

---

## 📖 引用

```
@misc{shi2025kronos,
      title={Kronos: A Foundation Model for the Language of Financial Markets},
      author={Yu Shi and Zongliang Fu and Shuo Chen and Bohan Zhao and Wei Xu and Changshui Zhang and Jian Li},
      year={2025},
      eprint={2508.02739},
      archivePrefix={arXiv},
      primaryClass={q-fin.ST},
      url={https://arxiv.org/abs/2508.02739},
}
```

## 📜 许可证

本项目基于 [MIT 许可证](./LICENSE) 开源。

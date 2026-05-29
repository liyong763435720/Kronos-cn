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

**功能：**
- 📊 支持 A 股、港股、美股、数字货币等多市场数据获取（AKShare / Tushare）
- 🔮 一键生成 K 线预测，可视化展示结果
- 📁 支持上传本地 CSV / Feather 格式数据
- 🤖 内置 Kronos-mini / Kronos-small / Kronos-base 三款模型可选

**本地启动：**

```bash
cd webui
pip install -r requirements.txt
python app.py
```

浏览器访问 `http://localhost:7070`

---

## 📡 数据接入

中文版 WebUI 支持三种数据来源，无需手动下载数据集即可直接预测。

### 方式一：AKShare（免费，推荐）

适合 **A 股市场**，无需注册，开箱即用。

```bash
pip install akshare
```

**支持的周期：**

| 类型 | 周期参数 |
|------|---------|
| 日线 / 周线 / 月线 | `daily` / `weekly` / `monthly` |
| 分钟线 | `5min` / `15min` / `30min` / `60min` |

**使用方法：** 在 WebUI「数据获取」面板选择 `AKShare`，输入股票代码（如 `600036`）和日期范围，点击获取即可。数据自动前复权处理。

---

### 方式二：Tushare Pro

适合需要更多数据权限或更稳定接口的用户，需在 [tushare.pro](https://tushare.pro) 注册并获取 Token。

```bash
pip install tushare
```

**股票代码自动识别规则：**

| 代码开头 | 交易所 | 示例 |
|---------|--------|------|
| `6` 或 `5` | 上交所（.SH） | `600036` → `600036.SH` |
| `4` 或 `8` | 北交所（.BJ） | `430047` → `430047.BJ` |
| 其他 | 深交所（.SZ） | `000001` → `000001.SZ` |

**支持的周期：** 与 AKShare 相同（日/周/月/5min/15min/30min/60min）

**Token 配置：** 在 WebUI 设置页面填入 Token，系统会自动持久化保存，无需每次重新输入。

---

### 方式三：上传本地文件

支持上传已有的本地数据文件，格式要求如下：

| 项目 | 要求 |
|------|------|
| 文件格式 | `.csv` 或 `.feather` |
| 必需列 | `open`、`high`、`low`、`close` |
| 时间列 | `timestamps` / `timestamp` / `date`（任一即可）|
| 可选列 | `volume`（成交量）、`amount`（成交额）|

**示例 CSV 格式：**

```csv
timestamps,open,high,low,close,volume,amount
2024-01-02 09:30:00,10.50,10.80,10.45,10.72,1234567,13012345.6
2024-01-02 09:35:00,10.72,10.90,10.68,10.85,987654,10698765.4
...
```

> 若数据中无时间列，系统将自动从 `2024-01-01` 起按小时生成时间戳。

---

## 📰 最新动态

- 🚩 **[2025.11.10]** Kronos 已被 AAAI 2026 接收。
- 🚩 **[2025.08.17]** 微调脚本已正式发布！欢迎参考，将 Kronos 适配到你自己的任务。
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

我们提供了在线演示，可可视化 Kronos 的预测结果。该网页展示了对 **BTC/USDT** 交易对未来 24 小时的预测。

**👉 [点击访问在线演示](https://shiyu-coder.github.io/Kronos-demo/)**

## 📦 模型库

我们发布了一系列不同规模的预训练模型，以满足不同的算力和应用需求。所有模型均可从 Hugging Face Hub 直接获取。

| 模型          | 分词器                                                                           | 上下文长度 | 参数量  | 开源状态 |
|--------------|---------------------------------------------------------------------------------|-----------|--------|---------|
| Kronos-mini  | [Kronos-Tokenizer-2k](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-2k)     | 2048      | 4.1M   | ✅ [NeoQuasar/Kronos-mini](https://huggingface.co/NeoQuasar/Kronos-mini)  |
| Kronos-small | [Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base) | 512       | 24.7M  | ✅ [NeoQuasar/Kronos-small](https://huggingface.co/NeoQuasar/Kronos-small) |
| Kronos-base  | [Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base) | 512       | 102.3M | ✅ [NeoQuasar/Kronos-base](https://huggingface.co/NeoQuasar/Kronos-base)   |
| Kronos-large | [Kronos-Tokenizer-base](https://huggingface.co/NeoQuasar/Kronos-Tokenizer-base) | 512       | 499.2M | ❌ |

---

## 🚀 快速开始

### 安装

1. 安装 Python 3.10+，然后安装依赖：

```shell
pip install -r requirements.txt
```

### 📈 生成预测

使用 `KronosPredictor` 类进行预测非常简单直接。它封装了数据预处理、归一化、预测和反归一化等步骤，让你只需几行代码即可从原始数据得到预测结果。

**重要说明**：`Kronos-small` 和 `Kronos-base` 的 `max_context` 为 **512**，这是模型能处理的最大序列长度。为获得最佳性能，建议输入数据长度（即 `lookback`）不超过此限制。`KronosPredictor` 会自动处理超长上下文的截断。

以下是生成第一个预测的分步指南。

#### 1. 加载分词器和模型

首先从 Hugging Face Hub 加载预训练的 Kronos 模型及其对应的分词器。

```python
from model import Kronos, KronosTokenizer, KronosPredictor

# 从 Hugging Face Hub 加载
tokenizer = KronosTokenizer.from_pretrained("NeoQuasar/Kronos-Tokenizer-base")
model = Kronos.from_pretrained("NeoQuasar/Kronos-small")
```

#### 2. 实例化预测器

创建 `KronosPredictor` 实例，传入模型、分词器和目标设备。

```python
# 初始化预测器
predictor = KronosPredictor(model, tokenizer, max_context=512)
```

#### 3. 准备输入数据

`predict` 方法需要三个主要输入：
- `df`：包含历史 K 线数据的 pandas DataFrame，必须包含 `['open', 'high', 'low', 'close']` 列，`volume` 和 `amount` 为可选列。
- `x_timestamp`：与 `df` 中历史数据对应的时间戳 pandas Series。
- `y_timestamp`：需要预测的未来时段的时间戳 pandas Series。

```python
import pandas as pd

# 加载数据
df = pd.read_csv("./data/XSHG_5min_600977.csv")
df['timestamps'] = pd.to_datetime(df['timestamps'])

# 定义上下文窗口和预测长度
lookback = 400
pred_len = 120

# 准备预测器输入
x_df = df.loc[:lookback-1, ['open', 'high', 'low', 'close', 'volume', 'amount']]
x_timestamp = df.loc[:lookback-1, 'timestamps']
y_timestamp = df.loc[lookback:lookback+pred_len-1, 'timestamps']
```

#### 4. 生成预测

调用 `predict` 方法生成预测。可通过 `T`、`top_p`、`sample_count` 等参数控制采样过程，实现概率性预测。

```python
# 生成预测
pred_df = predictor.predict(
    df=x_df,
    x_timestamp=x_timestamp,
    y_timestamp=y_timestamp,
    pred_len=pred_len,
    T=1.0,          # 采样温度
    top_p=0.9,      # 核采样概率
    sample_count=1  # 生成并平均的预测路径数量
)

print("预测数据预览：")
print(pred_df.head())
```

`predict` 方法返回一个 pandas DataFrame，包含以 `y_timestamp` 为索引的 `open`、`high`、`low`、`close`、`volume` 和 `amount` 预测值。

对于多时间序列的高效处理，Kronos 提供了 `predict_batch` 方法，支持对多个数据集并行预测，非常适合同时预测多个资产或时段的场景。

```python
# 准备批量预测的多个数据集
df_list = [df1, df2, df3]                        # DataFrame 列表
x_timestamp_list = [x_ts1, x_ts2, x_ts3]        # 历史时间戳列表
y_timestamp_list = [y_ts1, y_ts2, y_ts3]        # 未来时间戳列表

# 生成批量预测
pred_df_list = predictor.predict_batch(
    df_list=df_list,
    x_timestamp_list=x_timestamp_list,
    y_timestamp_list=y_timestamp_list,
    pred_len=pred_len,
    T=1.0,
    top_p=0.9,
    sample_count=1,
    verbose=True
)

# pred_df_list 按输入顺序返回预测结果
for i, pred_df in enumerate(pred_df_list):
    print(f"序列 {i} 的预测结果：")
    print(pred_df.head())
```

**批量预测的重要要求：**
- 所有序列必须具有相同的历史长度（回看窗口）
- 所有序列必须具有相同的预测长度（`pred_len`）
- 每个 DataFrame 必须包含必需列：`['open', 'high', 'low', 'close']`
- `volume` 和 `amount` 列为可选，缺失时自动填充为零

`predict_batch` 方法利用 GPU 并行性进行高效处理，并自动对每个序列独立进行归一化和反归一化。

#### 5. 示例与可视化

完整可运行的脚本（包含数据加载、预测和绘图）请参见 [`examples/prediction_example.py`](examples/prediction_example.py)。

运行该脚本将生成一张对比真实数据与模型预测结果的图表，类似下图所示：

<p align="center">
    <img src="figures/prediction_example.png" alt="预测示例" align="center" width="600px" />
</p>

此外，我们还提供了不使用成交量和成交额数据进行预测的脚本，详见 [`examples/prediction_wo_vol_example.py`](examples/prediction_wo_vol_example.py)。

---

## 🔧 在自有数据上微调（A 股市场示例）

我们提供了完整的 Kronos 微调流程。以下示例演示如何使用 [Qlib](https://github.com/microsoft/qlib) 准备中国 A 股市场数据并进行简单回测。

> **免责声明**：本流程仅用于演示微调过程，是一个简化示例，并非可投入生产的量化交易系统。一个稳健的量化策略需要更复杂的技术，如组合优化和风险因子中性化，才能获得稳定的超额收益（Alpha）。

微调过程分为四个主要步骤：

1. **配置**：设置路径和超参数。
2. **数据准备**：使用 Qlib 处理并分割数据。
3. **模型微调**：微调分词器和预测器模型。
4. **回测**：评估微调后模型的性能。

### 前置条件

1. 确保已安装 `requirements.txt` 中的所有依赖。
2. 本流程依赖 `qlib`，请安装：
    ```shell
    pip install pyqlib
    ```
3. 需要准备 Qlib 数据。请参考 [Qlib 官方文档](https://github.com/microsoft/qlib) 在本地下载并配置数据。示例脚本假设使用日频数据。

### 第一步：配置实验

数据、训练和模型路径的所有设置均集中在 `finetune/config.py` 中。在运行任何脚本之前，请根据你的环境**修改以下路径**：

- `qlib_data_path`：本地 Qlib 数据目录路径。
- `dataset_path`：保存处理后的训练/验证/测试 pickle 文件的目录。
- `save_path`：保存模型检查点的根目录。
- `backtest_result_path`：保存回测结果的目录。
- `pretrained_tokenizer_path` 和 `pretrained_predictor_path`：起始预训练模型的路径（可以是本地路径或 Hugging Face 模型名称）。

你还可以调整 `instrument`、`train_time_range`、`epochs`、`batch_size` 等参数以适配你的具体任务。如果不使用 [Comet.ml](https://www.comet.com/)，请设置 `use_comet = False`。

### 第二步：准备数据集

运行数据预处理脚本。该脚本将从 Qlib 目录加载原始市场数据，进行处理，划分为训练集、验证集和测试集，并保存为 pickle 文件。

```shell
python finetune/qlib_data_preprocess.py
```

运行完成后，你将在配置的 `dataset_path` 目录中找到 `train_data.pkl`、`val_data.pkl` 和 `test_data.pkl`。

### 第三步：执行微调

微调过程分为两个阶段：先微调分词器，再微调预测器。两个训练脚本均支持使用 `torchrun` 进行多 GPU 分布式训练。

#### 3.1 微调分词器

此步骤将分词器调整到特定领域的数据分布。

```shell
# 将 NUM_GPUS 替换为你要使用的 GPU 数量（例如 2）
torchrun --standalone --nproc_per_node=NUM_GPUS finetune/train_tokenizer.py
```

最佳分词器检查点将保存到 `config.py` 中配置的路径（由 `save_path` 和 `tokenizer_save_folder_name` 派生）。

#### 3.2 微调预测器

此步骤针对预测任务微调 Kronos 主模型。

```shell
# 将 NUM_GPUS 替换为你要使用的 GPU 数量（例如 2）
torchrun --standalone --nproc_per_node=NUM_GPUS finetune/train_predictor.py
```

最佳预测器检查点将保存到 `config.py` 中配置的路径。

### 第四步：回测评估

最后，运行回测脚本评估微调后的模型。该脚本将加载模型，对测试集进行推理，生成预测信号（如预测价格变化），并运行简单的 Top-K 策略回测。

```shell
# 指定推理使用的 GPU
python finetune/qlib_test.py --device cuda:0
```

脚本将在控制台输出详细的性能分析，并生成一张展示策略相对基准累计收益曲线的图表，类似下图所示：

<p align="center">
    <img src="figures/backtest_result_example.png" alt="回测示例" align="center" width="700px" />
</p>

### 💡 从演示到生产：重要注意事项

- **原始信号与纯 Alpha**：本演示中模型生成的信号是原始预测值。在实际量化工作流中，这些信号通常需要输入组合优化模型，并施加约束以中性化对常见风险因子（如市场 Beta、规模和价值等风格因子）的暴露，从而提炼出**"纯 Alpha"**，提升策略的稳健性。
- **数据处理**：提供的 `QlibDataset` 仅为示例。对于不同的数据源或格式，你需要相应调整数据加载和预处理逻辑。
- **策略与回测复杂度**：此处使用的简单 Top-K 策略仅为基础起点。生产级策略通常包含更复杂的组合构建、动态仓位调整和风险管理逻辑（如止损/止盈规则）。此外，高保真回测应精确模拟交易成本、滑点和市场冲击，以更准确地估算真实世界的绩效。

> **📝 AI 生成注释说明**：请注意，`finetune/` 目录中的许多代码注释由 AI 助手（Gemini 2.5 Pro）生成，仅供解释说明使用。这些注释可能存在不准确之处，请以代码本身的逻辑为准。

---

## 📖 引用

如果你在研究中使用了 Kronos，欢迎引用我们的[论文](https://arxiv.org/abs/2508.02739)：

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

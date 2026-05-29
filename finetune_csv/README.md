# 使用自定义 CSV 数据集对 Kronos 进行微调

本模块提供了一套完整的流程，用于在你自己的 CSV 格式金融数据上微调 Kronos 模型。支持顺序训练（先分词器后预测器）和单独组件训练，并具备完整的分布式训练能力。


## 1. 数据准备

### 必需的数据格式

你的 CSV 文件必须包含以下列：
- `timestamps`：每个数据点的时间戳
- `open`：开盘价
- `high`：最高价
- `low`：最低价
- `close`：收盘价
- `volume`：成交量
- `amount`：成交额

（如无成交量和成交额数据，可填 0）

### 示例数据格式

| timestamps | open | close | high | low | volume | amount |
|------------|------|-------|------|-----|--------|--------|
| 2019/11/26 9:35 | 182.45215 | 184.45215 | 184.95215 | 182.45215 | 15136000 | 0 |
| 2019/11/26 9:40 | 184.35215 | 183.85215 | 184.55215 | 183.45215 | 4433300 | 0 |
| 2019/11/26 9:45 | 183.85215 | 183.35215 | 183.95215 | 182.95215 | 3070900 | 0 |

> **参考**：请查看 `data/HK_ali_09988_kline_5min_all.csv` 了解完整的数据格式示例。


## 2. 配置准备

请编辑正确的数据路径和预训练模型路径，并设置训练参数。

```yaml
# 数据配置
data:
  data_path: "/path/to/your/data.csv"
  lookback_window: 512        # 使用的历史数据点数
  predict_window: 48           # 需要预测的未来点数
  max_context: 512            # 最大上下文长度

...

```
还有其他一些设置，请参见 `configs/config_ali09988_candle-5min.yaml` 中的注释说明。

## 3. 训练

### 方式一：顺序训练（推荐）

`train_sequential.py` 脚本可自动处理完整的训练流程：

```bash
# 完整训练（分词器 + 预测器）
python train_sequential.py --config configs/config_ali09988_candle-5min.yaml

# 跳过已存在的模型
python train_sequential.py --config configs/config_ali09988_candle-5min.yaml --skip-existing

# 仅训练分词器
python train_sequential.py --config configs/config_ali09988_candle-5min.yaml --skip-basemodel

# 仅训练预测器
python train_sequential.py --config configs/config_ali09988_candle-5min.yaml --skip-tokenizer
```

### 方式二：单独组件训练

分别训练各组件以获得更精细的控制：

```bash
# 第一步：训练分词器
python finetune_tokenizer.py --config configs/config_ali09988_candle-5min.yaml

# 第二步：训练预测器（需要已微调的分词器）
python finetune_base_model.py --config configs/config_ali09988_candle-5min.yaml
```

### DDP 分布式训练

在多 GPU 上加速训练：

```bash
# 设置通信后端（NVIDIA GPU 使用 nccl，CPU/混合使用 gloo）
DIST_BACKEND=nccl \
torchrun --standalone --nproc_per_node=8 train_sequential.py --config configs/config_ali09988_candle-5min.yaml
```

## 4. 训练结果

训练过程会生成以下输出：

### 模型检查点
- **分词器**：保存至 `{base_save_path}/{exp_name}/tokenizer/best_model/`
- **预测器**：保存至 `{base_save_path}/{exp_name}/basemodel/best_model/`

### 训练日志
- **控制台输出**：实时训练进度和指标
- **日志文件**：详细日志保存至 `{base_save_path}/logs/`
- **验证追踪**：根据验证损失保存最佳模型

## 5. 预测可视化

以下图片展示了在阿里巴巴（港股）数据上的训练结果示例：

![训练结果 1](examples/HK_ali_09988_kline_5min_all_historical_20250919_073929.png)

![训练结果 2](examples/HK_ali_09988_kline_5min_all_historical_20250919_073944.png)

![训练结果 3](examples/HK_ali_09988_kline_5min_all_historical_20250919_074012.png)

![训练结果 4](examples/HK_ali_09988_kline_5min_all_historical_20250919_074042.png)

![训练结果 5](examples/HK_ali_09988_kline_5min_all_historical_20250919_074251.png)

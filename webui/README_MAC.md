# Kronos WebUI - macOS 打包与使用说明

## 一、构建环境要求

| 项目 | 要求 |
|------|------|
| 操作系统 | macOS 12 Monterey 或更高版本 |
| 芯片 | Apple Silicon (M1/M2/M3) 或 Intel x86_64 |
| Python | 3.11（推荐用 Homebrew 安装） |
| 磁盘空间 | 构建时约需 5 GB，最终 .app 约 1-2 GB |

## 二、构建步骤（在 Mac 上执行）

### 1. 安装依赖

```bash
# 安装 Homebrew（已安装可跳过）
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 安装 Python 3.11
brew install python@3.11

# 安装精美 DMG 工具（可选）
brew install create-dmg

# 安装项目 Python 依赖
cd /path/to/Kronos/webui
pip3 install -r requirements.txt   # 若存在
pip3 install pyinstaller flask flask-cors torch pandas numpy plotly \
             scikit-learn scipy huggingface_hub safetensors akshare tushare
```

### 2. 执行打包

```bash
cd /path/to/Kronos/webui
chmod +x build_mac.sh
./build_mac.sh
```

打包完成后生成：
- `dist/KronosWebUI.app` — 可直接运行的应用包
- `dist/KronosWebUI.dmg` — 供分发的安装镜像

---

## 三、用户安装说明

1. 双击 `KronosWebUI.dmg` 打开安装镜像
2. 将 `KronosWebUI` 图标拖入 `Applications` 文件夹
3. 打开 Finder → 应用程序 → 双击 `KronosWebUI`

### 首次运行提示（Gatekeeper）

由于应用未经 Apple 公证，macOS 可能弹出安全提示：

**方法 A（推荐）**：
右键点击 `KronosWebUI.app` → 选择「打开」→ 在弹窗中点「打开」

**方法 B**：
在终端执行：
```bash
xattr -rd com.apple.quarantine /Applications/KronosWebUI.app
```
然后正常双击运行。

---

## 四、用户数据存储位置

| 类型 | 路径 |
|------|------|
| 预测结果 | `~/Library/Application Support/KronosWebUI/prediction_results/` |
| 上传数据 | `~/Library/Application Support/KronosWebUI/data/` |
| Tushare Token | App 内设置界面保存 |

---

## 五、注意事项

- **Apple Silicon (M 系列芯片)**：需在 Mac 上原生构建，不能用 Windows/Linux 交叉编译
- **Intel 与 ARM**：在 M1+ 上构建的 .app 可通过 Rosetta 2 在 Intel Mac 上运行，反之亦然
- **模型文件**：确保构建前 `~/.cache/huggingface/hub` 内已有下载好的 Kronos 模型文件

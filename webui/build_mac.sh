#!/bin/bash
# ================================================
#   Kronos WebUI 打包工具 - macOS 版
#   生成 .app + DMG 安装镜像
# ================================================

set -e
cd "$(dirname "$0")"

echo "================================================"
echo "  Kronos WebUI 打包工具 (macOS)"
echo "================================================"
echo ""

# ── 检查 Python ──────────────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "[错误] 未找到 python3，请先安装 Python 3.11+"
    echo "       推荐使用：brew install python@3.11"
    exit 1
fi
PYTHON=python3
echo "[OK] Python: $($PYTHON --version)"

# ── 检查 PyInstaller ─────────────────────────────────────────────────
if ! $PYTHON -c "import PyInstaller" &>/dev/null; then
    echo "[提示] 正在安装 PyInstaller..."
    pip3 install pyinstaller
fi
echo "[OK] PyInstaller 已就绪"

# ── 检查 create-dmg（可选）──────────────────────────────────────────
HAS_CREATE_DMG=0
if command -v create-dmg &>/dev/null; then
    HAS_CREATE_DMG=1
    echo "[OK] create-dmg 已找到，将生成精美 DMG"
else
    echo "[提示] 未找到 create-dmg，将使用系统 hdiutil 生成基础 DMG"
    echo "       如需精美 DMG 可执行：brew install create-dmg"
fi

# ── 步骤 1/3：清理旧输出 ─────────────────────────────────────────────
echo ""
echo "── 步骤 1/3：清理旧的打包输出 ──────────────────────────────────"
rm -rf dist/KronosWebUI dist/KronosWebUI.app dist/KronosWebUI.dmg build/
echo "[OK] 清理完成"

# ── 步骤 2/3：PyInstaller 打包 ───────────────────────────────────────
echo ""
echo "── 步骤 2/3：PyInstaller 打包（预计 10-30 分钟）────────────────"
$PYTHON -m PyInstaller kronos_webui_mac.spec --noconfirm
echo "[OK] PyInstaller 打包完成 → dist/KronosWebUI.app"

# ── 步骤 3/3：打包为 DMG ────────────────────────────────────────────
echo ""
echo "── 步骤 3/3：生成 DMG 安装镜像 ────────────────────────────────"

APP_PATH="dist/KronosWebUI.app"
DMG_PATH="dist/KronosWebUI.dmg"
DMG_TMP="dist/KronosWebUI_tmp.dmg"
VOLNAME="Kronos WebUI"

if [ $HAS_CREATE_DMG -eq 1 ]; then
    # 使用 create-dmg 生成带背景的精美 DMG
    create-dmg \
        --volname "$VOLNAME" \
        --window-size 540 380 \
        --icon-size 128 \
        --icon "KronosWebUI.app" 130 160 \
        --app-drop-link 400 160 \
        --hide-extension "KronosWebUI.app" \
        "$DMG_PATH" \
        "$APP_PATH"
else
    # 使用系统 hdiutil 生成基础 DMG
    STAGING_DIR="dist/dmg_staging"
    rm -rf "$STAGING_DIR"
    mkdir -p "$STAGING_DIR"
    cp -R "$APP_PATH" "$STAGING_DIR/"

    # 创建临时可读写 DMG，然后转为只读压缩
    hdiutil create \
        -srcfolder "$STAGING_DIR" \
        -volname "$VOLNAME" \
        -fs HFS+ \
        -fsargs "-c c=64,a=16,b=16" \
        -format UDRW \
        -size 2g \
        "$DMG_TMP"

    # 挂载并添加 Applications 链接
    DEVICE=$(hdiutil attach -readwrite -noverify -noautoopen "$DMG_TMP" | \
             egrep '^/dev/' | sed 1q | awk '{print $1}')
    MOUNT_POINT="/Volumes/$VOLNAME"

    ln -sf /Applications "$MOUNT_POINT/Applications" 2>/dev/null || true
    sync
    hdiutil detach "$DEVICE"

    # 转换为只读压缩格式
    hdiutil convert "$DMG_TMP" -format UDZO -imagekey zlib-level=9 -o "$DMG_PATH"
    rm -f "$DMG_TMP"
    rm -rf "$STAGING_DIR"
fi

echo ""
echo "================================================"
echo "  打包完成！"
echo ""
echo "  .app 应用：$APP_PATH"
echo "  DMG 镜像：$DMG_PATH"
echo ""
echo "  分发方式："
echo "  - 将 KronosWebUI.dmg 发给用户"
echo "  - 双击 DMG，拖动 KronosWebUI.app 到 Applications"
echo "  - 双击 Applications 中的 KronosWebUI 启动"
echo "================================================"

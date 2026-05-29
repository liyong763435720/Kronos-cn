# -*- mode: python ; coding: utf-8 -*-
"""
KronosWebUI PyInstaller 打包配置 - macOS 版
生成 .app 应用包 + DMG 安装镜像
运行方式：pyinstaller kronos_webui_mac.spec
"""

import os
from PyInstaller.utils.hooks import collect_all, collect_data_files

# ── 路径定义 ────────────────────────────────────────────────────────────
WEBUI_DIR  = os.path.dirname(os.path.abspath(SPEC))          # webui/
ROOT_DIR   = os.path.dirname(WEBUI_DIR)                       # Kronos/
HF_CACHE   = os.path.expanduser('~/.cache/huggingface/hub')   # 本机 HF 缓存

# ── 收集依赖数据文件 ────────────────────────────────────────────────────
datas = []
binaries = []
hiddenimports = []

# torch
torch_datas, torch_binaries, torch_hidden = collect_all('torch')
datas     += torch_datas
binaries  += torch_binaries
hiddenimports += torch_hidden

# Flask 模板引擎
jinja_datas, _, jinja_hidden = collect_all('jinja2')
datas += jinja_datas
hiddenimports += jinja_hidden

# plotly
datas += collect_data_files('plotly')

# huggingface_hub
hf_datas, _, hf_hidden = collect_all('huggingface_hub')
datas += hf_datas
hiddenimports += hf_hidden

# safetensors
datas += collect_data_files('safetensors')

# einops（model/module.py 依赖）
einops_datas, einops_bins, einops_hidden = collect_all('einops')
datas += einops_datas
hiddenimports += einops_hidden

# ── 项目自身文件 ────────────────────────────────────────────────────────
# Flask 模板
datas += [(os.path.join(WEBUI_DIR, 'templates'), 'templates')]

# Kronos model 包（通过 pathex + hiddenimports 编译进二进制，无需 datas）

# HuggingFace 模型缓存（含全部模型，约 557MB）
if os.path.isdir(HF_CACHE):
    datas += [(HF_CACHE, 'hf_home/hub')]

# ── 隐式导入补全 ────────────────────────────────────────────────────────
hiddenimports += [
    'flask', 'flask_cors',
    'pandas', 'numpy', 'plotly', 'plotly.graph_objects', 'plotly.utils',
    'sklearn', 'scipy',
    'huggingface_hub', 'safetensors', 'safetensors.torch',
    'model', 'model.kronos', 'model.module',
    'einops',                          # model/module.py 依赖
    'tqdm', 'tqdm.auto',               # model/kronos.py 依赖
    'akshare', 'tushare',
    'werkzeug', 'werkzeug.serving', 'werkzeug.middleware',
    'jinja2', 'markupsafe', 'click',
    'engineio', 'socketio',
]

# ── Analysis ────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(WEBUI_DIR, 'launcher_mac.py')],
    pathex=[ROOT_DIR, WEBUI_DIR],
    binaries=binaries,
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib', 'IPython', 'notebook', 'jupyter',
        'tkinter', 'PyQt5', 'PyQt6', 'wx',
        'test', 'tests', 'unittest',
    ],
    noarchive=False,
)

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='KronosWebUI',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,             # macOS 上 UPX 兼容性差，关闭
    console=False,         # macOS .app 不显示终端窗口
    icon=os.path.join(WEBUI_DIR, 'icon.icns') if os.path.exists(os.path.join(WEBUI_DIR, 'icon.icns')) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=False,
    upx_exclude=[],
    name='KronosWebUI',
)

# ── macOS .app 包 ────────────────────────────────────────────────────────
app = BUNDLE(
    coll,
    name='KronosWebUI.app',
    icon=os.path.join(WEBUI_DIR, 'icon.icns') if os.path.exists(os.path.join(WEBUI_DIR, 'icon.icns')) else None,
    bundle_identifier='com.kronos.webui',
    info_plist={
        'CFBundleName': 'KronosWebUI',
        'CFBundleDisplayName': 'Kronos WebUI',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSHighResolutionCapable': True,
        'LSUIElement': False,         # 在 Dock 中显示图标
        'NSRequiresAquaSystemAppearance': False,
    },
)

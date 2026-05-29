# -*- mode: python ; coding: utf-8 -*-
"""
KronosWebUI PyInstaller 打包配置
运行方式：pyinstaller kronos_webui.spec
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

# ── 项目自身文件 ────────────────────────────────────────────────────────
# Flask 模板
datas += [(os.path.join(WEBUI_DIR, 'templates'), 'templates')]

# Kronos model 包
datas += [(os.path.join(ROOT_DIR, 'model'), 'model')]

# HuggingFace 模型缓存（含全部模型，约 557MB）
datas += [(HF_CACHE, 'hf_home/hub')]

# ── 隐式导入补全 ────────────────────────────────────────────────────────
hiddenimports += [
    'flask', 'flask_cors',
    'pandas', 'numpy', 'plotly', 'plotly.graph_objects', 'plotly.utils',
    'sklearn', 'scipy',
    'huggingface_hub', 'safetensors', 'safetensors.torch',
    'model', 'model.kronos', 'model.module',
    'akshare', 'tushare',
    'werkzeug', 'werkzeug.serving', 'werkzeug.middleware',
    'jinja2', 'markupsafe', 'click',
    'engineio', 'socketio',
]

# ── Analysis ────────────────────────────────────────────────────────────
a = Analysis(
    [os.path.join(WEBUI_DIR, 'launcher.py')],
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
    upx=True,
    console=True,          # 保留控制台窗口，方便看日志/错误
    icon=None,             # 有 ico 文件可填路径，如 'icon.ico'
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='KronosWebUI',    # 输出目录名：dist/KronosWebUI/
)

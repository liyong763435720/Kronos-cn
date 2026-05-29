"""
PyInstaller 打包入口 - macOS 版
.app 包内路径与 Windows 不同，需要特殊处理。
"""
import os
import sys
import platform

# ── 1. 确定运行根目录 ──────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后，所有资源解压在 sys._MEIPASS
    BASE_DIR = sys._MEIPASS
    # macOS .app 中 executable 位于 Contents/MacOS/KronosWebUI
    # 用户数据放在 ~/Library/Application Support/KronosWebUI
    APP_SUPPORT = os.path.expanduser('~/Library/Application Support/KronosWebUI')
    APP_DIR = APP_SUPPORT
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# ── 2. 将 HF 缓存指向打包目录内的 hf_home ────────────────────────────
os.environ['HF_HOME']               = os.path.join(BASE_DIR, 'hf_home')
os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.join(BASE_DIR, 'hf_home', 'hub')
os.environ['TRANSFORMERS_CACHE']    = os.path.join(BASE_DIR, 'hf_home', 'hub')

# ── 3. 把项目根目录加入 sys.path ──────────────────────────────────────
sys.path.insert(0, BASE_DIR)

# ── 4. 重定向用户数据目录（预测结果、上传数据）────────────────────────
os.environ['KRONOS_DATA_DIR']    = os.path.join(APP_DIR, 'data')
os.environ['KRONOS_RESULTS_DIR'] = os.path.join(APP_DIR, 'prediction_results')
os.makedirs(os.environ['KRONOS_DATA_DIR'],    exist_ok=True)
os.makedirs(os.environ['KRONOS_RESULTS_DIR'], exist_ok=True)

# ── 5. Flask template 路径 ────────────────────────────────────────────
os.environ['KRONOS_TEMPLATE_DIR'] = os.path.join(BASE_DIR, 'templates')

# ── 6. macOS：解除 Apple 对未签名 App 的隔离属性（首次运行）──────────
if platform.system() == 'Darwin' and getattr(sys, 'frozen', False):
    try:
        import subprocess
        exe_path = os.path.dirname(os.path.dirname(os.path.dirname(sys.executable)))
        subprocess.run(
            ['xattr', '-rd', 'com.apple.quarantine', exe_path],
            capture_output=True
        )
    except Exception:
        pass   # 非致命，忽略

# ── 7. 启动 Flask + 自动打开浏览器 ───────────────────────────────────
import threading
import webbrowser
import time

PORT = 7070

def open_browser():
    time.sleep(2.5)
    webbrowser.open(f'http://localhost:{PORT}')

threading.Thread(target=open_browser, daemon=True).start()

# 导入并启动 Flask app
import app as flask_app
flask_app.app.run(debug=False, host='127.0.0.1', port=PORT)

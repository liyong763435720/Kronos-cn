"""
PyInstaller 打包入口。
必须在最顶部设置 HF_HOME，确保 huggingface_hub 加载本地模型缓存。
"""
import os
import sys

# ── 1. 确定运行根目录 ──────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    # PyInstaller 打包后，所有资源解压在 sys._MEIPASS
    BASE_DIR = sys._MEIPASS
    # 应用程序实际所在目录（exe 旁边），用于读写用户数据
    APP_DIR = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# ── 2. 将 HF 缓存指向打包目录内的 hf_home ────────────────────────────
os.environ['HF_HOME']            = os.path.join(BASE_DIR, 'hf_home')
os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.join(BASE_DIR, 'hf_home', 'hub')
os.environ['TRANSFORMERS_CACHE']    = os.path.join(BASE_DIR, 'hf_home', 'hub')

# ── 3. 把项目根目录加入 sys.path（让 model 包可以 import）───────────────
sys.path.insert(0, BASE_DIR)

# ── 4. 重定向用户数据目录到 exe 旁边（data / prediction_results）──────
os.environ['KRONOS_DATA_DIR']    = os.path.join(APP_DIR, 'data')
os.environ['KRONOS_RESULTS_DIR'] = os.path.join(APP_DIR, 'prediction_results')
os.makedirs(os.environ['KRONOS_DATA_DIR'],    exist_ok=True)
os.makedirs(os.environ['KRONOS_RESULTS_DIR'], exist_ok=True)

# ── 5. Flask template / static 路径 ──────────────────────────────────
os.environ['KRONOS_TEMPLATE_DIR'] = os.path.join(BASE_DIR, 'templates')

# ── 6. 启动 Flask ──────────────────────────────────────────────────────
import threading, webbrowser, time

def open_browser():
    time.sleep(2)
    webbrowser.open('http://localhost:7070')

threading.Thread(target=open_browser, daemon=True).start()

# 导入 app（app.py 会读上面设置的环境变量）
import app as flask_app
flask_app.app.run(debug=False, host='127.0.0.1', port=7070)

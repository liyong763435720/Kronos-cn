"""
PyInstaller 打包入口。
必须在最顶部设置 HF_HOME，确保 huggingface_hub 加载本地模型缓存。
"""
import os
import sys
import traceback

# ── 1. 确定运行根目录 ──────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# ── 2. 错误日志路径（写到 exe 同级目录，方便排查）────────────────────
LOG_FILE = os.path.join(APP_DIR, 'kronos_error.log')

def log(msg):
    """同时输出到控制台和日志文件。"""
    print(msg, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass

def fatal(msg):
    """致命错误：写日志后等待用户按键再退出，避免闪退。"""
    log('\n[FATAL] ' + msg)
    log(f'详细日志请查看：{LOG_FILE}')
    if getattr(sys, 'frozen', False):
        input('\n按 Enter 键退出...')
    sys.exit(1)

try:
    # ── 3. 将 HF 缓存指向打包目录内的 hf_home ──────────────────────────
    os.environ['HF_HOME']               = os.path.join(BASE_DIR, 'hf_home')
    os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.join(BASE_DIR, 'hf_home', 'hub')
    os.environ['TRANSFORMERS_CACHE']    = os.path.join(BASE_DIR, 'hf_home', 'hub')

    # ── 4. 把项目根目录加入 sys.path（让 model 包可以 import）─────────
    sys.path.insert(0, BASE_DIR)

    # ── 5. 重定向用户数据目录到 exe 旁边 ────────────────────────────────
    os.environ['KRONOS_DATA_DIR']    = os.path.join(APP_DIR, 'data')
    os.environ['KRONOS_RESULTS_DIR'] = os.path.join(APP_DIR, 'prediction_results')
    os.makedirs(os.environ['KRONOS_DATA_DIR'],    exist_ok=True)
    os.makedirs(os.environ['KRONOS_RESULTS_DIR'], exist_ok=True)

    # ── 6. Flask template 路径 ───────────────────────────────────────────
    os.environ['KRONOS_TEMPLATE_DIR'] = os.path.join(BASE_DIR, 'templates')

    log(f'[OK] BASE_DIR = {BASE_DIR}')
    log(f'[OK] APP_DIR  = {APP_DIR}')

    # ── 7. 启动 Flask + 自动打开浏览器 ──────────────────────────────────
    import threading
    import webbrowser
    import time

    PORT = 7070

    def open_browser():
        time.sleep(2.5)
        webbrowser.open(f'http://localhost:{PORT}')

    threading.Thread(target=open_browser, daemon=True).start()

    log(f'[OK] 正在启动 Flask，端口 {PORT}...')
    import app as flask_app
    flask_app.app.run(debug=False, host='127.0.0.1', port=PORT)

except Exception:
    fatal(traceback.format_exc())

"""
PyInstaller 打包入口 - Windows 版
"""
import os
import sys
import traceback
import socket
import time
import threading

# ── 1. 确定运行根目录 ──────────────────────────────────────────────────
if getattr(sys, 'frozen', False):
    BASE_DIR = sys._MEIPASS
    APP_DIR  = os.path.dirname(sys.executable)
else:
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    APP_DIR  = BASE_DIR

# ── 2. 错误日志（写到 exe 同级目录）──────────────────────────────────
LOG_FILE = os.path.join(APP_DIR, 'kronos_error.log')

# 清空上次日志
try:
    with open(LOG_FILE, 'w', encoding='utf-8') as f:
        f.write('')
except Exception:
    pass

def log(msg):
    print(msg, flush=True)
    try:
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(msg + '\n')
    except Exception:
        pass

def fatal(msg):
    log('\n[FATAL ERROR]\n' + msg)
    log(f'\n完整日志：{LOG_FILE}')
    input('\n按 Enter 键退出...')
    sys.exit(1)

try:
    log('=' * 50)
    log('Kronos WebUI 启动中...')
    log(f'BASE_DIR = {BASE_DIR}')
    log(f'APP_DIR  = {APP_DIR}')

    # ── 3. 用户数据目录 ───────────────────────────────────────────────
    USER_DATA   = os.path.join(os.environ.get('APPDATA', os.path.expanduser('~')), 'KronosWebUI')
    DATA_DIR    = os.path.join(USER_DATA, 'data')
    RESULTS_DIR = os.path.join(USER_DATA, 'prediction_results')
    for d in [DATA_DIR, RESULTS_DIR]:
        os.makedirs(d, exist_ok=True)

    os.environ['KRONOS_DATA_DIR']     = DATA_DIR
    os.environ['KRONOS_RESULTS_DIR']  = RESULTS_DIR
    os.environ['KRONOS_TEMPLATE_DIR'] = os.path.join(BASE_DIR, 'templates')
    log(f'[OK] 用户数据目录：{USER_DATA}')

    # ── 4. 模型目录：优先内置（离线），否则联网下载 ──────────────────
    BUNDLED_HF = os.path.join(BASE_DIR, 'hf_home')
    USER_HF    = os.path.join(USER_DATA, 'hf_home')

    if os.path.isdir(os.path.join(BUNDLED_HF, 'hub')):
        os.environ['HF_HOME']                  = BUNDLED_HF
        os.environ['HUGGINGFACE_HUB_CACHE']    = os.path.join(BUNDLED_HF, 'hub')
        os.environ['TRANSFORMERS_CACHE']       = os.path.join(BUNDLED_HF, 'hub')
        os.environ['HUGGINGFACE_HUB_OFFLINE']  = '1'
        log(f'[OK] 使用内置模型（离线模式）：{BUNDLED_HF}')
    else:
        os.makedirs(USER_HF, exist_ok=True)
        os.environ['HF_HOME']               = USER_HF
        os.environ['HUGGINGFACE_HUB_CACHE'] = os.path.join(USER_HF, 'hub')
        os.environ['TRANSFORMERS_CACHE']    = os.path.join(USER_HF, 'hub')
        os.environ.setdefault('HF_ENDPOINT', 'https://hf-mirror.com')
        log(f'[OK] 无内置模型，使用用户目录（在线下载）：{USER_HF}')

    # ── 4. 修复 frozen 环境下 app.py 的 __file__ 路径问题 ────────────
    sys.path.insert(0, BASE_DIR)
    # app.py 里有 os.path.abspath(__file__)，frozen 后需要把工作目录
    # 设为 BASE_DIR，否则相对路径解析出错
    os.chdir(BASE_DIR)

    # ── 5. 检测端口是否被占用 ────────────────────────────────────────
    PORT = 7070
    def is_port_in_use(port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('127.0.0.1', port)) == 0

    if is_port_in_use(PORT):
        log(f'[警告] 端口 {PORT} 已被占用，尝试端口 7071...')
        PORT = 7071
        if is_port_in_use(PORT):
            fatal(f'端口 {PORT} 也被占用，请关闭占用端口的程序后重试。')

    log(f'[OK] 使用端口 {PORT}')

    # ── 6. 等待 Flask 就绪后再开浏览器 ──────────────────────────────
    def wait_and_open_browser():
        url = f'http://localhost:{PORT}'
        for _ in range(30):           # 最多等 15 秒
            time.sleep(0.5)
            try:
                with socket.create_connection(('127.0.0.1', PORT), timeout=1):
                    break
            except OSError:
                continue
        import webbrowser
        webbrowser.open(url)
        log(f'[OK] 浏览器已打开：{url}')

    threading.Thread(target=wait_and_open_browser, daemon=True).start()

    # ── 7. 启动 Flask ────────────────────────────────────────────────
    log('[OK] 正在导入应用模块...')
    import app as flask_app
    log(f'[OK] Flask 启动，访问 http://localhost:{PORT}')
    flask_app.app.run(debug=False, host='127.0.0.1', port=PORT, use_reloader=False)

except Exception:
    fatal(traceback.format_exc())

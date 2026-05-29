"""
CI 构建脚本：下载所有 Kronos 模型到本地 HF 缓存，供 PyInstaller 打包使用。
"""
from huggingface_hub import snapshot_download

MODELS = [
    'NeoQuasar/Kronos-Tokenizer-2k',
    'NeoQuasar/Kronos-mini',
    'NeoQuasar/Kronos-Tokenizer-base',
    'NeoQuasar/Kronos-small',
    'NeoQuasar/Kronos-base',
]

for repo in MODELS:
    print(f'Downloading {repo}...', flush=True)
    snapshot_download(repo_id=repo)
    print(f'Done: {repo}', flush=True)

print('All models downloaded.')

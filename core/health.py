import requests
from config import FORGE_URL

def check_forge_health():
    """轻量心跳检测，快速发现 Forge 异常"""
    try:
        resp = requests.get(f"{FORGE_URL}/sdapi/v1/sd-models", timeout=5)
        return resp.status_code == 200
    except Exception as e:
        print(f"⚠️ Forge 心跳异常: {e}")
        return False

import os
from dotenv import load_dotenv

load_dotenv()


def _get_env(name: str, default=None):
    val = os.getenv(name)
    return default if val is None or val == "" else val


def _get_int(name: str, default: int) -> int:
    try:
        return int(_get_env(name, default))
    except Exception:
        return default


def _get_float(name: str, default: float) -> float:
    try:
        return float(_get_env(name, default))
    except Exception:
        return default


# Forge / Control loop
FORGE_URL = _get_env("FORGE_URL", "http://127.0.0.1:7860")
FORGE_TIMEOUT = _get_int("FORGE_TIMEOUT", 90)
FORGE_HEARTBEAT_INTERVAL = _get_int("FORGE_HEARTBEAT_INTERVAL", 5)

TARGET_SCORE = _get_float("TARGET_SCORE", 0.90)
MAX_ITERATIONS = _get_int("MAX_ITERATIONS", 15)
CONVERGENCE_PATIENCE = _get_int("CONVERGENCE_PATIENCE", 3)
CONVERGENCE_THRESHOLD = _get_float("CONVERGENCE_THRESHOLD", 0.005)

# Creative Brain (DeepSeek)
DEEPSEEK_MODEL = _get_env("DEEPSEEK_MODEL", "deepseek-ai/DeepSeek-V3")
DEEPSEEK_MAX_RETRIES = _get_int("DEEPSEEK_MAX_RETRIES", 5)
DEEPSEEK_TIMEOUT = _get_int("DEEPSEEK_TIMEOUT", 30)

# Judge (Qwen)
JUDGE_MODEL_NAME = _get_env("JUDGE_MODEL_NAME", "Pro/Qwen/Qwen2.5-VL-7B-Instruct")
JUDGE_MAX_RETRIES = _get_int("JUDGE_MAX_RETRIES", 3)
JUDGE_TIMEOUT = _get_int("JUDGE_TIMEOUT", 30)

# Logging
LOG_LEVEL = _get_env("LOG_LEVEL", "INFO")
LOG_FILE = _get_env("LOG_FILE", "pygmalion.log")

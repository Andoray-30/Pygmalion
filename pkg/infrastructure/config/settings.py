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

# Judge (Qwen) - 多模型评分池以充分利用2000次/天免费额度
# 每个模型限额500次/天，轮换使用4个模型可达2000次/天
# 📊 评分模型池 - 72B+多模态模型（精准度和推理能力均衡）
JUDGE_MODELS = {
    "primary": "Qwen/Qwen2.5-VL-72B-Instruct",      # 🥇 主力：VL-72B (当前)
    "backup1": "Qwen/QVQ-72B-Preview",              # 🥈 备用1：QVQ-72B (量化视觉)
    "backup2": "OpenGVLab/InternVL3_5-241B-A28B",   # 🥉 备用2：241B (超强推理)
    "backup3": "Qwen/Qwen3-VL-235B-A22B-Instruct"   # 🎖️ 备用3：235B (新一代)
}

# 当前使用的评分模型（动态轮换）
JUDGE_MODEL_NAME = _get_env("JUDGE_MODEL_NAME", JUDGE_MODELS["primary"])
JUDGE_MAX_RETRIES = _get_int("JUDGE_MAX_RETRIES", 3)
JUDGE_TIMEOUT = _get_int("JUDGE_TIMEOUT", 30)

# 🔄 模型轮换配置
JUDGE_MODEL_ROTATION_ENABLED = _get_env("JUDGE_MODEL_ROTATION_ENABLED", "true").lower() == "true"
JUDGE_MODEL_DAILY_LIMIT = _get_int("JUDGE_MODEL_DAILY_LIMIT", 500)  # 单个模型每日限制
JUDGE_MODEL_ROTATION_INTERVAL = _get_int("JUDGE_MODEL_ROTATION_INTERVAL", 150)  # 每150次评分轮换

# Logging
LOG_LEVEL = _get_env("LOG_LEVEL", "INFO")
LOG_FILE = _get_env("LOG_FILE", "pygmalion.log")

# ⚡ 三底模配置 (Triple-Model Strategy)
# 策略：快速探索 + 风格分流（真实感/动漫风格）
BASE_MODELS = {
    # 🚀 探索模式：SDXL Turbo (1步极速生成)
    # 用途：0.3秒/张 快速试错构图和提示词
    # 架构：SDXL 1024×1024
    # 适用：所有场景的初步探索
    "PREVIEW": _get_env("PREVIEW_MODEL", "sd_xl_turbo_1.0_fp16.safetensors"),
    
    # 🎨 真实感渲染：Juggernaut XL Ragnarok (4-6步摄影级)
    # 用途：8-10秒/张 摄影级真实感输出
    # 擅长：人像、产品、食物、建筑、风景摄影
    # 架构：SDXL 1024×1024
    "RENDER": _get_env("RENDER_MODEL", "juggernautXL_ragnarokBy.safetensors"),
    
    # 🎭 动漫风格：Animagine XL V3.1
    # 用途：6-8秒/张 高质量动漫/插画风格
    # 擅长：动漫角色、游戏CG、漫画、幻想场景、可爱风格
    # 架构：SDXL 1024×1024
    "ANIME": _get_env("ANIME_MODEL", "animagineXLV31_v31.safetensors")
}

# 🔧 模型切换阈值
MODEL_SWITCH_SCORE_THRESHOLD = _get_float("MODEL_SWITCH_SCORE_THRESHOLD", 0.78)
MODEL_SWITCH_MIN_ITERATIONS = _get_int("MODEL_SWITCH_MIN_ITERATIONS", 5)  # 最少探索5次才允许切换

# 🎨 LoRA 资源库 (分为 STYLES 和 ENHANCERS)
# 已根据 Forge/webui/models/Lora 目录下的实际模型进行同步
LORA_LIBRARY = {
    "STYLES": {
        "CYBERPUNK": {"file": "cyberpunk_edgerunners_style_sdxl", "weight": 0.8, "trigger": "cyberpunk style, neon lights"},
        "ANIME_LINEART": {"file": "LineAniRedmondV2-Lineart-LineAniAF", "weight": 0.7, "trigger": "lineart, cel shaded"},
        "PHOTOREALISTIC": {"file": "style_lora_realis", "weight": 0.8, "trigger": "raw photo, highly detailed"},
        "STUDIO_PORTRAIT": {"file": "studio_portrait_xl", "weight": 0.75, "trigger": "studio lighting, bokeh"}
    },
    "ENHANCERS": {
        "DETAIL": {"file": "xl_more_art-full_v1", "weight": 0.5, "trigger": "detailed, masterpiece"},
        "LIGHTING": {"file": "LowRA", "weight": 0.4, "trigger": "high contrast, atmospheric lighting"},
        "HANDS": {"file": "Hands v2.1", "weight": 0.6, "trigger": "perfect hands, highly detailed hands"},
        "ARTIFACTS": {"file": "ARTifacts", "weight": 0.5, "trigger": "high quality, sharp focus"}
    }
}

# 🎯 模型特定参数配置
MODEL_CONFIGS = {
    "PREVIEW": {
        "steps": 1,           # SDXL Turbo 1步极速（无需多步）
        "cfg_scale": 1.0,     # CFG=1 SDXL Turbo标准值
        "sampler": "DPM++ 2M Karras",  # SDXL推荐采样器
        "scheduler": "Karras",
        "enable_hr": False    # 探索期不开HR节省时间
    },
    "RENDER": {
        "steps": 20,           # 提高步数以获得更高画质，解决模糊问题
        "cfg_scale": 7.0,     # 标准 CFG 值提高色彩对比度
        "sampler": "DPM++ 2M Karras",  # SDXL推荐采样器
        "scheduler": "Karras",
        "enable_hr": True,    # HR高清处理激活
        "hr_scale": 1.5,      # 1.5倍放大更稳健
        "hr_second_pass_steps": 10,  # 更多重绘步数
        "denoising_strength": 0.4
    },
    "ANIME": {
        "steps": 28,          # Animagine 推荐步数（20-30最优）
        "cfg_scale": 7.0,     # 动漫模型推荐CFG值
        "sampler": "Euler a",  # 动漫风格推荐采样器
        "scheduler": "Normal",
        "enable_hr": True,    # 动漫细节需要HR
        "hr_scale": 1.5,      # 1.5倍放大（保持线条清晰）
        "hr_second_pass_steps": 15,
        "denoising_strength": 0.5
    }
}

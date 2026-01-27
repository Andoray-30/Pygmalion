import os
import time
import json
import signal
import datetime
from typing import Dict, List
from openai import OpenAI

DEFAULT_BASE_URL = "https://api-inference.modelscope.cn/v1"

def _get_token() -> str:
    return os.getenv("MODELSCOPE_API_KEY") or os.getenv("MODELSCOPE_ACCESS_TOKEN") or os.getenv("ACCESS_TOKEN")

def _categorize(model_id: str) -> str:
    mid = model_id.lower()
    if any(k in mid for k in ["qwen", "llama", "deepseek", "mistral", "glm", "yi"]):
        return "llm"
    if any(k in mid for k in ["vl", "multimodal", "vision-language"]):
        return "multimodal"
    if any(k in mid for k in ["diffusion", "stable-diffusion", "sdxl", "flux", "image"]):
        return "image"
    if any(k in mid for k in ["tts", "vits", "bark", "speech", "asr"]):
        return "audio"
    if any(k in mid for k in ["embedding", "text-embedding"]):
        return "embedding"
    return "other"

def list_models_once(api_key: str, base_url: str = DEFAULT_BASE_URL) -> Dict:
    client = OpenAI(api_key=api_key, base_url=base_url)
    models = client.models.list()

    data = [m.id for m in getattr(models, "data", [])]
    grouped: Dict[str, List[str]] = {}
    for mid in data:
        cat = _categorize(mid)
        grouped.setdefault(cat, []).append(mid)

    snapshot = {
        "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
        "count": len(data),
        "base_url": base_url,
        "groups": {k: sorted(v) for k, v in grouped.items()},
        "all": sorted(data),
    }
    return snapshot

def save_snapshot(snapshot: Dict, output_dir: str) -> str:
    os.makedirs(output_dir, exist_ok=True)
    ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(output_dir, f"modelscope_models_{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    latest = os.path.join(output_dir, "latest.json")
    with open(latest, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)
    return path

_stop = False

def _handle_sigint(signum, frame):
    global _stop
    _stop = True

signal.signal(signal.SIGINT, _handle_sigint)

def run(interval_sec: int = 1800, output_dir: str = "models_snapshot", base_url: str = DEFAULT_BASE_URL, print_console: bool = True):
    token = _get_token()
    if not token:
        raise RuntimeError("缺少 MODELSCOPE_API_KEY / MODELSCOPE_ACCESS_TOKEN，请在环境变量或 .env 中配置")

    while not _stop:
        try:
            snapshot = list_models_once(api_key=token, base_url=base_url)
            save_path = save_snapshot(snapshot, output_dir)
            if print_console:
                print(f"[{snapshot['timestamp']}] 模型数: {snapshot['count']} → 保存: {save_path}")
                for cat, ids in snapshot["groups"].items():
                    print(f"- {cat}: {len(ids)}")
        except Exception as e:
            print(f"⚠️ 查询失败: {e}")
        # sleep and loop
        for _ in range(interval_sec):
            if _stop:
                break
            time.sleep(1)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="定时查询 ModelScope 免费API模型列表并归档")
    parser.add_argument("--interval", type=int, default=1800, help="查询间隔秒数，默认30分钟")
    parser.add_argument("--output-dir", type=str, default="models_snapshot", help="快照输出目录")
    parser.add_argument("--base-url", type=str, default=DEFAULT_BASE_URL, help="API 基地址")
    parser.add_argument("--no-print", action="store_true", help="不在控制台打印分组统计")
    args = parser.parse_args()

    run(interval_sec=args.interval, output_dir=args.output_dir, base_url=args.base_url, print_console=not args.no_print)

import base64
import json
import os
import re

def encode_image(image_path):
    """将本地图片转换为 Base64，带文件存在性检查"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ 找不到图片: {image_path}")
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_json(text):
    """
    健壮解析：使用正则从大段回复中提取 JSON
    """
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None

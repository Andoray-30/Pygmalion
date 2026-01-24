import base64
import json
import os
import re
import time
from openai import OpenAI
from dotenv import load_dotenv

# ✅ 1. 安全升级：从 .env 文件加载环境变量
load_dotenv()
API_KEY = os.getenv("SILICON_KEY")

if not API_KEY:
    raise ValueError("🚨 未找到 API Key！请检查 .env 文件是否配置正确。")

# 配置
MODEL_NAME = "Pro/Qwen/Qwen2.5-VL-7B-Instruct" 
MAX_RETRIES = 3  # 网络重试次数
TIMEOUT = 30     # 超时时间(秒)

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

def encode_image(image_path):
    """将本地图片转换为 Base64，带文件存在性检查"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ 找不到图片: {image_path}")
        
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def extract_json(text):
    """
    ✅ 2. 健壮解析：使用正则从大段回复中提取 JSON
    防止模型废话（如 'Here is the json: ...'）导致解析失败
    """
    try:
        # 尝试直接解析
        return json.loads(text)
    except json.JSONDecodeError:
        # 如果失败，尝试用正则提取第一个 { ... } 区块
        match = re.search(r'\{.*\}', text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass
    return None

def rate_image(image_path, target_concept):
    """
    核心审图函数 (带重试机制)
    :return: float (-1.0 表示错误, 0.0-1.0 为正常评分)
    """
    print(f"🧐 [Judge] 正在审计: {target_concept}...")
    
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        print(f"❌ 图片加载失败: {e}")
        return -1.0

    system_prompt = f"""
You are a calibrated Image Quality Evaluator for a PID control system.

TASK: Rate the image on TWO independent dimensions:
1. Concept Alignment (Target: "{target_concept}")
   - 1.0: Perfect match in all aspects
   - 0.7: Core elements present but missing details
   - 0.5: Vaguely related
   - 0.3: Wrong subject matter
   
2. Technical Quality (Sharpness, Lighting, Artifacts)
   - 1.0: Professional photography level, no flaws
   - 0.8: Good but minor issues (slight blur in background)
   - 0.6: Noticeable problems (noise, watermarks, distortion)
   - 0.4: Severe issues (blurry, broken, low-res)

SCORING FORMULA:
Final Score = (Concept × 0.5) + (Quality × 0.5)

CRITICAL RULES:
- If Quality < 0.6, Final Score CANNOT exceed 0.7
- If Concept < 0.5, Final Score CANNOT exceed 0.6
- Scores > 0.9 require BOTH dimensions > 0.85
- BE HARSH. This is for optimization, not praise.

OUTPUT (JSON ONLY, NO MARKDOWN):
{{
  "concept_score": <float>,
  "quality_score": <float>,
  "final_score": <float>,
  "reason": "<50 words max, cite specific flaws>"
}}
"""
    user_prompt = "Rate this image."

    # ✅ 3. 重试机制
    for attempt in range(MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                temperature=0.2, # ✅ 4. 微调温度：0.2 既能保证格式，又有一点点灵活性
                timeout=TIMEOUT, # ✅ 5. 超时控制
                max_tokens=200   # 限制回复长度，省钱且快
            )

            content = response.choices[0].message.content.strip()
            result = extract_json(content)

            if result and "final_score" in result:
                print(f"📊 概念匹配: {result.get('concept_score', 'N/A'):.2f}")
                print(f"🎨 画质评分: {result.get('quality_score', 'N/A'):.2f}")
                print(f"📝 评价: {result.get('reason', 'No reason provided')}")
                print(f"🎯 最终得分: {result['final_score']:.2f}")
                return float(result['final_score'])
            else:
                print(f"⚠️ 响应格式错误 (尝试 {attempt+1}/{MAX_RETRIES}): {content}")

        except Exception as e:
            print(f"⚠️ API 请求异常 (尝试 {attempt+1}/{MAX_RETRIES}): {e}")
            time.sleep(1) # 失败后歇一秒再试

    print("❌ 多次重试失败，放弃审计。")
    return -1.0 # ✅ 6. 错误代码：返回 -1 区分于 0 分

# --- 单元测试 ---
if __name__ == "__main__":
    # 测试前请确保目录下有一张 'first_contact.png'
    score = rate_image("first_contact.png", "Cyberpunk Neon City")
    
    if score == -1:
        print("🔴 审计系统故障")
    elif score > 0.8:
        print("🟢 符合目标 (Target Reached)")
    else:
        print("🟡 尚未达标 (Needs Improvement)")
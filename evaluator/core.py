import os
import time
from openai import OpenAI
from dotenv import load_dotenv
from config import JUDGE_MODEL_NAME, JUDGE_MAX_RETRIES, JUDGE_TIMEOUT
from .utils import encode_image, extract_json

load_dotenv()
API_KEY = os.getenv("SILICON_KEY")

if not API_KEY:
    # 这里的raise可能会在导入时触发，建议放在函数内或初始化时检查，但保持原逻辑也行
    pass 

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

def rate_image(image_path, target_concept):
    """
    核心审图函数 (带重试机制)
    :return: dict 包含 final_score, concept_score, quality_score, reason
    """
    print(f"🧐 [Judge] 正在审计: {target_concept}...")
    
    # 再次检查API KEY，防止导入时未报错但运行时出错
    if not API_KEY:
         print("🚨 未找到 API Key！无法进行评分。")
         return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "reason": "Missing API Key"}

    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        print(f"❌ 图片加载失败: {e}")
        return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "reason": str(e)}

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

    for attempt in range(JUDGE_MAX_RETRIES):
        try:
            response = client.chat.completions.create(
                model=JUDGE_MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                temperature=0.2,
                timeout=JUDGE_TIMEOUT,
                max_tokens=200
            )

            content = response.choices[0].message.content.strip()
            result = extract_json(content)

            if result and "final_score" in result:
                print(f"📊 概念匹配: {result.get('concept_score', 'N/A'):.2f}")
                print(f"🎨 画质评分: {result.get('quality_score', 'N/A'):.2f}")
                print(f"📝 评价: {result.get('reason', 'No reason provided')}")
                print(f"🎯 最终得分: {result['final_score']:.2f}")
                return result
            else:
                print(f"⚠️ 响应格式错误 (尝试 {attempt+1}/{JUDGE_MAX_RETRIES}): {content}")

        except Exception as e:
            print(f"⚠️ API 请求异常 (尝试 {attempt+1}/{JUDGE_MAX_RETRIES}): {e}")
            time.sleep(1)

    print("❌ 多次重试失败，放弃审计。")
    return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "reason": "API failure"}

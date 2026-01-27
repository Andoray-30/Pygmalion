import os
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv
from config import JUDGE_MODEL_NAME, JUDGE_MAX_RETRIES, JUDGE_TIMEOUT, LOG_LEVEL, LOG_FILE
from .utils import encode_image, extract_json

load_dotenv()
API_KEY = os.getenv("SILICON_KEY")

# 配置日志系统
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

if not API_KEY:
    logger.warning("未检测到SILICON_KEY，评分功能可能不可用")

client = OpenAI(
    api_key=API_KEY,
    base_url="https://api.siliconflow.cn/v1"
)

# 历史评分缓存（用于EWMA平滑）
_score_history = []

def rate_image(image_path, target_concept, concept_weight=0.5, enable_smoothing=True):
    """
    核心审图函数 (三维评分 + 动态权重 + EWMA平滑)
    :param concept_weight: 概念权重 (0-1)，quality权重为1-concept_weight，aesthetics权重为0.15
    :param enable_smoothing: 是否启用历史评分平滑
    :return: dict 包含 final_score, concept_score, quality_score, aesthetics_score, reason
    """
    logger.info(f"开始评分: {target_concept} | 概念权重={concept_weight:.2f}")
    
    if not API_KEY:
        logger.error("缺失API Key，评分失败")
        return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reason": "Missing API Key"}

    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        logger.error(f"图片加载失败: {e}", exc_info=True)
        return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reason": str(e)}

    # 动态计算权重分配
    quality_weight = 1.0 - concept_weight - 0.15  # 为aesthetics预留15%权重
    aesthetics_weight = 0.15
    
    system_prompt = f"""
You are a calibrated Image Quality Evaluator for an adaptive control system.

TASK: Rate the image on THREE independent dimensions:

1. Concept Alignment (Target: "{target_concept}")
   - 1.0: Perfect match with all thematic elements
   - 0.7: Core concept present, minor details missing
   - 0.5: Vaguely related to theme
   - 0.3: Wrong subject matter
   
2. Technical Quality (Sharpness, Lighting, Color, Artifacts)
   - 1.0: Professional-grade, no flaws
   - 0.8: High quality with minor issues
   - 0.6: Noticeable problems (noise, blur, watermarks)
   - 0.4: Severe technical issues

3. Aesthetics (Composition, Creativity, Artistic Merit)
   - 1.0: Exceptional artistic value, creative excellence
   - 0.8: Strong composition and visual appeal
   - 0.6: Adequate but uninspired
   - 0.4: Poor composition or creative execution

SCORING FORMULA:
Final Score = (Concept × {concept_weight:.2f}) + (Quality × {quality_weight:.2f}) + (Aesthetics × {aesthetics_weight:.2f})

CRITICAL RULES:
- If Quality < 0.6, Final Score CANNOT exceed 0.7
- If Concept < 0.5, Final Score CANNOT exceed 0.6
- Scores > 0.9 require ALL dimensions > 0.85
- BE CALIBRATED. This is for optimization feedback.

OUTPUT (JSON ONLY, NO MARKDOWN):
{{
  "concept_score": <float>,
  "quality_score": <float>,
  "aesthetics_score": <float>,
  "final_score": <float>,
  "reason": "<50 words max, cite specific observations>"
}}
"""
    user_prompt = "Rate this image."

    for attempt in range(JUDGE_MAX_RETRIES):
        try:
            logger.debug(f"API调用尝试 {attempt+1}/{JUDGE_MAX_RETRIES}: model={JUDGE_MODEL_NAME}")
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
                max_tokens=250
            )

            content = response.choices[0].message.content.strip()
            result = extract_json(content)

            if result and "final_score" in result:
                raw_score = result['final_score']
                
                # 应用EWMA平滑（指数加权移动平均）
                if enable_smoothing and _score_history:
                    alpha = 0.3  # 平滑系数：0.3新值 + 0.7历史
                    smoothed_score = alpha * raw_score + (1 - alpha) * _score_history[-1]
                    logger.debug(f"评分平滑: 原始={raw_score:.4f} → 平滑后={smoothed_score:.4f}")
                    result['final_score'] = smoothed_score
                    result['raw_score'] = raw_score  # 保留原始分数用于调试
                
                _score_history.append(result['final_score'])
                if len(_score_history) > 10:  # 保留最近10次评分
                    _score_history.pop(0)
                
                logger.info(
                    f"评分完成: Concept={result.get('concept_score', -1):.2f}, "
                    f"Quality={result.get('quality_score', -1):.2f}, "
                    f"Aesthetics={result.get('aesthetics_score', -1):.2f}, "
                    f"Final={result['final_score']:.2f}"
                )
                logger.debug(f"评分理由: {result.get('reason', 'N/A')}")
                
                print(f"📊 概念={result.get('concept_score', -1):.2f} | 画质={result.get('quality_score', -1):.2f} | 美学={result.get('aesthetics_score', -1):.2f}")
                print(f"🎯 最终得分: {result['final_score']:.2f}")
                return result
            else:
                logger.warning(f"响应格式错误 (尝试{attempt+1}): {content[:100]}")

        except Exception as e:
            logger.warning(f"API请求异常 (尝试{attempt+1}): {e}", exc_info=(attempt == JUDGE_MAX_RETRIES-1))
            time.sleep(1)

    logger.error("评分失败：多次重试后仍无法获取有效结果")
    return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reason": "API failure"}

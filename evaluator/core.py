import os
import time
import logging
from openai import OpenAI
from dotenv import load_dotenv
from config import JUDGE_MODEL_NAME, JUDGE_MAX_RETRIES, JUDGE_TIMEOUT, LOG_LEVEL, LOG_FILE
from .utils import encode_image, extract_json

load_dotenv()

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

# 🔄 智能API管理器 - 优先免费,超时自动升级付费
class SmartAPIManager:
    def __init__(self):
        # 免费API配置 (ModelScope)
        self.free_api = {
            'name': 'ModelScope (FREE)',
            'key': os.getenv("MODELSCOPE_API_KEY"),
            'url': "https://api-inference.modelscope.cn/v1",
            'active': False,
            'failures': 0,
            'avg_time': 0,
            'is_premium': False
        }
        
        # 付费API配置 (SiliconFlow)
        self.premium_api = {
            'name': 'SiliconFlow (PAID)',
            'key': os.getenv("SILICON_KEY"),
            'url': "https://api.siliconflow.cn/v1",
            'active': False,
            'failures': 0,
            'avg_time': 0,
            'is_premium': True
        }
        
        # 性能阈值
        self.SPEED_THRESHOLD = 15.0  # 秒,超过则升级到付费
        self.FAILURE_THRESHOLD = 2   # 连续失败2次则升级
        self.response_times = []     # 记录响应时间用于计算平均值
        
        # 初始化
        self.current_api = None
        self.fallback_enabled = False
        self._init_clients()
    
    def _init_clients(self):
        """初始化两个API客户端"""
        # 检查免费API
        if self.free_api['key']:
            try:
                self.free_api['client'] = OpenAI(
                    api_key=self.free_api['key'],
                    base_url=self.free_api['url']
                )
                self.free_api['active'] = True
                logger.info("✓ 免费API (ModelScope) 已就绪")
            except Exception as e:
                logger.warning(f"✗ 免费API初始化失败: {e}")
                self.free_api['active'] = False
        else:
            logger.warning("⚠️ 未检测到MODELSCOPE_API_KEY,跳过免费API")
        
        # 检查付费API
        if self.premium_api['key']:
            try:
                self.premium_api['client'] = OpenAI(
                    api_key=self.premium_api['key'],
                    base_url=self.premium_api['url']
                )
                self.premium_api['active'] = True
                logger.info("✓ 付费API (SiliconFlow) 已就绪")
            except Exception as e:
                logger.warning(f"✗ 付费API初始化失败: {e}")
                self.premium_api['active'] = False
        else:
            logger.warning("⚠️ 未检测到SILICON_KEY,无法使用付费API")
        
        # 选择初始API: 优先免费
        if self.free_api['active']:
            self.current_api = self.free_api
            logger.info("🔄 使用免费API (ModelScope) 作为首选")
        elif self.premium_api['active']:
            self.current_api = self.premium_api
            self.fallback_enabled = True
            logger.info("🔄 免费API不可用,直接使用付费API (SiliconFlow)")
        else:
            logger.error("❌ 两个API都不可用!")
            self.current_api = None
    
    def get_client(self):
        """获取当前活跃API客户端"""
        if self.current_api and self.current_api['active']:
            return self.current_api['client']
        return None
    
    def record_response_time(self, elapsed_time):
        """记录响应时间"""
        self.response_times.append(elapsed_time)
        if len(self.response_times) > 20:  # 只保留最近20次
            self.response_times.pop(0)
        
        avg_time = sum(self.response_times) / len(self.response_times)
        self.current_api['avg_time'] = avg_time
        
        # 检查是否需要升级到付费API
        if (not self.current_api['is_premium'] and 
            avg_time > self.SPEED_THRESHOLD and 
            self.premium_api['active']):
            logger.warning(f"⚠️ 免费API响应缓慢 ({avg_time:.1f}s > {self.SPEED_THRESHOLD}s阈值),升级到付费API")
            self.current_api = self.premium_api
            self.fallback_enabled = True
    
    def handle_failure(self):
        """处理API失败"""
        self.current_api['failures'] += 1
        
        if (not self.current_api['is_premium'] and 
            self.current_api['failures'] >= self.FAILURE_THRESHOLD and
            self.premium_api['active']):
            logger.warning(f"⚠️ 免费API失败{self.FAILURE_THRESHOLD}次,升级到付费API")
            self.current_api = self.premium_api
            self.fallback_enabled = True
        
        # 重置计数
        self.current_api['failures'] = 0
    
    def get_api_status(self):
        """获取API状态信息"""
        return {
            'current': self.current_api['name'] if self.current_api else 'None',
            'free_ready': self.free_api['active'],
            'premium_ready': self.premium_api['active'],
            'fallback_enabled': self.fallback_enabled,
            'avg_response_time': self.current_api['avg_time'] if self.current_api else 0
        }

# 全局API管理器实例
api_manager = SmartAPIManager()

# 历史评分缓存（用于EWMA平滑）
_score_history = []

def rate_image(image_path, target_concept, concept_weight=0.5, enable_smoothing=True):
    """
    核心审图函数 (四维评分 + 动态权重 + EWMA平滑)
    新增维度: 物理合理性 (Physical Reasonableness)
    :param concept_weight: 概念权重 (0-1)，quality权重动态计算，aesthetics与reasonableness各占15%
    :param enable_smoothing: 是否启用历史评分平滑
    :return: dict 包含 final_score, concept_score, quality_score, aesthetics_score, reasonableness_score, reason
    """
    logger.info(f"开始评分: {target_concept} | 概念权重={concept_weight:.2f}")
    
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        logger.error(f"图片加载失败: {e}", exc_info=True)
        return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reasonableness_score": -1.0, "reason": str(e)}

    # 动态计算权重分配 (4维: Concept + Quality + Aesthetics + Reasonableness)
    aesthetics_weight = 0.15
    reasonableness_weight = 0.15
    quality_weight = 1.0 - concept_weight - aesthetics_weight - reasonableness_weight
    
    system_prompt = f"""
You are a calibrated Image Quality Evaluator with Physical Reasoning capabilities for an adaptive control system.

TASK: Rate the image on FOUR independent dimensions:

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

4. Physical Reasonableness (Physics Laws, Logic Consistency) ⚠️ NEW DIMENSION
   - 1.0: All elements obey physics and logic (lighting directions, object proportions, gravity, spatial relationships)
   - 0.8: Minor stylized exaggerations but coherent (fantasy elements acceptable if consistent)
   - 0.6: Noticeable issues (wrong shadows, impossible scales, floating objects without support)
   - 0.4: Major physics violations (inconsistent lighting sources, anatomical errors, perspective distortions)
   
   CRITICAL CHECKS FOR REASONABLENESS:
   • Lighting consistency: Shadows match light source positions
   • Object proportions: Relative sizes make sense (e.g., butterfly shouldn't be larger than trees)
   • Gravity & support: Objects without visible support should have plausible explanations
   • Spatial coherence: Depth, perspective, and occlusion relationships are logical
   • Material properties: Reflections, transparency, and surface interactions are realistic

SCORING FORMULA:
Final Score = (Concept × {concept_weight:.2f}) + (Quality × {quality_weight:.2f}) + (Aesthetics × {aesthetics_weight:.2f}) + (Reasonableness × {reasonableness_weight:.2f})

CRITICAL RULES:
- If Quality < 0.6, Final Score CANNOT exceed 0.7
- If Concept < 0.5, Final Score CANNOT exceed 0.6
- If Reasonableness < 0.6, Final Score CANNOT exceed 0.75 (physics violations are serious)
- Scores > 0.9 require ALL dimensions > 0.85
- BE CALIBRATED. This is for optimization feedback.

OUTPUT (JSON ONLY, NO MARKDOWN):
{{
  "concept_score": <float>,
  "quality_score": <float>,
  "aesthetics_score": <float>,
  "reasonableness_score": <float>,
  "final_score": <float>,
  "reason": "<50 words max, cite specific observations including physics issues if any>"
}}
"""
    user_prompt = "Rate this image."

    for attempt in range(JUDGE_MAX_RETRIES):
        try:
            client = api_manager.get_client()
            if not client:
                logger.error("❌ 无可用API客户端")
                return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reasonableness_score": -1.0, "reason": "No available API"}
            
            api_info = api_manager.current_api['name']
            logger.debug(f"API调用尝试 {attempt+1}/{JUDGE_MAX_RETRIES}: model={JUDGE_MODEL_NAME} | {api_info}")
            
            # 记录开始时间用于性能监测
            start_time = time.time()
            
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
            
            # 计算响应时间
            elapsed_time = time.time() - start_time
            api_manager.record_response_time(elapsed_time)

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
                
                # 添加API信息到结果
                result['api_used'] = api_manager.current_api['name']
                result['response_time'] = f"{elapsed_time:.2f}s"
                
                logger.info(
                    f"评分完成: Concept={result.get('concept_score', -1):.2f}, "
                    f"Quality={result.get('quality_score', -1):.2f}, "
                    f"Aesthetics={result.get('aesthetics_score', -1):.2f}, "
                    f"Reasonableness={result.get('reasonableness_score', -1):.2f}, "
                    f"Final={result['final_score']:.2f} | API={result['api_used']} ({result['response_time']})"
                )
                logger.debug(f"评分理由: {result.get('reason', 'N/A')}")
                
                print(f"📊 概念={result.get('concept_score', -1):.2f} | 画质={result.get('quality_score', -1):.2f} | 美学={result.get('aesthetics_score', -1):.2f} | 合理性={result.get('reasonableness_score', -1):.2f}")
                print(f"🎯 最终得分: {result['final_score']:.2f}")
                print(f"🔄 API: {result['api_used']} ({result['response_time']})")
                return result
            else:
                logger.warning(f"响应格式错误 (尝试{attempt+1}): {content[:100]}")
                api_manager.handle_failure()

        except Exception as e:
            logger.warning(f"API请求异常 (尝试{attempt+1}): {e}", exc_info=(attempt == JUDGE_MAX_RETRIES-1))
            api_manager.handle_failure()  # 记录失败,可能触发API切换
            time.sleep(1)

    logger.error("评分失败：多次重试后仍无法获取有效结果")
    return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reasonableness_score": -1.0, "reason": "API failure"}


def get_api_status():
    """获取当前API状态和性能指标"""
    return api_manager.get_api_status()

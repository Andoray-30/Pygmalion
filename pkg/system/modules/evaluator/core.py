import os
import time
import logging
import httpx
import random
from dotenv import load_dotenv
from pkg.infrastructure.config import (
    JUDGE_MODEL_NAME, JUDGE_MODELS, JUDGE_MAX_RETRIES, JUDGE_TIMEOUT, 
    LOG_LEVEL, LOG_FILE, JUDGE_MODEL_ROTATION_ENABLED, JUDGE_MODEL_ROTATION_INTERVAL
)
from .utils import encode_image, extract_json
from pkg.system.modules.reference.image_matcher import ReferenceImageMatcher  # ← 新增

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

# 🔄 智能API管理器 - 优先免费,超时自动升级付费 + 模型轮换
class SmartAPIManager:
    def __init__(self):
        # 免费API配置 (ModelScope)
        self.free_api = {
            'name': 'ModelScope (FREE)',
            'key': os.getenv("MODELSCOPE_API_KEY"),
            'url': os.getenv("MODELSCOPE_URL", "https://api-inference.modelscope.cn/v1"),
            'active': False,
            'failures': 0,
            'avg_time': 0,
            'is_premium': False
        }
        
        # 付费API配置 (SiliconFlow)
        self.premium_api = {
            'name': 'SiliconFlow (PAID)',
            'key': os.getenv("SILICON_KEY"),
            'url': os.getenv("SILICON_URL", "https://api.siliconflow.cn/v1"),
            'active': False,
            'failures': 0,
            'avg_time': 0,
            'is_premium': True
        }
        
        # 多模型轮换系统
        self.judge_model_pool = list(JUDGE_MODELS.values())
        self.current_judge_model = JUDGE_MODEL_NAME
        self.model_call_count = 0
        self.rotation_enabled = JUDGE_MODEL_ROTATION_ENABLED
        self.rotation_interval = JUDGE_MODEL_ROTATION_INTERVAL
        
        # 性能阈值
        self.SPEED_THRESHOLD = 15.0  # 秒,超过则升级到付费
        self.FAILURE_THRESHOLD = 2   # 连续失败2次则升级
        self.response_times = []     # 记录响应时间用于计算平均值
        
        # 初始化
        self.current_api = None
        self.fallback_enabled = False
        self._init_clients()
    
    def _init_clients(self):
        """初始化两个API配置（不再使用OpenAI客户端，改用httpx直接调用）"""
        # 检查免费API密钥
        if self.free_api['key']:
            self.free_api['active'] = True
            logger.info("✓ 免费API (ModelScope) 已就绪")
        else:
            logger.warning("⚠️ 未检测到MODELSCOPE_API_KEY,跳过免费API")
            self.free_api['active'] = False
        
        # 检查付费API密钥
        if self.premium_api['key']:
            self.premium_api['active'] = True
            logger.info("✓ 付费API (SiliconFlow) 已就绪")
        else:
            logger.warning("⚠️ 未检测到SILICON_KEY,无法使用付费API")
            self.premium_api['active'] = False
        
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
        
        # 打印模型池信息
        if self.rotation_enabled:
            logger.info(f"🔄 评分模型轮换已启用 (间隔: {self.rotation_interval}次)")
            logger.info(f"📚 模型池: {' → '.join([m.split('/')[-1] for m in self.judge_model_pool])}")

    def reload_config(self):
        """重新从环境变量加载配置（用于 Web 界面更新设置后同步）"""
        logger.info("🔄 正在重新加载 API 反馈配置...")
        
        # 更新源 A (Primary)
        self.free_api['name'] = os.getenv("EVAL_A_NAME", "Evaluator A")
        self.free_api['key'] = os.getenv("EVAL_A_KEY", os.getenv("MODELSCOPE_API_KEY"))
        self.free_api['url'] = os.getenv("EVAL_A_URL", os.getenv("MODELSCOPE_URL", "https://api-inference.modelscope.cn/v1"))
        
        # 更新源 B (Premium)
        self.premium_api['name'] = os.getenv("EVAL_B_NAME", "Evaluator B")
        self.premium_api['key'] = os.getenv("EVAL_B_KEY", os.getenv("SILICON_KEY"))
        self.premium_api['url'] = os.getenv("EVAL_B_URL", os.getenv("SILICON_URL", "https://api.siliconflow.cn/v1"))
        
        # 更新模型池
        model_a = os.getenv("EVAL_A_MODEL")
        model_b = os.getenv("EVAL_B_MODEL")
        
        if model_a or model_b:
            new_pool = []
            if model_a: new_pool.append(model_a)
            if model_b: new_pool.append(model_b)
            self.judge_model_pool = new_pool
            self.current_judge_model = new_pool[0]
            
        # 重新初始化客户端状态
        self._init_clients()
    
    def get_client(self):
        """获取当前API配置信息（不再返回OpenAI客户端）"""
        if self.current_api and self.current_api['active']:
            return self.current_api
        return None
    
    def get_judge_model(self):
        """获取当前评分模型（支持轮换）"""
        if self.rotation_enabled and self.model_call_count >= self.rotation_interval:
            # 轮换到下一个模型
            self.current_judge_model = random.choice(self.judge_model_pool)
            self.model_call_count = 0
            logger.info(f"🔄 评分模型已轮换: {self.current_judge_model.split('/')[-1]} (剩余: {self.model_call_count}/{self.rotation_interval})")
        
        self.model_call_count += 1
        return self.current_judge_model
    
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
        """处理API失败 - 对于速率限制(429)立即切换，其他错误累计到阈值后切换"""
        self.current_api['failures'] += 1
        
        # 🔥 改进逻辑：任何失败都可能需要切换，只要有备用API
        # 特别是429错误应该立即切换
        if (not self.current_api['is_premium'] and 
            self.premium_api['active']):
            # 尝试切换到付费API
            logger.warning(f"⚠️ 切换API: {self.current_api['name']} → {self.premium_api['name']}")
            self.current_api = self.premium_api
            self.fallback_enabled = True
        
        # 重置失败计数
        self.current_api['failures'] = 0
    
    def get_api_status(self):
        """获取API状态信息"""
        return {
            'current': self.current_api['name'] if self.current_api else 'None',
            'free_ready': self.free_api['active'],
            'premium_ready': self.premium_api['active'],
            'fallback_enabled': self.fallback_enabled,
            'avg_response_time': self.current_api['avg_time'] if self.current_api else 0,
            'judge_model': self.current_judge_model.split('/')[-1] if self.current_judge_model else 'None',
            'model_call_count': self.model_call_count
        }

# 全局API管理器实例
api_manager = SmartAPIManager()

def rate_image(image_path, target_concept, concept_weight=0.5, reference_image_path=None):
    """
    核心审图函数 (五维评分：4个基础维度 + 参考图维度)
    修复：
    1. 固定concept_weight=0.50（探索和渲染期保持一致，便于对比）
    2. 支持参考图评分维度（可选）
    :param concept_weight: 概念权重 (0-1)，其他维度按比例分配
    :param reference_image_path: 参考图路径（可选）
    :return: dict 包含 final_score, concept_score, quality_score, aesthetics_score, reasonableness_score, 
             以及可选的参考图5个维度: style_consistency, pose_similarity, composition_match, character_consistency, reference_match_score
    """
    logger.info(f"开始评分: {target_concept} | 概念权重={concept_weight:.2f} | 参考图={'有' if reference_image_path else '无'}")
    
    try:
        base64_image = encode_image(image_path)
    except Exception as e:
        logger.error(f"图片加载失败: {e}", exc_info=True)
        return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reasonableness_score": -1.0, "reason": str(e)}

    # ============ 动态权重分配 ============
    # 如果提供参考图，则使用5维评分；否则使用4维评分
    if reference_image_path:
        # 5维权重 (包含参考图评分)
        # 理念：参考图约束很重要，占25%；基础4维保持相对权重
        aesthetics_weight = 0.12
        reasonableness_weight = 0.10
        reference_match_weight = 0.25  # 参考图匹配度最高权重
        quality_weight = 1.0 - concept_weight - aesthetics_weight - reasonableness_weight - reference_match_weight
    else:
        # 4维权重 (无参考图时)
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

SCORING FORMULA (WITHOUT REFERENCE IMAGE):
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
            api_config = api_manager.get_client()
            if not api_config:
                logger.error("❌ 无可用API配置")
                return {"final_score": -1.0, "concept_score": -1.0, "quality_score": -1.0, "aesthetics_score": -1.0, "reasonableness_score": -1.0, "reason": "No available API"}
            
            # 🔄 获取当前评分模型（支持轮换）
            current_judge_model = api_manager.get_judge_model()
            
            api_info = api_config['name']
            logger.debug(f"API调用尝试 {attempt+1}/{JUDGE_MAX_RETRIES}: model={current_judge_model} | {api_info}")
            
            # 记录开始时间用于性能监测
            start_time = time.time()
            
            # 使用httpx直接调用API，避免OpenAI库的平台检测问题
            headers = {
                "Authorization": f"Bearer {api_config['key']}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": current_judge_model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]}
                ],
                "temperature": 0.2,
                "max_tokens": 250
            }
            
            with httpx.Client(timeout=JUDGE_TIMEOUT) as client:
                response = client.post(
                    f"{api_config['url']}/chat/completions",
                    headers=headers,
                    json=payload
                )
                
                # 🔥 立即处理HTTP错误（特别是429速率限制）
                if response.status_code == 429:
                    logger.warning(f"⚠️ API速率限制 (429) - 立即切换API (尝试{attempt+1}/{JUDGE_MAX_RETRIES})")
                    api_manager.handle_failure()
                    time.sleep(2 + attempt * 0.5)  # 退避延迟
                    continue  # 跳过本次，直接进入下一次重试（会自动获取新API）
                
                response.raise_for_status()
                data = response.json()
            
            # 计算响应时间
            elapsed_time = time.time() - start_time
            api_manager.record_response_time(elapsed_time)

            content = data['choices'][0]['message']['content'].strip()
            result = extract_json(content)

            if result and "final_score" in result:
                raw_score = result['final_score']
                
                # ============ 集成参考图评分 ============
                reference_scores = {}
                if reference_image_path and os.path.exists(reference_image_path):
                    try:
                        matcher = ReferenceImageMatcher()
                        reference_scores = matcher.evaluate_match(reference_image_path, image_path)
                        logger.debug(f"参考图评分: {reference_scores}")
                        
                        # 将参考图5个维度添加到结果
                        result['style_consistency'] = reference_scores.get('style_consistency', 0.5)
                        result['pose_similarity'] = reference_scores.get('pose_similarity', 0.5)
                        result['composition_match'] = reference_scores.get('composition_match', 0.5)
                        result['character_consistency'] = reference_scores.get('character_consistency', 0.5)
                        result['reference_match_score'] = reference_scores.get('overall_reference_match', 0.5)
                        
                        # 重新计算final_score，包含参考图维度
                        base_final = (
                            result.get('concept_score', 0.5) * concept_weight +
                            result.get('quality_score', 0.5) * quality_weight +
                            result.get('aesthetics_score', 0.5) * aesthetics_weight +
                            result.get('reasonableness_score', 0.5) * reasonableness_weight
                        )
                        
                        # 加入参考图权重
                        reference_weight = 0.25 if reference_image_path else 0.0
                        result['final_score'] = (
                            base_final * (1.0 - reference_weight) +
                            result['reference_match_score'] * reference_weight
                        )
                        
                        logger.info(
                            f"参考图评分已集成: "
                            f"Style={result['style_consistency']:.2f}, "
                            f"Pose={result['pose_similarity']:.2f}, "
                            f"Composition={result['composition_match']:.2f}, "
                            f"Character={result['character_consistency']:.2f}, "
                            f"RefMatch={result['reference_match_score']:.2f} | "
                            f"最终分数={result['final_score']:.2f}"
                        )
                    except Exception as e:
                        logger.warning(f"参考图评分失败，使用基础分数: {e}")
                        reference_scores = {}
                
                # 添加API和模型信息到结果
                result['api_used'] = api_manager.current_api['name']
                result['judge_model'] = current_judge_model.split('/')[-1]
                result['response_time'] = f"{elapsed_time:.2f}s"
                
                logger.info(
                    f"评分完成: Concept={result.get('concept_score', -1):.2f}, "
                    f"Quality={result.get('quality_score', -1):.2f}, "
                    f"Aesthetics={result.get('aesthetics_score', -1):.2f}, "
                    f"Reasonableness={result.get('reasonableness_score', -1):.2f}, "
                    f"Final={result['final_score']:.2f} | 模型={result['judge_model']} | API={result['api_used']} ({result['response_time']})"
                )
                logger.debug(f"评分理由: {result.get('reason', 'N/A')}")
                
                print(f"📊 概念={result.get('concept_score', -1):.2f} | 画质={result.get('quality_score', -1):.2f} | 美学={result.get('aesthetics_score', -1):.2f} | 合理性={result.get('reasonableness_score', -1):.2f}")
                if reference_scores:
                    print(f"🖼️ 参考图: 风格={result.get('style_consistency', -1):.2f} | 姿态={result.get('pose_similarity', -1):.2f} | 构图={result.get('composition_match', -1):.2f} | 角色={result.get('character_consistency', -1):.2f}")
                print(f"🎯 最终得分: {result['final_score']:.2f}")
                print(f"🤖 模型: {result['judge_model']} | 🔄 API: {result['api_used']} ({result['response_time']})")
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

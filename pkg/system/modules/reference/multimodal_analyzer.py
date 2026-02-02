"""
多模态AI风格分析器 - 使用SiliconFlow API进行参考图像分析
调用 InternVL3.5-241B 或 Qwen VL 235B 模型

重用项目现有组件：
- encode_image (from evaluator.utils) 替代本地 base64 编码
- httpx (from evaluator.core) 替代 requests 保持一致性
- extract_json (from evaluator.utils) 替代本地 JSON 解析
- 配置统一从 settings.py 读取
"""

import httpx
import json
import logging
import os
import base64
from pathlib import Path
from typing import Dict, Any, Optional
from pkg.infrastructure.config import JUDGE_TIMEOUT

logger = logging.getLogger(__name__)


def encode_image(image_path: str) -> str:
    """将本地图片转换为 Base64（避免循环导入）"""
    if not os.path.exists(image_path):
        raise FileNotFoundError(f"❌ 找不到图片: {image_path}")
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def extract_json(text: str) -> Optional[Dict]:
    """从文本中提取JSON（避免循环导入）"""
    import re
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


class MultimodalStyleAnalyzer:
    """使用多模态大模型分析参考图像的风格"""
    
    # API 配置（优先使用魔搭免费额度）
    MODELSCOPE_API_ENDPOINT = "https://api-inference.modelscope.cn/v1/chat/completions"
    SILICONFLOW_API_ENDPOINT = "https://api.siliconflow.cn/v1/chat/completions"
    
    # 可用模型（优先级：魔搭免费 > 硅基流动付费）
    AVAILABLE_MODELS = {
        "modelscope": [
            "OpenGVLab/InternVL3_5-241B-A28B",  # 🥇 魔搭免费 241B (首选)
            "Qwen/Qwen3-VL-235B-A22B-Instruct",  # 🥈 魔搭免费 235B
            "Qwen/Qwen2.5-VL-72B-Instruct",      # 🥉 魔搭免费 72B
        ],
        "siliconflow": [
            "Qwen/Qwen3-VL-235B-A22B-Instruct",  # 硅基付费 235B
            "Qwen/Qwen2.5-VL-72B-Instruct",      # 硅基付费 72B
            "deepseek-ai/deepseek-vl2",          # 硅基付费 DeepSeek VL2
        ]
    }
    
    # 风格分析提示词
    STYLE_ANALYSIS_PROMPT = """你是一位专业的艺术风格分析师。请分析这张参考图像的艺术风格，并以JSON格式返回分析结果。

分析要求：
1. 识别艺术风格类别（如：动漫/二次元、现实感、油画、水彩、素描、赛博朋克、概念美术等）
2. 提取关键视觉特征（颜色、构图、线条、质感等）
3. 根据风格推荐适合的渲染模型（ANIME/RENDER/PREVIEW）
4. 为提示词生成提供建议（给 DeepSeek 使用）

请以以下JSON格式返回（必须是有效的JSON）：
{
    "style_category": "识别的风格类别",
    "confidence": 0.85,
    "visual_features": {
        "dominant_colors": ["颜色1", "颜色2"],
        "composition": "构图特点描述",
        "line_quality": "线条特点",
        "texture_style": "质感风格"
    },
    "recommended_model": "ANIME|RENDER|PREVIEW",
    "model_reasoning": "为什么推荐这个模型的原因",
    "deepseek_hints": {
        "art_style": "艺术风格关键词",
        "visual_keywords": ["关键词1", "关键词2", "关键词3"],
        "forbidden_elements": ["应该避免的元素"],
        "emphasis": "应该强调的特点"
    }
}

现在分析这张图像："""
    
    def __init__(self, api_key: Optional[str] = None, modelscope_key: Optional[str] = None):
        """
        初始化分析器
        
        Args:
            api_key: SiliconFlow API密钥（付费，降级使用）
            modelscope_key: ModelScope API密钥（免费，优先使用）
        """
        # 优先使用魔搭免费API
        self.modelscope_key = modelscope_key or os.getenv("MODELSCOPE_API_KEY")
        # 降级使用硅基付费API
        self.siliconflow_key = api_key or os.getenv("SILICON_KEY")
        
        if not self.modelscope_key and not self.siliconflow_key:
            logger.warning("⚠️ 未设置 MODELSCOPE_API_KEY 或 SILICON_KEY，多模态分析将不可用")
        elif self.modelscope_key:
            logger.info("✅ 使用 ModelScope 免费API (2000次/天)")
        else:
            logger.info("⚠️ 使用 SiliconFlow 付费API (降级模式)")
    
    def analyze_reference_image(self, image_path: str, model: Optional[str] = None) -> Dict[str, Any]:
        """
        分析参考图像的艺术风格（优先使用魔搭免费API）
        
        Args:
            image_path: 本地图像文件路径
            model: 使用的模型（如果为None，自动选择）
        
        Returns:
            包含分析结果的字典
        """
        try:
            # 检查API密钥
            if not self.modelscope_key and not self.siliconflow_key:
                logger.error("❌ API密钥未配置")
                return self._get_default_analysis()
            
            # 【重用】使用evaluator.utils的encode_image
            try:
                image_data = encode_image(image_path)
            except FileNotFoundError as e:
                logger.error(f"❌ {e}")
                return self._get_default_analysis()
            
            # 优先尝试魔搭免费API
            if self.modelscope_key:
                for model in self.AVAILABLE_MODELS["modelscope"]:
                    logger.info(f"🔄 尝试 ModelScope (免费): {model}")
                    response = self._call_api(
                        self.MODELSCOPE_API_ENDPOINT,
                        self.modelscope_key,
                        image_data,
                        model
                    )
                    if response:
                        analysis = self._parse_response(response)
                        logger.info(f"✅ ModelScope 分析完成: {analysis.get('style_category', '未知风格')}")
                        return analysis
                
                logger.warning("⚠️ ModelScope 所有模型失败，降级到 SiliconFlow")
            
            # 降级到硅基付费API
            if self.siliconflow_key:
                for model in self.AVAILABLE_MODELS["siliconflow"]:
                    logger.info(f"🔄 尝试 SiliconFlow (付费): {model}")
                    response = self._call_api(
                        self.SILICONFLOW_API_ENDPOINT,
                        self.siliconflow_key,
                        image_data,
                        model
                    )
                    if response:
                        analysis = self._parse_response(response)
                        logger.info(f"✅ SiliconFlow 分析完成: {analysis.get('style_category', '未知风格')}")
                        return analysis
            
            # 所有API都失败
            logger.warning("⚠️ 所有API调用失败，使用默认分析")
            return self._get_default_analysis()
        
        except Exception as e:
            logger.error(f"❌ 多模态分析异常: {e}")
            return self._get_default_analysis()
    
    def _call_api(self, endpoint: str, api_key: str, image_data: str, model: str) -> Optional[str]:
        """
        调用多模态API（使用httpx保持项目一致性）
        
        Args:
            endpoint: API端点URL
            api_key: API密钥
            image_data: Base64 编码的图像数据
            model: 使用的模型
        
        Returns:
            API 响应的文本内容
        """
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_data}"}
                            },
                            {
                                "type": "text",
                                "text": self.STYLE_ANALYSIS_PROMPT
                            }
                        ]
                    }
                ],
                "max_tokens": 1000,
                "temperature": 0.3
            }
            
            # 【重用】使用httpx替代requests，与evaluator.core保持一致
            with httpx.Client(timeout=JUDGE_TIMEOUT) as client:
                response = client.post(
                    endpoint,
                    headers=headers,
                    json=payload
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                    return content
                else:
                    logger.warning(f"⚠️ API错误 {response.status_code}: {response.text[:100]}")
                    return None
        
        except httpx.TimeoutException:
            logger.error("❌ API请求超时")
            return None
        except httpx.RequestError as e:
            logger.error(f"❌ API请求异常: {e}")
            return None
        except Exception as e:
            logger.error(f"❌ 调用API异常: {e}")
            return None
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """
        解析 API 响应（重用evaluator.utils的extract_json）
        
        Args:
            response_text: API 返回的文本
        
        Returns:
            解析后的分析结果
        """
        try:
            # 【重用】使用evaluator.utils的extract_json替代本地实现
            data = extract_json(response_text)
            
            if data is None:
                logger.warning("⚠️ 响应中未找到有效JSON，使用默认分析")
                return self._get_default_analysis()
            
            # 验证必需字段
            required_fields = ["style_category", "recommended_model", "deepseek_hints"]
            if all(field in data for field in required_fields):
                return data
            else:
                logger.warning("⚠️ 响应缺少必需字段，使用默认分析")
                return self._get_default_analysis()
        
        except Exception as e:
            logger.error(f"❌ 解析异常: {e}")
            return self._get_default_analysis()
    
    def _get_default_analysis(self) -> Dict[str, Any]:
        """
        返回默认分析结果（当API不可用时）
        
        Returns:
            默认分析结果
        """
        return {
            "style_category": "unknown",
            "confidence": 0.0,
            "visual_features": {
                "dominant_colors": [],
                "composition": "无法分析",
                "line_quality": "未知",
                "texture_style": "未知"
            },
            "recommended_model": "PREVIEW",  # 默认使用预览模型
            "model_reasoning": "API不可用，使用默认模型",
            "deepseek_hints": {
                "art_style": "未指定",
                "visual_keywords": [],
                "forbidden_elements": [],
                "emphasis": "无特殊强调"
            }
        }


def analyze_reference_style_with_multimodal(
    image_path: str,
    api_key: Optional[str] = None
) -> Dict[str, Any]:
    """
    便捷函数：使用多模态AI分析参考图像风格
    
    Args:
        image_path: 参考图像路径
        api_key: SiliconFlow API密钥
    
    Returns:
        风格分析结果
    """
    analyzer = MultimodalStyleAnalyzer(api_key=api_key)
    return analyzer.analyze_reference_image(image_path)

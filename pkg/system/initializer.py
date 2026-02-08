#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Engine 初始化模块 - 负责 DiffuServoV4 的初始化逻辑
"""
import re
import datetime
from pkg.system.modules.reference import analyze_reference_style_with_multimodal


class EngineInitializer:
    """Engine 初始化工具类"""

    @staticmethod
    def initialize_reference_model(brain, theme, reference_image_path):
        """
        初始化参考图模型选择和相关属性
        
        Args:
            brain: CreativeDirector 实例
            theme: 用户主题
            reference_image_path: 参考图路径
            
        Returns:
            dict: 包含 initial_model_choice, model_locked, locked_model, reference_style_analysis
        """
        result = {
            "initial_model_choice": "PREVIEW",
            "model_locked": False,
            "locked_model": None,
            "reference_style_analysis": None,
        }

        if not reference_image_path:
            # 无参考图时使用 DeepSeek 推荐
            print(f"\n🔍 分析主题并选择最佳模型...")
            model_recommendation = brain.analyze_theme_and_recommend_model(theme)
            result["initial_model_choice"] = model_recommendation.get("model", "PREVIEW")
            return result

        # 有参考图时优先执行多模态分析
        try:
            print(f"\n🔍 [优先] 分析参考图风格...")
            analysis = analyze_reference_style_with_multimodal(reference_image_path)
            result["reference_style_analysis"] = analysis

            recommended_model = analysis.get("recommended_model", "PREVIEW")
            style_category = analysis.get("style_category", "unknown")
            confidence = analysis.get("confidence", 0.0)

            if recommended_model in ["ANIME", "RENDER"]:
                result["initial_model_choice"] = recommended_model
                result["model_locked"] = True
                result["locked_model"] = recommended_model
                print(f"🔒 [多模态锁定] {recommended_model} 模型 ({style_category}, {confidence:.0%}置信度)")
            else:
                # 如果多模态不确定，才使用 DeepSeek 推荐
                print(f"\n🔍 多模态分析不确定，使用DeepSeek推荐...")
                model_recommendation = brain.analyze_theme_and_recommend_model(theme)
                result["initial_model_choice"] = model_recommendation.get("model", "PREVIEW")

        except Exception as e:
            print(f"⚠️ 多模态分析失败: {e}，回退到DeepSeek推荐")
            model_recommendation = brain.analyze_theme_and_recommend_model(theme)
            result["initial_model_choice"] = model_recommendation.get("model", "PREVIEW")

        return result

    @staticmethod
    def generate_project_id(brain, theme):
        """
        生成项目 ID（英文名称 + 时间戳）
        
        Args:
            brain: CreativeDirector 实例
            theme: 用户主题
            
        Returns:
            str: 格式为 "safe_name_YYYYmmdd_HHMMSS"
        """
        raw_name = brain.generate_project_name(theme)
        raw_name = (raw_name or "untitled_project").strip()
        safe_name = re.sub(r"\s+", "_", raw_name)
        safe_name = re.sub(r"[^A-Za-z0-9_]+", "", safe_name)
        if not safe_name:
            safe_name = "untitled_project"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_name}_{timestamp}"

    @staticmethod
    def get_default_params(theme):
        """
        获取默认参数字典
        
        Args:
            theme: 用户主题
            
        Returns:
            dict: 默认参数配置
        """
        return {
            "prompt": f"cinematic shot of {theme}, misty sunbeams, lush foliage, volumetric light, 8k, masterpiece, sharp focus, highly detailed",
            "negative_prompt": "text, watermark, blurry, noise, distortion, ugly, low quality, jpeg artifacts, grain, nsfw",
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 832,
            "height": 1216,
            "sampler_name": "Euler a",
            "scheduler": "Simple",
            "seed": -1,
            "enable_hr": False,
            "hr_scale": 1.5,
            "hr_upscaler": "R-ESRGAN 4x+",
            "hr_second_pass_steps": 10,
            "denoising_strength": 0.35,
            "hr_additional_modules": []
        }

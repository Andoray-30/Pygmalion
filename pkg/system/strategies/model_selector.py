#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模型选择策略 - 根据主题、当前阶段、当前分数自动选择最优底模
"""
from pkg.infrastructure.config import (
    BASE_MODELS,
    MODEL_CONFIGS,
    MODEL_SWITCH_SCORE_THRESHOLD,
    MODEL_SWITCH_MIN_ITERATIONS
)


class ModelSelector:
    """智能模型选择器 - 根据主题、阶段、分数自动选择最优底模"""

    def __init__(self):
        self.models = {
            "TURBO": "sd_xl_turbo_1.0_fp16.safetensors",
            "QUALITY_REALISTIC": "Juggernaut_RunDiffusionPhoto2_Lightning.safetensors",
            "QUALITY_ANIME": "animagine-xl-3.1.safetensors",
        }

    def select(self, theme, state, current_score, iteration, initial_model_choice=None):
        """
        根据主题、当前阶段、当前分数选择最优底模

        Args:
            theme: 当前主题
            state: 当前状态 (INIT/EXPLORE/OPTIMIZE/FINETUNE/CONVERGED)
            current_score: 当前分数
            iteration: 当前迭代次数
            initial_model_choice: 初始选择的模型 (PREVIEW/RENDER/ANIME)

        Returns:
            str: 模型模式 (PREVIEW/RENDER/ANIME)
        """
        # 1. 判断主题类型
        is_anime = self._is_anime_theme(theme)

        # 2. 根据阶段选择策略
        if state in ["INIT", "EXPLORE"]:
            # 初期：追求速度
            return "PREVIEW"

        elif state == "OPTIMIZE":
            # 优化期：根据分数决定
            if current_score > 0.80 and iteration >= MODEL_SWITCH_MIN_ITERATIONS:
                # 分数已经接近目标，切换到高质量模型
                if initial_model_choice == "PREVIEW":
                    # 如果初始是PREVIEW，升级到对应的高质量模型
                    return "ANIME" if is_anime else "RENDER"
                else:
                    # 如果初始已经选择了RENDER或ANIME，保持不变
                    return initial_model_choice
            else:
                # 分数还很低，继续用快速模型试错
                return "PREVIEW"

        elif state in ["FINETUNE", "CONVERGED"]:
            # 精调期：必须用高质量模型
            if initial_model_choice == "PREVIEW":
                return "ANIME" if is_anime else "RENDER"
            else:
                return initial_model_choice

        return "PREVIEW"  # 默认

    def _is_anime_theme(self, theme):
        """判断主题是否为动漫风格"""
        anime_keywords = [
            "anime", "manga", "cartoon", "illustration", 
            "cute", "chibi", "fantasy art", "game character",
            "动漫", "漫画", "卡通", "插画", "可爱", "萌"
        ]
        theme_lower = theme.lower()
        return any(k in theme_lower for k in anime_keywords)

    def get_model_config(self, model_mode):
        """
        获取指定模型的配置

        Args:
            model_mode: 模型模式 (PREVIEW/RENDER/ANIME)

        Returns:
            dict: 模型配置
        """
        return MODEL_CONFIGS.get(model_mode, MODEL_CONFIGS["PREVIEW"])

    def get_model_file(self, model_mode):
        """
        获取指定模型的文件名

        Args:
            model_mode: 模型模式 (PREVIEW/RENDER/ANIME)

        Returns:
            str: 模型文件名
        """
        return BASE_MODELS.get(model_mode, BASE_MODELS["PREVIEW"])

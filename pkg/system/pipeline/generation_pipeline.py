#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成流水线 - 封装图片生成流程
"""
import os
from pkg.system.adapters.forge_adapter import ForgeAdapter
from pkg.system.strategies.model_selector import ModelSelector
from pkg.system.strategies.prompt_enhancer import PromptEnhancer


OUTPUT_DIR = "evolution_history"
os.makedirs(OUTPUT_DIR, exist_ok=True)


class GenerationPipeline:
    """生成流水线 - 负责图片生成的完整流程"""

    def __init__(self, forge_url=None, forge_timeout=None):
        """
        初始化生成流水线

        Args:
            forge_url: Forge服务器URL
            forge_timeout: Forge请求超时时间
        """
        self.forge_adapter = ForgeAdapter(url=forge_url, timeout=forge_timeout)
        self.model_selector = ModelSelector()
        self.prompt_enhancer = PromptEnhancer()

    def generate(self, theme, state, iteration, params, prev_score=None, 
                prev_feedback=None, best_dimensions=None, external_suggestion=None,
                initial_model_choice=None, current_score=0.0):
        """
        生成图片

        Args:
            theme: 主题
            state: 当前状态
            iteration: 迭代次数
            params: 基础参数字典
            prev_score: 前一次迭代的得分
            prev_feedback: 前一次迭代的反馈信息
            best_dimensions: 历史最佳维度分数
            external_suggestion: 外部传入的创意建议
            initial_model_choice: 初始选择的模型
            current_score: 当前分数

        Returns:
            dict: 生成结果
                {
                    "path": str,  # 图片路径
                    "params": dict,  # 使用的参数
                    "model_mode": str,  # 使用的模型模式
                    "prompt": str  # 使用的Prompt
                }
        """
        # 1. 智能模型选择
        model_mode = self.model_selector.select(
            theme=theme,
            state=state,
            current_score=current_score,
            iteration=iteration,
            initial_model_choice=initial_model_choice
        )

        # 2. 获取模型配置
        model_config = self.model_selector.get_model_config(model_mode)
        model_file = self.model_selector.get_model_file(model_mode)

        # 3. Prompt增强
        use_random = (state != "OPTIMIZE")
        core_prompt = self.prompt_enhancer.enhance(
            theme=theme,
            state=state,
            prev_score=prev_score,
            prev_feedback=prev_feedback,
            best_dimensions=best_dimensions,
            external_suggestion=external_suggestion,
            use_random=use_random
        )

        # 4. 根据模型类型调整质量后缀
        if model_mode == "ANIME":
            quality_suffix = ", masterpiece, best quality, highly detailed, vibrant colors, official art"
        else:
            quality_suffix = ", 8k resolution, masterpiece, photorealistic, sharp focus, highly detailed, cinematic lighting"

        params['prompt'] = f"{core_prompt}, {quality_suffix}"

        # 5. 应用模型配置
        params['steps'] = model_config['steps']
        params['cfg_scale'] = model_config['cfg_scale']
        params['enable_hr'] = model_config['enable_hr']
        if model_mode in ["RENDER", "ANIME"]:
            params['hr_scale'] = model_config.get('hr_scale', 2.0)
            params['hr_second_pass_steps'] = model_config.get('hr_second_pass_steps', 3)
            params['denoising_strength'] = model_config.get('denoising_strength', 0.35)

        # 6. 设置模型文件
        params['override_settings'] = {
            "sd_model_checkpoint": model_file
        }

        # 7. 生成图片
        result = self.forge_adapter.generate(
            params=params,
            output_dir=OUTPUT_DIR,
            project_id=self._get_project_id(theme),
            iteration=iteration
        )

        if result:
            return {
                "path": result['path'],
                "params": params.copy(),
                "model_mode": model_mode,
                "prompt": core_prompt
            }

        return None

    def _get_project_id(self, theme):
        """
        获取项目ID（简化版，实际应该从外部传入）

        Args:
            theme: 主题

        Returns:
            str: 项目ID
        """
        import re
        import datetime

        # 生成英文项目名
        raw_name = self.prompt_enhancer.brain.generate_project_name(theme)
        raw_name = (raw_name or "untitled_project").strip()
        safe_name = re.sub(r"\s+", "_", raw_name)
        safe_name = re.sub(r"[^A-Za-z0-9_]+", "", safe_name)
        if not safe_name:
            safe_name = "untitled_project"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{safe_name}_{timestamp}"

    def get_best_prompt(self):
        """获取历史最佳Prompt"""
        return self.prompt_enhancer.get_best_prompt()

    def reset(self):
        """重置流水线状态"""
        self.prompt_enhancer.reset()

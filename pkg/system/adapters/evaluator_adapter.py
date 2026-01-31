#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评分器适配器 - 封装评分器调用逻辑
"""
from pkg.system.modules.evaluator import rate_image, get_api_status


class EvaluatorAdapter:
    """评分器适配器 - 封装评分器调用"""

    def __init__(self):
        """初始化评分器适配器"""
        pass

    def evaluate(self, image_path, target_concept, concept_weight=0.5, enable_smoothing=False):
        """
        评估图片

        Args:
            image_path: 图片路径
            target_concept: 目标概念/主题
            concept_weight: 概念权重 (0-1)
            enable_smoothing: 是否启用历史评分平滑

        Returns:
            dict: 评分结果
                {
                    "final_score": float,
                    "concept_score": float,
                    "quality_score": float,
                    "aesthetics_score": float,
                    "reasonableness_score": float,
                    "reason": str
                }
        """
        return rate_image(
            image_path=image_path,
            target_concept=target_concept,
            concept_weight=concept_weight,
            enable_smoothing=enable_smoothing
        )

    def get_status(self):
        """
        获取评分器状态

        Returns:
            dict: 评分器状态信息
        """
        return get_api_status()

    def reload_config(self):
        """重新加载评分器配置"""
        from pkg.system.modules.evaluator.core import api_manager
        api_manager.reload_config()

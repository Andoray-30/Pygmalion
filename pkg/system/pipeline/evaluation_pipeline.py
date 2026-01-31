#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
评估流水线 - 封装图片评估流程
"""
from pkg.system.adapters.evaluator_adapter import EvaluatorAdapter


class EvaluationPipeline:
    """评估流水线 - 负责图片评估的完整流程"""

    def __init__(self):
        """初始化评估流水线"""
        self.evaluator_adapter = EvaluatorAdapter()

    def evaluate(self, image_path, theme, concept_weight=0.5, enable_smoothing=False):
        """
        评估图片

        Args:
            image_path: 图片路径
            theme: 主题
            concept_weight: 概念权重 (0-1)
            enable_smoothing: 是否启用历史评分平滑

        Returns:
            dict: 评估结果
                {
                    "final_score": float,
                    "concept_score": float,
                    "quality_score": float,
                    "aesthetics_score": float,
                    "reasonableness_score": float,
                    "reason": str
                }
        """
        return self.evaluator_adapter.evaluate(
            image_path=image_path,
            target_concept=theme,
            concept_weight=concept_weight,
            enable_smoothing=enable_smoothing
        )

    def get_status(self):
        """
        获取评估器状态

        Returns:
            dict: 评估器状态信息
        """
        return self.evaluator_adapter.get_status()

    def reload_config(self):
        """重新加载评估器配置"""
        self.evaluator_adapter.reload_config()

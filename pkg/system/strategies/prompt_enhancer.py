#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt增强策略 - 智能优化和增强Prompt
"""
from pkg.system.modules.creator import CreativeDirector


class PromptEnhancer:
    """Prompt增强器 - 根据反馈和状态优化Prompt"""

    def __init__(self):
        self.brain = CreativeDirector()
        self.best_prompt = None
        self.best_prompt_score = 0.0

    def enhance(self, theme, state, prev_score=None, prev_feedback=None, 
                best_dimensions=None, external_suggestion=None, use_random=True):
        """
        增强Prompt

        Args:
            theme: 主题
            state: 当前状态
            prev_score: 前一次迭代的得分
            prev_feedback: 前一次迭代的反馈信息
            best_dimensions: 历史最佳维度分数
            external_suggestion: 外部传入的创意建议
            use_random: 是否使用随机镜头

        Returns:
            str: 增强后的Prompt
        """
        # 构建反馈上下文
        feedback_context = self._build_feedback_context(
            prev_score, prev_feedback, best_dimensions, external_suggestion
        )

        # 生成核心Prompt
        if state == "OPTIMIZE" and not use_random:
            # OPTIMIZE阶段：固定镜头，稳定收敛
            core_prompt = self.brain.brainstorm_prompt(
                theme, feedback_context=feedback_context, use_random=False
            )
        else:
            # 其他阶段：使用随机镜头探索
            core_prompt = self.brain.brainstorm_prompt(
                theme, feedback_context=feedback_context, use_random=True
            )

        # 更新最佳Prompt
        if prev_score and prev_score > self.best_prompt_score:
            self.best_prompt = core_prompt
            self.best_prompt_score = prev_score

        return core_prompt

    def _build_feedback_context(self, prev_score, prev_feedback, best_dimensions, external_suggestion):
        """
        构建反馈上下文

        Args:
            prev_score: 前一次迭代的得分
            prev_feedback: 前一次迭代的反馈信息
            best_dimensions: 历史最佳维度分数
            external_suggestion: 外部传入的创意建议

        Returns:
            str: 反馈上下文字符串
        """
        feedback_context = ""

        # 优先使用外部建议
        if external_suggestion and len(external_suggestion) > 10:
            feedback_context = f"\nUser feedback/Creative direction: {external_suggestion}"

        # 其次使用评分反馈
        elif prev_score is not None and prev_feedback is not None:
            # 识别并强化强势维度
            strong_dims = []
            if best_dimensions:
                for dim, score in best_dimensions.items():
                    if score > 0.88:
                        strong_dims.append(f"{dim}({score:.2f})")

            strong_hint = f" Keep excelling in: {', '.join(strong_dims)}." if strong_dims else ""
            feedback_context = f"\nPrevious score: {prev_score:.2f}.{strong_hint} Focus on improving {prev_feedback}."

        # 处理外部创意建议或用户实时反馈
        if external_suggestion:
            feedback_context = f"{feedback_context}\nExternal Insight/User Request: {external_suggestion}"

        return feedback_context

    def get_best_prompt(self):
        """获取历史最佳Prompt"""
        return self.best_prompt

    def reset(self):
        """重置Prompt增强器状态"""
        self.best_prompt = None
        self.best_prompt_score = 0.0

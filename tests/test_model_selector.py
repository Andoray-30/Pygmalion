#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试 - ModelSelector
"""
import pytest
from pkg.system.strategies.model_selector import ModelSelector


@pytest.fixture
def selector():
    """创建ModelSelector实例"""
    return ModelSelector()


class TestModelSelector:
    """ModelSelector单元测试"""

    def test_init(self, selector):
        """测试初始化"""
        assert selector is not None
        assert hasattr(selector, 'models')
        assert len(selector.models) >= 3

    def test_select_init_state(self, selector):
        """测试INIT状态选择快速模型"""
        model = selector.select(
            theme="test theme",
            state="INIT",
            current_score=0.0,
            iteration=1
        )
        assert model == "PREVIEW"

    def test_select_explore_state(self, selector):
        """测试EXPLORE状态选择快速模型"""
        model = selector.select(
            theme="test theme",
            state="EXPLORE",
            current_score=0.5,
            iteration=3
        )
        assert model == "PREVIEW"

    def test_select_optimize_low_score(self, selector):
        """测试OPTIMIZE状态但分数较低时继续用快速模型"""
        model = selector.select(
            theme="test theme",
            state="OPTIMIZE",
            current_score=0.70,
            iteration=10
        )
        assert model == "PREVIEW"

    def test_select_optimize_high_score_realistic(self, selector):
        """测试OPTIMIZE状态高分时切换到高质量模型（写实）"""
        model = selector.select(
            theme="realistic city landscape",
            state="OPTIMIZE",
            current_score=0.85,
            iteration=10,
            initial_model_choice="PREVIEW"
        )
        assert model == "RENDER"

    def test_select_optimize_high_score_anime(self, selector):
        """测试OPTIMIZE状态高分时切换到动漫模型"""
        model = selector.select(
            theme="anime girl character",
            state="OPTIMIZE",
            current_score=0.85,
            iteration=10,
            initial_model_choice="PREVIEW"
        )
        assert model == "ANIME"

    def test_select_finetune_state(self, selector):
        """测试FINETUNE状态保持高质量模型"""
        model = selector.select(
            theme="test theme",
            state="FINETUNE",
            current_score=0.90,
            iteration=20,
            initial_model_choice="PREVIEW"
        )
        assert model in ["RENDER", "ANIME"]

    def test_is_anime_theme_detection(self, selector):
        """测试动漫主题检测"""
        # 动漫关键词
        assert selector._is_anime_theme("anime girl") is True
        assert selector._is_anime_theme("manga character") is True
        assert selector._is_anime_theme("cute chibi") is True
        assert selector._is_anime_theme("动漫少女") is True
        
        # 非动漫关键词
        assert selector._is_anime_theme("realistic city") is False
        assert selector._is_anime_theme("photorealistic portrait") is False

    def test_get_model_config(self, selector):
        """测试获取模型配置"""
        config = selector.get_model_config("PREVIEW")
        assert config is not None
        assert "steps" in config
        assert "cfg_scale" in config
        assert "enable_hr" in config

    def test_get_model_file(self, selector):
        """测试获取模型文件名"""
        from pkg.infrastructure.config import BASE_MODELS
        
        for mode in ["PREVIEW", "RENDER", "ANIME"]:
            model_file = selector.get_model_file(mode)
            assert model_file is not None
            assert model_file == BASE_MODELS[mode]

    def test_select_with_initial_choice_render(self, selector):
        """测试初始选择为RENDER时保持不变"""
        model = selector.select(
            theme="realistic city",
            state="OPTIMIZE",
            current_score=0.85,
            iteration=10,
            initial_model_choice="RENDER"
        )
        assert model == "RENDER"

    def test_select_minimum_iterations_check(self, selector):
        """测试最小迭代次数检查"""
        # 迭代次数不足时不应切换
        model = selector.select(
            theme="test theme",
            state="OPTIMIZE",
            current_score=0.85,
            iteration=2,  # 小于MODEL_SWITCH_MIN_ITERATIONS
            initial_model_choice="PREVIEW"
        )
        assert model == "PREVIEW"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

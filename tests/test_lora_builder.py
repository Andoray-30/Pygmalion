#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试 - LoRABuilder
"""
import pytest
from pkg.system.builders.lora_builder import LoRABuilder


@pytest.fixture
def lora_builder():
    """创建LoRABuilder实例"""
    return LoRABuilder()


@pytest.fixture
def custom_library():
    """自定义LoRA库"""
    return {
        "TEST_LORA": {
            "file": "test_lora",
            "weight": 0.8,
            "trigger": "test trigger"
        }
    }


class TestLoRABuilder:
    """LoRABuilder单元测试"""

    def test_init_with_default_library(self, lora_builder):
        """测试默认库初始化"""
        assert lora_builder.library is not None
        assert "CYBERPUNK" in lora_builder.library
        assert "ANIME_LINEART" in lora_builder.library

    def test_init_with_custom_library(self, custom_library):
        """测试自定义库初始化"""
        builder = LoRABuilder(lora_library=custom_library)
        assert "TEST_LORA" in builder.library
        assert builder.library["TEST_LORA"]["file"] == "test_lora"

    def test_build_existing_lora(self, lora_builder):
        """测试构建已存在的LoRA"""
        base_prompt = "city at night"
        result = lora_builder.build("CYBERPUNK", base_prompt)
        
        assert "<lora:cyberpunk_edgerunners_style_sdxl:" in result
        assert "city at night" in result
        assert "neon lights" in result  # trigger词

    def test_build_nonexistent_lora(self, lora_builder):
        """测试构建不存在的LoRA"""
        base_prompt = "city at night"
        result = lora_builder.build("NONEXISTENT", base_prompt)
        
        # 应该返回原始prompt
        assert result == base_prompt
        assert "<lora:" not in result

    def test_build_with_weight_override(self, lora_builder):
        """测试覆盖权重"""
        base_prompt = "city at night"
        result = lora_builder.build("CYBERPUNK", base_prompt, weight_override=0.5)
        
        assert "<lora:cyberpunk_edgerunners_style_sdxl:0.5>" in result

    def test_build_multi(self, lora_builder):
        """测试构建多个LoRA"""
        base_prompt = "city at night"
        style_keys = [
            ("CYBERPUNK", 0.8),
            ("PHOTOREALISTIC", 0.6)
        ]
        
        result = lora_builder.build_multi(style_keys, base_prompt)
        
        assert "<lora:cyberpunk_edgerunners_style_sdxl:0.8>" in result
        assert "<lora:style_lora_realis:0.6>" in result
        assert "city at night" in result

    def test_auto_select_cyberpunk(self, lora_builder):
        """测试自动选择赛博朋克LoRA"""
        base_prompt = "street scene"
        result = lora_builder.auto_select("cyberpunk city neon", base_prompt)
        
        assert "<lora:cyberpunk_edgerunners_style_sdxl:" in result

    def test_auto_select_anime(self, lora_builder):
        """测试自动选择动漫LoRA"""
        base_prompt = "girl character"
        result = lora_builder.auto_select("anime girl", base_prompt)
        
        assert "<lora:LineAniRedmondV2-Lineart-LineAniAF:" in result

    def test_auto_select_portrait(self, lora_builder):
        """测试自动选择人像LoRA"""
        base_prompt = "person"
        result = lora_builder.auto_select("portrait of a person", base_prompt)
        
        assert "<lora:studio_portrait_xl:" in result

    def test_auto_select_realistic(self, lora_builder):
        """测试自动选择写实LoRA"""
        base_prompt = "landscape"
        result = lora_builder.auto_select("realistic photo of landscape", base_prompt)
        
        assert "<lora:style_lora_realis:" in result

    def test_auto_select_no_match(self, lora_builder):
        """测试无匹配时返回原prompt"""
        base_prompt = "abstract art"
        result = lora_builder.auto_select("abstract art", base_prompt)
        
        # 没有匹配的关键词，应该返回原prompt
        assert result == base_prompt

    def test_add_lora(self, lora_builder):
        """测试动态添加LoRA"""
        lora_builder.add_lora(
            name="CUSTOM_LORA",
            file="custom_file",
            weight=0.9,
            trigger="custom trigger"
        )
        
        assert "CUSTOM_LORA" in lora_builder.library
        assert lora_builder.library["CUSTOM_LORA"]["file"] == "custom_file"
        assert lora_builder.library["CUSTOM_LORA"]["weight"] == 0.9

    def test_list_available(self, lora_builder):
        """测试列出可用LoRA"""
        available = lora_builder.list_available()
        
        assert isinstance(available, list)
        assert "CYBERPUNK" in available
        assert "ANIME_LINEART" in available

    def test_build_without_trigger(self):
        """测试没有trigger的LoRA"""
        custom_library = {
            "NO_TRIGGER": {
                "file": "test_file",
                "weight": 0.7,
                "trigger": ""
            }
        }
        builder = LoRABuilder(lora_library=custom_library)
        
        base_prompt = "test prompt"
        result = builder.build("NO_TRIGGER", base_prompt)
        
        assert "<lora:test_file:0.7>" in result
        assert "test prompt" in result
        # 不应该有多余的逗号
        assert not result.startswith(", ")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LoRA构建器 - 实现LoRA挂载功能
"""


class LoRABuilder:
    """LoRA构建器 - 负责LoRA挂载和Prompt生成"""

    def __init__(self, lora_library=None):
        """
        初始化LoRA构建器

        Args:
            lora_library: LoRA库配置字典
                {
                    "CYBERPUNK": {
                        "file": "cyberpunk_xl",
                        "weight": 0.8,
                        "trigger": "neon lights, futuristic"
                    },
                    "ANIME_STYLE": {
                        "file": "anime_lineart_xl",
                        "weight": 0.7,
                        "trigger": "anime style, cel shading"
                    }
                }
        """
        self.library = lora_library or self._get_default_library()

    def _get_default_library(self):
        """获取默认LoRA库"""
        return {
            "CYBERPUNK": {
                "file": "cyberpunk_xl",
                "weight": 0.8,
                "trigger": "neon lights, futuristic cityscape"
            },
            "ANIME_STYLE": {
                "file": "anime_lineart_xl",
                "weight": 0.7,
                "trigger": "anime style, cel shading"
            },
            "REALISTIC": {
                "file": "realistic_vision_xl",
                "weight": 0.6,
                "trigger": "photorealistic, detailed"
            },
            "PORTRAIT": {
                "file": "portrait_xl",
                "weight": 0.75,
                "trigger": "professional portrait, studio lighting"
            }
        }

    def build(self, style_key, base_prompt, weight_override=None):
        """
        构建带LoRA的Prompt

        Args:
            style_key: 风格关键词 (e.g., "CYBERPUNK", "ANIME_STYLE")
            base_prompt: 基础Prompt
            weight_override: 覆盖默认权重（可选）

        Returns:
            str: 包含LoRA标签的完整Prompt
        """
        if style_key not in self.library:
            print(f"⚠️ LoRA '{style_key}' 不在库中，跳过")
            return base_prompt

        lora_cfg = self.library[style_key]
        weight = weight_override if weight_override is not None else lora_cfg['weight']
        lora_str = f"<lora:{lora_cfg['file']}:{weight}>"
        trigger = lora_cfg.get('trigger', '')

        if trigger:
            return f"{lora_str}, {trigger}, {base_prompt}"
        else:
            return f"{lora_str}, {base_prompt}"

    def build_multi(self, style_keys, base_prompt):
        """
        构建多个LoRA的Prompt

        Args:
            style_keys: 风格关键词列表 [(style_key, weight), ...]
            base_prompt: 基础Prompt

        Returns:
            str: 包含多个LoRA标签的完整Prompt
        """
        lora_tags = []
        triggers = []

        for style_key, weight in style_keys:
            if style_key not in self.library:
                continue

            lora_cfg = self.library[style_key]
            lora_tags.append(f"<lora:{lora_cfg['file']}:{weight}>")
            trigger = lora_cfg.get('trigger', '')
            if trigger:
                triggers.append(trigger)

        lora_str = ", ".join(lora_tags)
        trigger_str = ", ".join(triggers)

        if trigger_str:
            return f"{lora_str}, {trigger_str}, {base_prompt}"
        else:
            return f"{lora_str}, {base_prompt}"

    def auto_select(self, theme, base_prompt):
        """
        根据主题自动选择LoRA

        Args:
            theme: 主题描述
            base_prompt: 基础Prompt

        Returns:
            str: 包含自动选择LoRA的Prompt
        """
        theme_lower = theme.lower()

        # 简单的关键词匹配
        if any(k in theme_lower for k in ["cyber", "neon", "futuristic", "sci-fi"]):
            return self.build("CYBERPUNK", base_prompt)
        elif any(k in theme_lower for k in ["anime", "manga", "cartoon"]):
            return self.build("ANIME_STYLE", base_prompt)
        elif any(k in theme_lower for k in ["portrait", "face", "person", "character"]):
            return self.build("PORTRAIT", base_prompt)
        elif any(k in theme_lower for k in ["photo", "realistic", "real"]):
            return self.build("REALISTIC", base_prompt)

        return base_prompt

    def add_lora(self, name, file, weight=0.7, trigger=""):
        """
        动态添加LoRA到库中

        Args:
            name: LoRA名称
            file: LoRA文件名（不含扩展名）
            weight: 默认权重
            trigger: 触发词
        """
        self.library[name] = {
            "file": file,
            "weight": weight,
            "trigger": trigger
        }

    def list_available(self):
        """列出所有可用的LoRA"""
        return list(self.library.keys())

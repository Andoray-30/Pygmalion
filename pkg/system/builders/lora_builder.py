#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LoRA构建器 - 实现LoRA挂载功能
"""


class LoRABuilder:
    """LoRA构建器 - 负责LoRA挂载和Prompt生成 (分类增强版)"""

    def __init__(self, lora_library=None):
        """
        初始化LoRA构建器
        """
        if lora_library:
            raw_library = lora_library
        else:
            try:
                from pkg.infrastructure.config.settings import LORA_LIBRARY
                raw_library = LORA_LIBRARY
            except ImportError:
                raw_library = self._get_fallback_library()

        self.categorized_library = self._normalize_library(raw_library)
        self.library = self._flatten_styles(self.categorized_library)

    def _get_fallback_library(self):
        """核心库加载失败时的兜底逻辑"""
        return {
            "STYLES": {
                "CYBERPUNK": {"file": "cyberpunk_xl", "weight": 0.8, "trigger": "neon lights"}
            },
            "ENHANCERS": {
                "DETAIL": {"file": "xl_more_art-full_v1", "weight": 0.5, "trigger": "detailed"}
            }
        }

    def _normalize_library(self, library):
        """统一库结构为包含 STYLES/ENHANCERS 的格式"""
        if "STYLES" in library or "ENHANCERS" in library:
            styles = library.get("STYLES", {})
            enhancers = library.get("ENHANCERS", {})
            return {"STYLES": styles, "ENHANCERS": enhancers}

        # 兼容旧版扁平结构
        return {"STYLES": library, "ENHANCERS": {}}

    def _flatten_styles(self, categorized_library):
        """将 STYLES 展平成旧版扁平结构供测试/旧API使用"""
        flat = dict(categorized_library.get("STYLES", {}))
        return flat

    def _resolve_style_key(self, style_key):
        """兼容别名映射"""
        if style_key is None:
            return None

        key = str(style_key).upper()
        aliases = {
            "ANIME_STYLE": "ANIME_LINEART",
            "REALISTIC": "PHOTOREALISTIC"
        }
        return aliases.get(key, key)

    def build_categorized(self, style_key=None, enhancers=None, base_prompt="", weight_override=None):
        """
        组合风格 LoRA 与 多个增强类 LoRA 的 Prompt
        """
        lora_tags = []
        triggers = []
        
        # 1. 挂载风格 LoRA
        if style_key and str(style_key).upper() != "NONE":
            style_lib = self.categorized_library.get("STYLES", {})
            resolved_key = self._resolve_style_key(style_key)
            cfg = style_lib.get(resolved_key)
            if cfg:
                weight = weight_override if weight_override is not None else cfg['weight']
                lora_tags.append(f"<lora:{cfg['file']}:{weight}>")
                if cfg.get("trigger"):
                    triggers.append(cfg["trigger"])

        # 2. 挂载增强 LoRA
        enhancers = enhancers or []
        enhancer_lib = self.categorized_library.get("ENHANCERS", {})
        for enc_key in enhancers:
            cfg = enhancer_lib.get(enc_key)
            if cfg:
                lora_tags.append(f"<lora:{cfg['file']}:{cfg['weight']}>")
                if cfg.get("trigger"):
                    triggers.append(cfg["trigger"])

        # 3. 组合
        lora_str = " ".join(lora_tags)
        trigger_str = ", ".join(triggers)
        
        final_prompt = base_prompt
        if trigger_str:
            final_prompt = f"{trigger_str}, {final_prompt}"
        if lora_str:
            final_prompt = f"{lora_str} {final_prompt}"
            
        return final_prompt.strip()

    def list_available(self):
        """返回所有可用的 STYLES 名称列表"""
        return list(self.categorized_library.get("STYLES", {}).keys())

    def build(self, style_key, base_prompt, weight_override=None):
        """旧版API：构建单个 LoRA"""
        if not style_key:
            return base_prompt

        style_lib = self.categorized_library.get("STYLES", {})
        resolved_key = self._resolve_style_key(style_key)
        cfg = style_lib.get(resolved_key)
        if not cfg:
            return base_prompt

        return self.build_categorized(resolved_key, [], base_prompt, weight_override=weight_override)

    def build_multi(self, style_keys, base_prompt):
        """旧版API：构建多个 LoRA"""
        if not style_keys:
            return base_prompt

        lora_tags = []
        triggers = []
        style_lib = self.categorized_library.get("STYLES", {})

        for style_key, weight in style_keys:
            resolved_key = self._resolve_style_key(style_key)
            cfg = style_lib.get(resolved_key)
            if not cfg:
                continue
            lora_tags.append(f"<lora:{cfg['file']}:{weight}>")
            if cfg.get("trigger"):
                triggers.append(cfg["trigger"])

        if not lora_tags:
            return base_prompt

        lora_str = " ".join(lora_tags)
        trigger_str = ", ".join(triggers)

        final_prompt = base_prompt
        if trigger_str:
            final_prompt = f"{trigger_str}, {final_prompt}"
        return f"{lora_str} {final_prompt}".strip()

    def auto_select(self, theme, base_prompt):
        """旧版API：基于关键词自动选择风格 LoRA"""
        theme_lower = (theme or "").lower()

        if "cyberpunk" in theme_lower:
            return self.build("CYBERPUNK", base_prompt)
        if "anime" in theme_lower:
            return self.build("ANIME_LINEART", base_prompt)
        if "portrait" in theme_lower or "person" in theme_lower:
            return self.build("STUDIO_PORTRAIT", base_prompt)
        if "realistic" in theme_lower:
            return self.build("PHOTOREALISTIC", base_prompt)

        return base_prompt

    def add_lora(self, name, file, weight=0.7, trigger=""):
        """旧版API：动态添加 LoRA"""
        entry = {"file": file, "weight": weight, "trigger": trigger}
        self.library[name] = entry
        self.categorized_library.setdefault("STYLES", {})[name] = entry

    def llm_select(self, theme, base_prompt, director):
        """
        [核心逻辑] 使用 LLM 智能选择 Style LoRA，并根据规则自动挂载 Enhancers
        """
        print(f"🧠 [智能决策] 正在分析主题 '{theme}' 的视觉风格需求...")
        
        # 1. 风格推荐
        available_styles = self.list_available()
        recommendation = director.recommend_lora(theme, available_styles)
        style_key = recommendation.get("lora_key")
        
        # 2. 自动挂载增强器 (Universal LoRAs)
        # 默认挂载通用画质与艺术感增强
        enhancers = ["DETAIL", "ARTIFACTS"] 
        
        # 语义探测：启发式挂载补充增强器
        theme_lower = theme.lower()
        # 检测人像相关（挂载手部修复/增强）
        if any(w in theme_lower for w in ["person", "girl", "portrait", "woman", "man", "hand"]):
            enhancers.append("HANDS")
        # 检测光影相关
        if any(w in theme_lower for w in ["lighting", "dark", "night", "glow", "shadow"]):
            enhancers.append("LIGHTING")

        # 3. 构建 Prompt
        if style_key and str(style_key).upper() != "NONE" and style_key in self.categorized_library.get("STYLES", {}):
            weight = recommendation.get("weight", 0.75)
            reason = recommendation.get("reason", "符合视觉意图")
            print(f"✨ [推荐选中] 风格: {style_key} + 增强器: {enhancers}")
            return self.build_categorized(style_key, enhancers, base_prompt, weight_override=weight)
        
        print(f"ℹ️ [策略中性] 无特定风格推荐，仅挂载增强器: {enhancers}")
        return self.build_categorized(None, enhancers, base_prompt)

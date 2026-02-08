#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IP-Adapter构建器 - 实现IP-Adapter集成功能
支持 FaceID、Plus、Style 等多种模式
"""
from PIL import Image
from .utils import encode_image_to_base64


class IPAdapterBuilder:
    """IP-Adapter构建器 - 负责IP-Adapter参数构建"""

    SUPPORTED_MODELS = {
        "faceid_plusv2": "ip-adapter-faceid-plusv2_sdxl.bin",
        "plus": "ip-adapter-plus_sdxl_vit-h.safetensors",
        "plus_face": "ip-adapter-plus-face_sdxl_vit-h.safetensors",
    }

    def __init__(self):
        """初始化IP-Adapter构建器"""
        pass

    def build(self, reference_image, model="faceid_plusv2", weight=0.8, 
              start=0.0, end=1.0):
        """
        构建单个IP-Adapter配置

        Args:
            reference_image: PIL.Image对象或图片路径
            model: IP-Adapter模型类型 (faceid_plusv2/plus/plus_face)
            weight: 控制权重 (0.0-2.0)
            start: 引导开始位置 (0.0-1.0)
            end: 引导结束位置 (0.0-1.0)

        Returns:
            dict: Forge API的IP-Adapter配置
        """
        if model not in self.SUPPORTED_MODELS:
            raise ValueError(f"不支持的IP-Adapter模型: {model}")

        # 加载图片
        if isinstance(reference_image, str):
            img = Image.open(reference_image)
        else:
            img = reference_image

        # 编码为Base64
        img_base64 = encode_image_to_base64(img)

        # 构建IP-Adapter配置
        return {
            "alwayson_scripts": {
                "forge_additional_modules": {
                    "args": [{
                        "module": "ip_adapter",
                        "model": self.SUPPORTED_MODELS[model],
                        "input_image": img_base64,
                        "weight": weight,
                        "guidance_start": start,
                        "guidance_end": end,
                        "control_mode": "balanced"
                    }]
                }
            }
        }

    def build_multi(self, configs):
        """
        构建多个IP-Adapter配置

        Args:
            configs: IP-Adapter配置列表
                [
                    {
                        "image": PIL.Image或路径,
                        "model": "faceid_plusv2",
                        "weight": 0.8,
                        "start": 0.0,
                        "end": 1.0
                    },
                    ...
                ]

        Returns:
            dict: 多个IP-Adapter的配置
        """
        args = []
        for cfg in configs:
            img = cfg.get("image")
            model = cfg.get("model", "faceid_plusv2")
            
            if isinstance(img, str):
                img = Image.open(img)

            img_base64 = encode_image_to_base64(img)

            args.append({
                "module": "ip_adapter",
                "model": self.SUPPORTED_MODELS[model],
                "input_image": img_base64,
                "weight": cfg.get("weight", 0.8),
                "guidance_start": cfg.get("start", 0.0),
                "guidance_end": cfg.get("end", 1.0),
                "control_mode": "balanced"
            })

        return {
            "alwayson_scripts": {
                "forge_additional_modules": {
                    "args": args
                }
            }
        }

    @classmethod
    def list_supported_models(cls):
        """列出所有支持的IP-Adapter模型"""
        return list(cls.SUPPORTED_MODELS.keys())

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ControlNet构建器 - 实现ControlNet集成功能
"""
import base64
import io
import numpy as np
from PIL import Image


class ControlNetBuilder:
    """ControlNet构建器 - 负责ControlNet参数构建"""

    SUPPORTED_TYPES = [
        "canny",      # 边缘检测
        "depth",      # 深度图
        "normal",     # 法线图
        "openpose",   # 姿态检测
        "mlsd",       # 线条检测
        "scribble",   # 涂鸦
        "seg",        # 分割
        "tile",       # 平铺
    ]

    def __init__(self):
        """初始化ControlNet构建器"""
        self.has_cv2 = self._check_cv2()

    def _check_cv2(self):
        """检查OpenCV是否可用"""
        try:
            import cv2
            return True
        except ImportError:
            print("⚠️ OpenCV未安装，ControlNet预处理功能受限")
            return False

    def build(self, reference_image, cn_type="canny", weight=0.8, 
              guidance_start=0.0, guidance_end=1.0, processor="none"):
        """
        构建ControlNet配置

        Args:
            reference_image: PIL.Image对象或图片路径
            cn_type: ControlNet类型 (canny/depth/openpose等)
            weight: 控制权重 (0.0-2.0)
            guidance_start: 引导开始位置 (0.0-1.0)
            guidance_end: 引导结束位置 (0.0-1.0)
            processor: 预处理器名称 ("none"表示已预处理)

        Returns:
            dict: Forge API的alwayson_scripts配置
        """
        if cn_type not in self.SUPPORTED_TYPES:
            raise ValueError(f"不支持的ControlNet类型: {cn_type}")

        # 加载图片
        if isinstance(reference_image, str):
            img = Image.open(reference_image)
        else:
            img = reference_image

        # 预处理图片
        if processor != "none" and self.has_cv2:
            processed = self._preprocess(img, cn_type)
        else:
            processed = img

        # 编码为Base64
        img_base64 = self._encode_image(processed)

        # 构建ControlNet配置
        return {
            "alwayson_scripts": {
                "controlnet": {
                    "args": [{
                        "enabled": True,
                        "image": img_base64,
                        "model": self._get_model_name(cn_type),
                        "weight": weight,
                        "guidance_start": guidance_start,
                        "guidance_end": guidance_end,
                        "processor_res": 512,
                        "threshold_a": 100,
                        "threshold_b": 200,
                        "resize_mode": 1,  # Scale to Fit
                        "control_mode": 0,  # Balanced
                        "pixel_perfect": True
                    }]
                }
            }
        }

    def build_multi(self, control_configs):
        """
        构建多个ControlNet配置

        Args:
            control_configs: ControlNet配置列表
                [
                    {
                        "image": PIL.Image,
                        "type": "canny",
                        "weight": 0.8
                    },
                    ...
                ]

        Returns:
            dict: 多个ControlNet的配置
        """
        args = []
        for cfg in control_configs:
            img = cfg.get("image")
            cn_type = cfg.get("type", "canny")
            weight = cfg.get("weight", 0.8)

            if isinstance(img, str):
                img = Image.open(img)

            processed = self._preprocess(img, cn_type) if self.has_cv2 else img
            img_base64 = self._encode_image(processed)

            args.append({
                "enabled": True,
                "image": img_base64,
                "model": self._get_model_name(cn_type),
                "weight": weight,
                "guidance_start": cfg.get("guidance_start", 0.0),
                "guidance_end": cfg.get("guidance_end", 1.0),
                "pixel_perfect": True
            })

        return {
            "alwayson_scripts": {
                "controlnet": {
                    "args": args
                }
            }
        }

    def _preprocess(self, img, cn_type):
        """
        预处理图片

        Args:
            img: PIL.Image对象
            cn_type: ControlNet类型

        Returns:
            PIL.Image: 预处理后的图片
        """
        if not self.has_cv2:
            return img

        import cv2

        # 转换为numpy数组
        img_array = np.array(img)
        
        # 确保是RGB格式
        if len(img_array.shape) == 2:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_GRAY2RGB)
        elif img_array.shape[2] == 4:
            img_array = cv2.cvtColor(img_array, cv2.COLOR_RGBA2RGB)

        # 根据类型预处理
        if cn_type == "canny":
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            edges = cv2.Canny(gray, 100, 200)
            processed = cv2.cvtColor(edges, cv2.COLOR_GRAY2RGB)
        elif cn_type == "depth":
            # 简单的深度估计（实际应使用深度模型）
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            processed = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        else:
            processed = img_array

        return Image.fromarray(processed)

    def _encode_image(self, img):
        """
        将PIL Image编码为Base64字符串

        Args:
            img: PIL.Image对象

        Returns:
            str: Base64编码的字符串
        """
        buffer = io.BytesIO()
        img.save(buffer, format='PNG')
        img_bytes = buffer.getvalue()
        return base64.b64encode(img_bytes).decode('utf-8')

    def _get_model_name(self, cn_type):
        """
        获取ControlNet模型名称

        Args:
            cn_type: ControlNet类型

        Returns:
            str: 模型文件名
        """
        # SDXL ControlNet模型命名
        model_map = {
            "canny": "control_v11p_sd15_canny",
            "depth": "control_v11f1p_sd15_depth",
            "normal": "control_v11p_sd15_normalbae",
            "openpose": "control_v11p_sd15_openpose",
            "mlsd": "control_v11p_sd15_mlsd",
            "scribble": "control_v11p_sd15_scribble",
            "seg": "control_v11p_sd15_seg",
            "tile": "control_v11f1e_sd15_tile",
        }
        return model_map.get(cn_type, f"control_v11p_sd15_{cn_type}")

    @classmethod
    def list_supported_types(cls):
        """列出所有支持的ControlNet类型"""
        return cls.SUPPORTED_TYPES.copy()

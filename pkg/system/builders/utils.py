#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Builders 通用工具函数
"""
import base64
import io
from PIL import Image


def encode_image_to_base64(img):
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

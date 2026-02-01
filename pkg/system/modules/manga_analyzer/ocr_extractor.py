#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
OCR 文本提取器 (OCR Extractor)

功能：从漫画图片中提取文本（台词、气泡、旁白等）

技术方案：
    PaddleOCR（推荐）
    - 优点：支持中文、日文、英文、竖排文本
    - 准确率高，开源免费
    - 支持GPU加速
    
    依赖: paddleocr (待安装)
    pip install paddleocr paddlepaddle

状态: 框架版本，核心OCR逻辑待集成
"""
import logging
from typing import List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class TextBox:
    """文本框信息"""
    content: str
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    type: str  # 'dialogue', 'narration', 'sfx'


class OCRExtractor:
    """
    OCR 文本提取器
    
    当前实现：占位符版本
    待集成：PaddleOCR
    """
    
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.ocr = None
        self._init_ocr()
    
    def _init_ocr(self):
        """初始化 OCR 模型"""
        try:
            from paddleocr import PaddleOCR
            logger.info(f"🔄 初始化 PaddleOCR (use_gpu={self.use_gpu})...")
            self.ocr = PaddleOCR(
                use_angle_cls=True,
                lang='ch',
                gpu=self.use_gpu
            )
            logger.info("✅ PaddleOCR 初始化成功")
        except ImportError:
            logger.warning("⚠️ PaddleOCR 未安装，仅支持占位符模式")
            logger.warning("   安装命令: pip install paddleocr paddlepaddle")
            self.ocr = None
    
    def extract(self, image_path: str, bbox: Tuple = None, language: str = 'zh_CN') -> List[TextBox]:
        """
        从图片中提取文本
        
        Args:
            image_path: 图片路径
            bbox: 感兴趣区域 (x, y, w, h)，None表示整个图片
            language: 语言代码 (zh_CN/ja_JP/en_US)
            
        Returns:
            List[TextBox]: 提取的文本列表
        """
        if self.ocr is None:
            logger.warning("⚠️ OCR 未初始化，返回空结果")
            return []
        
        try:
            import cv2
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"无法读取图片: {image_path}")
            
            # 如果指定了感兴趣区域，裁剪
            if bbox:
                x, y, w, h = bbox
                image = image[y:y+h, x:x+w]
            
            # 运行 OCR
            result = self.ocr.ocr(image, cls=True)
            
            # 转换输出格式
            text_boxes = []
            for line in result:
                for word_info in line:
                    # word_info = [[[x1,y1], [x2,y2], [x3,y3], [x4,y4]], (text, confidence)]
                    points, (text, conf) = word_info
                    
                    # 计算bounding box
                    xs = [p[0] for p in points]
                    ys = [p[1] for p in points]
                    x_min, y_min = int(min(xs)), int(min(ys))
                    x_max, y_max = int(max(xs)), int(max(ys))
                    
                    # 如果之前有区域偏移，需要加回
                    if bbox:
                        x_min += bbox[0]
                        y_min += bbox[1]
                    
                    text_boxes.append(TextBox(
                        content=text,
                        bbox=(x_min, y_min, x_max - x_min, y_max - y_min),
                        confidence=float(conf),
                        type=self._classify_text_type(text)
                    ))
            
            logger.info(f"✅ 提取文本 {len(text_boxes)} 个")
            return text_boxes
            
        except Exception as e:
            logger.error(f"❌ OCR 提取失败: {e}")
            return []
    
    def _classify_text_type(self, text: str) -> str:
        """
        分类文本类型
        
        Returns:
            'dialogue': 对话
            'narration': 旁白
            'sfx': 拟声词效果
        """
        # 简化分类逻辑
        if any(c in text for c in '！？！？!?'):
            return 'dialogue'
        elif any(c in text for c in '。，'):
            return 'narration'
        else:
            return 'sfx'


# TODO: 集成多语言支持
class MultiLanguageOCR:
    """多语言 OCR 支持"""
    
    SUPPORTED_LANGUAGES = {
        'zh_CN': 'ch',
        'zh_TW': 'ch_tra',
        'ja_JP': 'japan',
        'en_US': 'en',
        'ko_KR': 'korean'
    }
    
    pass

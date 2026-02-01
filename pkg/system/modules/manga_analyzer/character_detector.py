#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色检测器 (Character Detector)

功能：检测漫画页面中的人物角色

技术方案：
    方案A（简单）: 基于肤色检测 + 连通分量分析
        - 快速，无需模型
        - 效果有限
        
    方案B（推荐）: YOLOv8 人物检测
        - 准确率高
        - 支持自定义训练
        
    方案C（高级）: 人脸检测 + 角色识别
        - 支持角色跨页追踪
        - 复杂度高

当前实现：YOLOv8 框架
"""
import logging
from typing import List, Tuple
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Character:
    """角色信息"""
    char_id: str
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    confidence: float
    visual_desc: str = ""
    pose_keypoints: list = None
    face_embedding: list = None
    
    def __post_init__(self):
        if self.pose_keypoints is None:
            self.pose_keypoints = []
        if self.face_embedding is None:
            self.face_embedding = []


class CharacterDetector:
    """
    角色检测器
    
    基于 YOLOv8 的方法
    """
    
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.model = None
        self._init_model()
    
    def _init_model(self):
        """初始化 YOLO 模型"""
        try:
            from ultralytics import YOLO
            logger.info("🔄 加载 YOLOv8 人物检测模型...")
            # 使用预训练的 YOLOv8 nano 模型
            self.model = YOLO('yolov8n.pt')
            logger.info("✅ YOLOv8 模型加载成功")
        except ImportError:
            logger.warning("⚠️ YOLOv8 (ultralytics) 未安装")
            logger.warning("   安装命令: pip install ultralytics")
            self.model = None
    
    def detect(self, image_path: str, bbox: Tuple = None) -> List[Character]:
        """
        检测图片中的角色
        
        Args:
            image_path: 图片路径
            bbox: 感兴趣区域 (x, y, w, h)
            
        Returns:
            List[Character]: 检测到的角色列表
        """
        if self.model is None:
            logger.warning("⚠️ YOLOv8 模型未加载，返回空结果")
            return []
        
        try:
            import cv2
            
            # 读取图片
            image = cv2.imread(image_path)
            if image is None:
                raise FileNotFoundError(f"无法读取图片: {image_path}")
            
            # 如果指定了感兴趣区域，裁剪
            roi_offset = (0, 0)
            if bbox:
                x, y, w, h = bbox
                image = image[y:y+h, x:x+w]
                roi_offset = (x, y)
            
            # 运行 YOLO
            results = self.model(image, conf=0.5)
            
            # 转换输出格式
            characters = []
            char_idx = 0
            
            for r in results:
                for box in r.boxes:
                    # box.xyxy = [[x1, y1, x2, y2]]
                    x1, y1, x2, y2 = map(int, box.xyxy[0])
                    conf = float(box.conf[0])
                    
                    # YOLO 类别 0=person
                    if int(box.cls[0]) == 0:  # person class
                        # 加上区域偏移
                        x1 += roi_offset[0]
                        y1 += roi_offset[1]
                        x2 += roi_offset[0]
                        y2 += roi_offset[1]
                        
                        characters.append(Character(
                            char_id=f"C{char_idx + 1}",
                            bbox=(x1, y1, x2-x1, y2-y1),
                            confidence=conf,
                            visual_desc=""
                        ))
                        char_idx += 1
            
            logger.info(f"✅ 检测角色 {len(characters)} 个")
            return characters
            
        except Exception as e:
            logger.error(f"❌ 角色检测失败: {e}")
            return []


class FaceEmbeddingExtractor:
    """
    人脸特征提取器
    
    支持跨页角色追踪
    依赖: face_recognition
    """
    
    def __init__(self, use_gpu: bool = False):
        self.use_gpu = use_gpu
        self.model = None
        # TODO: 初始化人脸识别模型
    
    def extract(self, image, bbox: Tuple) -> list:
        """
        提取人脸特征向量
        
        Returns:
            list: 128维特征向量
        """
        # TODO: 实现
        return []

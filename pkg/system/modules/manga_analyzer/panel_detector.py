#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分镜检测器 (Panel Detector)

功能：自动检测漫画页面中的分镜框 (Panel Bounding Box)

技术方案：
    方案A（推荐）: 基于轮廓检测的传统CV方法
        - 优点：无需训练，速度快，适合大部分规整漫画
        - 缺点：对不规则分镜效果较差
        
    方案B（高级）: 深度学习模型 (DeepComicPanel)
        - 优点：准确率高，支持复杂分镜
        - 缺点：需要额外模型，速度较慢

当前实现：方案A（轮廓检测）
"""
import cv2
import numpy as np
from typing import List
from dataclasses import dataclass


@dataclass
class Panel:
    """分镜信息"""
    panel_id: int
    bbox: tuple[int, int, int, int]  # (x, y, width, height)
    order: int  # 阅读顺序（从右上到左下）
    texts: list = None
    characters: list = None
    
    def __post_init__(self):
        if self.texts is None:
            self.texts = []
        if self.characters is None:
            self.characters = []


class PanelDetector:
    """
    分镜检测器
    
    基于轮廓检测的方法：
    1. 灰度化 + 二值化
    2. 形态学操作（闭操作）
    3. 轮廓检测
    4. 过滤噪声（面积/长宽比）
    5. 排序（从右到左，从上到下）
    """
    
    def __init__(self, use_gpu: bool = True):
        self.use_gpu = use_gpu
        self.min_panel_area = 10000  # 最小分镜面积（像素）
        self.aspect_ratio_range = (0.3, 3.5)  # 长宽比范围
        
    def detect(self, image_path: str) -> List[Panel]:
        """
        检测漫画页面中的分镜
        
        Args:
            image_path: 漫画图片路径
            
        Returns:
            List[Panel]: 检测到的分镜列表
        """
        # 读取图片
        image = cv2.imread(image_path)
        if image is None:
            raise FileNotFoundError(f"无法读取图片: {image_path}")
        
        # 转灰度
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # 二值化（反向，因为漫画背景通常是白色）
        _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)
        
        # 形态学闭操作（连接断裂的边框）
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (15, 15))
        closed = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)
        
        # 查找轮廓
        contours, _ = cv2.findContours(
            closed, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # 过滤并提取分镜
        panels = []
        for i, contour in enumerate(contours):
            x, y, w, h = cv2.boundingRect(contour)
            area = w * h
            aspect_ratio = w / h if h > 0 else 0
            
            # 过滤噪声
            if (area >= self.min_panel_area and 
                self.aspect_ratio_range[0] <= aspect_ratio <= self.aspect_ratio_range[1]):
                panels.append(Panel(
                    panel_id=i + 1,
                    bbox=(x, y, w, h),
                    order=0  # 稍后排序
                ))
        
        # 排序（日本漫画：从右到左，从上到下）
        panels = self._sort_panels(panels)
        
        return panels
    
    def _sort_panels(self, panels: List[Panel]) -> List[Panel]:
        """
        对分镜进行排序（阅读顺序）
        
        日本漫画：右→左，上→下
        中文漫画：左→右，上→下（可配置）
        
        当前实现：右→左，上→下
        """
        # 按y坐标分组（同一行）
        rows = {}
        for panel in panels:
            y = panel.bbox[1]
            row_key = y // 100  # 粗略分组
            if row_key not in rows:
                rows[row_key] = []
            rows[row_key].append(panel)
        
        # 每行内按x坐标排序（从右到左）
        sorted_panels = []
        for row_key in sorted(rows.keys()):
            row_panels = sorted(rows[row_key], key=lambda p: -p.bbox[0])
            sorted_panels.extend(row_panels)
        
        # 更新order
        for i, panel in enumerate(sorted_panels):
            panel.order = i + 1
        
        return sorted_panels
    
    def visualize(self, image_path: str, panels: List[Panel], output_path: str = None):
        """
        可视化检测结果
        
        Args:
            image_path: 原图路径
            panels: 检测到的分镜列表
            output_path: 输出路径（可选）
        """
        image = cv2.imread(image_path)
        
        for panel in panels:
            x, y, w, h = panel.bbox
            # 绘制边框
            cv2.rectangle(image, (x, y), (x+w, y+h), (0, 255, 0), 3)
            # 绘制顺序标记
            cv2.putText(
                image, 
                str(panel.order), 
                (x + 10, y + 40), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                1.5, 
                (255, 0, 0), 
                3
            )
        
        if output_path:
            cv2.imwrite(output_path, image)
        
        return image


# TODO: 集成 DeepComicPanel 深度学习模型（可选）
class DeepPanelDetector:
    """
    基于深度学习的分镜检测器
    
    依赖: jianzfb/DeepComicPanel
    状态: 待实现
    """
    pass

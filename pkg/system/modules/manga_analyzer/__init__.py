#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
漫画分析模块 - 主入口

功能：
1. 分镜检测 (Panel Detection)
2. OCR文本提取 (Text Extraction)
3. 角色检测 (Character Detection)
4. 故事图谱构建 (Story Graph)

架构：
    漫画图片 → PanelDetector → OCRExtractor → CharacterDetector → StoryGraphBuilder → JSON输出

集成状态：
    ⚠️ 当前为框架版本，核心依赖未安装
    待安装: PaddleOCR, YOLOv8/Ultralytics

作者: Pygmalion Team
日期: 2026-02-01
"""
from .panel_detector import PanelDetector
from .ocr_extractor import OCRExtractor
from .character_detector import CharacterDetector
from .story_graph_builder import StoryGraphBuilder, StoryGraph

__all__ = [
    'PanelDetector',
    'OCRExtractor', 
    'CharacterDetector',
    'StoryGraphBuilder',
    'StoryGraph',
    'MangaAnalyzer'
]


class MangaAnalyzer:
    """
    漫画分析器 - 统一入口
    
    用法:
        analyzer = MangaAnalyzer()
        story_graph = analyzer.analyze("manga_page.jpg")
        story_graph.save("output.json")
    """
    
    def __init__(self, use_gpu: bool = True):
        """
        初始化漫画分析器
        
        Args:
            use_gpu: 是否使用GPU加速（默认True）
        """
        self.panel_detector = PanelDetector(use_gpu=use_gpu)
        self.ocr_extractor = OCRExtractor(use_gpu=use_gpu)
        self.character_detector = CharacterDetector(use_gpu=use_gpu)
        self.story_builder = StoryGraphBuilder()
        
    def analyze(self, image_path: str, language: str = 'zh_CN') -> StoryGraph:
        """
        分析漫画页面
        
        Args:
            image_path: 漫画图片路径
            language: 语言代码 (zh_CN/ja_JP/en_US)
            
        Returns:
            StoryGraph: 结构化故事图谱
        """
        # Step 1: 检测分镜
        panels = self.panel_detector.detect(image_path)
        
        # Step 2: 提取每个分镜的文本
        for panel in panels:
            panel.texts = self.ocr_extractor.extract(
                image_path, 
                bbox=panel.bbox,
                language=language
            )
        
        # Step 3: 检测角色
        for panel in panels:
            panel.characters = self.character_detector.detect(
                image_path,
                bbox=panel.bbox
            )
        
        # Step 4: 构建故事图谱
        story_graph = self.story_builder.build(
            image_path=image_path,
            panels=panels,
            language=language
        )
        
        return story_graph
    
    def analyze_batch(self, image_paths: list, language: str = 'zh_CN') -> list[StoryGraph]:
        """
        批量分析多个漫画页面
        
        Args:
            image_paths: 图片路径列表
            language: 语言代码
            
        Returns:
            list[StoryGraph]: 故事图谱列表
        """
        return [self.analyze(path, language) for path in image_paths]

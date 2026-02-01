#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
故事图谱构建器 (Story Graph Builder)

功能：将分镜、文本、角色信息组织成结构化的故事图谱

输出格式：JSON/YAML 结构化数据

架构：
    Panel × Text × Character → StoryGraph (JSON)
    
    {
      "metadata": {...},
      "panels": [{...}],
      "character_mapping": {...}
    }
"""
import json
import logging
from typing import List, Dict, Any
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class StoryGraph:
    """
    故事图谱 - 漫画的结构化表示
    """
    metadata: Dict[str, Any]
    panels: List[Dict[str, Any]]
    character_mapping: Dict[str, Any]
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'metadata': self.metadata,
            'panels': self.panels,
            'character_mapping': self.character_mapping
        }
    
    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        return json.dumps(self.to_dict(), ensure_ascii=False, indent=2)
    
    def save(self, output_path: str):
        """保存到文件"""
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.to_json())
        logger.info(f"✅ 故事图谱已保存: {output_path}")


class StoryGraphBuilder:
    """
    故事图谱构建器
    
    负责组织和统一分镜、文本、角色信息
    """
    
    def __init__(self):
        pass
    
    def build(self, image_path: str, panels: List, language: str = 'zh_CN') -> StoryGraph:
        """
        构建故事图谱
        
        Args:
            image_path: 原始漫画图片路径
            panels: Panel 对象列表
            language: 语言代码
            
        Returns:
            StoryGraph: 结构化故事图谱
        """
        
        # 元数据
        metadata = {
            'source': image_path,
            'language': language,
            'timestamp': datetime.now().isoformat(),
            'page_number': 1,
            'total_panels': len(panels),
            'total_characters': sum(len(p.characters) for p in panels) if panels else 0
        }
        
        # 转换分镜数据
        panels_data = []
        all_characters = {}
        
        for panel in panels:
            panel_data = {
                'panel_id': panel.panel_id,
                'bbox': panel.bbox,
                'order': panel.order,
                'texts': [
                    {
                        'content': t.content,
                        'bbox': t.bbox,
                        'confidence': t.confidence,
                        'type': t.type
                    } for t in panel.texts
                ] if panel.texts else [],
                'characters': [
                    {
                        'char_id': c.char_id,
                        'bbox': c.bbox,
                        'confidence': c.confidence,
                        'visual_desc': c.visual_desc or ""
                    } for c in panel.characters
                ] if panel.characters else []
            }
            
            panels_data.append(panel_data)
            
            # 收集角色
            for char in (panel.characters or []):
                if char.char_id not in all_characters:
                    all_characters[char.char_id] = {
                        'name': f'角色{char.char_id[-1]}',
                        'appearances': [],
                        'visual_desc': char.visual_desc or ""
                    }
                all_characters[char.char_id]['appearances'].append({
                    'panel_id': panel.panel_id,
                    'bbox': char.bbox
                })
        
        # 构建图谱
        story_graph = StoryGraph(
            metadata=metadata,
            panels=panels_data,
            character_mapping=all_characters
        )
        
        return story_graph
    
    def merge_graphs(self, graphs: List[StoryGraph]) -> StoryGraph:
        """
        合并多页故事图谱
        
        支持跨页角色追踪
        """
        # TODO: 实现多页合并逻辑
        pass


# 示例输出
EXAMPLE_STORY_GRAPH = {
    "metadata": {
        "source": "manga_page_001.jpg",
        "language": "zh_CN",
        "timestamp": "2026-02-01T10:30:00",
        "page_number": 1,
        "total_panels": 6,
        "total_characters": 3
    },
    "panels": [
        {
            "panel_id": 1,
            "bbox": [50, 50, 400, 300],
            "order": 1,
            "texts": [
                {
                    "content": "早上好啊！",
                    "bbox": [70, 80, 150, 40],
                    "confidence": 0.98,
                    "type": "dialogue"
                }
            ],
            "characters": [
                {
                    "char_id": "C1",
                    "bbox": [50, 100, 200, 250],
                    "confidence": 0.95,
                    "visual_desc": "粉发少女，穿白色连衣裙"
                }
            ]
        }
    ],
    "character_mapping": {
        "C1": {
            "name": "小美",
            "appearances": [
                {"panel_id": 1, "bbox": [50, 100, 200, 250]},
                {"panel_id": 2, "bbox": [300, 100, 200, 250]}
            ],
            "visual_desc": "粉发少女，穿白色连衣裙，表情开心"
        },
        "C2": {
            "name": "朋友",
            "appearances": [
                {"panel_id": 1, "bbox": [350, 100, 150, 250]}
            ],
            "visual_desc": "黑发少女"
        }
    }
}

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Prompt融合 - 将参考图语义标签与核心Prompt合并
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List


@dataclass
class PromptMergeResult:
    prompt: str
    tags_used: List[str]


class PromptMerger:
    """融合参考图标签到Prompt"""

    def __init__(self, max_tags: int = 6):
        self.max_tags = max_tags

    def merge(self, core_prompt: str, tags: Iterable[str]) -> PromptMergeResult:
        tag_list = [t.strip() for t in tags if t and t.strip()]
        if not tag_list:
            return PromptMergeResult(prompt=core_prompt, tags_used=[])

        # 去重并限制数量
        seen = set()
        unique_tags = []
        for tag in tag_list:
            if tag.lower() in seen:
                continue
            seen.add(tag.lower())
            unique_tags.append(tag)
            if len(unique_tags) >= self.max_tags:
                break

        merged_prompt = f"{core_prompt}, {', '.join(unique_tags)}"
        return PromptMergeResult(prompt=merged_prompt, tags_used=unique_tags)

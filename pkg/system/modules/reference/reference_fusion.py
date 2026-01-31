#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考图Prompt融合 - CLIP语义检索 + Prompt合并
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from .prompt_merger import PromptMerger, PromptMergeResult
from .reference_encoder import DEFAULT_TAG_BANK, ReferenceEncodingResult, ReferenceImageEncoder


@dataclass
class ReferenceFusionResult:
    prompt: str
    tags_used: List[str]
    scores: List[float]


class ReferencePromptFusion:
    """参考图与Prompt融合"""

    def __init__(self, tag_bank: Optional[List[str]] = None):
        self.encoder = ReferenceImageEncoder()
        self.merger = PromptMerger()
        self.tag_bank = tag_bank or list(DEFAULT_TAG_BANK)

    def fuse(self, core_prompt: str, reference_image_path: str) -> ReferenceFusionResult:
        encoding: ReferenceEncodingResult = self.encoder.encode(
            image_path=reference_image_path,
            candidate_tags=self.tag_bank,
            top_k=self.merger.max_tags,
        )
        merge_result: PromptMergeResult = self.merger.merge(core_prompt, encoding.tags)
        return ReferenceFusionResult(
            prompt=merge_result.prompt,
            tags_used=merge_result.tags_used,
            scores=encoding.scores,
        )

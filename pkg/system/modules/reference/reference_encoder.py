#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考图编码器 - 使用CLIP从参考图提取语义标签
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Tuple, Optional, Union

import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor


DEFAULT_MODEL_NAME = "openai/clip-vit-base-patch32"


@dataclass
class ReferenceEncodingResult:
    tags: List[str]
    scores: List[float]


class ReferenceImageEncoder:
    """参考图编码器 - 通过CLIP在候选标签中检索最相关的语义"""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME, device: Optional[str] = None):
        self.model_name = model_name
        if device:
            self.device = device
        else:
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model = None
        self._processor = None

    def _lazy_load(self) -> None:
        if self._model is None or self._processor is None:
            self._model = CLIPModel.from_pretrained(self.model_name).to(self.device)
            self._model.eval()
            self._processor = CLIPProcessor.from_pretrained(self.model_name)

    @staticmethod
    def _ensure_feature_tensor(output: Union[torch.Tensor, object]) -> torch.Tensor:
        """兼容不同 transformers 版本的输出结构，确保返回张量特征。"""
        if isinstance(output, torch.Tensor):
            return output
        if hasattr(output, "pooler_output") and output.pooler_output is not None:
            return output.pooler_output
        if hasattr(output, "last_hidden_state") and output.last_hidden_state is not None:
            return output.last_hidden_state.mean(dim=1)
        raise TypeError(f"Unexpected CLIP output type: {type(output)}")

    def encode(self, image_path: str, candidate_tags: Iterable[str], top_k: int = 6) -> ReferenceEncodingResult:
        """从参考图中提取最相关的语义标签

        Args:
            image_path: 参考图片路径
            candidate_tags: 候选标签列表
            top_k: 返回最相关标签数量

        Returns:
            ReferenceEncodingResult
        """
        self._lazy_load()

        image = Image.open(image_path).convert("RGB")
        texts = list(candidate_tags)
        if not texts:
            return ReferenceEncodingResult(tags=[], scores=[])

        with torch.no_grad():
            image_inputs = self._processor(images=image, return_tensors="pt")
            text_inputs = self._processor(text=texts, return_tensors="pt", padding=True)

            image_inputs = {k: v.to(self.device) for k, v in image_inputs.items()}
            text_inputs = {k: v.to(self.device) for k, v in text_inputs.items()}

            image_features = self._ensure_feature_tensor(self._model.get_image_features(**image_inputs))
            text_features = self._ensure_feature_tensor(self._model.get_text_features(**text_inputs))

            image_features = torch.nn.functional.normalize(image_features, p=2, dim=-1)
            text_features = torch.nn.functional.normalize(text_features, p=2, dim=-1)

            similarity = (image_features @ text_features.T).squeeze(0)
            scores = similarity.detach().cpu().tolist()

        ranked: List[Tuple[str, float]] = sorted(zip(texts, scores), key=lambda x: x[1], reverse=True)
        top_ranked = ranked[: max(1, min(top_k, len(ranked)))]

        return ReferenceEncodingResult(
            tags=[tag for tag, _ in top_ranked],
            scores=[float(score) for _, score in top_ranked],
        )


DEFAULT_TAG_BANK = [
    # 视觉风格
    "cinematic lighting",
    "soft diffused light",
    "dramatic shadows",
    "volumetric light",
    "neon glow",
    "studio portrait lighting",
    "backlit silhouette",
    "golden hour",
    "noir style",
    "vibrant color palette",
    "pastel color palette",
    "monochrome palette",
    "high contrast",
    "low saturation",
    # 材质与细节
    "highly detailed textures",
    "glossy surface",
    "matte texture",
    "metallic sheen",
    "organic materials",
    "fabric folds",
    "skin pores",
    "wet surfaces",
    "dust particles",
    # 构图
    "close-up composition",
    "wide angle shot",
    "symmetrical composition",
    "dynamic perspective",
    "shallow depth of field",
    "bokeh background",
    "rule of thirds",
    # 氛围
    "mysterious atmosphere",
    "dreamy atmosphere",
    "serene mood",
    "energetic mood",
    "epic scale",
    "intimate moment",
    # 主题/对象（通用）
    "character portrait",
    "full body shot",
    "environment scene",
    "urban setting",
    "nature setting",
    "fantasy setting",
    "sci-fi setting",
    "traditional clothing",
    "modern fashion",
]

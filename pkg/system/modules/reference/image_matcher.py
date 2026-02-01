#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参考图一致性评分 - 与生成图进行多维度对比
"""
from __future__ import annotations

import cv2
import numpy as np
import torch
from PIL import Image
from transformers import CLIPModel, CLIPProcessor
import logging

logger = logging.getLogger(__name__)


class ReferenceImageMatcher:
    """评估生成图与参考图的匹配度"""

    def __init__(self, device: str | None = None):
        self.device = device or ("cuda" if torch.cuda.is_available() else "cpu")
        self._model = None
        self._processor = None

    def _lazy_load(self) -> None:
        """懒加载模型"""
        if self._model is None or self._processor is None:
            self._model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32").to(self.device)
            self._model.eval()
            self._processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
            logger.info("✅ CLIP 模型已加载")

    def evaluate_match(self, reference_image_path: str, generated_image_path: str) -> dict:
        """
        计算两张图片的多维度匹配度

        Args:
            reference_image_path: 参考图路径
            generated_image_path: 生成图路径

        Returns:
            dict: {
                'style_consistency': 0.82,      # 风格一致性
                'pose_similarity': 0.75,        # 姿态相似度
                'composition_match': 0.76,      # 构图相似度
                'character_consistency': 0.70,  # 角色一致性
                'overall_reference_match': 0.75 # 总体匹配度
            }
        """
        try:
            ref_image = Image.open(reference_image_path).convert("RGB")
            gen_image = Image.open(generated_image_path).convert("RGB")
        except Exception as e:
            logger.error(f"❌ 加载图片失败: {e}")
            return self._default_scores()

        self._lazy_load()

        scores = {}

        # 1. 风格一致性（CLIP特征向量相似度）
        try:
            scores["style_consistency"] = self._compute_style_similarity(ref_image, gen_image)
        except Exception as e:
            logger.warning(f"⚠️ 计算风格一致性失败: {e}")
            scores["style_consistency"] = 0.5

        # 2. 姿态相似度（基于CLIP空间信息）
        try:
            scores["pose_similarity"] = self._estimate_pose_similarity(ref_image, gen_image)
        except Exception as e:
            logger.warning(f"⚠️ 计算姿态相似度失败: {e}")
            scores["pose_similarity"] = 0.5

        # 3. 构图相似度（边缘检测对比）
        try:
            scores["composition_match"] = self._compare_composition(ref_image, gen_image)
        except Exception as e:
            logger.warning(f"⚠️ 计算构图相似度失败: {e}")
            scores["composition_match"] = 0.5

        # 4. 角色一致性（色彩与纹理）
        try:
            scores["character_consistency"] = self._compare_character_features(ref_image, gen_image)
        except Exception as e:
            logger.warning(f"⚠️ 计算角色一致性失败: {e}")
            scores["character_consistency"] = 0.5

        # 5. 总体匹配度（加权平均）
        scores["overall_reference_match"] = (
            scores["style_consistency"] * 0.35
            + scores["pose_similarity"] * 0.25
            + scores["composition_match"] * 0.25
            + scores["character_consistency"] * 0.15
        )

        return scores

    def _compute_style_similarity(self, ref_image: Image.Image, gen_image: Image.Image) -> float:
        """计算风格一致性（CLIP特征向量相似度）"""
        with torch.no_grad():
            ref_inputs = self._processor(images=ref_image, return_tensors="pt").to(self.device)
            gen_inputs = self._processor(images=gen_image, return_tensors="pt").to(self.device)

            ref_features = self._model.get_image_features(**ref_inputs)
            gen_features = self._model.get_image_features(**gen_inputs)

            # L2 归一化
            ref_features = ref_features / ref_features.norm(dim=-1, keepdim=True)
            gen_features = gen_features / gen_features.norm(dim=-1, keepdim=True)

            # 余弦相似度 (范围: -1 到 1，我们映射到 0-1)
            similarity = (ref_features @ gen_features.T).item()
            return max(0.0, min(1.0, (similarity + 1) / 2))

    def _estimate_pose_similarity(self, ref_image: Image.Image, gen_image: Image.Image) -> float:
        """
        估计姿态相似度
        简化方案：基于CLIP的空间分布信息
        """
        # 当前简化方案：用 CNN 的卷积特征图对比
        # 后续可升级为 OpenPose/DWPose 精确提取骨骼关键点

        with torch.no_grad():
            ref_inputs = self._processor(images=ref_image, return_tensors="pt").to(self.device)
            gen_inputs = self._processor(images=gen_image, return_tensors="pt").to(self.device)

            # 使用视觉编码器的中层特征（含空间信息）
            ref_features = self._model.vision_model(**ref_inputs).last_hidden_state
            gen_features = self._model.vision_model(**gen_inputs).last_hidden_state

            # 计算特征图的空间相似性
            ref_mean = ref_features.mean(dim=1)  # (1, 768)
            gen_mean = gen_features.mean(dim=1)

            ref_mean = ref_mean / ref_mean.norm(dim=-1, keepdim=True)
            gen_mean = gen_mean / gen_mean.norm(dim=-1, keepdim=True)

            similarity = (ref_mean @ gen_mean.T).item()
            return max(0.0, min(1.0, (similarity + 1) / 2))

    def _compare_composition(self, ref_image: Image.Image, gen_image: Image.Image) -> float:
        """计算构图相似度（边缘检测）"""
        ref_array = cv2.cvtColor(np.array(ref_image), cv2.COLOR_RGB2BGR)
        gen_array = cv2.cvtColor(np.array(gen_image), cv2.COLOR_RGB2BGR)

        # 转灰度
        ref_gray = cv2.cvtColor(ref_array, cv2.COLOR_BGR2GRAY)
        gen_gray = cv2.cvtColor(gen_array, cv2.COLOR_BGR2GRAY)

        # Canny 边缘检测
        ref_edges = cv2.Canny(ref_gray, 100, 200)
        gen_edges = cv2.Canny(gen_gray, 100, 200)

        # 计算边缘匹配度
        intersection = np.logical_and(ref_edges, gen_edges).sum()
        union = np.logical_or(ref_edges, gen_edges).sum()

        if union == 0:
            return 0.5

        iou = intersection / union
        return min(1.0, iou * 2)  # 缩放以获得更好的分布

    def _compare_character_features(self, ref_image: Image.Image, gen_image: Image.Image) -> float:
        """计算角色一致性（色彩与纹理）"""
        ref_array = np.array(ref_image)
        gen_array = np.array(gen_image)

        # 计算主色调的相似度
        ref_colors = self._extract_dominant_colors(ref_array)
        gen_colors = self._extract_dominant_colors(gen_array)

        color_similarity = self._compare_color_palettes(ref_colors, gen_colors)

        # 计算直方图相似度（整体色彩分布）
        hist_similarity = self._compare_histograms(ref_array, gen_array)

        return (color_similarity + hist_similarity) / 2

    def _extract_dominant_colors(self, image_array: np.ndarray, n_colors: int = 5) -> list:
        """提取图片的主要颜色"""
        # 简化：直接使用图片的平均色彩特征
        pixels = image_array.reshape((-1, 3))
        pixels = np.float32(pixels)

        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)
        _, _, centers = cv2.kmeans(pixels, n_colors, None, criteria, 10, cv2.KMEANS_RANDOM_CENTERS)

        return centers.astype(int).tolist()

    def _compare_color_palettes(self, colors1: list, colors2: list) -> float:
        """比较两个色盘"""
        # 简化方案：计算最近邻匹配
        total_distance = 0
        for c1 in colors1:
            min_dist = min(np.linalg.norm(np.array(c1) - np.array(c2)) for c2 in colors2)
            total_distance += min_dist

        avg_distance = total_distance / len(colors1)
        # 归一化到 0-1 (最大距离约255*sqrt(3) ≈ 441)
        similarity = max(0.0, 1.0 - avg_distance / 441.0)
        return similarity

    def _compare_histograms(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """计算直方图相似度"""
        # 转HSV以获得更好的色彩感知
        img1_hsv = cv2.cvtColor(img1.astype(np.uint8), cv2.COLOR_RGB2HSV)
        img2_hsv = cv2.cvtColor(img2.astype(np.uint8), cv2.COLOR_RGB2HSV)

        hist1 = cv2.calcHist([img1_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])
        hist2 = cv2.calcHist([img2_hsv], [0, 1], None, [180, 256], [0, 180, 0, 256])

        hist1 = cv2.normalize(hist1, hist1).flatten()
        hist2 = cv2.normalize(hist2, hist2).flatten()

        similarity = cv2.compareHist(hist1, hist2, cv2.HISTCMP_BHATTACHARYYA)
        # 转换：Bhattacharyya距离越小越好，范围0-1
        return 1.0 - similarity

    def _default_scores(self) -> dict:
        """默认分数（出错时返回）"""
        return {
            "style_consistency": 0.5,
            "pose_similarity": 0.5,
            "composition_match": 0.5,
            "character_consistency": 0.5,
            "overall_reference_match": 0.5,
        }

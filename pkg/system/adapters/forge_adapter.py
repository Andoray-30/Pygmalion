#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Forge API适配器 - 封装Forge API调用逻辑
"""
import os
import requests
import base64
import time
from pkg.infrastructure.config import FORGE_URL, FORGE_TIMEOUT
from pkg.infrastructure.health import check_forge_health


class ForgeAdapter:
    """Forge API适配器 - 封装所有Forge API调用"""

    def __init__(self, url=None, timeout=None):
        """
        初始化Forge适配器

        Args:
            url: Forge服务器URL
            timeout: 请求超时时间（秒）
        """
        self.url = url or FORGE_URL
        self.timeout = timeout or FORGE_TIMEOUT

        # 启动前健康检查
        if not check_forge_health():
            raise RuntimeError(f"Forge 不可用，请检查: {self.url}")

    def generate(self, params, output_dir=None, project_id=None, iteration=1):
        """
        生成图片

        Args:
            params: 生成参数字典
            output_dir: 输出目录
            project_id: 项目ID
            iteration: 迭代次数

        Returns:
            dict: 包含图片路径和元数据的字典
                {
                    "path": str,  # 图片路径
                    "data": bytes,  # 图片数据
                    "filename": str  # 文件名
                }
        """
        try:
            # 发送请求
            resp = requests.post(
                f"{self.url}/sdapi/v1/txt2img",
                json=params,
                timeout=self.timeout
            )

            if resp.status_code != 200:
                print(f"❌ Forge HTTP {resp.status_code}")
                return None

            data = resp.json()
            images = data.get('images') or []
            if not images:
                print("⚠️ Forge 返回空 images，疑似故障")
                return None

            # 解码图片
            img_data = base64.b64decode(images[0])
            if len(img_data) < 1000:
                print(f"⚠️ Forge 返回的图片过小 ({len(img_data)} bytes)，疑似异常")
                return None

            # 保存图片
            if output_dir and project_id:
                theme_dir = os.path.join(output_dir, project_id)
                os.makedirs(theme_dir, exist_ok=True)

                filename = f"{project_id}_iter{iteration}.png"
                path = os.path.join(theme_dir, filename)

                with open(path, "wb") as f:
                    f.write(img_data)

                # 清理旧图片（保留最近20张）
                self._cleanup_old_images(theme_dir)

                return {
                    "path": path,
                    "data": img_data,
                    "filename": filename
                }

            return {
                "data": img_data,
                "filename": f"generated_{int(time.time())}.png"
            }

        except requests.Timeout:
            print("⏱️ Forge 请求超时，可能已卡死")
        except Exception as e:
            print(f"❌ API Error: {e}")

        return None

    def _cleanup_old_images(self, theme_dir, max_keep=20):
        """
        清理旧图片，只保留最近max_keep张

        Args:
            theme_dir: 主题目录
            max_keep: 最大保留数量
        """
        try:
            images = [
                os.path.join(theme_dir, p)
                for p in os.listdir(theme_dir)
                if p.lower().endswith(".png")
            ]
            images.sort(key=lambda p: os.path.getmtime(p))
            while len(images) > max_keep:
                old_path = images.pop(0)
                try:
                    os.remove(old_path)
                except Exception:
                    pass
        except Exception:
            pass

    def health_check(self):
        """
        健康检查

        Returns:
            bool: Forge是否可用
        """
        return check_forge_health()

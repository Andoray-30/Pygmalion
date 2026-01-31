#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试 - ForgeAdapter
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import base64
from pkg.system.adapters.forge_adapter import ForgeAdapter


@pytest.fixture
def mock_successful_response():
    """模拟成功的Forge API响应"""
    mock_resp = Mock()
    mock_resp.status_code = 200
    
    # 创建一个简单的1x1像素PNG图片
    img_data = b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89' + b'\x00' * 100
    mock_resp.json.return_value = {
        'images': [base64.b64encode(img_data).decode('utf-8')]
    }
    return mock_resp


@pytest.fixture
def mock_failed_response():
    """模拟失败的Forge API响应"""
    mock_resp = Mock()
    mock_resp.status_code = 500
    return mock_resp


@pytest.fixture
def mock_forge_adapter():
    """创建Mock的ForgeAdapter（跳过健康检查）"""
    with patch('pkg.system.adapters.forge_adapter.check_forge_health', return_value=True):
        return ForgeAdapter(url="http://mock-forge:7860", timeout=30)


class TestForgeAdapter:
    """ForgeAdapter单元测试"""

    def test_init_with_defaults(self):
        """测试默认初始化"""
        with patch('pkg.system.adapters.forge_adapter.check_forge_health', return_value=True):
            adapter = ForgeAdapter()
            assert adapter.url is not None
            assert adapter.timeout is not None

    def test_init_with_custom_params(self):
        """测试自定义参数初始化"""
        with patch('pkg.system.adapters.forge_adapter.check_forge_health', return_value=True):
            adapter = ForgeAdapter(url="http://custom:7860", timeout=60)
            assert adapter.url == "http://custom:7860"
            assert adapter.timeout == 60

    def test_init_fails_when_forge_unavailable(self):
        """测试Forge不可用时初始化失败"""
        with patch('pkg.system.adapters.forge_adapter.check_forge_health', return_value=False):
            with pytest.raises(RuntimeError, match="Forge 不可用"):
                ForgeAdapter()

    @patch('pkg.system.adapters.forge_adapter.requests.post')
    def test_generate_success(self, mock_post, mock_forge_adapter, mock_successful_response):
        """测试成功生成图片"""
        mock_post.return_value = mock_successful_response

        params = {
            "prompt": "test prompt",
            "steps": 4,
            "cfg_scale": 1.0
        }

        result = mock_forge_adapter.generate(
            params=params,
            output_dir="test_output",
            project_id="test_project",
            iteration=1
        )

        assert result is not None
        assert "path" in result
        assert "data" in result
        assert "filename" in result
        assert len(result["data"]) > 1000  # 确保图片数据足够大

    @patch('pkg.system.adapters.forge_adapter.requests.post')
    def test_generate_http_error(self, mock_post, mock_forge_adapter, mock_failed_response):
        """测试HTTP错误处理"""
        mock_post.return_value = mock_failed_response

        params = {"prompt": "test"}
        result = mock_forge_adapter.generate(params=params)

        assert result is None

    @patch('pkg.system.adapters.forge_adapter.requests.post')
    def test_generate_empty_images(self, mock_post, mock_forge_adapter):
        """测试空图片列表处理"""
        mock_resp = Mock()
        mock_resp.status_code = 200
        mock_resp.json.return_value = {"images": []}
        mock_post.return_value = mock_resp

        params = {"prompt": "test"}
        result = mock_forge_adapter.generate(params=params)

        assert result is None

    @patch('pkg.system.adapters.forge_adapter.requests.post')
    def test_generate_timeout(self, mock_post, mock_forge_adapter):
        """测试超时处理"""
        import requests
        mock_post.side_effect = requests.Timeout()

        params = {"prompt": "test"}
        result = mock_forge_adapter.generate(params=params)

        assert result is None

    @patch('pkg.system.adapters.forge_adapter.requests.post')
    def test_generate_without_output_dir(self, mock_post, mock_forge_adapter, mock_successful_response):
        """测试不保存文件的生成"""
        mock_post.return_value = mock_successful_response

        params = {"prompt": "test"}
        result = mock_forge_adapter.generate(params=params)

        assert result is not None
        assert "data" in result
        assert "filename" in result
        assert "path" not in result  # 不应该有path

    @patch('pkg.system.adapters.forge_adapter.requests.post')
    def test_generate_small_image_error(self, mock_post, mock_forge_adapter):
        """测试图片过小的错误处理"""
        mock_resp = Mock()
        mock_resp.status_code = 200
        # 返回一个很小的图片（<1000 bytes）
        small_img = b'x' * 100
        mock_resp.json.return_value = {
            'images': [base64.b64encode(small_img).decode('utf-8')]
        }
        mock_post.return_value = mock_resp

        params = {"prompt": "test"}
        result = mock_forge_adapter.generate(params=params)

        assert result is None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

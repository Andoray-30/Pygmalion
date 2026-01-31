#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试套件入口文件
"""
import pytest
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def run_all_tests():
    """运行所有测试"""
    pytest.main([
        os.path.dirname(__file__),
        "-v",
        "--tb=short",
        "--color=yes"
    ])


def run_specific_test(test_file):
    """运行指定测试文件"""
    pytest.main([
        os.path.join(os.path.dirname(__file__), test_file),
        "-v",
        "--tb=short"
    ])


if __name__ == "__main__":
    if len(sys.argv) > 1:
        run_specific_test(sys.argv[1])
    else:
        run_all_tests()

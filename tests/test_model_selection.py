#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试三模型智能选择系统
"""
from creator import CreativeDirector

def test_model_recommendation():
    """测试不同主题的模型推荐"""
    brain = CreativeDirector()
    
    test_cases = [
        "龙舌兰日出",           # 真实产品 → 应该推荐 RENDER
        "动漫女孩",             # 动漫风格 → 应该推荐 ANIME
        "魔法森林",             # 幻想场景 → 可能推荐 ANIME
        "专业人像摄影",         # 真实摄影 → 应该推荐 RENDER
        "可爱的猫咪插画",       # 插画风格 → 应该推荐 ANIME
        "建筑夜景",             # 真实场景 → 应该推荐 RENDER
        "二次元角色",           # 明确动漫 → 应该推荐 ANIME
        "产品渲染图",           # 真实产品 → 应该推荐 RENDER
    ]
    
    print("="*70)
    print("  三模型智能选择测试")
    print("="*70)
    
    for theme in test_cases:
        print(f"\n🎨 主题: {theme}")
        try:
            result = brain.analyze_theme_and_recommend_model(theme)
            print(f"   意图: {result.get('intent', 'N/A')}")
            print(f"   推荐: {result['model']}")
            print(f"   理由: {result['reason']}")
        except Exception as e:
            print(f"   ❌ 错误: {e}")
    
    print("\n" + "="*70)

if __name__ == "__main__":
    test_model_recommendation()

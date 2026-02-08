#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试架构优化效果：模型锁定 + 参考图硬约束 + 意图检测
"""
import os
import sys

# 添加项目根目录到路径
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from pkg.system.engine import DiffuServoV4

def test_keep_unchanged_mode():
    """
    测试"保持不变"模式的约束效果
    """
    print("=" * 80)
    print("🧪 测试场景：保持角色不变，只修改姿势")
    print("=" * 80)
    
    # 使用包含"保持不变"关键词的主题
    theme = "保持人物主题，脸型，衣服，背景不变，修改姿势为抱胸"
    reference_image = "evolution_history/references/ref_dafeaacd.jpg"
    
    if not os.path.exists(reference_image):
        print(f"⚠️ 参考图不存在: {reference_image}")
        print("请确保参考图路径正确")
        return
    
    print(f"\n📋 测试配置:")
    print(f"   主题: {theme}")
    print(f"   参考图: {reference_image}")
    print(f"\n预期行为:")
    print(f"   ✓ 检测到\"保持不变\"意图")
    print(f"   ✓ 多模态分析识别为动漫风格 → 锁定ANIME模型")
    print(f"   ✓ ControlNet权重提升至1.3")
    print(f"   ✓ 参考图评分权重提升至35%")
    print(f"   ✓ 参考匹配阈值提升至0.75")
    print(f"   ✓ 角色一致性<0.65时强制降分")
    print(f"\n" + "=" * 80)
    
    # 初始化引擎
    engine = DiffuServoV4(theme=theme, reference_image_path=reference_image)
    
    print(f"\n🔍 初始化结果检查:")
    print(f"   初始模型选择: {engine.initial_model_choice}")
    print(f"   模型锁定状态: {engine.model_locked}")
    print(f"   锁定的模型: {engine.locked_model}")
    print(f"   保持不变意图: {engine.keep_unchanged_intent}")
    print(f"   参考图ControlNet权重: {engine.reference_controlnet_weight}")
    print(f"   参考匹配阈值: {engine.reference_match_min}")
    
    # 运行生成（少量迭代测试）
    print(f"\n🚀 开始生成测试 (3次迭代)...")
    engine.run(target_score=0.90, max_iterations=3, reference_image_path=reference_image)
    
    print(f"\n" + "=" * 80)
    print("✅ 测试完成")
    print("=" * 80)
    
    # 验证结果
    print(f"\n📊 生成历史:")
    for entry in engine.history:
        print(f"\n   迭代 {entry['iter']}: 总分={entry['score']:.2f}")
        print(f"      概念={entry['concept']:.2f}, 质量={entry['quality']:.2f}")
        if 'reference_match' in entry:
            print(f"      参考匹配={entry['reference_match']:.2f}, 角色一致性={entry.get('character_consistency', 0):.2f}")
    
    # 验证约束是否生效
    print(f"\n🔍 约束效果验证:")
    for i, entry in enumerate(engine.history):
        ref_match = entry.get('reference_match', 1.0)
        char_consistency = entry.get('character_consistency', 1.0)
        
        if ref_match < 0.75:
            print(f"   ⚠️ 迭代{i+1}: 参考匹配 {ref_match:.2f} < 0.75阈值 (应被降分)")
        
        if char_consistency < 0.65:
            print(f"   ⚠️ 迭代{i+1}: 角色一致性 {char_consistency:.2f} < 0.65阈值 (应被强制上限)")
    
    print(f"\n✅ 测试结束")


def test_normal_mode():
    """
    测试正常模式（无"保持不变"关键词）
    """
    print("=" * 80)
    print("🧪 对照测试：正常生成模式（无保持不变约束）")
    print("=" * 80)
    
    theme = "一个粉发女仆抱胸站立"
    reference_image = "evolution_history/references/ref_dafeaacd.jpg"
    
    if not os.path.exists(reference_image):
        print(f"⚠️ 参考图不存在: {reference_image}")
        return
    
    print(f"\n📋 测试配置:")
    print(f"   主题: {theme}")
    print(f"   参考图: {reference_image}")
    print(f"\n预期行为:")
    print(f"   ✓ 不检测\"保持不变\"意图")
    print(f"   ✓ ControlNet权重保持1.0")
    print(f"   ✓ 参考图评分权重保持25%")
    print(f"   ✓ 参考匹配阈值保持0.70")
    
    engine = DiffuServoV4(theme=theme, reference_image_path=reference_image)
    
    print(f"\n🔍 初始化结果检查:")
    print(f"   保持不变意图: {engine.keep_unchanged_intent}")
    print(f"   参考图ControlNet权重: {engine.reference_controlnet_weight}")
    print(f"   参考匹配阈值: {engine.reference_match_min}")
    
    print(f"\n✅ 对照测试完成")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试架构优化效果")
    parser.add_argument("--mode", choices=["keep", "normal", "both"], default="both",
                        help="测试模式: keep=保持不变, normal=正常模式, both=两者都测试")
    
    args = parser.parse_args()
    
    if args.mode in ["keep", "both"]:
        test_keep_unchanged_mode()
    
    if args.mode in ["normal", "both"]:
        print("\n" + "=" * 80 + "\n")
        test_normal_mode()

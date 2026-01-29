#!/usr/bin/env python3
"""
测试多模型轮换机制
验证 ModelScope 2000次免费额度的充分利用
"""

import os
import sys
from dotenv import load_dotenv

load_dotenv()

# 模拟评分次数统计
print("=" * 70)
print("🔄 ModelScope 多模型轮换系统测试")
print("=" * 70)

from config import JUDGE_MODELS, JUDGE_MODEL_ROTATION_INTERVAL
from evaluator.core import api_manager

print("\n📚 可用模型池:")
for i, (key, model) in enumerate(JUDGE_MODELS.items(), 1):
    print(f"  {i}. {model.split('/')[-1]} ({model})")

print(f"\n⚙️ 轮换配置:")
print(f"  - 轮换间隔: {JUDGE_MODEL_ROTATION_INTERVAL} 次评分")
print(f"  - 轮换启用: {api_manager.rotation_enabled}")
print(f"  - 当前模型: {api_manager.current_judge_model.split('/')[-1]}")

print("\n📊 模拟 300 次评分的轮换过程:")
print("-" * 70)

# 模拟轮换
model_usage = {model.split('/')[-1]: 0 for model in JUDGE_MODELS.values()}

for i in range(1, 301):
    model = api_manager.get_judge_model()
    model_name = model.split('/')[-1]
    model_usage[model_name] += 1
    
    # 每50次显示一次
    if i % 50 == 0 or i == 150 or i == 300:
        print(f"✓ 第 {i:3d} 次评分 → 使用模型: {model_name:30s} (累计计数: {api_manager.model_call_count})")

print("\n" + "=" * 70)
print("📈 评分次数统计:")
print("-" * 70)

total = sum(model_usage.values())
for model, count in sorted(model_usage.items(), key=lambda x: x[1], reverse=True):
    percentage = (count / total) * 100
    bar = "█" * int(percentage / 5)
    print(f"  {model:30s}: {count:3d} 次 ({percentage:5.1f}%) {bar}")

print("\n💡 分析:")
print(f"  - 总评分次数: {total}")
print(f"  - 理想分配: 每个模型 75 次 (25%)")
print(f"  - 实际分布: 基于轮换间隔 {JUDGE_MODEL_ROTATION_INTERVAL}")
print(f"  - 首日可用额度: 4 个模型 × 500 次/模型 = 2000 次")
print(f"  - 当前方案可处理: 每日 300+ 张图片评分")

print("\n✅ 轮换系统测试完成!")
print("=" * 70)

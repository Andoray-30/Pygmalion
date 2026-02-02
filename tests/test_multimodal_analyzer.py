"""
多模态风格分析器测试 - 验证魔搭/硅基API集成

用法：
    python tests/test_multimodal_analyzer.py [图片路径]
"""

import sys
import os
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pkg.system.modules.reference.multimodal_analyzer import analyze_reference_style_with_multimodal


def test_analyzer(image_path: str = None):
    """测试多模态分析器"""
    
    print("=" * 70)
    print("多模态风格分析器测试")
    print("=" * 70)
    
    # 检查API密钥
    modelscope_key = os.getenv("MODELSCOPE_API_KEY")
    silicon_key = os.getenv("SILICON_KEY")
    
    if not modelscope_key and not silicon_key:
        print("\n警告: 未设置 MODELSCOPE_API_KEY 或 SILICON_KEY")
        return False
    
    if modelscope_key:
        print(f"魔搭免费API: {modelscope_key[:15]}... (优先)")
    if silicon_key:
        print(f"硅基付费API: {silicon_key[:15]}... (降级)")
    
    # 测试图像
    if image_path:
        test_image = image_path
    else:
        test_image = str(project_root / "tmp" / "reference.png")
    
    if not Path(test_image).exists():
        print(f"\n图像不存在: {test_image}")
        print(f"请放置参考图到: {project_root / 'tmp' / 'reference.png'}")
        print(f"或指定路径: python tests/test_multimodal_analyzer.py 图片路径")
        return False
    
    print(f"\n测试图像: {test_image}")
    print("\n调用多模态分析...\n")
    
    # 执行分析
    result = analyze_reference_style_with_multimodal(test_image)
    
    # 显示结果
    print("=" * 70)
    print("分析结果")
    print("=" * 70)
    print(f"\n风格: {result.get('style_category', 'unknown')}")
    print(f"置信度: {result.get('confidence', 0):.0%}")
    print(f"推荐模型: {result.get('recommended_model', 'PREVIEW')}")
    print(f"\n理由: {result.get('model_reasoning', '无')}")
    
    vf = result.get("visual_features", {})
    print(f"\n视觉特征:")
    print(f"  颜色: {', '.join(vf.get('dominant_colors', ['未知']))}")
    print(f"  构图: {vf.get('composition', '未知')}")
    
    hints = result.get("deepseek_hints", {})
    print(f"\nDeepSeek提示:")
    print(f"  风格: {hints.get('art_style', '未指定')}")
    print(f"  关键词: {', '.join(hints.get('visual_keywords', ['无']))}")
    
    print("\n" + "=" * 70)
    return True


if __name__ == "__main__":
    image_path = sys.argv[1] if len(sys.argv) > 1 else None
    success = test_analyzer(image_path)
    sys.exit(0 if success else 1)

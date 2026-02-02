"""
ControlNet约束功能测试
任务4: 验证ControlNet约束功能
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def test_controlnet_builder_initialization():
    """测试ControlNetBuilder初始化"""
    print("\n" + "="*60)
    print("🔧 测试1: ControlNetBuilder初始化")
    print("="*60)
    
    try:
        from pkg.system.builders.controlnet_builder import ControlNetBuilder
        
        print("\n🔧 初始化ControlNetBuilder...")
        builder = ControlNetBuilder()
        
        print("✅ ControlNetBuilder初始化成功")
        print(f"   支持的ControlNet类型: {len(builder.SUPPORTED_TYPES)}")
        for cn_type in builder.SUPPORTED_TYPES:
            print(f"      • {cn_type}")
        
        return True, builder
        
    except Exception as e:
        print(f"❌ 初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_controlnet_builder_canny(builder, reference_image_path):
    """测试Canny ControlNet配置生成"""
    print("\n" + "="*60)
    print("📐 测试2: Canny ControlNet配置生成")
    print("="*60)
    
    try:
        if not reference_image_path or not os.path.exists(reference_image_path):
            print(f"⚠️  参考图不存在: {reference_image_path}")
            print("   跳过此测试")
            return False, {}
        
        print(f"\n🖼️  参考图: {reference_image_path}")
        
        # 生成Canny配置
        print("\n📐 生成Canny ControlNet配置...")
        cn_config = builder.build(
            reference_image=reference_image_path,
            cn_type="canny",
            weight=0.8,
            guidance_start=0.0,
            guidance_end=1.0
        )
        
        print("✅ 配置生成成功")
        print(f"   ControlNet类型: canny")
        print(f"   权重: 0.8")
        print(f"   Guidance范围: [0.0, 1.0]")
        
        # 检查配置结构
        if 'alwayson_scripts' in cn_config:
            print(f"   ✅ alwayson_scripts字段存在")
            
            if 'controlnet' in cn_config['alwayson_scripts']:
                cn_module = cn_config['alwayson_scripts']['controlnet']
                print(f"   ✅ controlnet模块存在")
                print(f"   args数量: {len(cn_module.get('args', []))}")
            else:
                print(f"   ⚠️  controlnet模块不存在")
        else:
            print(f"   ⚠️  alwayson_scripts字段不存在")
        
        return True, cn_config
        
    except Exception as e:
        print(f"❌ Canny配置生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {}


def test_controlnet_builder_openpose(builder, reference_image_path):
    """测试OpenPose ControlNet配置生成"""
    print("\n" + "="*60)
    print("🕺 测试3: OpenPose ControlNet配置生成")
    print("="*60)
    
    try:
        if not reference_image_path or not os.path.exists(reference_image_path):
            print(f"⚠️  参考图不存在: {reference_image_path}")
            print("   跳过此测试")
            return False, {}
        
        print(f"\n🖼️  参考图: {reference_image_path}")
        
        # 生成OpenPose配置
        print("\n🕺 生成OpenPose ControlNet配置...")
        cn_config = builder.build(
            reference_image=reference_image_path,
            cn_type="openpose",
            weight=0.7,
            guidance_start=0.0,
            guidance_end=1.0
        )
        
        print("✅ 配置生成成功")
        print(f"   ControlNet类型: openpose")
        print(f"   权重: 0.7")
        print(f"   Guidance范围: [0.0, 1.0]")
        
        return True, cn_config
        
    except Exception as e:
        print(f"❌ OpenPose配置生成失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, {}


def test_engine_controlnet_integration():
    """测试Engine中ControlNet集成"""
    print("\n" + "="*60)
    print("🔄 测试4: Engine中ControlNet集成")
    print("="*60)
    
    try:
        from pkg.system.engine import DiffuServoV4
        
        reference_image_path = "tests/test_images/reference.jpg"
        
        if not reference_image_path or not os.path.exists(reference_image_path):
            print(f"⚠️  参考图不存在: {reference_image_path}")
            print("   跳过此测试")
            return False
        
        theme = "Character with pose from reference"
        engine = DiffuServoV4(theme=theme, reference_image_path=reference_image_path)
        
        print(f"\n📝 主题: {theme}")
        print(f"🖼️  参考图: {reference_image_path}")
        print(f"🎯 最大迭代: 2")
        
        # 运行2次迭代（快速测试）
        print("\n🎨 开始生成（带ControlNet）...")
        print("   观察日志中的ControlNet信息")
        
        engine.run(max_iterations=2)
        
        print(f"\n✅ 生成完成")
        print(f"   最终分数: {engine.best_score:.2f}")
        print(f"   迭代次数: {len(engine.history)}")
        return True
            
    except Exception as e:
        print(f"❌ Engine ControlNet集成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_controlnet_parameter_injection():
    """测试ControlNet参数注入到params"""
    print("\n" + "="*60)
    print("💉 测试5: ControlNet参数注入")
    print("="*60)
    
    try:
        from pkg.system.builders.controlnet_builder import ControlNetBuilder
        
        reference_image_path = "tests/test_images/reference.jpg"
        
        if not reference_image_path or not os.path.exists(reference_image_path):
            print(f"⚠️  参考图不存在: {reference_image_path}")
            print("   跳过此测试")
            return False
        
        builder = ControlNetBuilder()
        
        # 模拟Engine的params
        params = {
            "prompt": "A test prompt",
            "steps": 20,
            "cfg_scale": 7.0,
            "width": 832,
            "height": 1216
        }
        
        print(f"\n📋 初始params字段数: {len(params)}")
        print(f"   字段: {', '.join(params.keys())}")
        
        # 生成ControlNet配置
        cn_config = builder.build(
            reference_image=reference_image_path,
            cn_type="canny",
            weight=0.8,
            guidance_start=0.0,
            guidance_end=1.0
        )
        
        # 注入到params
        print("\n💉 注入ControlNet配置到params...")
        params.update(cn_config)
        
        print(f"✅ 注入成功")
        print(f"   更新后params字段数: {len(params)}")
        print(f"   新增字段: alwayson_scripts")
        
        # 验证注入
        if 'alwayson_scripts' in params:
            print("✅ ControlNet配置已成功注入")
            return True
        else:
            print("❌ ControlNet配置注入失败")
            return False
        
    except Exception as e:
        print(f"❌ 参数注入测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("🚀 开始ControlNet约束功能测试")
    print("="*60)
    print("\n⚠️  前提条件:")
    print("   1. Forge服务器必须正在运行")
    print("   2. 参考图文件: tests/test_images/reference.jpg")
    print("   3. ControlNet模型已安装")
    print("="*60)
    
    results = {
        'builder_init': False,
        'canny_config': False,
        'openpose_config': False,
        'parameter_injection': False,
        'engine_integration': False
    }
    
    # 1. 测试ControlNetBuilder初始化
    print("\n" + "━"*60)
    builder_ok, builder = test_controlnet_builder_initialization()
    results['builder_init'] = builder_ok
    
    # 2. 测试Canny配置生成
    if builder_ok:
        print("\n" + "━"*60)
        reference_image_path = "tests/test_images/reference.jpg"
        canny_ok, _ = test_controlnet_builder_canny(builder, reference_image_path)
        results['canny_config'] = canny_ok
    else:
        print("\n⚠️  跳过Canny配置测试（初始化失败）")
    
    # 3. 测试OpenPose配置生成
    if builder_ok:
        print("\n" + "━"*60)
        openpose_ok, _ = test_controlnet_builder_openpose(builder, reference_image_path)
        results['openpose_config'] = openpose_ok
    else:
        print("\n⚠️  跳过OpenPose配置测试（初始化失败）")
    
    # 4. 测试参数注入
    if builder_ok:
        print("\n" + "━"*60)
        results['parameter_injection'] = test_controlnet_parameter_injection()
    else:
        print("\n⚠️  跳过参数注入测试（初始化失败）")
    
    # 5. 测试Engine集成
    print("\n" + "━"*60)
    results['engine_integration'] = test_engine_controlnet_integration()
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name.ljust(20)}: {status}")
    
    # 判断总体状态
    critical_tests = ['builder_init', 'canny_config', 'parameter_injection']
    all_critical_passed = all(results[test] for test in critical_tests)
    
    print("\n" + "="*60)
    if all_critical_passed:
        print("✅ ControlNet约束功能正常")
        if results['openpose_config']:
            print("✅ OpenPose配置正常")
        if results['engine_integration']:
            print("✅ Engine集成正常")
        print("="*60)
        return True
    else:
        print("❌ 存在关键问题，请检查")
        print("="*60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
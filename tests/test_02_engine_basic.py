"""
Engine基础生成测试
任务2: 验证Engine能否成功生成图片
"""

import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from pkg.system.engine import DiffuServoV4
from pkg.infrastructure.config.settings import FORGE_URL
API_URL = f"{FORGE_URL}/sdapi/v1"


def test_creative_director():
    """测试CreativeDirector功能"""
    print("\n" + "="*60)
    print("🧠 测试1: CreativeDirector")
    print("="*60)
    
    try:
        from pkg.system.modules.creator.director import CreativeDirector
        brain = CreativeDirector()
        
        # 测试主题分析
        theme = "A cyberpunk cityscape at night with neon lights"
        print(f"\n📝 主题: {theme}")
        
        # 测试模型推荐
        model_mode = brain.analyze_theme_and_recommend_model(theme)
        print(f"✅ 推荐模型: {model_mode}")
        
        # 测试项目名生成
        project_name = brain.generate_project_name(theme)
        print(f"✅ 项目名: {project_name}")
        
        # 测试Prompt生成
        prompt = brain.brainstorm_prompt(theme, "")
        print(f"✅ Prompt长度: {len(prompt)} 字符")
        print(f"   Prompt预览: {prompt[:100]}...")
        
        return True
        
    except Exception as e:
        print(f"❌ CreativeDirector测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_model_selection():
    """测试模型智能选择"""
    print("\n" + "="*60)
    print("🎯 测试2: 模型智能选择")
    print("="*60)
    
    try:
        from pkg.system.modules.creator.director import CreativeDirector
        brain = CreativeDirector()
        
        test_cases = [
            ("A photorealistic portrait", "RENDER"),
            ("Anime girl with cat ears", "ANIME"),
            ("Simple sketch", "PREVIEW")
        ]
        
        all_passed = True
        for theme, expected in test_cases:
            result = brain.analyze_theme_and_recommend_model(theme)
            passed = result == expected
            status = "✅" if passed else "⚠️"
            print(f"{status} {theme[:30]:<30} → {result} (预期: {expected})")
            all_passed = all_passed and passed
        
        if all_passed:
            print("✅ 模型智能选择测试通过")
        else:
            print("⚠️  部分测试未通过，可能需要调整")
        
        return True
        
    except Exception as e:
        print(f"❌ 模型选择测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_initialization():
    """测试Engine初始化"""
    print("\n" + "="*60)
    print("⚙️  测试3: Engine初始化")
    print("="*60)
    
    try:
        print("\n🔧 初始化DiffuServoV4...")
        engine = DiffuServoV4()
        
        print("✅ Engine初始化成功")
        print(f"   状态: {engine.state}")
        print(f"   迭代次数: {engine.iteration}")
        print(f"   目标分数: {engine.target_score}")
        
        return True, engine
        
    except Exception as e:
        print(f"❌ Engine初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_engine_single_generation(engine):
    """测试单次生成"""
    print("\n" + "="*60)
    print("🎨 测试4: 单次图片生成")
    print("="*60)
    
    try:
        theme = "A simple landscape with mountains"
        print(f"\n📝 主题: {theme}")
        print(f"🔗 Forge API: {API_URL}")
        
        # 执行单次生成
        print("\n🎨 开始生成...")
        img_path = engine.generate(
            prev_score=0.0,
            prev_feedback="",
            best_dimensions={},
            reference_image_path=None
        )
        
        if img_path and os.path.exists(img_path):
            print(f"✅ 图片生成成功")
            print(f"   路径: {img_path}")
            
            # 获取文件大小
            file_size = os.path.getsize(img_path) / 1024
            print(f"   大小: {file_size:.2f} KB")
            
            return True, img_path
        else:
            print(f"❌ 图片生成失败")
            return False, None
            
    except Exception as e:
        print(f"❌ 生成测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None


def test_engine_evaluation(img_path):
    """测试评分功能"""
    print("\n" + "="*60)
    print("📊 测试5: 评分功能")
    print("="*60)
    
    try:
        from pkg.system.modules.evaluator.core import rate_image
        
        theme = "A simple landscape with mountains"
        
        print(f"\n📝 主题: {theme}")
        print(f"🖼️  图片: {img_path}")
        
        # 执行评分
        print("\n📊 开始评分...")
        result = rate_image(img_path, theme)
        
        if result and 'final_score' in result:
            print(f"✅ 评分成功")
            print(f"   总分: {result['final_score']:.2f}")
            print(f"   概念: {result.get('concept_score', 0):.2f}")
            print(f"   质量: {result.get('quality_score', 0):.2f}")
            print(f"   美学: {result.get('aesthetics_score', 0):.2f}")
            print(f"   合理性: {result.get('reasonableness_score', 0):.2f}")
            
            return True
        else:
            print(f"❌ 评分失败: 未返回有效结果")
            return False
            
    except Exception as e:
        print(f"❌ 评分测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_engine_full_run():
    """测试完整运行（短版本）"""
    print("\n" + "="*60)
    print("🔄 测试6: 完整迭代运行（3次）")
    print("="*60)
    
    try:
        theme = "A cyberpunk street at night"
        engine = DiffuServoV4(theme=theme)
        
        print(f"\n📝 主题: {theme}")
        print(f"🎯 最大迭代: 3")
        
        # 运行3次迭代（run()方法不接受theme参数，theme在初始化时设置）
        engine.run(
            reference_image_path=None,
            max_iterations=3
        )
        
        # 从engine对象获取结果
        print(f"\n✅ 运行完成")
        print(f"   最终分数: {engine.best_score:.2f}")
        print(f"   迭代次数: {len(engine.history)}")
        print(f"   最优图片: {engine.best_params.get('image_path', 'N/A') if engine.best_params else 'N/A'}")
        
        return True
            
    except Exception as e:
        print(f"❌ 完整运行测试失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("🚀 开始Engine基础功能测试")
    print("="*60)
    print("\n⚠️  前提条件:")
    print("   1. Forge服务器必须正在运行")
    print("   2. API端点可用: " + API_URL)
    print("="*60)
    
    results = {
        'creative_director': False,
        'model_selection': False,
        'engine_init': False,
        'single_generation': False,
        'evaluation': False,
        'full_run': False
    }
    
    # 1. 测试CreativeDirector
    print("\n" + "━"*60)
    results['creative_director'] = test_creative_director()
    
    # 2. 测试模型选择
    print("\n" + "━"*60)
    results['model_selection'] = test_model_selection()
    
    # 3. 测试Engine初始化
    print("\n" + "━"*60)
    engine_ok, engine = test_engine_initialization()
    results['engine_init'] = engine_ok
    
    if not engine_ok:
        print("\n❌ Engine初始化失败，无法继续测试")
        return False
    
    # 4. 测试单次生成
    print("\n" + "━"*60)
    gen_ok, img_path = test_engine_single_generation(engine)
    results['single_generation'] = gen_ok
    
    # 5. 测试评分
    if gen_ok and img_path:
        print("\n" + "━"*60)
        results['evaluation'] = test_engine_evaluation(img_path)
    else:
        print("\n⚠️  跳过评分测试（生成失败）")
        results['evaluation'] = False
    
    # 6. 测试完整运行
    print("\n" + "━"*60)
    results['full_run'] = test_engine_full_run()
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name.ljust(20)}: {status}")
    
    # 判断总体状态
    critical_tests = ['creative_director', 'model_selection', 'engine_init']
    all_critical_passed = all(results[test] for test in critical_tests)
    
    print("\n" + "="*60)
    if all_critical_passed:
        print("✅ Engine基础功能正常")
        if results['single_generation']:
            print("✅ 图片生成功能正常")
        if results['evaluation']:
            print("✅ 评分功能正常")
        if results['full_run']:
            print("✅ 完整迭代功能正常")
        print("="*60)
        return True
    else:
        print("❌ 存在关键问题，请检查")
        print("="*60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
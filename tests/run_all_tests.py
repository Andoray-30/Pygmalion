"""
测试运行脚本
按顺序执行所有测试任务
"""

import sys
import subprocess
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def run_test(test_file):
    """运行单个测试文件"""
    print("\n" + "="*80)
    print(f"🚀 运行测试: {test_file}")
    print("="*80)
    
    try:
        result = subprocess.run(
            [sys.executable, str(test_file)],
            cwd=str(project_root),
            capture_output=False,
            text=True
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"❌ 运行测试失败: {str(e)}")
        return False


def main():
    """主测试运行流程"""
    print("\n" + "="*80)
    print("🎯 Pygmalion 完整测试套件")
    print("="*80)
    print("\n📋 测试顺序:")
    print("   1. 任务1: Forge服务器健康检查")
    print("   2. 任务2: Engine基础生成测试")
    print("   3. 任务3: 参考图CLIP融合验证")
    print("   4. 任务4: ControlNet约束验证")
    print("   5. 任务5: 构图评分算法验证")
    print("="*80)
    
    # 测试文件列表
    test_files = [
        "tests/test_01_forge_health.py",
        "tests/test_02_engine_basic.py",
        "tests/test_03_reference_clip.py",
        "tests/test_04_controlnet.py",
        "tests/test_05_composition_scoring.py"
    ]
    
    results = {}
    
    # 运行所有测试
    for i, test_file in enumerate(test_files, 1):
        print(f"\n{'━'*80}")
        print(f"📍 测试 {i}/{len(test_files)}: {test_file}")
        print(f"{'━'*80}")
        
        success = run_test(test_file)
        results[test_file] = success
        
        if not success:
            print(f"\n⚠️  测试 {test_file} 失败")
            
            # 对于任务1，如果失败则停止
            if i == 1:
                print("\n" + "="*80)
                print("❌ Forge健康检查失败，无法继续后续测试")
                print("="*80)
                print("\n📝 解决方案:")
                print("   1. 启动Forge服务器: cd F:\\Cyber-Companion\\Pygmalion\\Forge")
                print("   2. 执行: python launch.py")
                print("   3. 等待启动完成后重新运行测试")
                print("="*80)
                break
        
        # 如果不是最后一个测试，询问是否继续
        if i < len(test_files) and success:
            print(f"\n✅ 测试 {test_file} 通过，准备下一个测试...")
    
    # 汇总结果
    print("\n" + "="*80)
    print("📊 最终测试结果汇总")
    print("="*80)
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test_file, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        test_name = test_file.split('/')[-1]
        print(f"   {test_name.ljust(30)}: {status}")
    
    print("\n" + "="*80)
    print(f"📈 测试通过率: {passed}/{total} ({passed/total*100:.1f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 所有测试通过！系统可以正常使用")
        return True
    else:
        print(f"\n⚠️  {total-passed} 个测试失败，请查看详细日志")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
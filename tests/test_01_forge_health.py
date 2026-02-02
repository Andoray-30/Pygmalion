"""
Forge服务器健康检查测试
任务1: 验证Forge环境是否正常运行
"""

import requests
import sys
import time
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Forge API配置
FORGE_URL = "http://127.0.0.1:7860"
API_URL = f"{FORGE_URL}/sdapi/v1"


def test_forge_connection():
    """测试Forge连接"""
    print("\n" + "="*60)
    print("🔍 任务1: Forge服务器健康检查")
    print("="*60)
    
    try:
        # 测试基础连接
        print("\n📡 测试Forge连接...")
        response = requests.get(FORGE_URL, timeout=5)
        
        if response.status_code == 200:
            print("✅ Forge服务器运行正常")
            print(f"   URL: {FORGE_URL}")
            return True
        else:
            print(f"❌ Forge响应异常: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到Forge服务器")
        print("   请确认Forge已启动: cd Forge && python launch.py")
        return False
    except Exception as e:
        print(f"❌ 连接错误: {str(e)}")
        return False


def test_forge_api():
    """测试Forge API可用性"""
    print("\n📊 测试Forge API端点...")
    
    try:
        # 测试选项端点
        response = requests.get(f"{API_URL}/options", timeout=5)
        
        if response.status_code == 200:
            print("✅ API端点可用")
            options = response.json()
            
            # 检查模型
            sd_model_checkpoint = options.get('sd_model_checkpoint', '未知')
            print(f"   当前模型: {sd_model_checkpoint}")
            
            # 检查API版本
            api_version = response.headers.get('Server', '未知')
            print(f"   API版本: {api_version}")
            
            return True, sd_model_checkpoint
        else:
            print(f"❌ API响应异常: {response.status_code}")
            return False, None
            
    except Exception as e:
        print(f"❌ API测试失败: {str(e)}")
        return False, None


def test_forge_models():
    """测试模型加载状态"""
    print("\n🎨 检查已安装的模型...")
    
    try:
        # 获取模型列表
        response = requests.get(f"{API_URL}/sd-models", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 检测到 {len(models)} 个模型:")
            
            # 按优先级分类（使用部分匹配）
            priority_models = {
                'sd_xl_turbo': '⭐ PREVIEW',
                'juggernautXL': '⭐ RENDER',
                'animagineXLV31': '⭐ ANIME'
            }
        
            found_priority = 0
            for model in models:
                model_name = model.get('title', model.get('name', '未知'))
                # 提取基本文件名（不含扩展名和哈希值）
                base_name = model_name.split('\\')[-1].split('.')[0].split('[')[0].strip()
                
                matched = False
                for key, label in priority_models.items():
                    if key in base_name:
                        found_priority += 1
                        print(f"   {label} {base_name}")
                        matched = True
                        break
                
                if not matched:
                    print(f"   • {base_name}")
            
            # 在循环外打印汇总信息
            print(f"\n核心模型状态: {found_priority}/3 已找到")
            
            if found_priority == 3:
                print("✅ 所有核心模型完整")
                return True
            else:
                print(f"⚠️  缺少 {3-found_priority} 个核心模型")
                return False
        else:
            print(f"❌ 获取模型列表失败: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ 模型检查失败: {str(e)}")
        return False


def test_controlnet_models():
    """测试ControlNet模型"""
    print("\n🎯 检查ControlNet模型...")
    
    try:
        # 获取ControlNet模型列表
        response = requests.get(f"{API_URL}/controlnet/model_list", timeout=5)
        
        if response.status_code == 200:
            models = response.json()
            print(f"✅ 检测到 {len(models)} 个ControlNet模型:")
            
            priority_cn = ['canny', 'openpose']
            found_priority = 0
            
            for model in models:
                model_name = model.lower()
                print(f"   • {model}")
                
                if any(cn_type in model_name for cn_type in priority_cn):
                    found_priority += 1
            
            print(f"\n核心ControlNet状态: {found_priority}/2 已找到")
            
            if found_priority >= 1:
                print("✅ ControlNet模型可用")
                return True
            else:
                print("⚠️  缺少核心ControlNet模型")
                return False
        else:
            print(f"⚠️  ControlNet端点不可用: {response.status_code}")
            print("   这可能不影响基础功能")
            return True
            
    except Exception as e:
        print(f"⚠️  ControlNet检查失败: {str(e)}")
        print("   这可能不影响基础功能")
        return True


def test_sample_generation():
    """测试简单生成（可选）"""
    print("\n🎨 测试简单生成...")
    print("   (跳过 - 将在Engine测试中进行)")
    return True


def main():
    """主测试流程"""
    print("\n" + "="*60)
    print("🚀 开始Forge服务器健康检查")
    print("="*60)
    
    results = {
        'connection': False,
        'api': False,
        'models': False,
        'controlnet': False
    }
    
    # 1. 测试连接
    results['connection'] = test_forge_connection()
    
    if not results['connection']:
        print("\n" + "="*60)
        print("❌ 测试失败: Forge服务器未运行")
        print("="*60)
        print("\n📝 解决方案:")
        print("   1. 打开新终端")
        print("   2. 执行: cd F:\\Cyber-Companion\\Pygmalion\\Forge")
        print("   3. 执行: python launch.py")
        print("   4. 等待启动完成，然后重新运行此测试")
        print("="*60)
        return False
    
    # 2. 测试API
    api_success, current_model = test_forge_api()
    results['api'] = api_success
    
    if not results['api']:
        print("\n⚠️  API测试失败，继续其他测试...")
    
    # 3. 测试模型
    results['models'] = test_forge_models()
    
    # 4. 测试ControlNet
    results['controlnet'] = test_controlnet_models()
    
    # 汇总结果
    print("\n" + "="*60)
    print("📊 测试结果汇总")
    print("="*60)
    
    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name.ljust(15)}: {status}")
    
    # 判断总体状态
    critical_tests = ['connection', 'models']
    all_critical_passed = all(results[test] for test in critical_tests)
    
    print("\n" + "="*60)
    if all_critical_passed:
        print("✅ Forge服务器状态良好，可以进行下一步测试")
        print("="*60)
        return True
    else:
        print("❌ 存在关键问题，请先解决后再继续")
        print("="*60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
# Pygmalion测试说明

## 📋 测试结构

```
tests/
├── __init__.py                  # 测试入口
├── test_forge_adapter.py        # ForgeAdapter单元测试
├── test_model_selector.py       # ModelSelector单元测试
├── test_parameter_tuner.py      # PID控制器单元测试
└── test_lora_builder.py         # LoRABuilder单元测试
```

## 🚀 运行测试

### 安装依赖
```bash
pip install pytest pytest-mock
```

### 运行所有测试
```bash
# 方法1：使用pytest
pytest tests/ -v

# 方法2：使用Python
python tests/__init__.py
```

### 运行单个测试文件
```bash
pytest tests/test_forge_adapter.py -v
```

### 运行特定测试用例
```bash
pytest tests/test_forge_adapter.py::TestForgeAdapter::test_generate_success -v
```

## 📊 测试覆盖率

### 安装coverage
```bash
pip install pytest-cov
```

### 生成覆盖率报告
```bash
pytest tests/ --cov=pkg --cov-report=html
```

查看报告：
```bash
# Windows
start htmlcov/index.html

# Linux/Mac
open htmlcov/index.html
```

## 🧪 测试说明

### 1. ForgeAdapter测试
- ✅ 初始化测试
- ✅ 成功生成图片
- ✅ HTTP错误处理
- ✅ 超时处理
- ✅ 空图片列表处理

### 2. ModelSelector测试
- ✅ 不同状态下的模型选择
- ✅ 动漫主题检测
- ✅ 分数阈值判断
- ✅ 迭代次数检查

### 3. PIDParameterTuner测试
- ✅ P/I/D三项独立测试
- ✅ 积分累积验证
- ✅ 微分项振荡抑制
- ✅ 收敛场景模拟

### 4. LoRABuilder测试
- ✅ LoRA构建
- ✅ 多LoRA组合
- ✅ 自动选择
- ✅ 动态添加

## 🔧 Mock策略

### Forge API Mock
```python
@patch('pkg.system.adapters.forge_adapter.requests.post')
def test_example(mock_post):
    mock_resp = Mock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {"images": [...]}
    mock_post.return_value = mock_resp
```

### 健康检查Mock
```python
with patch('pkg.system.adapters.forge_adapter.check_forge_health', return_value=True):
    adapter = ForgeAdapter()
```

## 📈 持续集成

### GitHub Actions示例
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - run: pip install -r requirements.txt
      - run: pip install pytest pytest-mock
      - run: pytest tests/ -v
```

## 🎯 测试最佳实践

1. **单一职责**：每个测试只验证一个功能
2. **独立性**：测试之间不应相互依赖
3. **可重复**：多次运行结果一致
4. **快速**：避免sleep和真实API调用
5. **清晰命名**：`test_<功能>_<场景>`

## 🐛 调试技巧

### 打印详细输出
```bash
pytest tests/ -v -s
```

### 只运行失败的测试
```bash
pytest tests/ --lf
```

### 进入调试模式
```bash
pytest tests/ --pdb
```

## 📝 添加新测试

### 模板
```python
import pytest
from pkg.system.xxx import YourClass

@pytest.fixture
def your_fixture():
    return YourClass()

class TestYourClass:
    def test_something(self, your_fixture):
        result = your_fixture.method()
        assert result == expected_value
```

---

**维护者**: Pygmalion Team  
**最后更新**: 2026-01-31

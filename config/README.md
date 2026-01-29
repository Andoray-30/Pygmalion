# config/ - 配置管理模块

## 📋 模块用途

集中管理 Pygmalion 系统的全局配置、API 密钥、模型路径和算法超参数。

## 📂 文件说明

### `settings.py`
系统全局配置文件，包含：

#### API 配置
```python
API_KEY_MODELSCOPE = "your_key"      # ModelScope (免费评分 API)
API_KEY_SILICONFLOW = "your_key"     # SiliconFlow (付费评分 API)
API_KEY_DEEPSEEK = "your_key"        # DeepSeek (提示词生成 API)
```

#### 模型配置
```python
MODEL_PATH = "path/to/sd_xl_turbo_1.0_fp16.safetensors"
LOCAL_MODEL_ENABLED = True
GPU_DEVICE = "cuda:0"
DTYPE = "fp16"  # 半精度加速
```

#### 评分配置
```python
TARGET_SCORE = 0.9              # 目标评分
SCORE_THRESHOLD_EXPLORE = 0.85  # 探索阶段启动阈值
SCORE_THRESHOLD_OPTIMIZE = 0.86 # 优化阶段启动阈值
```

#### 迭代配置
```python
MAX_ITERATIONS = 30              # 最大迭代次数
EXPLORE_ITERATIONS = 5           # 探索阶段时长
EARLY_STOP_PATIENCE = 5          # 无进展停止轮数
```

#### 参数范围
```python
STEPS_SDXL_TURBO = 1            # SDXL Turbo 固定 1 步
CFG_RANGE = (1.0, 2.0)          # CFG Scale 范围
HR_SCALE_RANGE = (1.0, 2.0)     # HR Scale 范围
```

#### 超参数
```python
PID_KP = 0.5                     # PID 比例系数
PID_KI = 0.1                     # PID 积分系数
PID_KD = 0.2                     # PID 微分系数
```

### `__init__.py`
模块初始化文件，暴露配置接口。

## 🔧 使用示例

### 读取配置
```python
from config import API_KEY_MODELSCOPE, TARGET_SCORE, MAX_ITERATIONS

print(f"目标分数: {TARGET_SCORE}")
print(f"最大迭代: {MAX_ITERATIONS}")
```

### 修改运行时配置
```python
from config import settings

settings.TARGET_SCORE = 0.95
settings.MAX_ITERATIONS = 50
```

## ⚙️ 配置文件优先级

1. **环境变量** (最高优先级)
   ```bash
   set PYGMALION_TARGET_SCORE=0.95
   ```

2. **settings.py** (次优先级)

3. **.env 文件** (最低优先级)
   ```
   MODELSCOPE_API_KEY=xxx
   SILICONFLOW_API_KEY=xxx
   ```

## 🔐 安全建议

- ✅ 不要将 `settings.py` 提交到版本控制
- ✅ 使用 `.env` 文件存储敏感密钥
- ✅ 本地开发可使用 `.env.example` 作为模板

## 📝 常见配置场景

### 场景 1: 快速测试
```python
MAX_ITERATIONS = 5
TARGET_SCORE = 0.8
EXPLORE_ITERATIONS = 2
```

### 场景 2: 精细优化
```python
MAX_ITERATIONS = 50
TARGET_SCORE = 0.95
EXPLORE_ITERATIONS = 10
```

### 场景 3: 仅用评分 API
```python
LOCAL_MODEL_ENABLED = False
API_ONLY_MODE = True
```

## 🚨 故障排查

| 问题 | 解决方案 |
|------|--------|
| API 连接失败 | 检查 API_KEY，验证网络连接 |
| GPU 显存不足 | 修改 DTYPE 为 "fp32" 或降低 BATCH_SIZE |
| 模型加载失败 | 检查 MODEL_PATH 是否正确 |

---

**最后更新**: 2026-01-29

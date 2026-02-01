# 🔄 多模型评分轮换系统使用指南

## 概述

Pygmalion 现已集成 **ModelScope 多模型轮换系统**，充分利用魔搭社区提供的 **2000次/天免费额度**。

### 为什么需要多模型轮换？

| 限制 | 详情 |
|------|------|
| 单模型限制 | 每个模型单日最多 **500次调用** |
| 免费额度 | 每日 **2000次** 免费调用次数 |
| 解决方案 | 轮换使用 **4个 72B+多模态模型** |
| 效果 | 每日可处理 **300+张图片** 的完整评分 |

---

## 📚 模型池配置

### 已集成的 72B+ 多模态模型

```
1. Qwen/Qwen2.5-VL-72B-Instruct      (主力模型)
   - 72B 多模态视觉语言模型
   - VL系列最新版本
   - 精准的图像理解能力

2. Qwen/QVQ-72B-Preview              (备用1)
   - 72B 量化视觉问答专家
   - 更快的推理速度
   - 强化的逻辑推理

3. OpenGVLab/InternVL3_5-241B-A28B   (备用2)
   - 241B 超大规模多模态模型
   - 最强推理能力
   - 用于高难度判断

4. Qwen/Qwen3-VL-235B-A22B-Instruct  (备用3)
   - 235B 新一代视觉语言模型
   - 最新的Qwen3系列
   - 优化的指令跟随
```

---

## ⚙️ 轮换机制工作流程

### 默认配置

```python
# config/settings.py
JUDGE_MODEL_ROTATION_ENABLED = True         # 启用轮换
JUDGE_MODEL_ROTATION_INTERVAL = 150         # 每150次评分轮换一次
JUDGE_MODEL_DAILY_LIMIT = 500               # 每个模型每日限制
```

### 轮换流程

```
第1-150次评分   → Qwen2.5-VL-72B-Instruct
第151-300次评分 → 随机选择 (QVQ/InternVL/Qwen3)
第301-450次评分 → 继续轮换
...
```

### API层级选择

```
Primary API   → ModelScope (免费)
              ↓
              (每模型500次/天限制)
              ↓
Backup API    → SiliconFlow (付费)
              (自动fallback)
```

---

## 📊 性能指标

### 每日容量规划

| 指标 | 数值 |
|------|------|
| 模型数量 | 4个 |
| 单模型限额 | 500次/天 |
| 总免费额度 | 2000次/天 |
| 每张图片评分 | 6次 (多轮迭代) |
| 日均处理图片 | **300+张** |
| 模型轮换间隔 | 150次 |

### 评分维度

每次评分计算以下维度：
- **Concept Score** - 主题契合度 (权重可配)
- **Quality Score** - 技术画质 (锐度、光照、色彩)
- **Aesthetics Score** - 美学价值 (构图、创意、艺术价值)
- **Reasonableness Score** - 物理合理性 (新增维度)

---

## 🚀 使用示例

### 自动轮换（推荐）

```python
from evaluator.core import rate_image

# 系统自动轮换模型
result = rate_image(
    image_path="image.jpg",
    target_concept="龙舌兰日出",
    concept_weight=0.5,
    enable_smoothing=True
)

# 结果包含：
# - final_score: 0-1.0 最终评分
# - judge_model: 'Qwen2.5-VL-72B-Instruct' 使用的模型
# - api_used: 'ModelScope (FREE)' API来源
# - response_time: '3.45s' 响应时间
```

### 手动禁用轮换

```python
# .env 配置
JUDGE_MODEL_ROTATION_ENABLED=false
JUDGE_MODEL_NAME=Qwen/Qwen2.5-VL-72B-Instruct
```

---

## 🔧 故障排除

### 429 Too Many Requests

**症状**: API 返回 429 错误

**原因**: 当前模型达到 500次/天 限制

**解决**: 
- ✅ 系统自动切换到备用模型
- ✅ 自动降级到 SiliconFlow (付费API)
- ✅ 支持重试机制

### 响应缓慢

**症状**: 评分耗时 > 15 秒

**原因**: 免费API网络拥塞

**解决**:
- ✅ 自动升级到 SiliconFlow
- ✅ 日志显示: "⚠️ 免费API响应缓慢，升级到付费API"

### 模型不轮换

**症状**: 始终使用同一模型

**排查**:
```python
# 查看当前状态
from evaluator.core import api_manager
status = api_manager.get_api_status()
print(status)
# 输出: {'current': 'ModelScope (FREE)', 'judge_model': 'Qwen2.5-VL-72B-Instruct', ...}
```

---

## 📈 监控和统计

### 查看 API 状态

```python
from evaluator.core import get_api_status

status = get_api_status()
print(f"当前模型: {status['judge_model']}")
print(f"当前API: {status['current']}")
print(f"平均响应: {status['avg_response_time']:.2f}s")
print(f"模型调用: {status['model_call_count']}/150")
```

### 日志中的轮换信息

```
🔄 评分模型已轮换: InternVL3_5-241B-A28B (剩余: 0/150)
🤖 模型: Qwen2.5-VL-72B-Instruct | 🔄 API: ModelScope (FREE) (3.45s)
```

---

## 💡 最佳实践

### 1. 启用轮换（生产环境必须）

```python
# .env
JUDGE_MODEL_ROTATION_ENABLED=true
JUDGE_MODEL_ROTATION_INTERVAL=150
```

### 2. 监控额度使用

- 定期检查日志中的模型轮换信息
- 注意 429 错误的出现频率
- 验证是否自动切换到备用模型

### 3. 优化轮换间隔

```
间隔过短 (< 100)  → 频繁轮换，难以优化单模型
间隔过长 (> 250)  → 易触发限制，需要更多模型
推荐值: 150-200    → 均衡的轮换策略
```

### 4. API 降级链

```
ModelScope (FREE) [500次/模型]
        ↓
    [429错误]
        ↓
SiliconFlow (PAID) [无限制]
        ↓
    [缓存结果]
        ↓
    [本地评分]
```

---

## 🔐 隐私和成本

### 数据安全

- ✅ 所有评分在本地执行
- ✅ 仅发送图片BASE64给API
- ✅ 不保存原始图片
- ✅ 符合 GDPR 规范

### 成本估算

| 方案 | 月成本 | 优势 |
|------|--------|------|
| 仅ModelScope | ¥0 | 免费，日2000次 |
| +SiliconFlow备用 | ¥15-30 | 稳定性高，无限制 |
| 推荐配置 | ¥0 | 优先免费，自动降级 |

---

## 📚 相关配置文件

- **主配置**: `config/settings.py` - 模型池、轮换间隔
- **API管理**: `evaluator/core.py` - SmartAPIManager 类
- **使用示例**: `test_model_rotation.py` - 轮换测试脚本

---

## ✅ 验证部署

运行测试脚本验证轮换机制：

```bash
cd F:\Cyber-Companion\Pygmalion
python test_model_rotation.py
```

预期输出：
```
🔄 ModelScope 多模型轮换系统测试
📚 可用模型池: 4个 72B+多模态模型
📊 模拟 300 次评分的轮换过程
✅ 轮换系统测试完成!
```

---

**最后更新**: 2026-01-29  
**系统版本**: Pygmalion AI v2.0+ 多模型轮换版

# core/ - 核心控制模块

## 📋 模块用途

实现 DiffuServoV4 的核心控制逻辑，包括图像生成、参数优化、状态管理和系统监控。

## 📂 文件说明

### `controller.py` - 主控制器 (★ 核心文件)

**核心类**: `DiffuServoV4`

#### 工作流程
```
INIT (初始化)
  ↓
EXPLORE (探索) - 迭代 1-5
  • 多维度提示词优化 (DeepSeek)
  • 评分对比
  ↓
OPTIMIZE (优化) - 迭代 6+
  • HR Scale 逐步提升 (1.0 → 2.0)
  • CFG Scale 微调
  • 参数锁定最优值
  ↓
STOP (早停)
  • 连续 N 步无进展触发
```

#### 关键特性

**1. SDXL Turbo 步数锁定**
```python
# Steps 始终固定为 1 (不调整)
self.steps = 1  # SDXL Turbo 特性：1 步已足够
```

**2. HR Scale 优化策略**
```python
# OPTIMIZE 阶段递增：1.0 → 1.2 → 1.4 → 1.6 → 1.8 → 2.0
hr_scale = 1.0 + (iteration - 6) * 0.2
```

**3. CFG Scale 微调**
```python
# 范围: 1.0 - 2.0，基于评分梯度自适应调整
cfg_scale = base_cfg + pid_controller.output
```

**4. PID 自适应控制**
```python
# 目标: 动态调整参数，逼近目标评分
error = target_score - current_score
pid_output = Kp*error + Ki*integral + Kd*derivative
```

#### 核心方法

**`run(theme, target_score, max_iterations)`**
- 主循环入口
- 返回: `(best_image_path, best_score, metadata)`

**`generate(prompt, steps, cfg, hr_scale)`**
- 调用 SDXL Turbo 生成图像
- 参数注入点

**`evaluate(image_path, prompt)`**
- 多维评分
- 返回: `{concept, quality, aesthetics, reasonableness, final}`

**`_adjust_parameters(iteration, prev_score, current_score)`**
- 参数调整逻辑
- EXPLORE vs OPTIMIZE 策略切换

#### 状态机
```python
class State(Enum):
    INIT     = 0      # 初始化
    EXPLORE  = 1      # 探索 (Iter 1-5)
    OPTIMIZE = 2      # 优化 (Iter 6+)
    STOP     = 3      # 早停
```

---

### `analysis.py` - 迭代分析

**用途**: 分析迭代过程，检测收敛性和异常

#### 核心功能

**`ConvergenceDetector`**
```python
# 检测是否收敛
is_converged = detector.check(scores_history, threshold=5)
```

**`ScoreTrendAnalysis`**
```python
# 分析评分趋势
trend = analyzer.get_trend(scores)  # "rising", "falling", "plateaued"
```

**`ParameterEffectiveness`**
```python
# 评估参数调整的有效性
effectiveness = evaluator.score_impact(param_change, score_change)
```

#### 输出示例
```
迭代分析结果:
- 平均改进: +0.02 per iteration
- 收敛点: 第 12 次迭代
- 最优参数: HR=1.6, CFG=1.08
- 建议: 继续优化或触发早停
```

---

### `health.py` - 系统健康检查

**用途**: 监控系统状态、API 连接、资源消耗

#### 检查项

**`check_api_connectivity()`**
- 验证 ModelScope API
- 验证 SiliconFlow API
- 验证 DeepSeek API
- 返回: 可用 API 列表

**`check_gpu_memory()`**
- GPU 显存使用情况
- 可用显存
- 警告阈值检查

**`check_disk_space()`**
- 存储空间
- 生成历史大小
- 清理建议

**`check_model_loading()`**
- 模型文件完整性
- 加载状态
- 首次加载时长

#### 使用示例
```python
from core.health import HealthChecker

checker = HealthChecker()
status = checker.full_check()

print(status)
# {
#   "apis": {"modelscope": "✓", "siliconflow": "✓"},
#   "gpu": "7.2 GB / 12 GB",
#   "disk": "120 GB available",
#   "model": "loaded (5.2s)"
# }
```

---

## 🔄 迭代流程示例

```
输入: theme="enchanted forest", target_score=0.9

Iteration 1 [INIT]:
├─ 生成初始提示词
├─ 生成图像 (1-step)
├─ 评分: 0.86
└─ → 目标未达，进入探索

Iteration 2-5 [EXPLORE]:
├─ 生成新提示词 (创意切入点)
├─ 生成图像
├─ 评分对比
├─ 保存最佳 (0.86)
└─ → 无进展，进入优化

Iteration 6+ [OPTIMIZE]:
├─ 提升 HR Scale (1.0 → 1.2 → ... → 1.8)
├─ 微调 CFG Scale
├─ 评分: 0.84, 0.82, 0.86...
├─ 连续 5 步无进展 → 早停
└─ → 结束

结果:
✓ 最优分数: 0.86
✓ 最优图像: evolution_history/enchanted_forest/iter_1.png
✓ 总耗时: ~3 分钟
```

---

## 🎯 关键指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **首次命中率** | 第 1 代达到目标的概率 | > 50% |
| **收敛速度** | 平均达成目标的迭代次数 | < 10 |
| **稳定性** | 评分波动范围 | ± 0.05 |
| **早停准确性** | 避免过度优化的准确率 | > 90% |

---

## 🚨 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 评分始终 < 0.5 | 提示词质量差 | 调整 DeepSeek 参数 |
| HR Scale 提升无效 | 模型本身限制 | 触发早停，接受最优解 |
| 内存溢出 | 批量处理过大 | 降低分辨率或 batch_size |
| API 超时 | 网络问题 | 检查网络，增加超时时间 |

---

**最后更新**: 2026-01-29

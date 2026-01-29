# evaluator/ - 评分系统模块

## 📋 模块用途

使用 AI 模型对生成的图像进行多维度评分，驱动迭代优化过程。

## 📂 文件说明

### `core.py` - 评分引擎 (★ 核心文件)

**核心类**: `ImageEvaluator`

#### 评分维度

系统采用 **4 维评分体系**:

| 维度 | 权重 | 说明 | 范围 |
|------|------|------|------|
| **Concept Alignment** | 40% | 与提示词主题的匹配度 | 0.0-1.0 |
| **Image Quality** | 30% | 画质、清晰度、细节 | 0.0-1.0 |
| **Aesthetics** | 20% | 美学、色彩、构图 | 0.0-1.0 |
| **Reasonableness** | 10% | 合理性、避免扭曲 | 0.0-1.0 |

**综合评分公式**
```
Final Score = 0.40 * Concept + 0.30 * Quality + 0.20 * Aesthetics + 0.10 * Reasonableness
```

#### 核心方法

**`evaluate(image_path, prompt)`**
```python
evaluator = ImageEvaluator()
score = evaluator.evaluate(
    image_path="path/to/image.png",
    prompt="enchanted forest, mystical glow..."
)
# 返回: {"concept": 0.90, "quality": 0.85, "aesthetics": 0.90, "reasonableness": 0.80, "final": 0.86}
```

**`batch_evaluate(image_paths, prompts)`**
```python
scores = evaluator.batch_evaluate(
    image_paths=["img1.png", "img2.png"],
    prompts=["prompt1", "prompt2"]
)
# 返回: [score1, score2, ...]
```

#### 双 API 支持

系统支持两个评分 API，并能自动切换：

**1. ModelScope API (免费)**
- 优点: 免费，无费用限制
- 缺点: 速度稍慢，精准度略低
- 调用额度: 无限

**2. SiliconFlow API (付费)**
- 优点: 更精准，更快
- 缺点: 需要付费
- 适用: 高质量评分需求

#### API 切换机制

```python
# 自动切换策略
- 首选 ModelScope (免费)
- ModelScope 故障 → 切换到 SiliconFlow
- 两者都故障 → 使用缓存分数或本地启发式评分
```

**手动指定 API**
```python
evaluator = ImageEvaluator(preferred_api="siliconflow")
```

---

### `utils.py` - 工具函数

**功能**:

**1. 分数正规化**
```python
from evaluator.utils import normalize_score

raw_score = 95  # 满分 100
normalized = normalize_score(raw_score)  # 0.95
```

**2. 权重计算**
```python
from evaluator.utils import calculate_weighted_score

scores = {
    "concept": 0.90,
    "quality": 0.85,
    "aesthetics": 0.90,
    "reasonableness": 0.80
}
weights = {
    "concept": 0.40,
    "quality": 0.30,
    "aesthetics": 0.20,
    "reasonableness": 0.10
}

final_score = calculate_weighted_score(scores, weights)
```

**3. 分数缓存**
```python
from evaluator.utils import ScoreCache

cache = ScoreCache()
# 保存分数
cache.save(image_hash, score)
# 读取分数
cached_score = cache.get(image_hash)
```

**4. 分数统计**
```python
from evaluator.utils import score_statistics

stats = score_statistics(score_list)
# {
#   "mean": 0.86,
#   "std": 0.03,
#   "min": 0.81,
#   "max": 0.90
# }
```

---

## 🔄 评分流程

```
输入: 图像路径 + 提示词
    ↓
[1] 图像预处理 (resize, normalize)
    ↓
[2] 特征提取 (色彩、清晰度、构图)
    ↓
[3] 发送到 API (ModelScope/SiliconFlow)
    ↓
[4] 接收 4 维评分
    ↓
[5] 加权计算最终分数
    ↓
[6] 缓存结果
    ↓
输出: 最终分数 (0.0-1.0)
```

---

## 📊 评分分布示例

```
分数范围      | 说明
───────────────────────────
0.90 - 1.00  | 优秀 (Excellent) ⭐⭐⭐
0.80 - 0.89  | 良好 (Good)      ⭐⭐
0.70 - 0.79  | 中等 (Fair)      ⭐
0.60 - 0.69  | 一般 (Poor)      -
< 0.60       | 失败 (Bad)       ✗
```

---

## 🚨 故障处理

**API 故障时的降级策略**
```python
try:
    score = evaluator.evaluate_with_api(image, prompt)
except APIError:
    # 尝试备用 API
    try:
        score = evaluator.evaluate_with_fallback(image, prompt)
    except:
        # 使用缓存或启发式评分
        score = evaluator.get_cached_or_heuristic(image)
```

**缓存机制**
- 相同图像多次评分时使用缓存
- 缓存过期时间: 24 小时
- 手动清理: `evaluator.clear_cache()`

---

## 📈 精度对标

| 情景 | ModelScope | SiliconFlow | 推荐 |
|------|----------|------------|------|
| 快速迭代 | ✓ | - | ModelScope |
| 最终评估 | - | ✓ | SiliconFlow |
| 混合使用 | ✓ | ✓ | 首选 MS，困难用 SF |

---

## 🎯 校准和微调

如需自定义权重:

```python
evaluator = ImageEvaluator(
    weights={
        "concept": 0.5,      # 增加主题匹配权重
        "quality": 0.3,
        "aesthetics": 0.15,
        "reasonableness": 0.05
    }
)
```

---

## 💾 缓存位置

```
cache/
└── scores/
    ├── {image_hash}.json
    └── metadata.json
```

---

**最后更新**: 2026-01-29

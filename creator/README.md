# creator/ - 提示词生成模块

## 📋 模块用途

使用 AI (DeepSeek) 驱动的创意提示词生成和优化，为图像生成提供高质量的文本指导。

## 📂 文件说明

### `director.py` - 提示词生成引擎 (★ 核心文件)

**核心类**: `PromptDirector`

#### 核心职责

**1. 初始提示词生成**
```python
director = PromptDirector()
initial_prompt = director.generate_initial(theme="enchanted forest")
# "enchanted forest, mystical glow, bioluminescent flora, tower..."
```

**2. 创意多元化探索** (EXPLORE 阶段)
```python
# 多维度切入点，避免重复
dimensions = [
    "Emphasis on Color Palette",      # 颜色维度
    "Emphasis on Lighting & Atmosphere", # 光影维度
    "Emphasis on Composition & Perspective", # 构图维度
    "Emphasis on Material & Texture", # 材质维度
    "Emphasis on Emotion/Vibe"        # 情感维度
]

for dim in dimensions:
    new_prompt = director.generate_variant(theme, dimension=dim)
```

**3. 参数微调** (OPTIMIZE 阶段)
```python
# 基于评分反馈进行微调
optimized_prompt = director.refine(
    base_prompt="...",
    feedback="increase detail in bioluminescence",
    intensity=0.7
)
```

**4. 历史最佳回滚**
```python
# 检测到停滞时回滚到历史最佳
best_prompt = director.get_best_from_history(top_k=1)
```

#### 提示词模板

**基础结构**
```
[主题] + [风格] + [技术特征] + [光影] + [构图] + [质感]
```

**示例**
```
enchanted forest, mystical glow, bioluminescent flora, 
cinematic volumetric lighting, towering ancient trees,
intricate velvety textures, golden hour, ethereal atmosphere
```

#### 维度系统

| 维度 | 关键词示例 | 用途 |
|------|---------|------|
| **色彩** | twilight, vibrant, monochrome | 改变配色方案 |
| **光影** | volumetric lighting, golden hour, cinematic | 增强视觉效果 |
| **材质** | velvety, crystalline, metallic, translucent | 丰富细节 |
| **构图** | foreground focus, rule of thirds, depth | 改善布局 |
| **情感** | ethereal, ominous, peaceful, dynamic | 强化氛围 |

---

## 🔄 工作流程

### INIT 阶段 (Iter 1)
```
输入主题: "enchanted forest"
    ↓
DeepSeek 分析: 理解主题核心
    ↓
生成初始提示词: 包含主题、风格、技术特征
    ↓
返回提示词 → 进入图像生成
```

### EXPLORE 阶段 (Iter 2-5)
```
评分: 0.86 ✓ 不变
    ↓
检测停滞 → 选择新维度
    ↓
"Emphasis on Color Palette"
    ↓
DeepSeek 生成变体
    ↓
新提示词 → 进入图像生成
```

### OPTIMIZE 阶段 (Iter 6+)
```
评分: 0.84 ✗ 下降
    ↓
基于反馈微调最佳提示词
    ↓
调整强度: intensity = 0.5
    ↓
微调提示词 → 进入图像生成
```

---

## 📊 提示词版本管理

系统自动保存所有提示词版本，便于回滚和对比：

```python
# 查看历史版本
versions = director.history.get_all()
for v in versions:
    print(f"Iter {v['iteration']}: Score={v['score']:.2f}")
    print(f"Prompt: {v['prompt']}")

# 回滚到最佳版本
best = director.history.get_best()
```

---

## 🤖 DeepSeek API 集成

**调用方式**
```python
from creator.director import PromptDirector

director = PromptDirector()
prompt = director.generate_initial(
    theme="enchanted forest",
    style="cinematic",
    context="fantasy"
)
```

**参数说明**
- `theme`: 主题 (必需)
- `style`: 风格风格 (可选)
- `context`: 场景背景 (可选)
- `temperature`: 创意度 (0.1 - 1.0, 默认 0.7)
- `max_tokens`: 最大长度 (默认 200)

**错误处理**
```python
try:
    prompt = director.generate_initial("enchanted forest")
except DeepSeekAPIError as e:
    print(f"DeepSeek 失败: {e}")
    prompt = director.get_fallback_prompt("enchanted forest")
except TimeoutError:
    print("API 超时，使用历史最佳")
    prompt = director.get_best_from_history()
```

---

## 💾 缓存机制

系统缓存已生成的提示词，加速重复查询：

```
cache/
├── {theme}/
│   ├── initial.json
│   ├── variants_{dimension}.json
│   └── metadata.json
```

**清理缓存**
```bash
python -c "from creator import PromptDirector; PromptDirector().clear_cache()"
```

---

## 🎯 质量指标

| 指标 | 说明 | 目标值 |
|------|------|--------|
| **多样性** | 生成提示词的差异度 | > 0.7 |
| **相关性** | 提示词与主题的匹配度 | > 0.85 |
| **有效性** | 能产生高分图像的比例 | > 60% |
| **一致性** | 同一主题的提示词稳定性 | > 0.8 |

---

## 🚨 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| DeepSeek 超时 | 网络慢或 API 拥堵 | 增加超时时间，启用重试 |
| 提示词重复 | 缓存未更新 | 清理缓存重新生成 |
| 分数不升 | 提示词质量差 | 增加 temperature 提高创意度 |
| API 限流 | 请求过于频繁 | 添加请求间隔 |

---

## 📝 提示词最佳实践

✅ **优秀提示词**
```
enchanted forest, mystical twilight glow, 
bioluminescent flora and fauna, cinematic volumetric lighting,
ancient towering trees, intricate velvety textures,
ethereal atmosphere, 4K resolution
```

❌ **不良提示词**
```
forest pretty
nice trees
fantasy world
```

---

**最后更新**: 2026-01-29

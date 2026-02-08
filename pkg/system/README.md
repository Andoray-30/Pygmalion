# System - 系统核心

## 📋 概述

DiffuServoV4 自适应图像生成引擎及相关智能体模块。

---

## 🏗️ 核心架构

```
DiffuServoV4 引擎
    ├─ CreativeDirector (创意大脑)
    ├─ Evaluator (图像评分器)
    ├─ ReferenceProcessor (参考图处理)
    ├─ ControlNetBuilder (ControlNet 构建)
    ├─ IPAdapterBuilder (IP-Adapter 构建)
    ├─ LoRABuilder (LoRA 构建)
    └─ Strategies (优化策略)
```

---

## 📂 目录结构

```
system/
├── __init__.py
├── engine.py           # DiffuServoV4 主引擎
├── initializer.py      # 引擎初始化逻辑
├── adapters/           # Forge API 适配器
├── builders/           # Payload 构建器
│   ├── controlnet_builder.py
│   ├── ipadapter_builder.py
│   ├── lora_builder.py
│   └── utils.py
├── modules/            # 功能模块
│   ├── creator/        # 创意生成（DeepSeek）
│   ├── evaluator/      # 图像评分（多模态VL模型）
│   └── reference/      # 参考图处理（CLIP/多模态）
├── pipeline/           # 生成流程管理
└── strategies/         # 优化策略
    ├── model_selector.py
    ├── parameter_tuner.py
    └── prompt_enhancer.py
```

---

## 🚀 快速开始

### 基础用法

```python
from pkg.system import DiffuServoV4

# 初始化引擎
engine = DiffuServoV4(
    theme="动漫女孩，粉色头发，抱胸姿势",
    reference_image_path="reference.jpg"
)

# 运行生成
engine.run(
    target_score=0.90,      # 目标分数
    max_iterations=5        # 最大迭代次数
)
```

### 高级用法：参考图约束

```python
# "保持不变"模式
engine = DiffuServoV4(
    theme="保持人物主体不变，衣服不变，修改姿势为抱胸",
    reference_image_path="reference.jpg"
)

# 自动检测意图并强化约束
# - ControlNet 权重: 1.0 → 1.5
# - 参考匹配阈值: 0.70 → 0.80
# - 模型锁定: ANIME 模型不切换

engine.run(target_score=0.90, max_iterations=5)
```

---

## 🧩 核心组件

### 1. DiffuServoV4 引擎 (`engine.py`)

**职责：** 自适应控制图像生成流程

**核心特性：**
- 🎯 **智能模型选择**：根据主题和参考图自动选择 PREVIEW/ANIME/RENDER
- 🔒 **模型锁定机制**：多模态分析推荐后锁定模型，防止错误切换
- 🎨 **多重约束系统**：ControlNet + IP-Adapter + 参考融合
- 📊 **自适应评分**：动态调整权重，支持"保持不变"意图
- ⚡ **早停机制**：收敛检测，避免浪费算力

**状态机：**
```
INIT → EXPLORE → OPTIMIZE → FINETUNE → CONVERGED
```

---

### 2. 创意生成模块 (`modules/creator/`)

📖 [详细文档](modules/creator/README.md)

**核心功能：**
- DeepSeek 驱动的 Prompt 生成
- 主题意图分析（识别"动漫"/"写实"/"抽象"）
- 镜头视角随机化（"close-up"/"wide shot"等）
- 风格强化关键词注入

```python
from pkg.system.modules.creator import CreativeDirector

brain = CreativeDirector()
prompt = brain.brainstorm_prompt(
    base_theme="enchanted forest",
    feedback_context="Improve lighting"
)
```

---

### 3. 图像评分模块 (`modules/evaluator/`)

📖 [详细文档](modules/evaluator/README.md)

**核心功能：**
- 五维评分：概念匹配、技术质量、美学艺术、物理合理、参考匹配
- 多模型轮换：ModelScope (免费) ↔ SiliconFlow (付费)
- 智能降级：超时自动切换 API
- 参考图专项评分：风格一致性、姿态相似度、构图匹配、角色保真

```python
from pkg.system.modules.evaluator import rate_image

result = rate_image(
    image_path="output.png",
    target_concept="anime girl",
    reference_image_path="reference.jpg",
    keep_unchanged=True  # 强化参考约束
)
# result: {final_score, concept, quality, aesthetics, 
#          reference_match, character_consistency, ...}
```

---

### 4. 参考图处理模块 (`modules/reference/`)

**核心功能：**
- 📸 **多模态风格分析**：识别"动漫/二次元"、"写实摄影"、"3D 渲染"
- 🏷️ **CLIP 标签融合**：提取视觉特征并融合到 Prompt
- 🎭 **图像匹配评估**：CLIP 相似度计算，支持风格/姿态/角色匹配

```python
from pkg.system.modules.reference import analyze_reference_style_with_multimodal

analysis = analyze_reference_style_with_multimodal("reference.jpg")
# {
#   'style_category': '动漫/二次元',
#   'confidence': 0.95,
#   'recommended_model': 'ANIME',
#   'deepseek_hints': {...}
# }
```

---

### 5. Payload 构建器 (`builders/`)

#### ControlNet 构建器
```python
from pkg.system.builders import ControlNetBuilder

builder = ControlNetBuilder()
config = builder.build_multi([
    {"image": "ref.jpg", "type": "canny", "weight": 1.3},
    {"image": "ref.jpg", "type": "openpose", "weight": 0.8}
])
# 多单元 ControlNet 配置
```

#### IP-Adapter 构建器
```python
from pkg.system.builders import IPAdapterBuilder

builder = IPAdapterBuilder()
config = builder.build_multi([
    {"image": "ref.jpg", "model": "faceid_plusv2", "weight": 0.8},
    {"image": "ref.jpg", "model": "plus", "weight": 0.5}
])
# 人脸 + 全局风格锁定
```

---

## 🔧 优化策略 (`strategies/`)

### 模型选择器 (`ModelSelector`)
根据主题和反馈动态选择 PREVIEW/ANIME/RENDER 模型。

### 参数调优器 (`PIDParameterTuner`)
基于 PID 控制理论，自适应调整 CFG、步数、去噪强度。

### Prompt 增强器 (`PromptEnhancer`)
注入镜头视角、光照、艺术风格等关键词。

---

## 🎯 工作流程

### 典型生成流程

```
1. 初始化 DiffuServoV4
   ├─ 多模态分析参考图 → 推荐 ANIME 模型
   ├─ 检测"保持不变"意图 → 强化约束
   └─ 锁定模型防止切换

2. 第 1 次迭代 (INIT 状态)
   ├─ CreativeDirector 生成 Prompt
   ├─ 构建 ControlNet + IP-Adapter Payload
   ├─ 调用 Forge API 生成图片
   └─ Evaluator 评分 → 0.62 (角色一致性 0.59)

3. 第 2 次迭代 (EXPLORE 状态)
   ├─ 检测到角色一致性不足 → 强化 ControlNet 权重
   ├─ 重新生成并评分 → 0.68 (角色一致性 0.65)
   └─ 评分提升，进入 OPTIMIZE 状态

4. 第 3 次迭代 (OPTIMIZE 状态)
   ├─ 启用 HR 放大
   ├─ 锁定最佳镜头视角
   └─ 评分 → 0.85 (达标)

5. 收敛 → 返回最佳结果
```

---

## 📊 关键配置

### 收敛条件
```python
TARGET_SCORE = 0.90            # 目标分数
CONVERGENCE_PATIENCE = 3       # 容忍无进展次数
CONVERGENCE_THRESHOLD = 0.005  # 最小进步阈值
```

### 模型切换条件
```python
MODEL_SWITCH_SCORE_THRESHOLD = 0.75  # 切换最低分
MODEL_SWITCH_MIN_ITERATIONS = 3      # 切换最少迭代
```

### 约束权重（"保持不变"模式）
```python
reference_match_min = 0.80           # 参考匹配阈值
reference_controlnet_weight = 1.5    # ControlNet 权重
reference_match_weight = 0.35        # 评分权重占比
```

---

## 🐛 调试建议

### 1. 查看生成日志
```python
import logging
logging.basicConfig(level=logging.DEBUG)

engine.run(...)
# 查看详细的 Prompt、评分、状态转换日志
```

### 2. 检查参考图分析
```python
from pkg.system.initializer import EngineInitializer

result = EngineInitializer.initialize_reference_model(
    brain, theme, reference_image_path
)
print(result['reference_style_analysis'])
```

### 3. 验证约束配置
```python
print(f"模型锁定: {engine.model_locked}")
print(f"ControlNet 权重: {engine.reference_controlnet_weight}")
print(f"参考匹配阈值: {engine.reference_match_min}")
```

---

## ⚠️ 常见问题

### 1. 模型错误切换
**问题：** ANIME → PREVIEW 导致角色崩坏

**原因：** 未检测到"保持不变"意图或模型未锁定

**解决：**
```python
# 确保主题包含关键词
theme = "保持人物主体不变，修改姿势"  # ✅
theme = "修改姿势"                      # ❌ 未检测到意图
```

### 2. 角色一致性低
**问题：** `character_consistency < 0.65` 但总分高

**原因：** 参考约束权重不足

**解决：**
```python
# 手动强化约束
engine.keep_unchanged_intent = True
engine.reference_match_min = 0.80
engine.reference_controlnet_weight = 1.5
```

### 3. Forge API 超时
**问题：** `requests.Timeout` 或生成卡死

**解决：**
- 检查 Forge WebUI 状态
- 增加超时时间：`FORGE_TIMEOUT=120`
- 减少生成步数或分辨率

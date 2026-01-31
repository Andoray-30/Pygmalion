# Pygmalion 架构文档

## 📐 系统架构概览

Pygmalion 是一个基于PID控制理论的自适应AI图像生成系统，采用**分层模块化架构**，实现了高内聚、低耦合的设计原则。

```
┌─────────────────────────────────────────────────────────────┐
│                       Interface Layer                        │
│                     (interface/server.py)                    │
└────────────┬────────────────────────────────────────────────┘
             │
┌────────────▼────────────────────────────────────────────────┐
│                      Orchestration Layer                     │
│                      (system/engine.py)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  INIT    │→ │ EXPLORE  │→ │ OPTIMIZE │→ │ FINETUNE │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                       Pipeline Layer                         │
│                (pipeline/generation_pipeline.py)             │
│  ┌──────────────────────────────────────────────────────┐   │
│  │ 1. Model Selection → 2. Prompt Enhancement →         │   │
│  │ 3. LoRA Mounting → 4. ControlNet Setup → 5. Generate│   │
│  └──────────────────────────────────────────────────────┘   │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      Strategy Layer                          │
│  ┌────────────────┐ ┌────────────────┐ ┌──────────────┐    │
│  │ ModelSelector  │ │PromptEnhancer  │ │ ParameterTuner│   │
│  │   (智能选模型)  │ │  (Prompt优化)   │ │  (PID控制器)   │   │
│  └────────────────┘ └────────────────┘ └──────────────┘    │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      Builder Layer (NEW)                     │
│  ┌────────────────┐ ┌────────────────────────────────────┐  │
│  │  LoRABuilder   │ │     ControlNetBuilder             │  │
│  │ (LoRA挂载)     │ │  (姿态/边缘控制)                    │  │
│  └────────────────┘ └────────────────────────────────────┘  │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      Adapter Layer                           │
│  ┌────────────────┐ ┌────────────────────────────────────┐  │
│  │ ForgeAdapter   │ │    EvaluatorAdapter               │  │
│  │ (API封装)      │ │     (评分器封装)                    │  │
│  └────────────────┘ └────────────────────────────────────┘  │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ 各层职责

### 1. **Interface Layer（接口层）**
- **文件**: `pkg/interface/server.py`
- **职责**: FastAPI服务器，处理HTTP请求
- **功能**:
  - `/generate` - 创建生成任务
  - `/status/{project_id}` - 查询状态
  - `/models` - 列出可用模型

### 2. **Orchestration Layer（编排层）**
- **文件**: `pkg/system/engine.py`
- **职责**: 状态机管理与流程编排
- **核心逻辑**:
  ```python
  INIT → EXPLORE → OPTIMIZE → FINETUNE → CONVERGED
  ```
- **设计原则**:
  - ✅ 只负责状态转换
  - ✅ 调用Pipeline执行具体任务
  - ❌ 不直接操作API或生成图片

### 3. **Pipeline Layer（流水线层）**
- **文件**: `pkg/system/pipeline/generation_pipeline.py`
- **职责**: 图片生成的完整流程
- **步骤**:
  1. 智能模型选择（ModelSelector）
  2. Prompt增强（PromptEnhancer）
  3. LoRA挂载（LoRABuilder）
  4. ControlNet配置（ControlNetBuilder）
  5. 调用Forge API生成图片

### 4. **Strategy Layer（策略层）**
- **文件**:
  - `pkg/system/strategies/model_selector.py`
  - `pkg/system/strategies/prompt_enhancer.py`
  - `pkg/system/strategies/parameter_tuner.py`
- **职责**: 核心算法实现
- **详细说明**:

#### 4.1 ModelSelector（模型选择器）
```python
def select(theme, state, current_score, iteration):
    """
    根据主题、状态、分数自动选择最优底模
    
    INIT/EXPLORE: PREVIEW (快速试错)
    OPTIMIZE (score>0.80): RENDER/ANIME (高质量)
    FINETUNE: 保持高质量模型
    """
```

#### 4.2 PromptEnhancer（Prompt增强器）
- 调用DeepSeek生成创意Prompt
- 根据评分反馈迭代优化
- 支持锁定最佳Prompt（OPTIMIZE阶段）

#### 4.3 ParameterTuner（参数调优器 - PID控制器）
```python
class PIDParameterTuner:
    """完整的P+I+D控制器"""
    
    def compute(target_score, current_score):
        # P项: 比例控制 (当前误差)
        p_term = Kp * (target - current)
        
        # I项: 积分控制 (累积误差，消除稳态误差)
        integral += error * dt
        i_term = Ki * integral
        
        # D项: 微分控制 (误差变化率，抑制振荡)
        derivative = (error - last_error) / dt
        d_term = Kd * derivative
        
        return p_term + i_term + d_term
```

**优势**:
- ✅ P项：快速响应
- ✅ I项：消除0.88→0.90的稳态误差
- ✅ D项：防止分数振荡（0.85↔0.92）

---

### 5. **Builder Layer（构建器层 - 新增）**
- **文件**:
  - `pkg/system/builders/lora_builder.py`
  - `pkg/system/builders/controlnet_builder.py`
- **职责**: 构建复杂Payload

#### 5.1 LoRABuilder（LoRA挂载）
```python
# 使用方法
lora = LoRABuilder()

# 单个LoRA
prompt = lora.build("CYBERPUNK", "city at night")
# 输出: "<lora:cyberpunk_xl:0.8>, neon lights, city at night"

# 多个LoRA
prompt = lora.build_multi([
    ("CYBERPUNK", 0.8),
    ("REALISTIC", 0.6)
], "city street")

# 自动选择
prompt = lora.auto_select("anime girl", base_prompt)
```

**内置LoRA库**:
- `CYBERPUNK` - 赛博朋克风格
- `ANIME_STYLE` - 动漫线稿
- `REALISTIC` - 写实增强
- `PORTRAIT` - 人像专用

#### 5.2 ControlNetBuilder（姿态/边缘控制）
```python
# 使用方法
cn = ControlNetBuilder()

# 边缘检测
payload = cn.build(
    reference_image=Image.open("pose.jpg"),
    cn_type="canny",
    weight=0.8
)

# 多个ControlNet
payload = cn.build_multi([
    {"image": img1, "type": "canny", "weight": 0.8},
    {"image": img2, "type": "openpose", "weight": 0.6}
])
```

**支持的类型**:
- `canny` - 边缘检测
- `depth` - 深度图
- `openpose` - 姿态控制
- `mlsd` - 线条检测

---

### 6. **Adapter Layer（适配器层）**
- **文件**:
  - `pkg/system/adapters/forge_adapter.py`
  - `pkg/system/adapters/evaluator_adapter.py`
- **职责**: 封装外部API调用
- **优势**:
  - ✅ 隔离变化（切换到ComfyUI只需改Adapter）
  - ✅ 便于Mock测试
  - ✅ 统一错误处理

---

## 🔄 完整执行流程示例

```python
# 1. 用户请求
POST /generate {"theme": "cyberpunk city", "style_hint": "CYBERPUNK"}

# 2. Engine初始化状态机
engine = DiffuServoV4(theme="cyberpunk city")
state = "INIT"

# 3. Pipeline执行生成
pipeline = GenerationPipeline()

# 4. 策略层决策
model = ModelSelector.select("cyberpunk city", "INIT", 0.0, 1)
# 返回: "PREVIEW" (快速试错)

# 5. Prompt增强
prompt = PromptEnhancer.enhance("cyberpunk city", state="INIT")
# 返回: "neon-lit cityscape with flying cars, ..."

# 6. 挂载LoRA
lora = LoRABuilder()
prompt = lora.build("CYBERPUNK", prompt)
# 返回: "<lora:cyberpunk_xl:0.8>, neon lights, ..."

# 7. 调用Forge生成图片
result = ForgeAdapter.generate(params)

# 8. 评分并更新状态
score = EvaluatorAdapter.rate(result['path'], theme)
if score > 0.5:
    state = "EXPLORE"

# 9. PID控制器调整参数
pid = PIDParameterTuner()
adjustments = pid.compute(target_score=0.90, current_score=score)
params['steps'] += adjustments['steps_delta']
params['cfg_scale'] += adjustments['cfg_delta']

# 10. 循环迭代直到收敛
```

---

## 🚀 扩展指南

### 添加新的底模
```python
# 1. 在 pkg/infrastructure/config.py 中注册
BASE_MODELS["NEW_MODEL"] = "new_model.safetensors"
MODEL_CONFIGS["NEW_MODEL"] = {
    "steps": 20,
    "cfg_scale": 7.0,
    "enable_hr": True
}

# 2. 在 ModelSelector 中添加选择逻辑
def select(...):
    if "specific_keyword" in theme:
        return "NEW_MODEL"
```

### 添加新的LoRA
```python
# 在代码中动态添加
lora_builder = LoRABuilder()
lora_builder.add_lora(
    name="MY_LORA",
    file="my_custom_lora",
    weight=0.75,
    trigger="special style, unique look"
)
```

### 添加新的ControlNet类型
```python
# 在 ControlNetBuilder 中扩展
SUPPORTED_TYPES.append("new_type")

def _get_model_name(self, cn_type):
    if cn_type == "new_type":
        return "control_v11p_sd15_newtype"
```

---

## 🧪 测试策略

### 单元测试
```python
# tests/test_model_selector.py
def test_model_selector():
    selector = ModelSelector()
    model = selector.select(
        theme="anime girl",
        state="INIT",
        current_score=0.0,
        iteration=1
    )
    assert model == "PREVIEW"  # 初期应该使用快速模型
```

### 集成测试
```python
# tests/test_pipeline.py
def test_generation_pipeline():
    pipeline = GenerationPipeline()
    
    # Mock Forge Adapter
    pipeline.forge_adapter = MockForgeAdapter()
    
    result = pipeline.generate(
        theme="test theme",
        state="INIT",
        iteration=1,
        params={"steps": 4}
    )
    
    assert result is not None
    assert "path" in result
```

---

## 📊 性能优化建议

### 1. **模型切换优化**
```python
# 避免频繁切换导致显存抖动
if not self.has_switched_to_render:
    if score > 0.80:
        switch_to_render()
        self.has_switched_to_render = True  # 单向阀
```

### 2. **Prompt缓存**
```python
# 在OPTIMIZE阶段锁定最佳Prompt
if state == "OPTIMIZE":
    use_best_prompt()  # 不再随机生成
```

### 3. **Early Stopping**
```python
# 检测停滞，提前终止
if no_improvement_count >= 8:
    stop_iteration()
```

---

## 🔐 安全与配置

### API密钥管理
```python
# ❌ 错误：硬编码
DEEPSEEK_API_KEY = "sk-xxx"

# ✅ 正确：环境变量
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")
```

### 配置文件
```python
# pkg/infrastructure/config.py
FORGE_URL = os.getenv("FORGE_URL", "http://127.0.0.1:7860")
TARGET_SCORE = float(os.getenv("TARGET_SCORE", "0.90"))
```

---

## 📈 监控与日志

### 关键指标
- 迭代次数
- 分数变化趋势
- 状态转换时机
- PID控制器输出

### 日志示例
```python
print(f"[Iter {iter}] [{state}] [RENDER] Score: {score:.2f}")
print(f"🎛️ [PID] P+I+D输出: steps_delta=+2, cfg_delta=+0.3")
```

---

## 🎯 未来规划

### 短期目标
- [ ] IP-Adapter支持（锁脸功能）
- [ ] 多图批量生成
- [ ] 实时进度推送（WebSocket）

### 长期目标
- [ ] 支持ComfyUI后端
- [ ] 分布式训练
- [ ] 风格迁移学习

---

## 📚 参考文档

- [Stable Diffusion WebUI API](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API)
- [PID控制器理论](https://en.wikipedia.org/wiki/PID_controller)
- [ControlNet论文](https://arxiv.org/abs/2302.05543)

---

**架构版本**: v2.0  
**最后更新**: 2026-01-31  
**维护者**: Pygmalion Team

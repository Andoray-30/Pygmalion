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
│                      Core Engine Layer                       │
│                      (system/engine.py)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │  INIT    │→ │ EXPLORE  │→ │ OPTIMIZE │→ │ FINETUNE │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
│  集成: 模型选择 + Prompt增强 + LoRA挂载 + 评分反馈         │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      Strategy Layer                          │
│  ┌────────────────┐ ┌────────────────┐ ┌──────────────┐    │
│  │ ModelSelector  │ │PromptEnhancer  │ │ParameterTuner│    │
│  │   (智能选模型)  │ │  (Prompt优化)   │ │  (PID控制器)  │    │
│  └────────────────┘ └────────────────┘ └──────────────┘    │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      Builder Layer                           │
│  ┌────────────────┐                                          │
│  │  LoRABuilder   │  LoRA风格挂载与管理                      │
│  └────────────────┘                                          │
└──────┬──────────────────────────────────────────────────────┘
       │
┌──────▼──────────────────────────────────────────────────────┐
│                      Module Layer                            │
│  ┌────────────────┐ ┌──────────────────────────────────┐    │
│  │  Evaluator     │ │   Reference Matcher              │    │
│  │  (评分系统)     │ │   (参考图一致性)                   │    │
│  └────────────────┘ └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 🏗️ 各层职责

### 1. **Interface Layer（接口层）**
- **文件**: `pkg/interface/server.py`
- **职责**: Flask + SocketIO 服务器，处理WebSocket和HTTP请求
- **功能**:
  - WebSocket 实时生成通信
  - `/api/upload_reference` - 参考图上传
  - 状态管理与会话控制

### 2. **Core Engine Layer（核心引擎层）**
- **文件**: `pkg/system/engine.py`
- **职责**: 状态机管理与生成流程编排
- **核心逻辑**:
  ```python
  INIT → EXPLORE → OPTIMIZE → FINETUNE → CONVERGED
  ```
- **特点**:
  - ✅ 直接集成：模型选择、Prompt增强、LoRA挂载、API调用
  - ✅ 状态驱动：根据分数和梯度自动切换状态
  - ✅ 自适应调参：PID控制器动态优化参数

### 3. **Strategy Layer（策略层）**
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
- `PHOTOREALISTIC` - 摄影级写实
- `STUDIO_PORTRAIT` - 影棚人像

---

### 4. **Builder Layer（构建器层）**
- **文件**: `pkg/system/builders/lora_builder.py`
- **职责**: LoRA风格管理与挂载

```python
# 使用方法
lora = LoRABuilder()

# 单个LoRA
prompt = lora.build("CYBERPUNK", "city at night")
# 输出: "<lora:cyberpunk_edgerunners_style_sdxl:0.8> cyberpunk style, neon lights, city at night"

# LLM智能选择
prompt = lora.llm_select(theme="cyberpunk city", base_prompt="...", director=brain)
# 自动根据主题推荐风格并挂载增强器
```

**支持的风格**:
- `CYBERPUNK` - 赛博朋克风格
- `ANIME_LINEART` - 动漫线稿
- `PHOTOREALISTIC` - 摄影级写实
- `STUDIO_PORTRAIT` - 影棚人像

---

### 5. **Module Layer（模块层）**
- **文件**:
  - `pkg/system/modules/evaluator/core.py` - 多维评分系统
  - `pkg/system/modules/reference/image_matcher.py` - 参考图一致性
- **职责**: 独立功能模块

#### 5.1 Evaluator（评分系统）
- 多模型轮换评分（Qwen2.5-VL-72B等）
- 5维度评分：概念、质量、美学、合理性、参考图一致性
- 智能API管理与错误恢复

#### 5.2 Reference Matcher（参考图匹配）
- CLIP特征提取
- 5个一致性维度：风格、姿态、构图、角色、总体匹配度
- 加权融合到最终评分

---

## 🔄 完整执行流程示例

```python
# 1. 用户请求（WebSocket）
emit('generate', {
    "theme": "cyberpunk city", 
    "reference_image_path": "/path/to/ref.jpg"
})

# 2. Engine初始化状态机
engine = DiffuServoV4(
    theme="cyberpunk city",
    reference_image_path="/path/to/ref.jpg"
)
state = "INIT"

# 3. 策略层决策
model = ModelSelector.select("cyberpunk city", "INIT", 0.0, 1)
# 返回: "PREVIEW" (快速试错)

# 4. Prompt增强
prompt = PromptEnhancer.enhance("cyberpunk city", state="INIT")
# 返回: "neon-lit cityscape with flying cars, ..."

# 5. 挂载LoRA（LLM智能决策）
lora = LoRABuilder()
prompt = lora.llm_select("cyberpunk city", prompt, director)
# 返回: "<lora:cyberpunk_edgerunners_style_sdxl:0.8> <lora:xl_more_art-full_v1:0.5> ..."

# 6. 直接调用Forge API生成
resp = requests.post(f"{FORGE_URL}/sdapi/v1/txt2img", json=params)
image_path = save_image(resp.json()['images'][0])

# 7. 评分（包含参考图一致性）
score_result = rate_image(
    image_path, 
    theme, 
    reference_image_path="/path/to/ref.jpg"
)
# 返回: {
#   "final_score": 0.75,
#   "concept_score": 0.8,
#   "quality_score": 0.7,
#   "reference_match_score": 0.72,
#   ...
# }

# 8. 状态转换
if score_result['final_score'] > 0.5:
    state = "EXPLORE"

# 9. PID控制器调整参数
tuner = AdaptiveParameterTuner()
params = tuner.adjust(
    params, 
    state, 
    score_buffer, 
    target_score=0.90, 
    result=score_result
)

# 10. 循环迭代直到收敛
```

---

## 🚀 扩展指南

### 添加新的底模
```python
# 在 pkg/infrastructure/config/settings.py 中注册
BASE_MODELS["NEW_MODEL"] = "new_model.safetensors"
MODEL_CONFIGS["NEW_MODEL"] = {
    "steps": 20,
    "cfg_scale": 7.0,
    "enable_hr": True,
    "hr_scale": 1.5,
    "hr_second_pass_steps": 10,
    "denoising_strength": 0.4
}

# 在 ModelSelector 中添加选择逻辑
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

# tests/test_lora_builder.py
def test_lora_build():
    builder = LoRABuilder()
    result = builder.build("CYBERPUNK", "city at night")
    assert "<lora:" in result
    assert "cyberpunk style" in result
```

**测试覆盖**: 48个单元测试覆盖核心组件（ModelSelector, LoRABuilder, ParameterTuner等）

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

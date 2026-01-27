# 🎨 Pygmalion - 智能AI创意生成系统

**Current Version: 4.2** | 基于闭环控制的自适应图像生成代理

Pygmalion 是一个智能化的 AI 绘画代理系统，结合 **4D评分体系** 和 **双API架构**，实现物理合理性检测与成本优化的自动化创意生成。包含完整的版本演进与更新历史。

---

## 🌟 核心特性

### 🔬 4D 评分系统
- **Concept** — 概念匹配度
- **Quality** — 技术质量 (清晰度、噪点、伪影)
- **Aesthetics** — 美学价值 (构图、创意、艺术性)
- **Reasonableness** — 物理合理性 (光照、比例、重力、空间逻辑) ⭐ 新增

### 🔄 智能双API架构
- **免费优先**: ModelScope API (`api-inference.modelscope.cn`)
- **自动升级**: SiliconFlow API (`api.siliconflow.cn`)
- **切换条件**: 平均响应 > 15s 或 连续失败 ≥ 2 次
- **成本优化**: 免费为主，必要时升级付费（节省 90%+ 成本）

### 🧠 创意大脑
- **DeepSeek-V3**: 通用艺术透镜，生成富有想象力的提示词

### 🎯 自适应控制 (DiffuServo V4)
- **状态机**: INIT → EXPLORE → OPTIMIZE → FINETUNE → CONVERGED
- **动态权重**: 根据阶段调节概念/质量权重
- **智能早停**: 梯度监测自动收敛
- **低分回退**: FINETUNE 阶段连续 3 次低分自动回退到 OPTIMIZE

---

## 📦 项目结构

```
Pygmalion/
├── config/                 # 配置管理 (.env, settings.py)
├── evaluator/              # 评分系统 (4D + 双API)
│   ├── core.py            # SmartAPIManager + rate_image()
│   └── utils.py           # 图像编码/JSON解析
├── creator/               # 创意生成 (DeepSeek)
│   └── director.py
├── core/                  # 控制循环
│   ├── controller.py      # DiffuServoV4 主控
│   ├── analysis.py        # 梯度计算工具
│   └── health.py          # Forge 健康检查
├── evolution_history/     # 生成结果存储（按主题分类）
├── main.py                # 程序入口
└── ARCHITECTURE.md        # 系统架构与流程图
```

---

## 🚀 快速开始

### 1. 安装依赖 (Python 3.8+)
```bash
pip install openai requests python-dotenv
```

### 2. 配置 `.env` (至少一个API密钥)
```bash
# 免费API (推荐优先)
MODELSCOPE_API_KEY=your_modelscope_key

# 付费API (可选备份)
SILICON_KEY=your_silicon_key

# DeepSeek (创意生成)
DEEPSEEK_API_KEY=your_deepseek_key

# Forge WebUI 地址
FORGE_URL=http://127.0.0.1:7860

# 目标分数与迭代次数
TARGET_SCORE=0.90
MAX_ITERATIONS=30
```

### 3. 启动 Forge (SD WebUI Forge)
```
访问 http://127.0.0.1:7860
```

### 4. 开始生成
```bash
python main.py
```

---

## 📊 4D 评分详解

### 评分维度

| 维度 | 权重 | 说明 | 约束 |
|------|------|------|------|
| Concept | 动态 (30-70%) | 主题匹配 | Concept < 0.5 → Final ≤ 0.6 |
| Quality | 动态 | 清晰度/噪点/伪影 | Quality < 0.6 → Final ≤ 0.7 |
| Aesthetics | 15% | 构图/创意/艺术性 | — |
| Reasonableness | 15% | 光照/比例/重力/空间 | Reasonableness < 0.6 → Final ≤ 0.75 |

### 评分公式

```python
Final = Concept×w1 + Quality×w2 + Aesthetics×0.15 + Reasonableness×0.15

# 动态权重调整 (按状态)
EXPLORE:   w1=0.70, w2=0.10
OPTIMIZE:  w1=0.30, w2=0.40
FINETUNE:  w1=0.50, w2=0.20

# EWMA 平滑 (平滑因子 α=0.3)
Smoothed = 0.3 × Raw + 0.7 × Previous
```

### 物理合理性检测 (NEW in v4.1)

Qwen2.5-VL-72B 多维度评估：
- ✅ **光照一致性** — 阴影方向与光源匹配
- ✅ **物体比例** — 相对尺寸合理（如蝴蝶不应大于树木）
- ✅ **重力与支撑** — 漂浮物需有合理解释
- ✅ **空间相干性** — 深度、透视、遮挡逻辑正确
- ✅ **材质属性** — 反射、透明度表现真实

**评分标准**:
- 1.0: 完全符合物理法则
- 0.8: 轻微风格化但连贯（魔幻/艺术允许）
- 0.6: 明显物理问题（错误阴影、不可能的尺度）
- 0.4: 严重物理违背（不一致光源、解剖错误、透视扭曲）

---

## 🔄 双API 智能切换

### 自动升级条件
- 默认使用免费API (ModelScope)
- 当 `avg_response_time > 15s` → 升级到付费API (SiliconFlow)
- 或 `failures >= 2 次` → 升级到付费API
- 重启程序即可恢复免费API优先

### API 状态查询
```python
from evaluator import get_api_status
status = get_api_status()
print(status)
# {
#   'current': 'ModelScope (FREE)',
#   'free_ready': True,
#   'premium_ready': True,
#   'fallback_enabled': False,
#   'avg_response_time': 6.2
# }
```

---

## ⚙️ 系统参数调优

### 全局配置 (config/settings.py)
```python
# 模型选择
JUDGE_MODEL_NAME = "Qwen2.5-VL-72B-Instruct"  # 评分模型 (v4.1+ 升级)
DEEPSEEK_MODEL = "DeepSeek-V3"                # 创意模型

# 目标与迭代
TARGET_SCORE = 0.90
MAX_ITERATIONS = 30

# 超时与重试
FORGE_TIMEOUT = 180                           # 图生超时 (秒)
JUDGE_TIMEOUT = 60                            # 评分超时 (秒)
JUDGE_MAX_RETRIES = 3                         # 评分重试次数

# 日志
LOG_LEVEL = "INFO"
LOG_FILE = "pygmalion.log"
```

### 自适应控制参数 (core/controller.py)
```python
# 学习率系数
Kp_steps = 1.5                                 # Steps 调参比例
Kp_cfg = 0.6                                   # CFG 调参比例

# 收敛检测
CONVERGENCE_PATIENCE = 3                       # 无进展忍耐次数
CONVERGENCE_THRESHOLD = 0.001                 # 改进阈值

# 评分权重
aesthetics_weight = 0.15
reasonableness_weight = 0.15
concept_weight = 动态 (0.3-0.7)
```

### API 阈值 (evaluator/core.py)
```python
SPEED_THRESHOLD = 15.0                         # 升级到付费的响应时间 (秒)
FAILURE_THRESHOLD = 2                          # 升级到付费的失败次数
```

---

## 📈 性能指标 (实测)

| 指标 | 数值 |
|------|------|
| 免费API 响应时间 | 5-7 秒 (平均 6.2s) |
| 付费API 响应时间 | 3-5 秒 |
| 评分模型 72B 推理时间 | 20-25 秒 |
| 图生超时 | 180 秒 |
| 成本优化 | 免费 90%+ 的情况，自动升级必要时 |
| 物理问题识别准确率 | >80% |

---

## 📁 输出结构

```
evolution_history/
  ├── enchanted_forest/           # 主题文件夹
  │   ├── enchanted_forest_20260128_143022_iter1.png
  │   ├── enchanted_forest_20260128_143022_iter2.png
  │   └── ...
  └── <other_themes>/
      └── ...

# 元数据存储于内存中，program.py 输出最终报告
```

### 最终输出示例
```
======================================================================
✅ 结果：达到目标分数
======================================================================
🏆 最优分数: 0.92
📍 最优方案来自第 12 代
💾 最优图片路径: evolution_history/enchanted_forest/enchanted_forest_*.png
======================================================================
```

---

## 🚨 常见问题

| 问题 | 解决方案 |
|------|---------|
| **API密钥错误** | 检查 `.env` 中密钥格式与空格 |
| **Forge 连接失败** | 确保 Forge WebUI 已启动 (`http://127.0.0.1:7860`) |
| **免费API慢** | 超过 15 秒会自动切换到付费API，检查网络 |
| **物理合理性低** | 分数 < 0.6 时最终分数被限制 ≤ 0.75，尝试更详细的 Prompt |
| **强制使用付费** | 从 `.env` 中移除 `MODELSCOPE_API_KEY` |
| **模型不支持** | 在 `config/settings.py` 中切换模型 (e.g., Qwen2.5-VL-7B) |

---

## 🛠️ 技术栈

- **Python**: 3.8+
- **评分模型**: Qwen2.5-VL-72B-Instruct (v4.1+ 升级)
- **创意模型**: DeepSeek-V3
- **生成引擎**: Stable Diffusion WebUI Forge
- **API 框架**: OpenAI SDK
- **API 提供商**: ModelScope (免费) + SiliconFlow (付费)
- **控制算法**: DiffuServo V4 (P-Control + 智能早停)

---

## 📚 相关资源

- [ModelScope 官网](https://modelscope.cn) — 免费API 提供商
- [SiliconFlow 官网](https://siliconflow.cn) — 付费API 提供商
- [DeepSeek 平台](https://platform.deepseek.com) — 创意模型
- [SD WebUI Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) — 生成引擎
- [ARCHITECTURE.md](ARCHITECTURE.md) — 系统架构与流程图详解

---

## 📝 版本历史

### [v4.2] - 2026-01-28: 文档整合与精简

**主要变更**:
- ✨ 统一根目录文档为单一入口 README.md
- 🗑️ 删除冗余说明文件（UPGRADE_4D_EVALUATION.md、QUICK_START.md 等）
- 🗑️ 删除临时测试脚本（test_4d_scoring.py、test_e2e.py）
- 📚 集成 CHANGELOG 内容至 README
- 🔗 新增 ARCHITECTURE.md（系统架构可视化）

**文件变更**:
```
修改: README.md (内容整合)
删除: CHANGELOG.md (合并至 README)
新增: ARCHITECTURE.md (架构文档)
删除: test_*.py (临时文件)
删除: 其他 *.md (UPGRADE、QUICK_START 等)
```

---

### [v4.1] - 2026-01-27: 物理合理性评估升级 ⭐ 重大升级

**核心升级**:

#### 评估模型 10 倍升级
```
旧: Qwen2.5-VL-7B-Instruct
新: Qwen2.5-VL-72B-Instruct
提升: 参数量 7B → 72B，推理能力显著增强
```

#### 四维评分系统 (3D → 4D)
新增维度 **Physical Reasonableness**（物理合理性）：
- 光照一致性（阴影与光源方向匹配）
- 物体比例（相对尺寸合理）
- 重力支撑（漂浮物需合理解释）
- 空间相干（深度、透视、遮挡逻辑）
- 材质真实（反射、透明度表现）

#### 权重分配 (4维动态加权)
```python
Final = (Concept × w1) + (Quality × w2) + 
        (Aesthetics × 0.15) + (Reasonableness × 0.15)
# w1: 0.3-0.7 (状态机动态调整)
# w2: 自动计算确保总和 = 1.0
```

#### 约束规则增强
```python
IF reasonableness_score < 0.6:
    final_score ≤ 0.75  # 物理违背严格限制
```

**JSON 输出格式变化**:
```json
{
  "concept_score": 0.85,
  "quality_score": 0.90,
  "aesthetics_score": 0.88,
  "reasonableness_score": 0.65,        // ← NEW
  "final_score": 0.82,
  "reason": "Light contradiction, butterfly size wrong"
}
```

**预期效果**:
| 场景 | 旧评分 | 新评分 | 变化 |
|------|--------|--------|------|
| 美学图+物理合理 | 0.88 | 0.88 | ✓ 无变化 |
| 美学图+物理违背 | 0.87 | 0.75 | ⚠️ 被约束 |
| 漂浮城堡(魔幻) | 0.82 | 0.78 | - 需优化 |

**兼容性**: ✅ 完全向后兼容，旧评分逻辑保留

---

### [v1.0.0] - 2026-01-27: 代码模块化重构

**主要改进**:

#### 代码结构重构
- **config/** — 集中管理所有参数与环境变量
- **core/** — DiffuServo V4 控制器、梯度分析、健康检查
- **creator/** — DeepSeek 创意提示词生成
- **evaluator/** — Qwen 多维度评分 + 双API管理

#### 功能改进
- 动态主题支持（DiffuServoV4 初始化时自定义）
- 智能存储路径（按主题自动分类）
- 评分失败防护（无效分数检查）
- 梯度计算修正（score_buffer 重复追加 bug 修复）

#### 清理工作
- 删除旧测试脚本 (Test_Pygmalion.py)
- 删除过时审计报告 (CODE_AUDIT.md)
- 清理生成历史

**架构优势**:
- ✅ 可维护性 — 模块职责明确
- ✅ 可扩展性 — 易于添加新评估器、创意生成器
- ✅ 可读性 — 代码组织清晰、注释充分
- ✅ 灵活性 — 环境变量覆盖支持

---

## 📄 许可证

MIT License

---

**最后更新**: 2026-01-28  
**当前版本**: v4.2  
**维护者**: Andoray-30 / Pygmalion Team


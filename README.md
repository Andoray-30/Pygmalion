# 🎨 Pygmalion DiffuServo V4

**智能自适应图像生成系统** - AI 驱动的提示词优化 + 多模型评分 + 实时流式显示

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## ⚡ 快速开始

详见 [QUICK_START.md](QUICK_START.md) (5 分钟快速上手)

## ✨ 核心特性

| 特性 | 说明 |
|------|------|
| 🧠 AI 提示词优化 | DeepSeek 多维度创意生成 + 智能回滚 |
| 📊 多模型评分 | 4×72B+ 模型自动轮换 (每150次) |
| 🌐 实时流式 | Gradio Web UI, 每个迭代即时推送 |
| 💾 会话恢复 | JSON 存储, 页面刷新自动恢复 |
| 🎯 自适应控制 | INIT→EXPLORE→OPTIMIZE→FINETUNE→CONVERGED |
| 🔄 智能早停 | 收敛时自动停止, 节省资源 |
| ⚙️ API 自动降级 | 免费→付费, 429错误自动切换 |

---

## 📂 项目结构

```
Pygmalion/
├── webui/app.py              # 🌐 Web UI (Gradio)
├── core/
│   ├── controller.py         # DiffuServoV4 控制器
│   ├── state_manager.py      # 会话管理
│   └── ...
├── config/settings.py        # 全局配置
├── evaluator/core.py         # API 管理 + 模型轮换
├── creator/director.py       # DeepSeek 提示词生成
└── tests/                    # 单元测试
```

详见 [config/README.md](config/README.md) | [core/README.md](core/README.md)

---

## 🎮 使用指南

1. 启动: `python webui/app.py` 
2. 访问: http://localhost:7861
3. 输入主题 → 设置参数 → 点击开始生成
4. 每个迭代即时显示结果和分数
5. 切换"会话恢复"标签页查看历史

---

## 🔧 配置

### API 配额

| 服务 | 额度 | 说明 |
|------|------|------|
| ModelScope | 2000次/天 | 4个模型, 每150次切换 |
| SiliconFlow | 按月计费 | 429错误自动降级 |
| DeepSeek | 自定义 | 提示词生成 |

### 模型轮换

4个评分模型自动轮换:
- Qwen2.5-VL-72B-Instruct (主力)
- QVQ-72B-Preview (量化, 速快)
- InternVL3_5-241B (超强)
- Qwen3-VL-235B (最新)

### 生成参数调优

在 `config/settings.py` 中配置:

```python
# DeepSeek 创意提示词参数
DEEPSEEK_TEMPERATURE = 0.8          # 创意度 (0.0-1.0)
DEEPSEEK_TOP_P = 0.9                # 多样性 (0.0-1.0)

# 自适应控制参数
CONVERGENCE_THRESHOLD = 0.003       # 分数改进阈值
CONVERGENCE_PATIENCE = 5            # 早停耐心值 (迭代数)

# 模型轮换
JUDGE_MODEL_ROTATION_ENABLED = True
JUDGE_MODEL_ROTATION_INTERVAL = 150
```

---

---

## 📊 会话数据格式

```json
{
  "session_id": "gen_1706555920123",
  "theme": "enchanted forest",
  "status": "completed",
  "best_score": 0.923,
  "iterations": [...]
}
```

---

## ⚠️ 常见问题

| 问题 | 解决方案 |
|------|---------|
| 无法实时显示 | 重启 Web UI: `python webui/app.py` |
| 429 错误频繁 | 检查 SILICONFLOW_API_KEY 是否配置 |
| 生成质量差 | 提高目标分数 (0.88-0.92) 或迭代次数 |

---

## 📄 许可证

[MIT License](LICENSE)

## 🔗 更多资源

- 🐙 [GitHub Issues](../../issues)
- 📚 [详细文档](config/README.md)
- 🧪 [测试代码](tests/)


├── main.py          # 主程序
├── app.py           # Web UI
├── config/          # API 配置、参数设置 → [README](config/README.md)
├── core/            # 核心控制逻辑 → [README](core/README.md)
├── creator/         # 提示词生成 → [README](creator/README.md)
├── evaluator/       # 多维度评分 → [README](evaluator/README.md)
├── integrations/    # 第三方集成 → [README](integrations/README.md)
└── evolution_history/  # 结果存档 → [README](evolution_history/README.md)
```

**详细文档**: 查看各模块文件夹中的 README.md

---

## 🔄 工作流程

```
主题输入 (enchanted forest)
    ↓
[DeepSeek] 生成初始提示词
    ↓
[SDXL Turbo] 1-step 图像生成 (4-5s)
    ↓
[评分系统] 4D 评分 (0.0-1.0)
    ↓
目标达成? → 是 → 完成 ✅
    ↓ 否
迭代 ≤ 5? → EXPLORE (创意探索)
    ↓           ├─ 颜色维度
    ↓           ├─ 光影维度
    ↓           └─ 构图维度
迭代 > 5? → OPTIMIZE (参数调优)
                ├─ HR Scale (1.0→1.8)
                └─ CFG Scale (1.0→2.0)
    ↓
连续 5 步无进展? → 早停 🛑
```

---

## 📊 性能指标

| 指标 | 值 | 说明 |
|------|-----|-----|
| **最高分** | 0.86 | 当前最佳表现 |
| **平均分** | 0.84 | 稳定收敛范围 |
| **生成速度** | 4-5s | SDXL Turbo 单步 |
| **总耗时** | 15-30 分钟 | 完整迭代周期 |
| **API 响应** | 6-7s | ModelScope 免费 API |

---

## ⚙️ 核心参数

| 参数 | 值 | 说明 |
|------|-----|-----|
| **Steps** | 1 | SDXL Turbo 固定 (不调整) |
| **CFG** | 1.0-2.0 | 提示词遵循度 (可微调) |
| **HR Scale** | 1.0-2.0 | 高清修复倍率 (渐进提升) |
| **Target Score** | 0.9 | 目标评分阈值 |
| **Max Iterations** | 30 | 最大迭代次数 |

修改参数: 编辑 `config/settings.py`

---

## 🔍 查看结果

```bash
# 查看最新生成
ls evolution_history/{主题}/​*.png

# 查看元数据
cat evolution_history/{主题}/metadata.json

# 查看最佳图像
cat evolution_history/{主题}/metadata.json | jq '.best_image'
```

详见: [evolution_history/README.md](evolution_history/README.md)

---

## 🚨 常见问题

| 问题 | 解决方案 |
|------|---------|
| API 连接失败 | 检查 `.env` 密钥和网络连接 |
| 分数卡在 0.86 | 这是系统物理极限，早停是正常行为 |
| 生成速度慢 | ModelScope API 可能拥堵，会自动切换到 SiliconFlow |
| 显存不足 | 编辑 `config/settings.py`，降低批处理大小 |

更多问题: 查看对应模块的 README.md

---

## 📚 学习路径

**新手**:
1. 阅读本文档 (5 分钟)
2. 配置 `.env` 并运行 `python main.py`
3. 查看 `evolution_history/` 中的结果

**开发者**:
1. 查看各模块 README.md 了解细节
2. 阅读 `config/settings.py` 了解可调参数
3. 研究 `core/controller.py` 了解控制逻辑

**优化者**:
1. 查看 [creator/README.md](creator/README.md) 学习提示词优化
2. 查看 [evaluator/README.md](evaluator/README.md) 理解评分机制
3. 根据需要调整 `config/settings.py` 参数

---

## 🛠️ 技术栈

- **Python**: 3.8+
- **生成模型**: SDXL Turbo (1-step)
- **提示词 AI**: DeepSeek-V3
- **评分 API**: ModelScope (免费) / SiliconFlow (付费)
- **控制算法**: DiffuServoV4 (PID + 状态机 + 智能早停)

---

## 📝 版本信息

**Current Version**: v4.0 (2026-01-29)

**核心改进**:
- ✅ SDXL Turbo 1-step 锁定 (步数不再调整)
- ✅ HR Scale 渐进优化策略 (1.0 → 1.8)
- ✅ CFG Scale 微调机制 (基于评分梯度)
- ✅ 智能早停 (连续 5 步无进展自动停止)
- ✅ 双 API 支持 (免费 + 付费自动切换)

---

**🎨 开始创作！** ✨


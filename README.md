# 🎨 Pygmalion - 智能AI创意生成系统

**Version 2.0** | 基于闭环控制的自适应图像生成代理

Pygmalion 是一个智能化的 AI 绘画代理系统，结合 **4D评分体系** 和 **双API架构**，实现物理合理性检测与成本优化的自动化创意生成。

---

## 🌟 核心特性

### 🔬 4D 评分系统 (V2.0)
- Concept — 概念匹配度
- Quality — 技术质量 (清晰度、噪点、伪影)
- Aesthetics — 美学价值 (构图、创意、艺术性)
- Reasonableness — 物理合理性 (光照、比例、重力、空间逻辑) 🆕

### 🔄 智能双API架构
- 免费优先: ModelScope API (`api-inference.modelscope.cn`)
- 自动升级: SiliconFlow API (`api.siliconflow.cn`)
- 切换条件: 平均响应 > 15s 或 连续失败 ≥ 2 次
- 成本优化: 免费为主，必要时升级付费

### 🧠 创意大脑
- DeepSeek-V3: 通用艺术透镜，生成富有想象力的提示词

### 🎯 自适应控制 (DiffuServo V4)
- 状态机: INIT → EXPLORE → OPTIMIZE → FINETUNE → CONVERGED
- 动态权重: 根据阶段调节概念/质量权重
- 智能早停: 梯度监测自动收敛

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
│   └── controller.py      # DiffuServoV4 主控
├── test_e2e.py            # 端到端测试
├── test_4d_scoring.py     # 4D评分测试
└── main.py                # 程序入口
```

---

## 🚀 快速开始

1) 安装依赖 (Python 3.8+)
```bash
pip install openai requests python-dotenv
```

2) 配置 `.env` (至少一个API密钥)
```bash
# 免费API (推荐优先)
MODELSCOPE_API_KEY=your_modelscope_key

# 付费API (可选备份)
SILICON_KEY=your_silicon_key

# DeepSeek (创意生成)
DEEPSEEK_API_KEY=your_deepseek_key
```

3) 启动 Forge (SD WebUI Forge)
```
http://127.0.0.1:7860
```

4) 运行测试
```bash
python test_e2e.py          # 端到端测试
python test_4d_scoring.py   # 4D评分测试
```

5) 开始生成
```bash
python main.py
```

---

## 📊 4D 评分细节

| 维度 | 权重 | 说明 | 约束 |
|------|------|------|------|
| Concept | 动态 | 主题匹配 | Concept < 0.5 → Final ≤ 0.6 |
| Quality | 动态 | 清晰度/噪点/伪影 | Quality < 0.6 → Final ≤ 0.7 |
| Aesthetics | 15% | 构图/创意/艺术性 | — |
| Reasonableness | 15% | 光照/比例/重力/空间 | Reasonableness < 0.6 → Final ≤ 0.75 |

**评分公式**
```python
Final = Concept×w1 + Quality×w2 + Aesthetics×0.15 + Reasonableness×0.15
# EXPLORE: w1=0.7, OPTIMIZE: w1=0.3, FINETUNE: w1=0.5
```

**物理合理性检测**
- 光照一致性 (阴影方向与光源匹配)
- 物体比例 (无夸张尺度)
- 重力与支撑 (漂浮需有解释)
- 空间相干性 (透视/深度/遮挡)
- 材质属性 (反射/透明度真实)

---

## 🔄 双API切换

- 默认使用免费API (ModelScope)
- 当 `avg_response_time > 15s` 或 `failures >= 2` 自动升级到付费API (SiliconFlow)
- 重启即可恢复免费API优先

**状态查询**
```python
from evaluator import get_api_status
print(get_api_status())
# {'current': 'ModelScope (FREE)', 'free_ready': True, 'premium_ready': True, 'fallback_enabled': False, 'avg_response_time': 6.2}
```

---

## 🧪 测试

```bash
python test_e2e.py      # 端到端全量测试
python test_4d_scoring.py  # 4D评分专项
```

**示例输出**
```
[PASS] All core tests passed
System Status:
  [OK] Module imports
  [OK] Configuration loaded
  [OK] Dual-API system ready
  [OK] Image rating working
  [OK] Logging system active
```

---

## 📁 输出

```
evolution_history/
  ├── <theme_timestamp>/
  │   ├── iter1.png
  │   ├── iter2.png
  │   └── metadata.json  # 记录每次迭代评分与参数
```

---

## ⚙️ 调优

- 目标分数 / 迭代次数: `.env` 中 `TARGET_SCORE`, `MAX_ITERATIONS`
- API阈值: `evaluator/core.py` 中 `SPEED_THRESHOLD`, `FAILURE_THRESHOLD`
- 评分权重: `rate_image()` 中调整 `aesthetics_weight`, `reasonableness_weight`

---

## 📈 性能 (实测)

- 免费API (ModelScope): 5-7 秒 (平均 6.2s)
- 付费API (SiliconFlow): 3-5 秒
- 当前策略: 免费优先，必要时自动升级付费，降低 90%+ 成本

---

## 🚨 常见问题

- **API密钥错误**: 检查 `.env` 中密钥与空格
- **免费API慢**: 超过 15s 会自动切换到付费API
- **物理合理性低**: 分数 < 0.6 会限制最终分数 (≤ 0.75)
- **强制使用付费**: 去掉 `.env` 中 `MODELSCOPE_API_KEY`

---

## 🛠️ 技术栈

- Python 3.8+
- Qwen2.5-VL-72B (评分)
- DeepSeek-V3 (创意)
- SD WebUI Forge (生成)
- OpenAI SDK (API框架)
- ModelScope + SiliconFlow (双API)

---

## 📚 资源

- ModelScope: https://modelscope.cn
- SiliconFlow: https://siliconflow.cn
- DeepSeek: https://platform.deepseek.com
- SD WebUI Forge: https://github.com/lllyasviel/stable-diffusion-webui-forge

---

## 📄 许可证

MIT License

---

**最后更新**: 2026-01-28  
**维护者**: Pygmalion Team


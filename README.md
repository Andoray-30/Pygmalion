# Pygmalion - AI 图像生成系统

基于 Stable Diffusion 的自适应多智能体协作创作系统。

---

## ✨ 核心特性

- 🎨 **自适应生成**：根据评分反馈自动调整参数
- 🔒 **参考图约束**：ControlNet + IP-Adapter 多重约束
- 🤖 **智能体协作**：创意构思 + 多模态评分 + 动态优化
- 🎯 **意图识别**："保持不变"场景自动强化约束
- ⚡ **早停机制**：收敛检测，避免无效迭代

---

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置环境
```bash
cp .env.example .env
# 编辑 .env 填入 API 密钥
```

### 3. 启动系统
```bash
# Windows
run_system.bat

# Linux/Mac
python launch.py
```

访问 `http://localhost:5000` 使用 Web UI

---

## 📋 系统要求

- Python 3.11+
- Stable Diffusion WebUI Forge
- 8GB+ VRAM（推荐 12GB+）
- API 密钥：
  - DeepSeek (创意生成)
  - ModelScope (免费评分)
  - SiliconFlow (付费评分，可选)

---

## 📖 文档导航

| 文档 | 说明 |
|------|------|
| [快速入门](QUICKSTART.md) | 5分钟上手教程 |
| [系统架构](docs/ARCHITECTURE.md) | 技术架构设计 |
| [核心包文档](pkg/README.md) | 代码模块说明 |
| [配置指南](pkg/infrastructure/config/README.md) | 环境变量配置 |

---

## 🏗️ 架构概览

```
用户交互 (Web UI)
    ↓
Flask + Socket.IO
    ↓
DiffuServoV4 引擎
    ├─ CreativeDirector (DeepSeek)
    ├─ Evaluator (多模态 VL)
    ├─ ReferenceProcessor (CLIP)
    └─ ControlNet/IP-Adapter 构建
    ↓
Forge WebUI API
    ↓
生成结果
```

---

## 💡 典型用例

### 基础生成
```python
from pkg.system import DiffuServoV4

engine = DiffuServoV4(theme="动漫女孩，粉色头发")
engine.run(target_score=0.90, max_iterations=5)
```

### 参考图约束
```python
engine = DiffuServoV4(
    theme="保持人物不变，修改姿势为抱胸",
    reference_image_path="reference.jpg"
)
engine.run(target_score=0.90, max_iterations=5)
# 自动检测"保持不变"意图并强化约束
```

---

## 🔧 常见问题

### Forge 连接失败
```bash
# 检查 Forge 是否启动
curl http://127.0.0.1:7860

# 修改 .env 配置
FORGE_URL=http://127.0.0.1:7860
```

### API 密钥无效
```bash
# 检查 .env 文件
SILICON_KEY=sk-xxx
MODELSCOPE_KEY=xxx
```

### 生成结果不理想
- 提高 `target_score` (0.85 → 0.90)
- 增加 `max_iterations` (5 → 10)
- 使用参考图约束
- 检查 Prompt 关键词

---

## 📊 性能参考

| 配置 | 平均耗时 | 显存占用 |
|------|----------|----------|
| 832×1216, 28步 | 45-60秒/张 | 8-10GB |
| 1024×1536, 28步 | 60-90秒/张 | 10-12GB |
| HR放大(1.5×) | +30-45秒 | +2-3GB |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

**开发环境：**
```bash
git clone https://github.com/yourusername/Pygmalion.git
cd Pygmalion
pip install -r requirements.txt
pytest tests/  # 运行测试
```

---

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE)

---

## 🙏 致谢

- [Stable Diffusion WebUI Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge)
- [DeepSeek API](https://platform.deepseek.com/)
- [ModelScope](https://modelscope.cn/)
- [OpenAI CLIP](https://github.com/openai/CLIP)

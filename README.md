# Pygmalion AI

智能AI图像生成系统 - 自适应Prompt优化 + 多模态风格分析

## 核心特性

- 🎨 **智能风格识别**: 参考图自动分析，推荐最佳底模（ANIME/RENDER）
- 🧠 **自适应优化**: DeepSeek-V3驱动的Prompt迭代进化
- 📊 **多维评分**: 200B+多模态模型评估（概念/质量/美学/合理性）
- 🎯 **ControlNet集成**: 姿态/构图精准控制
- 🔄 **API智能降级**: 魔搭免费(2000次/天) → 硅基付费

## 技术栈

- **生成引擎**: Stable Diffusion WebUI Forge (SDXL)
- **创意大脑**: DeepSeek-V3 (671B)
- **评分模型**: InternVL3.5-241B / Qwen3-VL-235B
- **风格分析**: 多模态VL模型
- **后端**: Python 3.10 + Flask-SocketIO
- **前端**: React + Socket.IO

## 快速开始

```powershell
# 自动安装（含模型下载~18GB）
.\setup.bat

# 启动系统
.\run_system.bat
```

访问 http://localhost:5000

详细文档: [QUICKSTART.md](QUICKSTART.md) | [架构说明](docs/ARCHITECTURE.md)

## 项目结构

```
Pygmalion/
├── pkg/
│   ├── system/          # 核心生成引擎
│   │   ├── engine.py    # DiffuServoV4控制器
│   │   ├── modules/     # 创意/评分/参考模块
│   │   └── builders/    # ControlNet/LoRA构建器
│   ├── interface/       # Web服务器
│   └── infrastructure/  # 配置/工具
├── Forge/               # SD WebUI Forge
├── tests/               # 测试套件
└── docs/                # 详细文档
```

## 环境要求

- Windows 10/11 + Python 3.10.x
- NVIDIA GPU (8GB+显存)
- API密钥: ModelScope (免费) / SiliconFlow (付费)

## 许可证

MIT License

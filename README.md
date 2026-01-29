#  Pygmalion AI

**智能自适应图像生成系统** - AI 驱动的提示词优化 + 多模型评分 + 现代化 Web UI

[![Python 3.10+](https://img.shields.io/badge/Python-3.10+-blue)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

##  快速开始

只需一行命令即可启动整个系统：
```powershell
.\run_system.bat
```
详细安装与配置指南请参阅 [QUICKSTART.md](QUICKSTART.md)

---

##  核心特性

| 特性 | 说明 |
|------|------|
|  **AI 创意引擎** | 集成 DeepSeek-V3 自动进行提示词工程与迭代优化 |
|  **多模型评分** | 472B+ 级多模态模型 (Qwen2.5-VL 等) 自动轮换评分 |
|  **对话式 UI** | 类似 Gemini 的现代化 Web 界面，支持实时反馈与交互 |
|  **WebSocket 通信** | 基于 Socket.IO 的双向低延迟实时消息推送 |
|  **最优解收敛** | 自动在多轮迭代中收敛至最佳画质与主题契合度 |
|  **全自定义配置** | 支持在 Web 界面直接配置 API 密钥、模型 ID 与自定义网关 |

---

##  项目结构 (pkg 架构)

```text
Pygmalion/
  launch.py              # 系统入口
  run_system.bat         # 一键启动脚本
  requirements.txt       # 项目依赖
  QUICKSTART.md          # 快速入门指南

  pkg/                   # 核心代码包
     interface/         # 接口层 (Web/WebSocket)
       server.py         # Flask-SocketIO 后端
        web/           # 前端资源 (HTML/CSS/JS)
   
     system/            # 系统层 (Logic/Modules)
       engine.py         # DiffuServoV4 核心控制器
        modules/       # 功能模块 (Creator/Evaluator)
   
     infrastructure/    # 基础设施层 (Config/Utils)
         config/        # 全局配置集

  evolution_history/     # 图片生成演进记录 (输出目录)
  Forge/                 # Stable Diffusion 后端集成目录
```

---

##  评分模型轮换系统

为了最大化利用免费 API 额度并保证评分精度，系统内置了模型轮换机制：

- **主力模型**: `Qwen2.5-VL-72B-Instruct`
- **轮换池**: 包括 `QVQ-72B-Preview`, `InternVL3.5`, `Qwen3-VL` 等。
- **机制**: 默认每 150 次调用自动切换模型，充分利用 ModelScope 的 2000次/天 免费额度。
- **降级**: 当 ModelScope 达到限额或不可用时，自动 Fallback 到 SiliconFlow 付费接口。

---

##  实时消息协议

系统通过 WebSocket 推送以下核心事件：
- `status_update`: 全局运行状态
- `suggestion`: DeepSeek 提供的创意优化建议
- `image_generated`: 单次迭代图片生成路径
- `evaluation`: 多维度（画质、美学、合理性等）详细评分反馈
- `score_update`: 当次迭代分数及是否破纪录的状态更新
- `completion`: 最终生成报告

---

##  后端技术栈

- **Web 框架**: Flask & Flask-SocketIO
- **核心逻辑**: Python 3.10+
- **生成引擎**: DiffuServo Architecture (集成 Stable Diffusion WebUI Forge)
- **大模型支持**: DeepSeek-V3 (创意), Qwen2.5-VL-72B (视觉评分)

---

##  更新日志

### [1.1.0] - 2026-01-29
-  **架构重构**: 迁移至 `pkg` 命名空间结构。
-  **UI 升级**: 实现 Google Material Design / Gemini 风格对话界面。
-  **设置面板**: 新增 Web 端 API 与模型自定义配置功能。
-  **反馈循环**: 修复了迭代计数与评分显示的准确性问题。

---

##  开源协议
基于 MIT 协议开源。详见 [LICENSE](LICENSE)

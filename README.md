# 🤖 Pygmalion (DiffuServo V4)

Pygmalion 是一个基于 **DiffuServo V4** 算法的自动化 AI 绘画代理。它利用闭环控制系统（Closed-Loop Control），结合 **DeepSeek (创意大脑)**、**SD WebUI Forge (绘图引擎)** 和 **Qwen (审美裁判)**，自动演化并寻找最佳的图像生成参数。

## 🌟 核心特性

- **🧠 创意大脑**: 集成 DeepSeek-V3，自动根据简短主题扩展出丰富的 SDXL 提示词。
- **⚖️ 自动审美**: 集成 Qwen2.5-VL，对生成的图像进行多维度评分（内容匹配度 + 技术画质）。
- **🔄 自适应控制**: 使用 PID 控制器思想，动态调整 Step、CFG、HighRes Fix 等参数。
- **🛑 智能早停**: 实时监测分数梯度，自动识别收敛或振荡状态，节省计算资源。
- **📂 结构化归档**: 自动按主题整理生成结果，保留最优参数配置。

## 📁 项目结构

```
Pygmalion/
│
├── config/                 # ⚙️ 配置中心
│   ├── settings.py         # 核心参数 (目标分数, 超时, 模型选择)
│   └── .env                # API Key 等敏感信息 (需自行创建)
│
├── core/                   # 🧠 核心控制器
│   ├── controller.py       # DiffuServo 状态机与主循环
│   ├── analysis.py         # 梯度计算与数据分析
│   └── health.py           # 健康检查模块
│
├── creator/                # 🎨 创意生成模块 (DeepSeek)
│   └── director.py         # Prompt 扩写与优化
│
├── evaluator/              # ⚖️ 图像评估模块 (Qwen)
│   ├── core.py             # 评分主逻辑
│   └── utils.py            # 图像处理工具
│
├── evolution_history/      # 📂 输出目录 (自动按主题分类)
├── main.py                 # 🚀 启动入口
└── requirements.txt        # 依赖列表
```

## 🚀 快速开始

1.  **环境准备**:
    确保已安装 Python 3.10+，并配置好 `Forge` 运行在 `http://127.0.0.1:7860`。

2.  **配置 API**:
    在 `config/` 目录下创建或修改 `.env` 文件，填入 SiliconFlow 的 API Key：
    ```env
    SILICON_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxx
    ```

3.  **运行**:
    ```bash
    # 默认运行 (主题: Enchanted Forest)
    python main.py
    ```

    或者修改 `main.py` 中的 `theme` 参数来更换绘画主题。

## 📊 工作流程

1.  **INIT**: 初始化参数，DeepSeek 生成创意 Prompt。
2.  **EXPLORE**: 快速探索，调整 Step 和 CFG 寻找可行域。
3.  **OPTIMIZE**: 若画质评分不足，自动开启 HighRes Fix 并微调放大倍率。
4.  **FINETUNE**: 锁定参数，微调 Seed 以寻找最佳噪点。
5.  **CONVERGED**: 达到目标分数或梯度收敛，自动结束任务。

## 📝 许可证

MIT License


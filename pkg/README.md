# Pygmalion 核心包结构

## 📦 模块组织

### `infrastructure/` - 基础设施层
配置管理、健康检查、工具函数等底层支持。

**关键文件：**
- `config/` - 环境变量、模型配置、API配置
- `health.py` - Forge WebUI 健康检查
- `utils.py` - 通用工具函数

📖 [详细文档](infrastructure/README.md)

---

### `interface/` - 接口层
Web UI 和 Socket.IO 实时通信接口。

**关键文件：**
- `server.py` - Flask + Socket.IO 服务器
- `web/` - 前端资源（HTML/JS/CSS）

📖 [详细文档](interface/README.md)

---

### `system/` - 系统核心
图像生成引擎、智能体模块、策略系统。

**关键组件：**
- `engine.py` - DiffuServoV4 自适应控制引擎
- `initializer.py` - 引擎初始化逻辑
- `builders/` - Payload 构建器（ControlNet、IP-Adapter、LoRA）
- `modules/` - 功能模块（创意生成、图像评估、参考图处理）
- `strategies/` - 优化策略（模型选择、参数调优）

📖 [详细文档](system/README.md)

---

## 🚀 快速开始

```python
from pkg.system import DiffuServoV4

# 初始化引擎
engine = DiffuServoV4(
    theme="动漫女孩，粉色头发",
    reference_image_path="path/to/reference.jpg"
)

# 运行生成
engine.run(
    target_score=0.90,
    max_iterations=5
)
```

---

## 📐 架构设计

```
用户请求
    ↓
interface (Flask + Socket.IO)
    ↓
system.engine (DiffuServoV4)
    ├─ modules.creator (创意生成)
    ├─ modules.evaluator (图像评分)
    ├─ modules.reference (参考图处理)
    ├─ builders (ControlNet/LoRA构建)
    └─ strategies (优化策略)
    ↓
Forge WebUI (图像生成)
    ↓
返回结果 → 用户
```

---

## 🔧 配置说明

所有配置位于 `.env` 文件：

```bash
# API 密钥
SILICON_KEY=sk-xxx          # 创意生成 API
MODELSCOPE_KEY=xxx          # 免费评分 API
SILICONFLOW_KEY=sk-xxx      # 付费评分 API

# Forge 配置
FORGE_URL=http://127.0.0.1:7860
FORGE_TIMEOUT=90

# 模型轮换
JUDGE_MODEL_ROTATION_ENABLED=true
JUDGE_MODEL_ROTATION_INTERVAL=150
```

📖 完整配置说明: [config/README.md](infrastructure/config/README.md)

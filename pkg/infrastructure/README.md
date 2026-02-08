# Infrastructure - 基础设施层

## 📋 概述

提供配置管理、健康检查、日志系统等底层支持功能。

---

## 📂 目录结构

```
infrastructure/
├── __init__.py
├── health.py          # Forge WebUI 健康检查
├── utils.py           # 通用工具函数（梯度计算等）
└── config/            # 配置管理
    ├── __init__.py
    ├── README.md      # 配置详细说明
    ├── base.py        # 基础配置
    ├── forge.py       # Forge API 配置
    ├── judge.py       # 评分 API 配置
    └── models.py      # 模型配置
```

---

## 🔧 核心功能

### 1. 健康检查 (`health.py`)

```python
from pkg.infrastructure.health import check_forge_health

# 检查 Forge WebUI 是否可用
if check_forge_health():
    print("✅ Forge 就绪")
```

**功能：**
- 定期心跳检测（默认每5次迭代）
- 超时控制（15秒）
- 自动重试机制

---

### 2. 工具函数 (`utils.py`)

```python
from pkg.infrastructure.utils import compute_gradient

# 计算评分梯度（用于自适应调参）
gradient = compute_gradient(score_buffer)
```

**功能：**
- 评分梯度计算（PID 控制）
- 数据归一化
- 数学工具函数

---

### 3. 配置管理 (`config/`)

📖 [详细配置文档](config/README.md)

**核心配置模块：**

| 模块 | 说明 |
|------|------|
| `base.py` | 全局基础配置（日志、超时、收敛条件） |
| `forge.py` | Forge WebUI 连接配置 |
| `judge.py` | 评分 API 配置（ModelScope/SiliconFlow） |
| `models.py` | 底模配置（PREVIEW/ANIME/RENDER） |

---

## 🌐 环境变量

`.env` 文件示例：

```bash
# API 密钥
SILICON_KEY=sk-xxx
MODELSCOPE_KEY=xxx
SILICONFLOW_KEY=sk-xxx

# Forge 配置
FORGE_URL=http://127.0.0.1:7860
FORGE_TIMEOUT=90

# 日志
LOG_LEVEL=INFO
LOG_FILE=pygmalion.log

# 收敛条件
CONVERGENCE_PATIENCE=3
CONVERGENCE_THRESHOLD=0.005
```

---

## 📊 配置热加载

评分 API 支持运行时重新加载：

```python
from pkg.system.modules.evaluator import api_manager

api_manager.reload_config()  # 重新读取 .env
```

---

## 🔍 调试建议

### 查看当前配置
```python
from pkg.infrastructure.config import *

print(f"Forge URL: {FORGE_URL}")
print(f"Target Score: {TARGET_SCORE}")
print(f"Judge Models: {JUDGE_MODELS}")
```

### 日志级别控制
```bash
# .env
LOG_LEVEL=DEBUG  # 详细日志
LOG_LEVEL=INFO   # 标准日志（推荐）
LOG_LEVEL=WARNING # 仅警告
```

---

## ⚠️ 常见问题

### 1. Forge 连接失败
```python
RuntimeError: Forge 不可用，请检查 http://127.0.0.1:7860
```
**解决：**
- 检查 Forge WebUI 是否启动
- 验证 `FORGE_URL` 配置
- 防火墙是否阻止端口

### 2. API 密钥无效
```python
401 Unauthorized
```
**解决：**
- 检查 `.env` 文件中的密钥
- 确认密钥未过期
- 重启服务以重新加载配置

# 📚 Pygmalion 文档中心

完整的技术文档和开发指南。

---

## 🗺️ 文档导航

### 📖 入门文档
| 文档 | 说明 |
|------|------|
| [README](../README.md) | 项目概览和特性介绍 |
| [快速入门](../QUICKSTART.md) | 5分钟上手教程 |

---

### 🏗️ 核心文档
| 文档 | 说明 |
|------|------|
| [系统架构](ARCHITECTURE.md) | 完整技术架构设计 |
| [核心包文档](../pkg/README.md) | 代码模块组织说明 |

---

### 🔧 配置文档
| 文档 | 说明 |
|------|------|
| [配置系统](../pkg/infrastructure/config/README.md) | 环境变量和参数配置 |
| [Forge 集成](../pkg/system/adapters/README.md) | Forge API 适配器 |

---

### 🧩 模块文档
| 文档 | 说明 |
|------|------|
| [系统核心](../pkg/system/README.md) | DiffuServoV4 引擎和智能体 |
| [创意生成](../pkg/system/modules/creator/README.md) | DeepSeek 驱动的 Prompt 生成 |
| [图像评分](../pkg/system/modules/evaluator/README.md) | 多模态评分和模型轮换 |
| [接口层](../pkg/interface/README.md) | Web UI 和 Socket.IO |

---

### 🧪 开发文档
| 文档 | 说明 |
|------|------|
| [测试指南](../tests/README.md) | 单元测试和集成测试 |

---

## 🔍 按功能查找

### 我想了解...

**生成流程**
→ [系统架构](ARCHITECTURE.md) > 工作流程章节

**参考图约束**
→ [系统核心](../pkg/system/README.md) > 参考图处理

**评分机制**
→ [图像评分](../pkg/system/modules/evaluator/README.md) > 五维评分

**模型选择**
→ [创意生成](../pkg/system/modules/creator/README.md) > 意图分析

**API 配置**
→ [配置系统](../pkg/infrastructure/config/README.md) > 环境变量

---

## 🛠️ 常用命令速查

### 启动服务
```bash
python launch.py              # 启动 Pygmalion
cd Forge/webui && webui.bat   # 启动 Forge
```

### 测试
```bash
pytest tests/                 # 运行所有测试
python test_optimization.py   # 运行优化测试
```

### 配置
```bash
cp .env.example .env          # 复制配置模板
nano .env                     # 编辑配置
```

---

## 📊 性能优化指南

### 提升生成速度
1. 降低分辨率（832×1216 → 768×1024）
2. 减少步数（28 → 20）
3. 使用 PREVIEW 模型（1步快速预览）

### 提升生成质量
1. 提高目标评分（0.85 → 0.90）
2. 增加迭代次数（5 → 10）
3. 使用参考图约束
4. 启用 HR 放大（自动触发）

---

## ⚠️ 故障排查

### 常见错误
| 错误 | 文档链接 |
|------|----------|
| Forge 连接失败 | [接口层文档](../pkg/interface/README.md#常见问题) |
| API 密钥无效 | [配置系统](../pkg/infrastructure/config/README.md#环境变量) |
| 模型错误切换 | [系统核心](../pkg/system/README.md#常见问题) |
| 显存不足 | [系统架构](ARCHITECTURE.md#性能优化) |

---

## 🤝 贡献文档

文档改进建议？欢迎提交 Pull Request！

**文档规范：**
- 使用 Markdown 格式
- 代码示例需包含完整上下文
- 添加目录和跳转链接
- 保持简洁清晰

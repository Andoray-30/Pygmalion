# Changelog - Pygmalion (DiffuServo V4)

## [v1.0.0] - 2026-01-27

### ✨ Major Refactoring

#### 代码模块化重构
- **已拆分**: 将单一 monolithic 文件重构为模块化架构
- **config/** - 配置管理中心
  - `settings.py`: 集中管理所有环境变量与参数（FORGE_URL、模型选择、超时设置等）
  - 支持 `.env` 文件覆盖，便于不同环境配置

- **core/** - 核心控制器
  - `controller.py`: DiffuServo V4 主类，包含状态机与自适应控制逻辑
  - `analysis.py`: 梯度计算与数据分析工具
  - `health.py`: Forge 健康检查模块

- **creator/** - 创意生成模块（DeepSeek）
  - `director.py`: CreativeDirector 类，负责 Prompt 扩写与优化

- **evaluator/** - 图像评估模块（Qwen）
  - `core.py`: 核心评分逻辑与重试机制
  - `utils.py`: 图像编码与 JSON 解析工具

#### 功能改进
- **动态主题支持**: DiffuServoV4 初始化时支持自定义主题参数
- **智能存储路径**: 生成的图片自动按主题分类存储
  - 目录结构：`evolution_history/{主题}/`
  - 文件命名：`{主题}_{年月日}_{时分秒}_iter{迭代数}.png`
  - 防止跨主题运行时的文件冲突

- **评分失败防护**: 在梯度缓冲区中加入无效分数检查
  - 防止 `-1.0` 分数污染收敛判断
  - 跳过无效分数并保持缓冲区完整性

- **Bug 修复**: 修复原代码中 `score_buffer` 在每轮迭代中被追加两次的逻辑错误
  - 梯度计算现在更准确

### 🧹 清理工作
- **删除**: 移除旧的测试脚本 (`Test_Pygmalion.py`)
- **删除**: 移除过时的审计报告 (`CODE_AUDIT.md`)
- **删除**: 清理生成历史中的所有旧图片
- **更新**: 精简并重写 `README.md`，突出核心特性和快速入门

### 📊 架构优势
- **可维护性**: 每个模块职责明确，便于独立测试与修改
- **可扩展性**: 易于添加新的评估器、创意生成器或控制算法
- **可读性**: 代码组织清晰，注释充分
- **配置灵活**: 集中式配置管理，环境变量覆盖支持

### 🚀 使用说明
```bash
# 默认运行（主题：Enchanted Forest）
python main.py

# 自定义主题运行（在 main.py 中修改 theme 参数）
```

---

## 技术栈
- **Stable Diffusion**: Forge WebUI (SD生成引擎)
- **LLM 模型**: 
  - DeepSeek-V3 (创意 Prompt 扩写)
  - Qwen2.5-VL (多模态图像评分)
- **API 提供商**: SiliconFlow
- **控制算法**: DiffuServo V4 (PID 自适应控制 + 智能早停)

---

**维护者**: Andoray-30  
**许可证**: MIT

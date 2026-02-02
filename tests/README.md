# Pygmalion 测试套件

**创建日期**: 2026-02-01  
**版本**: 1.0  
**状态**: ✅ 已完成

---

## 📋 概述

Pygmalion测试套件包含5个核心测试任务，用于验证系统的所有主要功能。测试按照任务优先级从高到低排列，确保核心功能首先得到验证。

---

## 🎯 测试任务列表

### 任务1: Forge服务器健康检查 ⭐ 立即执行
**文件**: `test_01_forge_health.py`

**测试内容**:
- Forge连接测试
- API端点验证
- 模型加载检查
- ControlNet模型检查

**运行时间**: 约1分钟

**重要性**: 🔴 高优先级（阻塞项）- 必须通过才能继续后续测试

---

### 任务2: Engine基础生成测试
**文件**: `test_02_engine_basic.py`

**测试内容**:
- CreativeDirector功能测试
- 模型智能选择测试
- Engine初始化测试
- 单次图片生成测试
- 评分功能测试
- 完整迭代运行测试（3次）

**运行时间**: 约5-10分钟

**重要性**: 🔴 高优先级

---

### 任务3: 参考图CLIP融合验证
**文件**: `test_03_reference_clip.py`

**测试内容**:
- ReferencePromptFusion初始化测试
- CLIP标签提取测试
- Prompt融合测试
- 参考图分解日志测试
- Engine参考图集成测试

**运行时间**: 约3-5分钟

**重要性**: 🔴 高优先级（核心功能）

---

### 任务4: ControlNet约束验证
**文件**: `test_04_controlnet.py`

**测试内容**:
- ControlNetBuilder初始化测试
- Canny ControlNet配置生成测试
- OpenPose ControlNet配置生成测试
- ControlNet参数注入测试
- Engine ControlNet集成测试

**运行时间**: 约5-10分钟

**重要性**: 🔴 高优先级（新增功能）

---

### 任务5: 构图评分算法验证
**文件**: `test_05_composition_scoring.py`

**测试内容**:
- ReferenceImageMatcher初始化测试
- 布局网格分析测试
- 梯度方向直方图分析测试
- 自适应Canny边缘检测分析测试
- 三种算法融合测试
- 算法权重配置测试
- 评分范围验证测试

**运行时间**: 约3-5分钟

**重要性**: 🔴 高优先级（核心算法）

---

## 🚀 快速开始

### 方式1: 运行所有测试（推荐）

```powershell
# 终端1: 启动Forge服务器
cd F:\Cyber-Companion\Pygmalion\Forge
python launch.py

# 等待Forge启动完成，看到以下输出：
# Running on local URL:  http://127.0.0.1:7860
# Model loaded in X.XXs

# 终端2: 运行所有测试
cd F:\Cyber-Companion\Pygmalion
python tests/run_all_tests.py
```

### 方式2: 单独运行每个测试

```powershell
# 终端1: 启动Forge服务器
cd F:\Cyber-Companion\Pygmalion\Forge
python launch.py

# 终端2: 逐个运行测试
cd F:\Cyber-Companion\Pygmalion
python tests/test_01_forge_health.py
python tests/test_02_engine_basic.py
python tests/test_03_reference_clip.py
python tests/test_04_controlnet.py
python tests/test_05_composition_scoring.py
```

---

## 📊 测试文件结构

```
tests/
├── test_01_forge_health.py              # Forge健康检查
├── test_02_engine_basic.py              # Engine基础功能
├── test_03_reference_clip.py            # 参考图CLIP融合
├── test_04_controlnet.py                # ControlNet约束
├── test_05_composition_scoring.py       # 构图评分算法
├── run_all_tests.py                     # 统一测试脚本
├── TEST_REPORT.md                       # 测试报告
├── README.md                            # 本文件
└── test_images/
    ├── reference.jpg                    # 参考图
    └── generated.jpg                    # 生成图
```

---

## 🔍 测试依赖

### 必需依赖
1. **Forge服务器运行中**
   - URL: http://127.0.0.1:7860
   - API: /sdapi/v1/*
   
2. **Python环境**
   - Python 3.10+
   - 所有项目依赖包已安装

3. **测试图像**
   - `tests/test_images/reference.jpg` - 参考图
   - `tests/test_images/generated.jpg` - 生成图（可选）

### 可选依赖
1. **GPU显存**: 建议8GB+
2. **网络连接**: 用于API调用（评分模型）

---

## 📈 预期测试时间

| 任务 | 预计时间 |
|------|---------|
| 任务1: Forge健康检查 | 1分钟 |
| 任务2: Engine基础测试 | 5-10分钟 |
| 任务3: 参考图CLIP融合 | 3-5分钟 |
| 任务4: ControlNet验证 | 5-10分钟 |
| 任务5: 构图评分算法 | 3-5分钟 |
| **总计** | **约20-35分钟** |

---

## ✅ 测试通过标准

### 任务1通过标准
- ✅ Forge服务器运行正常
- ✅ API端点可用
- ✅ 至少3个核心模型加载成功

### 任务2通过标准
- ✅ CreativeDirector初始化成功
- ✅ 模型智能选择准确
- ✅ Engine初始化成功
- ✅ 单次图片生成成功
- ✅ 评分功能正常
- ✅ 完整迭代运行成功

### 任务3通过标准
- ✅ ReferencePromptFusion初始化成功
- ✅ CLIP标签提取成功
- ✅ Prompt融合成功
- ✅ 参考图分解日志正常
- ✅ Engine参考图集成成功

### 任务4通过标准
- ✅ ControlNetBuilder初始化成功
- ✅ Canny配置生成成功
- ✅ ControlNet参数注入成功
- ✅ Engine ControlNet集成成功

### 任务5通过标准
- ✅ ReferenceImageMatcher初始化成功
- ✅ 布局网格分析正常
- ✅ 梯度直方图分析正常
- ✅ 自适应Canny分析正常
- ✅ 三种算法融合正常
- ✅ 评分范围验证通过

---

## 🐛 常见问题

### 问题1: Forge连接失败
**错误**: `❌ 无法连接到Forge服务器`

**解决方案**:
1. 确认Forge服务器正在运行
2. 检查端口7860是否被占用
3. 查看Forge启动日志

### 问题2: 图片生成失败
**错误**: `❌ 图片生成失败`

**解决方案**:
1. 检查API端点URL是否正确
2. 确认模型已加载
3. 检查显存是否充足

### 问题3: 评分失败
**错误**: `❌ 评分失败`

**解决方案**:
1. 检查API Key配置
2. 确认评分模型可用
3. 检查网络连接

### 问题4: 参考图文件不存在
**错误**: `⚠️  参考图不存在`

**解决方案**:
1. 确认测试图像文件存在
2. 检查文件路径是否正确
3. 重新下载测试图像

---

## 📝 测试报告

测试运行完成后，详细的测试结果将保存在 `tests/TEST_REPORT.md` 中，包含：
- 每个任务的测试结果
- 失败原因分析
- 解决方案建议
- 测试通过率统计

---

## 🎯 下一步

### 测试全部通过后
1. ✅ 系统可以正常使用
2. 📝 查看生成的测试图片
3. 🎨 开始使用Pygmalion进行创作
4. 📚 阅读用户文档了解更多功能

### 部分测试失败
1. 🔍 查看TEST_REPORT.md中的详细错误信息
2. 🔧 根据故障排查指南解决问题
3. 🔄 重新运行失败的测试
4. 💬 如问题持续，联系技术支持

---

## 📞 技术支持

如有问题或建议，请：
- 查看项目文档: `docs/`
- 查看架构文档: `ARCHITECTURE.md`
- 查看快速开始: `QUICKSTART.md`

---

**测试套件版本**: 1.0  
**最后更新**: 2026-02-01  
**维护者**: Pygmalion Team
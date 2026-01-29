#  Pygmalion AI 快速入门指南

本文档将引导您在 5 分钟内完成 Pygmalion AI 系统的安装与启动。

---

##  环境要求

- **操作系统**: Windows 10/11 (推荐)
- **Python**: 3.10.x (必须)
- **GPU**: NVIDIA 显卡 (建议 8GB+ 显存以运行 Forge 后端)
- **网络**: 能够访问 ModelScope / SiliconFlow API

---

##  安装步骤

### 1. 克隆与环境准备
```powershell
git clone <repository_url>
cd Pygmalion
```

### 2. 初始化环境
运行 `run_system.bat`，它会自动检测并建议环境。如果您是首次使用，建议手动创建虚拟环境：
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 3. 配置 API 密钥
复制模板文件：
```powershell
copy .env.example .env
```
用编辑器打开 `.env`，填入您的密钥（或者启动后在网页设置中填入）：
- `MODELSCOPE_API_KEY`: 魔搭 API 密钥（用于免费评分）
- `SILICON_KEY`: 硅基流动 API 密钥（用于 DeepSeek 和付费备用评分）

---

##  一键启动

在项目根目录下双击运行：
```powershell
.\run_system.bat
```
该脚本会自动完成以下操作：
1. 清理残留进程。
2. 清理 Python 编译缓存。
3. 启动 **Forge 后端** (端口 7860)。
4. 启动 **Pygmalion Web 服务** (端口 5000)。
5. 自动在浏览器打开界面。

---

##  使用流程

1. **进入界面**: 访问 `http://localhost:5000`。
2. **基础配置**: 
   - 在左侧面板设置 **目标分数** (推荐 0.85)。
   - 设置 **最大迭代次数** (推荐 5-10)。
3. **输入需求**: 
   - 在底部输入框输入主题，例如：`赛博朋克风格的猫娘在霓虹雨夜，精致细节，8k画质`。
4. **观看演进**:
   - 系统会首先调用 DeepSeek 优化提示词。
   - 随后进入迭代：生成图片 -> 模型评分 -> 提出改进建议 -> 再次生成。
5. **获取结果**:
   - 最优结果会实时更新在右侧。
   - 所有的生成路径都会保存在 `evolution_history/` 文件夹下。

---

##  进阶：配置自定义 API

如果您想使用其他服务（如 OpenAI 或本地 Ollama）：
1. 点击导航栏右上角的 **设置**。
2. 在弹出框中修改 **API URL** 与 **模型 ID**。
3. 点击保存，系统将立即应用配置。

---

##  常见问题

- **网页打不开？**: 检查 `Pygmalion Web` 终端窗口是否有报错，确保端口 5000 未被占用。
- **图片一直生成中？**: 确保 Forge 后端已成功完成 `Model loaded`。
- **评分失败？**: 请检查 API 密钥是否正确，或网络是否通畅。

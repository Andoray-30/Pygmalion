#  Pygmalion AI 快速入门指南

本文档将引导您在 5 分钟内完成 Pygmalion AI 系统的安装与启动。

---

##  环境要求

- **操作系统**: Windows 10/11 (推荐)
- **Python**: 3.10.x (必须)
- **显卡需求**: NVIDIA 显卡 (建议 8GB+ 显存)
- **后端依赖**: [Stable Diffusion WebUI Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge) (必须)
- **网络**: 能够访问相关大模型 API (ModelScope / SiliconFlow)

---

##  关于 Forge 后端

本系统依赖 Forge 作为图像生成引擎。您有两种方式配置它：

### 方案 A：集成模式（推荐）
1. 在项目根目录下通过 Git 克隆或解压 Forge：
   ```powershell
   git clone https://github.com/lllyasviel/stable-diffusion-webui-forge Forge
   ```
2. 确保 `Forge/run.bat` 存在。
3. 这样使用 `run_system.bat` 时，系统会自动帮您开启后端。

### 方案 B：独立/远程模式
1. 如果您已经在其他盘符或远程服务器运行了 Forge。
2. 启动该服务，并确保开启了 `--api` 参数。
3. 在 Pygmalion 的 **设置面板** 中，将 **Forge URL** 修改为该服务的地址（如 `http://192.168.1.10:7860`）。

---

##  安装步骤

### 1. 自动化安装 (推荐)
如果您是首次使用，只需双击运行项目根目录下的：
```powershell
.\setup.bat
```
该脚本会自动：
- 创建 Python 虚拟环境。
- 安装所有依赖库。
- 克隆 Forge 后端（如果不存在）。
- **自动从 HuggingFace 下载 3 个必备底模** (约 18GB，请确保空间充足)。

### 2. 手动安装 (如果自动下载失败)
如果您网络环境特殊，建议手动准备：
1. **环境**: `python -m venv venv` -> `.\venv\Scripts\activate` -> `pip install -r requirements.txt`。
2. **Forge**: 在根目录运行 `git clone https://github.com/lllyasviel/stable-diffusion-webui-forge Forge`。
3. **底模**: 将以下模型下载并放入 `Forge/models/Stable-diffusion/` 文件夹：
   - `sd_xl_turbo_1.0_fp16.safetensors`
   - `juggernautXL_ragnarokBy.safetensors`
   - `animagineXLV31_v31.safetensors`

### 3. 配置 API 密钥
推荐直接在启动后的 **Web 界面 -> 设置 ()** 中填入：
- `SILICON_KEY`: 核心 API 密钥 (用于创意大脑)
- `EVAL_A_API_KEY`: 评分服务 A 的密钥
- `EVAL_B_API_KEY`: 评分服务 B 的密钥

---

##  一键启动

在项目根目录下双击运行：
```powershell
.\run_system.bat
```
该脚本会自动完成所有启动操作并打开浏览器界面。

---

##  使用流程
1. **进入界面**: 访问 `http://localhost:5000`。
2. **输入需求**: 在底部输入框输入主题并点击发送。
3. **观看演进**: 系统会实时展示提示词优化逻辑与图片迭代效果。

---

##  进阶：配置自定义 API
点击导航栏右上角的 **设置 ()** 即可修改所有后端服务地址、模型 ID 及密钥。

---

##  常见问题
- **底模下载慢？**: 请开启代理或手动在 HF 下载对应模型至 `Forge/models/Stable-diffusion/`。
- **内存溢出？**: 检查显存是否达到 8GB，或关闭其他占用显存的软件。

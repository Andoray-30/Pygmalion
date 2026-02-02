# Pygmalion AI 快速入门

5分钟完成系统安装启动。

## 环境要求

- Windows 10/11 + Python 3.10.x
- NVIDIA显卡 (8GB+显存推荐)
- [Stable Diffusion WebUI Forge](https://github.com/lllyasviel/stable-diffusion-webui-forge)
- 网络: 访问 ModelScope / SiliconFlow API

## Forge后端配置

### 方案A：集成模式（推荐）
```powershell
git clone https://github.com/lllyasviel/stable-diffusion-webui-forge Forge
```
确保 `Forge/run.bat` 存在，`run_system.bat` 会自动启动。

### 方案B：独立模式
已有Forge服务，在Web界面设置中修改Forge URL。

## 安装

### 自动安装（推荐）
```powershell
.\setup.bat
```
自动完成：虚拟环境、依赖、Forge克隆、模型下载(~18GB)。

### 手动安装
1. 环境: `python -m venv venv` → `.\venv\Scripts\activate` → `pip install -r requirements.txt`
2. Forge: `git clone https://github.com/lllyasviel/stable-diffusion-webui-forge Forge`
3. 模型: 下载放入 `Forge/models/Stable-diffusion/`:
   - `sd_xl_turbo_1.0_fp16.safetensors`
   - `juggernautXL_ragnarokBy.safetensors`
   - `animagineXLV31_v31.safetensors`

### API密钥
启动后在Web界面设置：
- `MODELSCOPE_API_KEY`: 魔搭免费API (优先)
- `SILICON_KEY`: 硅基付费API (降级)

## 启动

```powershell
.\run_system.bat
```
自动打开 `http://localhost:5000`

## 使用

1. 输入主题
2. 可选：上传参考图（自动识别风格）
3. 观看实时迭代优化

详细文档: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

---

##  进阶：配置自定义 API
点击导航栏右上角的 **设置 ()** 即可修改所有后端服务地址、模型 ID 及密钥。

---

##  常见问题
- **底模下载慢？**: 请开启代理或手动在 HF 下载对应模型至 `Forge/models/Stable-diffusion/`。
- **内存溢出？**: 检查显存是否达到 8GB，或关闭其他占用显存的软件。

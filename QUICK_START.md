# ⚡ 快速开始 (5 分钟)

## 🔧 环境准备

```bash
# 1. 克隆项目
git clone https://github.com/your-username/Pygmalion.git
cd Pygmalion

# 2. 创建虚拟环境
python -m venv venv

# 3. 激活虚拟环境
# Windows:
.\venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 4. 安装依赖
pip install -r requirements.txt
```

## 🔑 API 配置

```bash
# 复制配置文件
cp .env.example .env

# 编辑 .env 填入你的 API 密钥
# 必需: DEEPSEEK_API_KEY
# 可选: MODELSCOPE_API_KEY, SILICONFLOW_API_KEY
```

## 🚀 启动应用

```bash
# Web UI 模式 (推荐)
python webui/app.py

# 访问 http://localhost:7861
```

## 📝 使用步骤

1. **输入主题** - 例: `enchanted forest`
2. **设置参数** - 目标分数 (0.7-0.95), 最大迭代 (5-30)
3. **开始生成** - 点击 **开始生成** 按钮
4. **实时监看** - 每个迭代立即显示结果
5. **查看历史** - 切换到 **会话恢复** 标签页

---

📖 详见 [README.md](README.md) | 🔗 [GitHub](https://github.com) | ❓ [FAQ](docs/FAQ.md)

# Pygmalion 快速入门

5分钟完成首次生成！

---

## 🔧 步骤 1：安装依赖

```bash
# 克隆项目
git clone https://github.com/yourusername/Pygmalion.git
cd Pygmalion

# 安装依赖（推荐使用虚拟环境）
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

pip install -r requirements.txt
```

---

## 🔑 步骤 2：配置 API 密钥

### 2.1 复制配置模板
```bash
cp .env.example .env
```

### 2.2 编辑 `.env` 文件
```bash
# 必需：创意生成 API
SILICON_KEY=sk-xxxxxxxxxxxxxxxx  # DeepSeek API Key

# 必需：免费评分 API（2000次/天）
MODELSCOPE_KEY=xxxxxxxx  # ModelScope API Key

# 可选：付费评分 API（备用）
SILICONFLOW_KEY=sk-xxxxxxxx
```

**获取密钥：**
- DeepSeek: https://platform.deepseek.com/
- ModelScope: https://modelscope.cn/my/myaccesstoken

---

## 🎨 步骤 3：启动 Forge WebUI

Pygmalion 需要 Forge 作为图像生成后端。

### 3.1 如果已安装 Forge
```bash
cd Forge/webui
./webui.bat  # Windows
# 或
./webui.sh   # Linux/Mac
```

### 3.2 如果未安装 Forge
```bash
# Windows
cd Forge
setup.bat  # 一键安装

# Linux/Mac
git clone https://github.com/lllyasviel/stable-diffusion-webui-forge.git
cd stable-diffusion-webui-forge
./webui.sh
```

**验证 Forge 是否启动：**
访问 `http://127.0.0.1:7860`，应该能看到 Forge 界面。

---

## 🚀 步骤 4：启动 Pygmalion

```bash
# Windows
run_system.bat

# Linux/Mac
python launch.py
```

**成功启动后会看到：**
```
🚀 Pygmalion System Launching...
 * Running on http://127.0.0.1:5000
 * Running on http://10.x.x.x:5000
```

---

## 🖥️ 步骤 5：使用 Web UI

### 5.1 打开浏览器
访问 `http://localhost:5000`

### 5.2 设置参数
- **生成主题**: `动漫女孩，粉色头发，可爱笑容`
- **目标评分**: `0.85`（默认）
- **最大迭代**: `5`（默认）

### 5.3 （可选）上传参考图
- 点击 🖼️ 图标上传参考图
- 系统会自动识别风格并应用约束

### 5.4 开始生成
点击 **"🚀 开始生成"** 按钮

---

## 📊 步骤 6：查看实时进度

生成过程中会实时显示：
- 当前迭代次数
- 评分（概念/质量/美学/合理性）
- 生成图片预览
- 最佳结果

**典型耗时：** 45-60秒/张（832×1216, 28步）

---

## 📁 步骤 7：查看结果

生成完成后，图片保存在：
```
evolution_history/
└── project_name_timestamp/
    ├── project_iter1.png  # 第1次迭代
    ├── project_iter2.png  # 第2次迭代
    └── ...
```

**最佳结果** 会在 Web UI 中高亮显示。

---

## 🎯 进阶用法

### 使用参考图约束
```
主题：保持人物主体不变，衣服不变，修改姿势为抱胸
参考图：上传原始角色图片
```

系统会自动：
- 识别参考图风格（动漫/写实/3D）
- 锁定对应模型（ANIME/RENDER）
- 应用 ControlNet + IP-Adapter 约束
- 检测"保持不变"意图并强化权重

### 调整生成质量
```bash
# 提高质量（但耗时更长）
目标评分: 0.90 → 0.95
最大迭代: 5 → 10

# 快速预览（降低质量）
目标评分: 0.85 → 0.80
最大迭代: 5 → 3
```

---

## ❓ 常见问题

### Q1: Forge 连接失败
**错误信息：** `RuntimeError: Forge 不可用`

**解决：**
1. 检查 Forge 是否启动：`curl http://127.0.0.1:7860`
2. 检查 `.env` 配置：`FORGE_URL=http://127.0.0.1:7860`
3. 重启 Forge WebUI

---

### Q2: API 密钥无效
**错误信息：** `401 Unauthorized`

**解决：**
1. 检查 `.env` 文件中的密钥是否正确
2. 确认密钥未过期
3. 重启 Pygmalion 服务（重新加载配置）

---

### Q3: 生成速度慢
**原因：** 显存不足或步数过多

**优化：**
1. 降低分辨率：`832×1216` → `768×1024`
2. 减少步数：`28` → `20`
3. 关闭 HR 放大（在高分时自动启用）
4. 升级显卡（推荐 12GB+ VRAM）

---

### Q4: 角色一致性差
**问题：** 生成结果与参考图差异大

**解决：**
1. 确保主题包含"保持不变"关键词
2. 上传高质量参考图（>512px）
3. 提高目标评分（0.85 → 0.90）
4. 增加迭代次数（5 → 10）

---

## 📚 下一步

- 📖 阅读 [系统架构文档](docs/ARCHITECTURE.md)
- 🔧 学习 [高级配置](pkg/infrastructure/config/README.md)
- 🧪 运行 [测试脚本](tests/README.md)
- 🤝 参与 [开发贡献](README.md#贡献指南)

# Pygmalion AI - Web UI 使用指南

> 🌐 现代化的 Google 风格对话式 AI 图片生成界面

## 📋 功能特性

✨ **对话式界面** - 像微信群组一样，Deepseek、生成器、评分模型轮流发话
🎨 **实时生成** - WebSocket 实时显示生成过程和评分
📊 **多模型评分** - 自动评分和排名
🔄 **智能迭代** - 自动达到目标分数后停止
🌍 **Google 设计** - 简洁、专业、现代化的用户界面

## 🚀 快速开始

### 前置条件
- Python 3.8+
- pip 包管理器
- 已配置根目录 .env 文件

### 安装步骤

1. **在项目根目录安装依赖**
```bash
# 在 Pygmalion/ 目录下
pip install -r requirements.txt
```

2. **启动服务**

进入 web 目录并选择后端版本：

**方案 A: Flask-SocketIO 版本（推荐）**
```bash
cd web
python app_socketio.py
```
- ✅ 支持 WebSocket 实时双向通信
- ✅ 性能更好，延迟更低
- ✅ 现代化的事件驱动架构

**方案 B: 基础 Flask 版本**
```bash
cd web
python app.py
```
- 👍 轻量级，依赖较少
- 🔄 支持 Server-Sent Events (SSE) 流式传输
- 💡 适合无法使用 WebSocket 的网络环境

3. **访问界面**
```
🌐 打开浏览器访问: http://localhost:5000
```

## 🎯 使用流程

### 第一步：设置参数

左侧参数面板设置：

| 参数 | 默认值 | 说明 |
|------|--------|------|
| **生成主题** | - | 描述想要生成的内容 |
| **目标分数** | 0.8 | 0.0-1.0，满足此分数时停止 |
| **最大迭代数** | 5 | 最多生成的次数 |
| **快速模式** | OFF | 启用时跳过复杂评分 |

### 第二步：启动生成

点击 **🚀 开始生成** 按钮，系统将：

1. 📝 启动会话，生成会话 ID
2. 🧠 Deepseek 生成创意建议
3. 🎨 生成器创建图片
4. 📊 评分模型打分
5. 🔄 根据分数继续迭代，直到达到目标或最大次数

### 第三步：查看结果

**中间对话区** 显示：
- 各个 AI 的消息气泡（带不同表情符号）
- 生成过程的实时更新
- 评分结果

**右侧结果面板** 显示：
- 🏆 最优分数
- 📈 进度条
- 🖼️ 最优图片预览
- 📸 前 9 张排名图片缩略图

## 💻 系统架构

### 前端 (Frontend)
- **框架**: Vanilla JavaScript (无框架，轻量级)
- **通信**: WebSocket (Socket.IO) 或 SSE
- **样式**: CSS3 Grid + Flexbox (响应式设计)
- **文件**:
  - `templates/index.html` - 页面结构
  - `static/style.css` - 样式表
  - `static/app.js` - 业务逻辑

### 后端 (Backend)
- **框架**: Flask + Flask-SocketIO
- **通信协议**: WebSocket (Socket.IO)
- **文件**:
  - `app_socketio.py` - SocketIO 后端（推荐）
  - `app.py` - 基础 Flask 后端

### 核心集成
- **评分模型**: 自动从 `config/settings.py` 加载
- **生成器**: 集成 Stable Diffusion Forge
- **AI 建议**: 集成 Deepseek API

## 📡 WebSocket 事件

### 客户端发送事件

```javascript
// 启动生成
socket.emit('start_generation', {
    theme: '需要生成的主题',
    target_score: 0.8,          // 0.0-1.0
    max_iterations: 5,          // 最大次数
    quick_mode: false           // 快速模式
});

// 发送自定义消息（可选）
socket.emit('custom_message', {
    content: '消息内容'
});
```

### 服务器发送事件

```javascript
// 会话创建
socket.on('session_created', (data) => {
    // data.session_id - 会话 ID
});

// Deepseek 建议
socket.on('suggestion', (data) => {
    // data.sender - 发送者
    // data.message - 建议内容
});

// 迭代开始
socket.on('iteration_start', (data) => {
    // data.iteration - 当前迭代编号
    // data.total - 总迭代数
});

// 评分更新
socket.on('evaluation', (data) => {
    // data.sender - 评分模型名称
    // data.message - 评分信息
    // data.score - 分数
});

// 分数更新
socket.on('score_update', (data) => {
    // data.score - 最新分数
    // data.image_path - 图片路径
    // data.is_best - 是否为最优
});

// 生成完成
socket.on('completion', (data) => {
    // data.best_score - 最优分数
    // data.best_image - 最优图片路径
    // data.total_iterations - 总迭代数
    // data.total_images - 总图片数
});

// 错误
socket.on('error', (data) => {
    // data.message - 错误消息
});
```

## 🔧 配置文件

### settings.py
系统从 `config/settings.py` 读取：
## 🔧 配置文件

### settings.py
系统从 `config/settings.py` 读取：
- 评分模型列表
- 模型轮换设置
- API 端点

### 环境变量
所有配置统一在**根目录 .env 文件**中管理：
```bash
# 在项目根目录（不是 web/ 目录）
# 参考 .env.example 配置
DEEPSEEK_API_KEY=your-key
MODELSCOPE_API_KEY=your-key
PORT=5000
DEBUG=True
```

## 🐛 故障排除

### 问题：无法连接到 WebSocket

**解决方案**：
1. 检查防火墙设置
2. 确保没有浏览器插件阻止 WebSocket
3. 尝试使用基础 Flask 版本 (`app.py`)

### 问题：依赖安装失败

**解决方案**：
```bash
# 在项目根目录清除缓存重试
pip cache purge
pip install -r requirements.txt --no-cache-dir
```

### 问题：图片不显示

**解决方案**：
1. 检查图片文件是否正确生成
2. 验证图片路径权限
3. 检查浏览器控制台是否有 CORS 错误

## 📊 API 端点

### GET /api/status
获取系统状态
```bash
curl http://localhost:5000/api/status
```

### GET /api/sessions
列出所有会话
```bash
curl http://localhost:5000/api/sessions
```

### GET /api/sessions/{session_id}
获取特定会话信息
```bash
curl http://localhost:5000/api/sessions/{session_id}
```

### GET /api/images/{session_id}
获取会话的所有图片
```bash
curl http://localhost:5000/api/images/{session_id}
```

## 🎨 界面自定义

### 改变颜色主题

编辑 `static/style.css` 中的 CSS 变量：

```css
:root {
    --color-primary: #4285F4;      /* Google Blue */
    --color-secondary: #34A853;    /* Google Green */
    --color-warning: #FBBC04;      /* Google Yellow */
    --color-danger: #EA4335;       /* Google Red */
}
```

### 修改布局

`static/style.css` 中的 Grid 布局：

```css
.main-container {
    display: grid;
    grid-template-columns: 320px 1fr 360px;  /* 左侧栏 | 中间 | 右侧栏 */
}
```

## 📱 响应式设计

自适应不同屏幕大小：
- 🖥️ **桌面** (>1200px) - 3 列完整布局
- 💻 **平板** (768-1200px) - 2 列简化布局
- 📱 **手机** (<768px) - 1 列垂直布局

## 🔐 安全建议

1. **生产环境**：
   - 设置强 `SECRET_KEY`
   - 启用 HTTPS/WSS
   - 配置 CORS 白名单

2. **API 保护**：
   - 添加认证机制
   - 实施速率限制
   - 验证输入数据

## 📚 文件结构

```
web/
├── app.py                  # Flask 基础版本
├── app_socketio.py        # Flask-SocketIO 版本（推荐）
├── __init__.py            # 模块初始化
├── run.bat                # Windows 启动脚本
├── README.md              # 本文件
├── templates/
│   └── index.html         # 主页面
└── static/
    ├── app.js             # 前端逻辑
    ├── style.css          # 样式表（500+ 行）
    └── images/            # 生成的图片目录
```

## 🚀 性能优化

- ✅ CSS Grid 原生性能好
- ✅ WebSocket 低延迟通信
- ✅ 图片缓存优化
- ✅ 事件驱动减少轮询

## 🤝 扩展功能

### 添加自定义模型

编辑 `core/controller.py`：
```python
class DiffuServoV4:
    def add_judge_model(self, model_path):
        # 添加新的评分模型
        pass
```

### 自定义评分逻辑

编辑 `evaluator/core.py`：
```python
def evaluate_image(self, image_path):
    # 自定义评分算法
    pass
```

## 📞 支持

如有问题，请查看：
- [主项目 README](../README.md)
- [快速开始指南](../QUICK_START.md)
- [完整文档](../CHANGELOG.md)

---

**Made with ❤️ by Pygmalion Team**

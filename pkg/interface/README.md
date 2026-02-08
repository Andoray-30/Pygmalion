# Interface - 接口层

## 📋 概述

提供 Web UI 和实时通信接口，用户通过浏览器与 Pygmalion 引擎交互。

---

## 🏗️ 架构设计

```
浏览器客户端
    ↓ (HTTP/WebSocket)
Flask 服务器 + Socket.IO
    ↓
DiffuServoV4 引擎
    ↓
返回结果 (实时推送)
```

---

## 📂 目录结构

```
interface/
├── __init__.py
├── server.py          # Flask + Socket.IO 主服务器
└── web/
    ├── static/        # 静态资源（CSS/JS）
    │   ├── app.js     # 前端逻辑
    │   └── style.css  # 样式表
    └── templates/     # HTML 模板
        └── index.html # 主页面
```

---

## 🚀 启动服务

### 方法 1：使用启动脚本
```bash
python launch.py
# 或
run_system.bat
```

### 方法 2：直接运行
```python
from pkg.interface import app, socketio

socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

**访问地址：** `http://localhost:5000`

---

## 📡 Socket.IO 事件

### 客户端 → 服务器

| 事件 | 参数 | 说明 |
|------|------|------|
| `generate` | `{theme, target_score, max_iterations, reference_image}` | 开始生成任务 |
| `user_feedback` | `{text}` | 发送用户反馈 |
| `request_status` | - | 请求系统状态 |

### 服务器 → 客户端

| 事件 | 数据类型 | 说明 |
|------|----------|------|
| `message` | `{type, data}` | 通用消息 |
| `generation_start` | `{theme, session_id}` | 生成开始 |
| `iteration_update` | `{iteration, score, image_url}` | 迭代更新 |
| `generation_complete` | `{best_score, image_count}` | 生成完成 |
| `error` | `{error}` | 错误信息 |

---

## 🎨 前端交互流程

### 1. 上传参考图
```javascript
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch('/api/upload_reference', {
    method: 'POST',
    body: formData
})
.then(res => res.json())
.then(data => {
    referenceImagePath = data.file_path;
});
```

### 2. 开始生成
```javascript
socket.emit('generate', {
    theme: "动漫女孩，粉色头发",
    target_score: 0.90,
    max_iterations: 5,
    reference_image: referenceImagePath
});
```

### 3. 监听进度
```javascript
socket.on('message', (payload) => {
    const { type, data } = payload;
    
    switch(type) {
        case 'iteration_update':
            console.log(`迭代 ${data.iteration}: ${data.score}`);
            displayImage(data.image_url);
            break;
        case 'generation_complete':
            console.log(`完成！最佳分数: ${data.best_score}`);
            break;
    }
});
```

---

## 🔧 API 端点

### REST API

| 端点 | 方法 | 说明 |
|------|------|------|
| `/` | GET | 主页面 |
| `/api/status` | GET | 系统状态 |
| `/api/upload_reference` | POST | 上传参考图 |
| `/api/settings` | GET | 获取设置 |
| `/api/settings` | POST | 更新设置 |
| `/outputs/<path>` | GET | 访问生成图片 |

---

## 📊 会话管理

每个生成任务对应一个会话：

```python
session_id = str(uuid.uuid4())
active_sessions[sid] = {
    'session_id': session_id,
    'theme': theme,
    'engine': engine,
    'start_time': datetime.now()
}
```

**会话生命周期：**
1. 客户端连接 → 创建会话
2. 生成完成 → 保留会话（5分钟）
3. 客户端断开 → 清理会话

---

## 🖼️ 图片管理

### 存储结构
```
evolution_history/
├── references/              # 参考图
│   └── ref_8ac6f716.jpg
└── project_name_timestamp/  # 生成结果
    ├── project_iter1.png
    ├── project_iter2.png
    └── ...
```

### 自动清理
- 每个项目保留最近 20 张图片
- 超出部分自动删除最旧图片

---

## ⚙️ 配置选项

### 服务器配置
```python
# server.py
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pygmalion-secret')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB
```

### Socket.IO 配置
```python
socketio = SocketIO(
    app,
    cors_allowed_origins="*",
    async_mode='threading',
    ping_timeout=60,
    ping_interval=25
)
```

---

## 🐛 调试技巧

### 查看实时日志
```python
# 在 server.py 中启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

### 测试 Socket.IO 连接
```javascript
// 浏览器控制台
socket.on('connect', () => console.log('✅ 已连接'));
socket.on('disconnect', () => console.log('❌ 已断开'));
```

### 查看活跃会话
访问 `http://localhost:5000/api/status` 查看当前活跃会话数。

---

## ⚠️ 常见问题

### 1. 无法访问生成图片
**问题：** `404 Not Found` 访问 `/outputs/...`

**解决：**
- 检查图片路径是否正确
- 确认 `evolution_history` 目录权限
- 查看服务器日志确认图片已生成

### 2. Socket.IO 连接失败
**问题：** 前端无法建立 WebSocket 连接

**解决：**
- 检查防火墙设置
- 确认端口 5000 未被占用
- 查看浏览器控制台错误信息

### 3. 参考图上传失败
**问题：** 上传后无响应

**解决：**
- 检查图片大小（< 16MB）
- 确认图片格式（JPG/PNG）
- 查看 `evolution_history/references/` 权限

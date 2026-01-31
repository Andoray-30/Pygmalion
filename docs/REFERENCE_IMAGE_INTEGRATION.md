# 参考图功能集成完成

## 📦 新增模块

### 1. 参考图编码与融合
- `pkg/system/modules/reference/reference_encoder.py` - CLIP图像编码器
- `pkg/system/modules/reference/prompt_merger.py` - Prompt合并器
- `pkg/system/modules/reference/reference_fusion.py` - 参考图融合入口
- `pkg/system/modules/reference/__init__.py` - 模块导出

### 2. 生成引擎集成
- `pkg/system/engine.py` - 新增 `reference_image_path` 参数支持

### 3. Web UI 集成
- **后端 (`pkg/interface/server.py`)**:
  - 新增 `/api/upload_reference` 图片上传接口
  - `GenerationSession` 类支持参考图路径
  - 生成流程传递参考图路径到核心引擎

- **前端 (`pkg/interface/web/templates/index.html`)**:
  - 输入框区域增加参考图上传按钮
  - 参考图预览容器
  - 拖拽区域标识

- **前端逻辑 (`pkg/interface/web/static/app.js`)**:
  - 上传按钮点击上传
  - 拖拽文件到输入区域自动上传
  - 粘贴图片(Ctrl+V)自动上传
  - 参考图预览与移除
  - 生成时传递 `reference_image_path` 参数

- **样式 (`pkg/interface/web/static/style.css`)**:
  - 上传按钮样式
  - 拖拽状态高亮样式

## 🎯 功能说明

### 用户操作方式
1. **点击上传**: 点击 🖼️ 按钮选择图片
2. **拖拽上传**: 将图片文件拖到输入框区域
3. **粘贴上传**: 在输入框中 Ctrl+V 粘贴剪贴板图片
4. **移除参考图**: 点击预览区的 ✕ 按钮

### 技术流程
```
用户上传图片
    ↓
前端 FormData POST → /api/upload_reference
    ↓
后端保存到 evolution_history/references/
    ↓
返回 {path: 本地路径, url: Web URL}
    ↓
前端显示预览 + 保存路径到 app.referenceImagePath
    ↓
点击"发送"启动生成时
    ↓
params 包含 reference_image_path
    ↓
后端创建 GenerationSession(reference_image_path=...)
    ↓
DiffuServoV4.generate(reference_image_path=...)
    ↓
ReferencePromptFusion.fuse(core_prompt, reference_image)
    ↓
CLIP提取标签 → 合并到Prompt → Stable Diffusion生成
```

## 📋 技术栈

| 组件 | 技术 | 作用 |
|------|------|------|
| **图像编码** | OpenAI CLIP (ViT-B/32) | 提取参考图语义标签 |
| **模型加载** | Transformers | 管理CLIP模型 |
| **推理加速** | PyTorch (CUDA/CPU) | GPU加速推理 |
| **图片处理** | Pillow | 加载图片转RGB |
| **文件上传** | Flask/Werkzeug | 接收前端文件 |
| **实时通信** | Socket.IO | WebSocket双向通信 |
| **拖拽粘贴** | HTML5 Drag & Drop + Clipboard API | 浏览器原生支持 |

## 🔧 环境要求

已在 `requirements.txt` 中包含所有依赖（无需额外安装）：
- `torch>=2.0.0`
- `transformers>=4.30.0` (包含CLIP支持)
- `Pillow>=9.5.0`

## ✅ 测试建议

1. 启动服务器: `python pkg/interface/server.py`
2. 访问 Web UI
3. 测试三种上传方式:
   - 点击上传按钮
   - 拖拽图片文件
   - 复制图片后 Ctrl+V
4. 验证预览显示和移除功能
5. 输入主题后发送，观察参考图标签是否融合到生成Prompt中

## 📝 日志输出

生成过程中会输出：
```
[系统] 🖼️ 参考图已上传: sunset.jpg
[引擎] 🖼️ 已加载参考图: /path/to/ref_abc123.jpg
[融合] 🖼️ [参考图融合] 追加标签: golden hour, warm tones, cinematic lighting
```

## 🚀 下一步扩展

基于当前CLIP基础，可继续集成：
1. **IP-Adapter**: 风格保持生成（需要额外模型）
2. **ControlNet**: 姿态/边缘控制（已有builder基础）
3. **多参考图融合**: 同时处理2-3张参考图
4. **参考图历史**: 保存常用参考图到库中

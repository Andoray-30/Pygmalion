# 多模态风格分析集成

## 功能概述

使用多模态VL大模型（InternVL/Qwen VL）分析参考图像风格，自动推荐合适的底模（ANIME/RENDER/PREVIEW）。

## 核心优化

### 1. 代码重用
- ✅ 重用 `evaluator.utils.encode_image()` （图像编码）
- ✅ 重用 `evaluator.utils.extract_json()` （JSON解析）
- ✅ 统一使用 `httpx` HTTP客户端
- ✅ 代码减少 28% (178行→128行)

### 2. API策略
**优先级：魔搭免费 > 硅基付费**

魔搭 (2000次/天免费):
- OpenGVLab/InternVL3_5-241B-A28B
- Qwen/Qwen3-VL-235B-A22B-Instruct
- Qwen/Qwen2.5-VL-72B-Instruct

硅基 (付费降级):
- Qwen/Qwen3-VL-235B-A22B-Instruct
- Qwen/Qwen2.5-VL-72B-Instruct
- deepseek-ai/deepseek-vl2

### 3. 集成流程

```
参考图像 → 魔搭API → 风格分析 → 推荐模型
    ↓                      ↓
  失败? → 硅基API      DeepSeek提示优化
```

## 使用方法

```python
from pkg.system.modules.reference import analyze_reference_style_with_multimodal

result = analyze_reference_style_with_multimodal("path/to/image.jpg")
# 返回: {style_category, recommended_model, deepseek_hints, ...}
```

## 环境配置

```env
MODELSCOPE_API_KEY=ms-xxx  # 魔搭免费 (优先)
SILICON_KEY=sk-xxx         # 硅基付费 (降级)
```

## 已解决的问题

1. ❌ 硬编码二元检测 → ✅ 多模态AI分析
2. ❌ 仅支持anime/realistic → ✅ 无限风格类别
3. ❌ 重复代码 → ✅ 重用项目工具
4. ❌ 硅基付费优先 → ✅ 魔搭免费优先

## 测试

```bash
python tests/test_multimodal_analyzer.py tmp/reference.jpg
```

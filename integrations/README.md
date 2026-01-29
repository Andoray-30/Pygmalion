# integrations/ - 第三方集成模块

## 📋 模块用途

集成第三方服务和自动化任务，扩展系统功能。

## 📂 文件说明

### `modelscope_watcher.py` - ModelScope 模型监控

**核心功能**: 自动监控 ModelScope 平台最新模型，定期保存快照。

#### 功能说明

**1. 模型列表抓取**
```python
from integrations.modelscope_watcher import ModelScopeWatcher

watcher = ModelScopeWatcher()
models = watcher.fetch_latest_models()
# 返回: [{"name": "sd_xl_turbo", "version": "1.0", "size": "4.5GB"}, ...]
```

**2. 定期快照**
```python
# 自动每天保存一次快照
watcher.enable_auto_snapshot(interval_hours=24)

# 手动快照
snapshot = watcher.take_snapshot()
# 保存到: models_snapshot/modelscope_models_YYYYMMdd_HHMMSS.json
```

**3. 变化检测**
```python
# 检测新模型或更新
changes = watcher.detect_changes()
# 返回: {"new": [...], "updated": [...], "removed": [...]}

if changes["new"]:
    print(f"发现新模型: {changes['new']}")
    # 发送通知
    watcher.notify_updates(changes)
```

**4. 版本对比**
```python
# 对比两个快照
diff = watcher.compare_snapshots(
    snapshot1="modelscope_models_20260129_154733.json",
    snapshot2="modelscope_models_20260129_154800.json"
)
```

#### 快照格式

```json
{
  "timestamp": "2026-01-29 15:47:33",
  "total_models": 2845,
  "models": [
    {
      "name": "sd_xl_turbo_1.0_fp16",
      "category": "text-to-image",
      "size": "4.5GB",
      "downloads": 125000,
      "version": "1.0",
      "release_date": "2025-12-01",
      "description": "SDXL Turbo - 1-step generation"
    },
    ...
  ]
}
```

---

## 📊 快照存储

快照自动保存在 `models_snapshot/` 目录:

```
models_snapshot/
├── latest.json                              # 最新快照
├── modelscope_models_20260127_154733.json  # 历史快照 1
├── modelscope_models_20260127_154734.json  # 历史快照 2
└── ...
```

**查看最新快照**
```bash
cat models_snapshot/latest.json | jq '.models | length'
# 输出: 2845 (总模型数)
```

---

## 🔄 自动监控工作流

```
启动 ModelScopeWatcher
    ↓
每 24 小时检查一次
    ↓
获取最新模型列表
    ↓
与上一个快照对比
    ↓
有更新? 
├─ 是 → 保存新快照 + 发送通知
└─ 否 → 跳过
    ↓
定时运行
```

---

## 💾 使用示例

**启用后台监控**
```python
from integrations.modelscope_watcher import ModelScopeWatcher

watcher = ModelScopeWatcher()
watcher.enable_auto_snapshot(interval_hours=24)

# 系统将在后台自动运行
```

**手动监控和查询**
```python
# 获取所有 SDXL 相关模型
sdxl_models = watcher.search_models(query="sdxl")

# 获取最近 7 天的变化
recent_changes = watcher.get_changes_since(days=7)

# 导出报告
watcher.export_report(format="csv", output_path="model_report.csv")
```

---

## 🚨 故障排查

| 问题 | 原因 | 解决 |
|------|------|------|
| 无法连接 ModelScope | 网络问题 | 检查网络，增加超时时间 |
| 快照为空 | API 返回错误 | 检查 API 可用性 |
| 存储空间满 | 快照过多 | 清理旧快照 (> 30 天) |

**清理旧快照**
```python
watcher.cleanup_old_snapshots(days=30)
```

---

## 📈 扩展点

### 添加新集成

在 `integrations/` 中创建新文件，例如 `huggingface_watcher.py`:

```python
# integrations/huggingface_watcher.py
class HuggingFaceWatcher:
    def fetch_latest_models(self):
        # 实现 HuggingFace 模型抓取
        pass
```

---

**最后更新**: 2026-01-29

# 多模态分析器（无torch依赖）
from .multimodal_analyzer import MultimodalStyleAnalyzer, analyze_reference_style_with_multimodal

# Prompt融合（需要torch，延迟导入避免冲突）
def __getattr__(name):
    if name == "ReferencePromptFusion":
        from .reference_fusion import ReferencePromptFusion
        return ReferencePromptFusion
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


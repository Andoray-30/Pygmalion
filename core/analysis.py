def compute_gradient(score_buffer):
    """
    计算分数梯度（最近7次的变化趋势，使用Trimmed Mean增强稳健性）
    返回: (平均梯度, 振荡幅度)
    """
    if len(score_buffer) < 2:
        return 0.0, 0.0
    
    # 使用最近7个数据点（或全部，如果少于7）
    window_size = min(7, len(score_buffer))
    recent = score_buffer[-window_size:]
    
    # 计算所有相邻点的梯度
    gradients = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
    
    if not gradients:
        return 0.0, 0.0
    
    # Trimmed Mean：去掉最高和最低梯度后计算平均
    # 这样可以避免单次异常值（如Qwen评分抽风）导致梯度爆炸
    if len(gradients) > 2:
        sorted_gradients = sorted(gradients)
        trimmed = sorted_gradients[1:-1]  # 去掉最高和最低
        avg_grad = sum(trimmed) / len(trimmed) if trimmed else 0.0
    else:
        avg_grad = sum(gradients) / len(gradients)
    
    # 振荡幅度：使用Trimmed Mean后的范围（更稳健）
    if len(gradients) > 2:
        sorted_gradients = sorted(gradients)
        trimmed = sorted_gradients[1:-1]
        volatility = (max(trimmed) - min(trimmed)) if trimmed else 0.0
    else:
        volatility = max(gradients) - min(gradients) if gradients else 0.0
    
    return avg_grad, volatility

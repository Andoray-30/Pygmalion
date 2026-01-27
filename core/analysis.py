def compute_gradient(score_buffer):
    """
    计算分数梯度（最近3次的变化趋势）
    返回: (平均梯度, 振荡幅度)
    """
    if len(score_buffer) < 2:
        return 0.0, 0.0
    
    recent = score_buffer[-3:]  # 最近3次
    gradients = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
    avg_grad = sum(gradients) / len(gradients) if gradients else 0.0
    volatility = max(gradients) - min(gradients) if gradients else 0.0
    
    return avg_grad, volatility

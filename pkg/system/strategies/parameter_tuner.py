#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
参数调优策略 - 完整的PID控制器实现
"""
import random
from pkg.infrastructure.utils import compute_gradient


class PIDParameterTuner:
    """完整的PID参数调优器 - 支持P、I、D三项控制"""

    def __init__(self, Kp=1.5, Ki=0.3, Kd=0.5):
        """
        初始化PID控制器

        Args:
            Kp: 比例系数
            Ki: 积分系数
            Kd: 微分系数
        """
        self.Kp = Kp
        self.Ki = Ki
        self.Kd = Kd

        self.integral = 0.0      # 积分累积
        self.last_error = 0.0    # 上次误差

    def compute(self, target_score, current_score, dt=1.0):
        """
        计算PID输出

        Args:
            target_score: 目标分数
            current_score: 当前分数
            dt: 时间间隔（迭代次数）

        Returns:
            dict: 参数调整建议 {"steps_delta": int, "cfg_delta": float}
        """
        error = target_score - current_score  # 例如: 0.05

        # P 项：比例控制
        p_term = self.Kp * error

        # I 项：积分控制（累积误差）
        self.integral += error * dt
        i_term = self.Ki * self.integral

        # D 项：微分控制（误差变化率）
        derivative = (error - self.last_error) / dt
        d_term = self.Kd * derivative

        # 总输出
        output = p_term + i_term + d_term

        self.last_error = error

        # 将输出映射到参数调整
        return {
            "steps_delta": int(output * 5),  # 例如: +2 步
            "cfg_delta": output * 0.5        # 例如: +0.1 CFG
        }

    def reset(self):
        """重置PID控制器状态"""
        self.integral = 0.0
        self.last_error = 0.0


class AdaptiveParameterTuner:
    """自适应参数调优器 - 基于状态和梯度的智能调优（增强版：集成完整PID）"""

    def __init__(self):
        self.Kp_steps = 1.5
        self.Kp_cfg = 0.6
        self.adaptive_factor = 1.0
        
        # 🆕 集成PID控制器
        self.pid_controller = PIDParameterTuner(Kp=1.5, Ki=0.3, Kd=0.5)
        self.use_full_pid = True  # 启用完整PID控制

    def adjust(self, params, state, score_buffer, target_score, result):
        """
        根据当前状态和分数自适应调整参数（增强版：PID + 自适应）

        Args:
            params: 当前参数字典
            state: 当前状态
            score_buffer: 分数缓冲区
            target_score: 目标分数
            result: 评分结果字典

        Returns:
            dict: 更新后的参数
        """
        params = params.copy()
        current_score = result.get('final_score', 0)
        concept = result.get('concept_score', 0)
        quality = result.get('quality_score', 0)

        # 计算梯度
        avg_grad, volatility = compute_gradient(score_buffer)

        # 🆕 使用完整PID控制器计算参数调整
        if self.use_full_pid and len(score_buffer) >= 2:
            pid_output = self.pid_controller.compute(target_score, current_score, dt=1.0)
            steps_delta = pid_output['steps_delta']
            cfg_delta = pid_output['cfg_delta']
            print(f"🎛️ [PID] P+I+D输出: steps_delta={steps_delta}, cfg_delta={cfg_delta:.2f}")
        else:
            # 降级到P-Control
            error = target_score - current_score
            steps_delta = int(error * self.Kp_steps * self.adaptive_factor)
            cfg_delta = error * self.Kp_cfg * self.adaptive_factor

        # 自适应学习率调整
        if avg_grad > 0.05:
            self.adaptive_factor = min(1.5, self.adaptive_factor + 0.1)
        elif avg_grad < -0.03:
            self.adaptive_factor = max(0.5, self.adaptive_factor - 0.15)

        # 检测振荡
        if volatility > 0.1 and len(score_buffer) >= 3:
            print("⚠️ 检测到参数振荡，停止调参，只改Seed")
            params['seed'] = random.randint(1, 9999999999)
            return params

        error = target_score - current_score

        # 根据状态调整参数
        if state == "INIT":
            print("🔄 初始化阶段，Reroll Seed")
            params['seed'] = random.randint(1, 9999999999)

        elif state == "EXPLORE":
            if quality < concept:
                # 使用PID输出调整参数
                params['steps'] = min(8, max(4, int(params['steps'] + steps_delta)))
                params['cfg_scale'] = min(2.5, max(1.0, params['cfg_scale'] + cfg_delta))
                print(f"🔧 [EXPLORE] PID调整: steps→{params['steps']}, cfg→{params['cfg_scale']:.2f}")
            else:
                prompt = params.get('prompt')
                if prompt and "vivid" not in prompt:
                    params['prompt'] = prompt + ", vivid colors, cinematic lighting"
                print("🔧 [EXPLORE] 增强Prompt语义")

            params['seed'] = random.randint(1, 9999999999)

        elif state == "OPTIMIZE":
            # SDXL Turbo是1-step优化模型，增加steps会降低质量！保持步数不变
            # 改为在HR维度进行调整（使用PID的cfg_delta进行微调）
            if quality < 0.85:
                hr_delta = max(1, int(abs(cfg_delta) * 2))  # 将cfg_delta映射到HR步数
                params['hr_second_pass_steps'] = min(6, params['hr_second_pass_steps'] + hr_delta)
                print(f"🔧 [OPTIMIZE] 增加HR第二遍步数→{params['hr_second_pass_steps']}")

            if avg_grad < 0.02 and params.get('hr_scale', 1.0) < 1.8:
                params['hr_scale'] = min(1.8, params['hr_scale'] + 0.1)
                print(f"🔧 [OPTIMIZE] 提升HR倍率→{params['hr_scale']:.1f}")

            params['seed'] = random.randint(1, 9999999999)

        elif state == "FINETUNE":
            print("🎯 [FINETUNE] 锁定参数，Reroll Seed")
            params['seed'] = random.randint(1, 9999999999)

        return params

    def reset_pid(self):
        """重置PID控制器状态"""
        self.pid_controller.reset()
        self.adaptive_factor = 1.0

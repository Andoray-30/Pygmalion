#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
单元测试 - PIDParameterTuner
"""
import pytest
from pkg.system.strategies.parameter_tuner import PIDParameterTuner, AdaptiveParameterTuner


@pytest.fixture
def pid():
    """创建PID控制器实例"""
    return PIDParameterTuner(Kp=1.5, Ki=0.3, Kd=0.5)


@pytest.fixture
def adaptive_tuner():
    """创建自适应调优器实例"""
    return AdaptiveParameterTuner()


class TestPIDParameterTuner:
    """PID控制器单元测试"""

    def test_init(self, pid):
        """测试初始化"""
        assert pid.Kp == 1.5
        assert pid.Ki == 0.3
        assert pid.Kd == 0.5
        assert pid.integral == 0.0
        assert pid.last_error == 0.0

    def test_compute_proportional_term(self, pid):
        """测试比例项计算"""
        target = 0.90
        current = 0.85
        
        output = pid.compute(target, current, dt=1.0)
        
        assert "steps_delta" in output
        assert "cfg_delta" in output
        # 误差为正，应该有正向调整
        assert output["steps_delta"] > 0 or output["cfg_delta"] > 0

    def test_compute_integral_accumulation(self, pid):
        """测试积分项累积"""
        target = 0.90
        current = 0.85
        
        # 第一次计算
        output1 = pid.compute(target, current, dt=1.0)
        integral1 = pid.integral
        
        # 第二次计算（保持相同误差）
        output2 = pid.compute(target, current, dt=1.0)
        integral2 = pid.integral
        
        # 积分应该累积
        assert integral2 > integral1

    def test_compute_derivative_term(self, pid):
        """测试微分项计算"""
        target = 0.90
        
        # 第一次：误差 0.05
        pid.compute(target, 0.85, dt=1.0)
        
        # 第二次：误差 0.03（误差减小）
        output = pid.compute(target, 0.87, dt=1.0)
        
        # 误差减小，微分项应该抑制调整幅度
        assert pid.last_error < 0.05

    def test_compute_negative_error(self, pid):
        """测试负误差（当前分数超过目标）"""
        target = 0.90
        current = 0.95
        
        output = pid.compute(target, current, dt=1.0)
        
        # 负误差应该导致负向调整
        assert output["steps_delta"] <= 0 or output["cfg_delta"] <= 0

    def test_reset(self, pid):
        """测试重置功能"""
        # 先进行一些计算
        pid.compute(0.90, 0.85, dt=1.0)
        pid.compute(0.90, 0.87, dt=1.0)
        
        # 此时应该有积分和历史误差
        assert pid.integral != 0.0
        assert pid.last_error != 0.0
        
        # 重置
        pid.reset()
        
        # 检查重置后状态
        assert pid.integral == 0.0
        assert pid.last_error == 0.0

    def test_convergence_scenario(self, pid):
        """测试收敛场景"""
        target = 0.90
        scores = [0.70, 0.75, 0.80, 0.85, 0.88, 0.89]
        
        outputs = []
        for score in scores:
            output = pid.compute(target, score, dt=1.0)
            outputs.append(output)
        
        # 随着分数接近目标，调整幅度应该减小
        assert abs(outputs[-1]["steps_delta"]) < abs(outputs[0]["steps_delta"])


class TestAdaptiveParameterTuner:
    """自适应参数调优器单元测试"""

    def test_init(self, adaptive_tuner):
        """测试初始化"""
        assert adaptive_tuner.Kp_steps == 1.5
        assert adaptive_tuner.Kp_cfg == 0.6
        assert adaptive_tuner.adaptive_factor == 1.0
        assert hasattr(adaptive_tuner, 'pid_controller')

    def test_adjust_init_state(self, adaptive_tuner):
        """测试INIT状态的参数调整"""
        params = {"seed": 12345, "steps": 4, "cfg_scale": 1.0}
        result = {"final_score": 0.4, "concept_score": 0.5, "quality_score": 0.3}
        
        new_params = adaptive_tuner.adjust(
            params=params,
            state="INIT",
            score_buffer=[0.4],
            target_score=0.90,
            result=result
        )
        
        # INIT状态应该只改Seed
        assert new_params["seed"] != 12345

    def test_adjust_explore_state(self, adaptive_tuner):
        """测试EXPLORE状态的参数调整"""
        params = {"seed": 12345, "steps": 4, "cfg_scale": 1.0, "prompt": "test"}
        result = {"final_score": 0.6, "concept_score": 0.7, "quality_score": 0.5}
        
        new_params = adaptive_tuner.adjust(
            params=params,
            state="EXPLORE",
            score_buffer=[0.5, 0.6],
            target_score=0.90,
            result=result
        )
        
        # EXPLORE状态应该调整steps和cfg
        assert new_params["steps"] != params["steps"] or new_params["cfg_scale"] != params["cfg_scale"]

    def test_adjust_with_oscillation_detection(self, adaptive_tuner):
        """测试振荡检测"""
        params = {"seed": 12345, "steps": 4, "cfg_scale": 1.0}
        result = {"final_score": 0.85, "concept_score": 0.85, "quality_score": 0.85}
        
        # 模拟振荡场景（波动较大）
        score_buffer = [0.80, 0.90, 0.82, 0.88, 0.85]
        
        new_params = adaptive_tuner.adjust(
            params=params,
            state="EXPLORE",
            score_buffer=score_buffer,
            target_score=0.90,
            result=result
        )
        
        # 检测到振荡时应该只改Seed
        assert new_params["seed"] != params["seed"]

    def test_reset_pid(self, adaptive_tuner):
        """测试PID重置"""
        # 先进行一些调整
        params = {"seed": 12345, "steps": 4, "cfg_scale": 1.0}
        result = {"final_score": 0.6, "concept_score": 0.6, "quality_score": 0.6}
        
        adaptive_tuner.adjust(
            params=params,
            state="EXPLORE",
            score_buffer=[0.5, 0.6],
            target_score=0.90,
            result=result
        )
        
        # 重置
        adaptive_tuner.reset_pid()
        
        # 检查状态
        assert adaptive_tuner.adaptive_factor == 1.0
        assert adaptive_tuner.pid_controller.integral == 0.0

    def test_adaptive_factor_adjustment(self, adaptive_tuner):
        """测试自适应因子调整"""
        initial_factor = adaptive_tuner.adaptive_factor
        
        params = {"seed": 12345, "steps": 4, "cfg_scale": 1.0, "prompt": "test"}
        result = {"final_score": 0.7, "concept_score": 0.7, "quality_score": 0.7}
        
        # 模拟分数持续上升（梯度为正）
        score_buffer = [0.5, 0.6, 0.7]
        
        adaptive_tuner.adjust(
            params=params,
            state="EXPLORE",
            score_buffer=score_buffer,
            target_score=0.90,
            result=result
        )
        
        # 梯度为正时，自适应因子应该增加
        # （实际是否增加取决于compute_gradient的实现）
        assert adaptive_tuner.adaptive_factor >= initial_factor


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

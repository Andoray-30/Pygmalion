#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DiffuServo V4 - 自适应扩散模型控制系统
"""
import time
import os
import requests
import base64
import random
import datetime
import re
from pkg.infrastructure.config import (
        FORGE_URL,
        TARGET_SCORE,
        MAX_ITERATIONS,
        FORGE_TIMEOUT,
        FORGE_HEARTBEAT_INTERVAL,
        CONVERGENCE_PATIENCE,
        CONVERGENCE_THRESHOLD,
        BASE_MODELS,
        MODEL_CONFIGS,
        MODEL_SWITCH_SCORE_THRESHOLD,
        MODEL_SWITCH_MIN_ITERATIONS,
)
from pkg.system.modules.creator import CreativeDirector
from pkg.system.modules.evaluator import rate_image
from pkg.infrastructure.health import check_forge_health
from pkg.infrastructure.utils import compute_gradient
from pkg.system.builders import ControlNetBuilder

OUTPUT_DIR = "evolution_history"
os.makedirs(OUTPUT_DIR, exist_ok=True)

class DiffuServoV4:
    """工业级自适应控制器"""
    
    # 状态定义
    STATE_INIT = "INIT"           # 初始化：保守参数，探索可行域
    STATE_EXPLORE = "EXPLORE"     # 探索：逐步调参，寻找改进方向
    STATE_OPTIMIZE = "OPTIMIZE"   # 优化：HR激活，细致调参
    STATE_FINETUNE = "FINETUNE"   # 精细调优：锁定参数，只改Seed
    STATE_CONVERGED = "CONVERGED" # 收敛成功
    
    def __init__(self, theme="enchanted forest", reference_image_path=None):
        # 🧠 初始化创意大脑
        self.brain = CreativeDirector()
        self.theme = theme
        self.reference_image_path = reference_image_path  # 新增：参考图路径
        self.reference_fusion = None
        
        # 🎯 [新增] 智能模型选择：根据主题推荐最佳底模
        print(f"\n🔍 分析主题并选择最佳模型...")
        model_recommendation = self.brain.analyze_theme_and_recommend_model(theme)
        self.initial_model_choice = model_recommendation.get("model", "PREVIEW")
        
        # 🏷️ 生成英文项目名（DeepSeek）并固定本次运行
        raw_name = self.brain.generate_project_name(self.theme)
        raw_name = (raw_name or "untitled_project").strip()
        safe_name = re.sub(r"\s+", "_", raw_name)
        safe_name = re.sub(r"[^A-Za-z0-9_]+", "", safe_name)
        if not safe_name:
            safe_name = "untitled_project"
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        self.project_id = f"{safe_name}_{timestamp}"
        
        self.params = {
            "prompt": f"cinematic shot of {theme}, misty sunbeams, lush foliage, volumetric light, 8k, masterpiece, sharp focus, highly detailed",
            "negative_prompt": "text, watermark, blurry, noise, distortion, ugly, low quality, jpeg artifacts, grain, nsfw",
            "steps": 20,  # 增加步数以获得更好质量，防止 Turbo 模式过快导致的潜在问题
            "cfg_scale": 7.0,  # 标准 CFG
            "width": 832,   # SDXL 推荐分辨率
            "height": 1216, # SDXL 推荐分辨率
            "sampler_name": "Euler a", # 更稳健的采样器
            "scheduler": "Simple", # 标准调度器
            "seed": -1,
            "enable_hr": False,
            "hr_scale": 1.5,
            "hr_upscaler": "R-ESRGAN 4x+",
            "hr_second_pass_steps": 10,
            "denoising_strength": 0.35,
            "hr_additional_modules": []
        }
        
        # 🔴 状态追踪
        self.state = self.STATE_INIT
        self.iteration = 0
        
        # 🟡 性能追踪
        self.best_score = 0.0
        self.best_params = self.params.copy()
        self.history = []

        # 🎯 运行参数（可由外部覆盖）
        self.target_score = TARGET_SCORE
        self.max_iterations = MAX_ITERATIONS
        
        # 🟢 梯度追踪
        self.score_buffer = []  # 最近5次的分数
        self.no_improvement_count = 0
        self.convergence_patience = 10  # 【改进】从CONVERGENCE_PATIENCE→10步，更保守
        self.convergence_threshold = CONVERGENCE_THRESHOLD
        
        # 🟣 【新增】Prompt缓存与镜头锁定（用于稳定收敛）
        self.best_prompt = None  # 历史最佳prompt
        self.best_prompt_score = 0.0
        self.locked_lens = None  # OPTIMIZE期间锁定的艺术镜头
        self.best_dimensions = {}  # 记录各维度的最佳分数
        self.stagnation_count = 0  # 停滞计数器（连续无进展的迭代数）
        self.stagnation_threshold = 8  # 【改进】停滞触发阈值：从6→8，给更多尝试空间
        
        # 🎨 ControlNet构建器
        self.controlnet_builder = ControlNetBuilder()
        
        # � FINETUNE阶段低分回退机制
        self.finetune_low_score_count = 0  # 连续低分计数
        self.finetune_low_score_threshold = 0.7  # 低分阈值
        self.finetune_low_score_patience = 3  # 连续低分次数达到3次后回退
        
        # 🚀 双模型切换状态 (Dual-Model Strategy)
        self.current_model_mode = "PREVIEW"  # 默认从快速模式开始
        self.has_switched_to_render = False  # 单向阀：防止反复切换显存抖动
        self.model_switch_timestamp = None   # 记录切换时间用于性能分析
        
        # �🔵 自适应学习率
        self.Kp_steps = 1.5
        self.Kp_cfg = 0.6
        self.adaptive_factor = 1.0
        self.heartbeat_interval = max(1, FORGE_HEARTBEAT_INTERVAL)

        # 🩺 启动前快速健康检查
        if not check_forge_health():
            raise RuntimeError(f"Forge 不可用，请检查: {FORGE_URL}")

    def state_transition(self, current_score, concept, quality, aesthetics=None, reasonableness=None):
        """状态机：根据分数自动切换策略 + 停滞检测 (改进版)"""
        avg_grad, volatility = compute_gradient(self.score_buffer)
        
        # 【新增】停滞检测：如果连续迭代无进展，主动回退
        if self.iteration > 1 and current_score < self.best_score - 0.01:  # 分数下降
            self.stagnation_count += 1
            if self.stagnation_count >= self.stagnation_threshold:
                print(f"⚠️ 检测到停滞{self.stagnation_count}次，回退到最佳prompt进行调整")
                self.stagnation_count = 0
        else:
            self.stagnation_count = 0  # 有进展则重置计数
        
        if self.state == self.STATE_INIT:
            if current_score > 0.5:
                print("✅ 初始参数有效，进入探索阶段")
                self.state = self.STATE_EXPLORE
            else:
                print("⚠️ 初始参数不佳，继续探索调整")
        
        elif self.state == self.STATE_EXPLORE:
            # 【改进】EXPLORE→OPTIMIZE的触发条件：至少6步+高分
            # 给EXPLORE充分的时间探索，不要急于进入OPTIMIZE
            if current_score > 0.82 and self.iteration >= 6:
                print(f"🎯 分数已优化至{current_score:.2f}，锁定最佳策略进入优化阶段")
                self.state = self.STATE_OPTIMIZE
                # 【关键】锁定当前最佳镜头和prompt，后续不再随机
                self.locked_lens = "BEST_ACHIEVED"
                self.finetune_low_score_count = 0
        
        elif self.state == self.STATE_OPTIMIZE:
            # 【改进】精细优化：基于梯度主动调整
            if current_score >= 0.88:
                print("📍 质量已优秀，进入微调阶段")
                self.state = self.STATE_FINETUNE
        
        elif self.state == self.STATE_FINETUNE:
            # 🔄 微调收敛：记录各维度最佳值
            if aesthetics is not None:
                self.best_dimensions['aesthetics'] = max(self.best_dimensions.get('aesthetics', 0), aesthetics)
            if reasonableness is not None:
                self.best_dimensions['reasonableness'] = max(self.best_dimensions.get('reasonableness', 0), reasonableness)
            
            if current_score < self.finetune_low_score_threshold:
                self.finetune_low_score_count += 1
                if self.finetune_low_score_count >= 3:
                    print(f"⏹️ 连续{self.finetune_low_score_count}次低分，提前停止迭代")
                    self.state = self.STATE_CONVERGED
                    return True
            else:
                self.finetune_low_score_count = 0
            
            if current_score >= self.target_score:
                print("🏆 收敛成功！")
                self.state = self.STATE_CONVERGED
                return True
        
        return False
    
    def adaptive_control(self, result):
        """自适应P-Control（依赖 run() 中的 score_buffer.append）"""
        current_score = result.get('final_score', 0)
        concept = result.get('concept_score', 0)
        quality = result.get('quality_score', 0)
        
        # 注意：score_buffer 在 run() 方法中追加，此处不重复追加（避免梯度污染）
        avg_grad, volatility = compute_gradient(self.score_buffer)
        
        # 🔑 自适应学习率调整
        if avg_grad > 0.05:
            self.adaptive_factor = min(1.5, self.adaptive_factor + 0.1)
            print("📈 分数改进中，提升学习率因子: %.2f" % self.adaptive_factor)
        elif avg_grad < -0.03:
            self.adaptive_factor = max(0.5, self.adaptive_factor - 0.15)
            print("📉 分数恶化，降低学习率因子: %.2f" % self.adaptive_factor)
        
        if volatility > 0.1 and len(self.score_buffer) >= 3:
            print("⚠️ 检测到参数振荡，停止调参，只改Seed")
            self.state = self.STATE_FINETUNE
            self.params['seed'] = random.randint(1, 9999999999)
            return
        
        error = self.target_score - current_score
        
        if self.state == self.STATE_INIT:
            print("🔄 初始化阶段，Reroll Seed")
            self.params['seed'] = random.randint(1, 9999999999)
        
        elif self.state == self.STATE_EXPLORE:
            if quality < concept:
                step_delta = error * self.Kp_steps * self.adaptive_factor
                self.params['steps'] = min(8, max(4, int(self.params['steps'] + max(1, step_delta))))
                
                cfg_delta = error * self.Kp_cfg * self.adaptive_factor
                self.params['cfg_scale'] = min(2.5, max(1.0, self.params['cfg_scale'] + cfg_delta))
                print("🔧 [EXPLORE] 调整: steps→%d, cfg→%.2f" % (self.params['steps'], self.params['cfg_scale']))
            else:
                if "vivid" not in self.params['prompt']:
                    self.params['prompt'] += ", vivid colors, cinematic lighting"
                print("🔧 [EXPLORE] 增强Prompt语义")
            
            self.params['seed'] = random.randint(1, 9999999999)
        
        elif self.state == self.STATE_OPTIMIZE:
            # 【关键纠正】SDXL Turbo是1-step优化模型，增加steps会降低质量！保持步数不变
            # 改为在HR维度进行调整（CFG调整过于激进，禁用）
            if quality < 0.85:
                self.params['hr_second_pass_steps'] = min(6, self.params['hr_second_pass_steps'] + 1)
                print("🔧 [OPTIMIZE] 增加HR第二遍步数→%d" % self.params['hr_second_pass_steps'])
            
            if avg_grad < 0.02 and self.params.get('hr_scale', 1.0) < 1.8:
                self.params['hr_scale'] = min(1.8, self.params['hr_scale'] + 0.1)
                print("🔧 [OPTIMIZE] 提升HR倍率→%.1f" % self.params['hr_scale'])
            
            self.params['seed'] = random.randint(1, 9999999999)
        
        elif self.state == self.STATE_FINETUNE:
            print("🎯 [FINETUNE] 锁定参数，Reroll Seed")
            self.params['seed'] = random.randint(1, 9999999999)
    
    def check_convergence(self, current_score):
        """收敛检测"""
        if current_score > self.best_score:
            self.best_score = current_score
            self.best_params = self.params.copy()
            self.no_improvement_count = 0
            print(f"🏆 新纪录: {current_score:.2f}")
            return False
        
        self.no_improvement_count += 1
        
        # 【改进】延迟收敛检测，至少运行15步后才判断真正收敛
        if self.iteration < 15:
            return False
        
        if len(self.score_buffer) >= 3:
            recent_3 = self.score_buffer[-3:]
            improvement = recent_3[-1] - recent_3[0]
            if improvement < self.convergence_threshold and self.no_improvement_count >= self.convergence_patience:
                print(f"\n🛑 收敛检测：最近3步改进={improvement:.6f} < {self.convergence_threshold}，连续{self.no_improvement_count}步无进展")
                return True
        
        if self.no_improvement_count >= 8:
            print(f"\n🛑 硬性早停：连续{self.no_improvement_count}步无进展，放弃")
            return True
        
        return False
    
    def generate(self, prev_score=None, prev_feedback=None, best_dimensions=None, external_suggestion=None, reference_image_path=None):
        """生成图片 (单模型版 + 评分反馈循环 + Prompt缓存)
        Args:
            prev_score: 前一次迭代的得分(用于反馈)
            prev_feedback: 前一次迭代的反馈信息(最弱维度)
            best_dimensions: 历史最佳维度分数(用于反馈)
            external_suggestion: [新增] 外部传入的创意建议或用户反馈
            reference_image_path: [新增] 参考图片路径（用于Prompt融合）
        """
        # [关键修复] 增加内部迭代计数，确保模型切换逻辑生效
        self.iteration += 1
        
        # 🎯 [核心改进] 如果收到重大用户建议，尝试重新分析模型意图
        if external_suggestion and len(external_suggestion) > 10:
            print(f"🔄 [动态分析] 收到重大反馈，尝试重新评估模型建议...")
            re_rec = self.brain.analyze_theme_and_recommend_model(f"{self.theme} (Feedback: {external_suggestion})")
            new_model = re_rec.get("model", "PREVIEW")
            if new_model != self.initial_model_choice:
                print(f"🎯 [模型切换] 从 {self.initial_model_choice} 切换到 {new_model} 以响应反馈")
                self.initial_model_choice = new_model

        # 🎯 【改进】反馈机制优化：既要改进弱项，也要保持强项
        feedback_context = ""
        
        # 优先使用外部建议
        if external_suggestion:
            feedback_context = f"\nUser feedback/Creative direction: {external_suggestion}"
        
        elif prev_score is not None and prev_feedback is not None:
            # 识别并强化强势维度
            strong_dims = []
            if best_dimensions:
                for dim, score in best_dimensions.items():
                    if score > 0.88:
                        strong_dims.append(f"{dim}({score:.2f})")
            
            strong_hint = f" Keep excelling in: {', '.join(strong_dims)}." if strong_dims else ""
            feedback_context = f"\nPrevious score: {prev_score:.2f}.{strong_hint} Focus on improving {prev_feedback}."
        
        # [新增] 处理外部创意建议或用户实时反馈
        if external_suggestion:
            feedback_context = f"{feedback_context}\nExternal Insight/User Request: {external_suggestion}"

        # 【关键改进】OPTIMIZE阶段禁用随机镜头，使用最佳方向
        if self.state == "OPTIMIZE" and self.locked_lens == "BEST_ACHIEVED":
            core_prompt = self.brain.brainstorm_prompt(self.theme, feedback_context=feedback_context, use_random=False)
        else:
            core_prompt = self.brain.brainstorm_prompt(self.theme, feedback_context=feedback_context, use_random=True)                                   
        
        # 【改进】Prompt缓存：如果生成失败或停滞，回退到历史最佳
        if self.stagnation_count > 0 and self.best_prompt is not None:
            print(f"🔄 检测到停滞，使用历史最佳prompt（分数：{self.best_prompt_score:.2f}）")
            core_prompt = self.best_prompt
        else:
            # 【记录】每次都保存prompt用于后续回退
            if prev_score and prev_score > self.best_prompt_score:
                self.best_prompt = core_prompt
                self.best_prompt_score = prev_score if prev_score else 0.0

        # 🖼️ [新增] 参考图Prompt融合（可选）
        if reference_image_path:
            try:
                if self.reference_fusion is None:
                    from pkg.system.modules.reference import ReferencePromptFusion
                    self.reference_fusion = ReferencePromptFusion()
                fusion_result = self.reference_fusion.fuse(core_prompt, reference_image_path)
                core_prompt = fusion_result.prompt
                if fusion_result.tags_used:
                    print(f"🖼️ [参考图融合] 追加标签: {', '.join(fusion_result.tags_used)}")
            except Exception as e:
                print(f"⚠️ 参考图融合失败: {e}")
        
        if self.params['seed'] == -1 or self.iteration > 1:
            self.params['seed'] = random.randint(1, 9999999999)
        
        # 🎯 [改进] 智能模型选择：初始使用DeepSeek推荐，持续使用相同风格
        if self.iteration == 1:
            # 第1代：使用DeepSeek分析结果
            target_mode = self.initial_model_choice
            print(f"🎯 [智能选择] 使用 {target_mode} 模型（基于DeepSeek意图分析）")
        elif self.best_score >= MODEL_SWITCH_SCORE_THRESHOLD and self.iteration >= MODEL_SWITCH_MIN_ITERATIONS:
            # 高分阶段：如果初始选择是PREVIEW，升级到对应的高质量模型
            if self.initial_model_choice == "PREVIEW":
                target_mode = "RENDER"  # 默认升级到真实感渲染
                print(f"🎯 [智能升级] 分数达到 {self.best_score:.2f}，升级到 RENDER 模型获取更高画质")
            else:
                # 如果初始已经选择了RENDER或ANIME，保持不变
                target_mode = self.initial_model_choice
        else:
            # 探索阶段：持续使用推荐模型
            target_mode = getattr(self, 'initial_model_choice', 'PREVIEW')
        
        # 🎨 [改进] 根据模型类型调整质量后缀（必须在target_mode赋值之后）
        if target_mode == "ANIME":
            quality_suffix = ", masterpiece, best quality, highly detailed, vibrant colors, official art"
        else:
            quality_suffix = ", 8k resolution, masterpiece, photorealistic, sharp focus, highly detailed, cinematic lighting"
        self.params['prompt'] = f"{core_prompt}, {quality_suffix}"
        
        # 应用模型配置
        current_config = MODEL_CONFIGS[target_mode]
        self.params['steps'] = current_config['steps']
        self.params['cfg_scale'] = current_config['cfg_scale']
        self.params['enable_hr'] = current_config['enable_hr']
        if target_mode in ["RENDER", "ANIME"]:
            self.params['hr_scale'] = current_config.get('hr_scale', 2.0)
            self.params['hr_second_pass_steps'] = current_config.get('hr_second_pass_steps', 3)
            self.params['denoising_strength'] = current_config.get('denoising_strength', 0.35)
        
        # 设置模型文件
        target_model_file = BASE_MODELS[target_mode]
        self.params['override_settings'] = {
            "sd_model_checkpoint": target_model_file
        }
        
        # 🎨 [新增] ControlNet约束（如果有参考图）
        if reference_image_path:
            try:
                cn_builder = ControlNetBuilder()
                cn_config = cn_builder.build(
                    reference_image=reference_image_path,
                    cn_type="canny",
                    weight=0.8,
                    guidance_start=0.0,
                    guidance_end=0.8
                )
                # 将 ControlNet 配置合并到 params
                if "alwayson_scripts" in cn_config:
                    if "alwayson_scripts" not in self.params:
                        self.params["alwayson_scripts"] = {}
                    self.params["alwayson_scripts"].update(cn_config["alwayson_scripts"])
                print(f"🎨 ControlNet 已激活: type=canny, weight=0.8, ref={reference_image_path}")
            except Exception as e:
                print(f"⚠️ ControlNet 激活失败: {e}，将继续使用纯文本约束")
        
        # 📊 状态日志
        hr_status = "[HR ON]" if self.params.get('enable_hr') else "[HR OFF]"
        state_tag = f"[{self.state}]"
        print(f"\n⚡ [Iter {self.iteration}] {state_tag} [{target_mode}] {hr_status} Steps={self.params['steps']}, CFG={self.params['cfg_scale']:.2f}")
        print(f"📦 模型: {target_model_file}")
        print(f"⏳ 正在生成图片... (超时限制: {FORGE_TIMEOUT}秒)")
        
        try:
            resp = requests.post(f"{FORGE_URL}/sdapi/v1/txt2img", json=self.params, timeout=FORGE_TIMEOUT)
            if resp.status_code != 200:
                print(f"❌ Forge HTTP {resp.status_code}")
                return None

            data = resp.json()
            images = data.get('images') or []
            if not images:
                print("⚠️ Forge 返回空 images，疑似故障")
                return None

            img_data = base64.b64decode(images[0])
            if len(img_data) < 1000:
                print(f"⚠️ Forge 返回的图片过小 ({len(img_data)} bytes)，疑似异常")
                return None

            # 🛠️ 存储路径：ProjectName_Time/ProjectName_Time_iterX.png
            theme_dir = os.path.join(OUTPUT_DIR, self.project_id)
            os.makedirs(theme_dir, exist_ok=True)

            filename = f"{self.project_id}_iter{self.iteration}.png"
            path = os.path.join(theme_dir, filename)
            
            with open(path, "wb") as f:
                f.write(img_data)

            # 📦 仅保留最近 20 张图片，删除更早的
            try:
                images = [
                    os.path.join(theme_dir, p)
                    for p in os.listdir(theme_dir)
                    if p.lower().endswith(".png")
                ]
                images.sort(key=lambda p: os.path.getmtime(p))
                while len(images) > 20:
                    old_path = images.pop(0)
                    try:
                        os.remove(old_path)
                    except Exception:
                        pass
            except Exception:
                pass

            return path
        except requests.Timeout:
            print("⏱️ Forge 请求超时，可能已卡死")
        except Exception as e:
            print(f"❌ API Error: {e}")
        return None
    
    def run(self, target_score=None, max_iterations=None, reference_image_path=None):
        # 更新参考图路径（如果提供）
        if reference_image_path is not None:
            self.reference_image_path = reference_image_path
        
        if target_score is not None:
            self.target_score = float(target_score)
        if max_iterations is not None:
            self.max_iterations = int(max_iterations)

        print("🚀 DiffuServo V4 启动：智能自适应控制（自动早停）")
        print(f"   目标分数: {self.target_score}")
        print(f"   最大迭代: {self.max_iterations}")
        if self.reference_image_path:
            print(f"   参考图: {self.reference_image_path}")
        
        converged = False
        early_stopped = False
        
        for self.iteration in range(1, self.max_iterations + 1):
            if self.iteration % self.heartbeat_interval == 0:
                if not check_forge_health():
                    print("💥 Forge 健康检查失败，提前停止")
                    break

            # 🎯 【关键改动】准备反馈信息：将前一次迭代的评分传给DeepSeek
            prev_score = None
            prev_feedback = None
            if self.iteration > 1 and len(self.history) > 0:
                prev_entry = self.history[-1]
                prev_score = prev_entry['score']
                # 构建反馈：识别最弱的维度进行改进
                scores = {
                    'Concept': prev_entry['concept'],
                    'Quality': prev_entry['quality'],
                    'Aesthetics': prev_entry['aesthetics'],
                    'Reasonableness': prev_entry['reasonableness']
                }
                weakest = min(scores, key=scores.get)
                prev_feedback = f"Focus on improving {weakest} (currently {scores[weakest]:.2f})"
                
                # 【改进】同时更新各维度最佳值
                for dim_name, dim_score in scores.items():
                    key = dim_name.lower()
                    if key not in self.best_dimensions or dim_score > self.best_dimensions[key]:
                        self.best_dimensions[key] = dim_score

            img_path = self.generate(prev_score=prev_score, prev_feedback=prev_feedback, best_dimensions=self.best_dimensions, reference_image_path=self.reference_image_path)
            if not img_path:
                continue
            
            # 🎯 固定权重：保证评分的可比性
            concept_weight = 0.5  # 所有阶段使用统一权重
            
            res = rate_image(img_path, self.theme, concept_weight=concept_weight, reference_image_path=self.reference_image_path)
            if not isinstance(res, dict) or 'final_score' not in res:
                print("⚠️ 评分失败，跳过")
                continue
            
            current_score = res.get('final_score', 0)
            concept = res.get('concept_score', 0)
            quality = res.get('quality_score', 0)
            aesthetics = res.get('aesthetics_score', 0)
            reasonableness = res.get('reasonableness_score', 0)
            
            # 参考图维度（如果提供了参考图）
            reference_match = res.get('reference_match_score', None)
            style_consistency = res.get('style_consistency', None)
            pose_similarity = res.get('pose_similarity', None)
            composition_match = res.get('composition_match', None)
            character_consistency = res.get('character_consistency', None)
            
            # 安全检查：防止 -1.0 污染 Buffer
            if current_score < 0:
                print("⚠️ 检测到无效分数，跳过梯度更新")
                continue

            history_entry = {
                'iter': self.iteration,
                'score': current_score,
                'concept': concept,
                'quality': quality,
                'aesthetics': aesthetics,
                'reasonableness': reasonableness,
                'state': self.state,
                'image_path': img_path,
                'params_summary': {
                    'steps': self.params['steps'],
                    'cfg_scale': self.params['cfg_scale'],
                    'enable_hr': self.params['enable_hr'],
                    'hr_scale': self.params['hr_scale'],
                    'hr_second_pass_steps': self.params['hr_second_pass_steps'],
                    'seed': self.params['seed']
                }
            }
            
            # 添加参考图维度（如果有）
            if reference_match is not None:
                history_entry['reference_match'] = reference_match
                history_entry['style_consistency'] = style_consistency
                history_entry['pose_similarity'] = pose_similarity
                history_entry['composition_match'] = composition_match
                history_entry['character_consistency'] = character_consistency
            
            self.history.append(history_entry)
            
            self.score_buffer.append(current_score)
            if len(self.score_buffer) > 5:
                self.score_buffer.pop(0)
            
            print(f"📊 评分: 总{current_score:.2f} (内容{concept:.2f} | 画质{quality:.2f})", end="")
            if reference_match is not None:
                print(f" | 参考图{reference_match:.2f}", end="")
            print()
            if reference_match is not None:
                print(
                    "    🧩 参考图分解: "
                    f"风格{style_consistency:.2f} | 姿态{pose_similarity:.2f} | "
                    f"构图{composition_match:.2f} | 角色{character_consistency:.2f}"
                )
            
            if self.state_transition(current_score, concept, quality, aesthetics=aesthetics, reasonableness=reasonableness):
                print(f" → 🎯 达到目标！")
                converged = True
                break
            else:
                print()
            
            self.adaptive_control(res)
            
            if self.check_convergence(current_score):
                early_stopped = True
                break
            
            time.sleep(1)
        
        self._print_final_report(converged, early_stopped)
    
    def _print_final_report(self, converged, early_stopped):
        print("\n" + "="*70)
        if converged:
            print("✅ 结果：达到目标分数")
        elif early_stopped:
            print("⏸️ 结果：早停触发（收敛判定）")
        else:
            print("⏹️ 结果：达到最大迭代次数")
        
        print("="*70)
        print(f"🏆 最优分数: {self.best_score:.2f}")
        
        if self.best_score > 0:
            best_iter_list = [h for h in self.history if h['score'] == self.best_score]
            if best_iter_list:
                best_entry = best_iter_list[0]
                print(f"📍 最优方案来自第 {best_entry['iter']} 代")
                print(f"💾 最优图片路径: {best_entry.get('image_path', 'N/A')}")
        
        print("="*70)


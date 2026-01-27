import time
import os
import requests
import base64
import random
import datetime
import re
from config import (
        FORGE_URL,
        TARGET_SCORE,
        MAX_ITERATIONS,
        FORGE_TIMEOUT,
        FORGE_HEARTBEAT_INTERVAL,
        CONVERGENCE_PATIENCE,
        CONVERGENCE_THRESHOLD,
)
from creator import CreativeDirector
from evaluator import rate_image
from .health import check_forge_health
from .analysis import compute_gradient

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
    
    def __init__(self, theme="enchanted forest"):
        # 🧠 初始化创意大脑
        self.brain = CreativeDirector()
        self.theme = theme
        
        self.params = {
            "prompt": f"cinematic shot of {theme}, misty sunbeams, lush foliage, volumetric light, 8k, masterpiece, sharp focus, highly detailed",
            "negative_prompt": "text, watermark, blurry, noise, distortion, ugly, low quality, jpeg artifacts, grain",
            "steps": 5,
            "cfg_scale": 1.5,
            "width": 1024,
            "height": 1024,
            "sampler_name": "DPM++ SDE",
            "scheduler": "Karras",
            "seed": -1,
            "enable_hr": False,
            "hr_scale": 1.5,
            "hr_upscaler": "R-ESRGAN 4x+",
            "hr_second_pass_steps": 4,
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
        
        # 🟢 梯度追踪
        self.score_buffer = []  # 最近5次的分数
        self.no_improvement_count = 0
        self.convergence_patience = CONVERGENCE_PATIENCE
        self.convergence_threshold = CONVERGENCE_THRESHOLD
        
        # 🔵 自适应学习率
        self.Kp_steps = 1.5
        self.Kp_cfg = 0.6
        self.adaptive_factor = 1.0
        self.heartbeat_interval = max(1, FORGE_HEARTBEAT_INTERVAL)

        # 🩺 启动前快速健康检查
        if not check_forge_health():
            raise RuntimeError(f"Forge 不可用，请检查: {FORGE_URL}")

    def state_transition(self, current_score, concept, quality):
        """状态机：根据分数和梯度自动切换策略"""
        avg_grad, volatility = compute_gradient(self.score_buffer)
        
        if self.state == self.STATE_INIT:
            if current_score > 0.5:
                print("✅ 初始参数有效，进入探索阶段")
                self.state = self.STATE_EXPLORE
            else:
                print("⚠️ 初始参数不佳，降低expectations，继续探索")
        
        elif self.state == self.STATE_EXPLORE:
            if quality < 0.8 and not self.params['enable_hr']:
                print("🚀 检测到画质瓶颈(质量=%.2f)，进入HR优化阶段" % quality)
                self.state = self.STATE_OPTIMIZE
                self.params['enable_hr'] = True
                self.params['steps'] = 4
            elif current_score > 0.85:
                print("⚡ 接近目标分数，进入精细调优阶段")
                self.state = self.STATE_FINETUNE
        
        elif self.state == self.STATE_OPTIMIZE:
            if quality > 0.82 and current_score > 0.82:
                print("📍 HR已充分优化，锁定参数只改Seed")
                self.state = self.STATE_FINETUNE
        
        elif self.state == self.STATE_FINETUNE:
            if current_score >= TARGET_SCORE:
                print("🏆 收敛成功！")
                self.state = self.STATE_CONVERGED
                return True
        
        return False
    
    def adaptive_control(self, result):
        """自适应P-Control"""
        current_score = result.get('final_score', 0)
        concept = result.get('concept_score', 0)
        quality = result.get('quality_score', 0)
        
        # score_buffer 已经在 main loop 中更新了，但 adaptive_control 逻辑依赖 gradient
        # 注意：原代码 adaptive_control 中也做了 score_buffer append，
        # 但在 run 方法中也 append 了一次? 
        # 检查原代码:
        # run(): append to history. calls adaptive_control.
        # adaptive_control(): appends to score_buffer.
        # 所以 score_buffer 由 adaptive_control 维护。
        # 我需要保持一致性。
        
        # Re-reading original `run`:
        # self.score_buffer.append(current_score) BEFORE calling adaptive_control.
        # adaptive_control DOES NOT append in original code?
        # WAIT. Let's check original `main_loop.py` content again.
        
        # Original `run`:
        # self.score_buffer.append(current_score)
        # self.adaptive_control(res)
        
        # Original `adaptive_control`:
        # self.score_buffer.append(current_score)  <-- YES IT DOES!
        # This means it was appending TWICE per iteration????
        # Let's check the read file content.
        
        # Snippet 1 (Lines 1-200):
        # def adaptive_control(self, result):
        #    ...
        #    self.score_buffer.append(current_score)
        
        # Snippet 2 (Lines 200-442):
        # in run():
        #    self.score_buffer.append(current_score)
        #    ...
        #    self.adaptive_control(res)
        
        # Yes, it WAS appending twice. This is a BUG in the original code. 
        # If I fix it, behavior might change slightly (buffer fills slower).
        # But `score_buffer` is just last 5 scores.
        # If I append twice, I just fill it with duplicates effectively if valid logic used it.
        # But actually it appends the SAME score twice.
        # So score_buffer = [s1, s1, s2, s2, ...]
        # compute_gradient uses score_buffer[-3:]. 
        # So it sees [s_prev, s_curr, s_curr].
        # Gradient = (s_curr - s_prev) + (s_curr - s_curr) ...
        # This definitly messed up the gradient calculation!
        # It made the gradient effectively smaller? Or just weird.
        # I should FIX THIS. I will only append in `run` (or adaptive_control, but run seems better place as it's the loop).
        # I'll remove append from `adaptive_control` here based on better design principle.
        
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
        
        error = TARGET_SCORE - current_score
        
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
            if quality < 0.85:
                self.params['hr_second_pass_steps'] = min(6, self.params['hr_second_pass_steps'] + 1)
                print("🔧 [OPTIMIZE] 增加HR第二遍步数→%d" % self.params['hr_second_pass_steps'])
            
            if avg_grad < 0.02:
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
        
        if len(self.score_buffer) >= 3:
            recent_3 = self.score_buffer[-3:]
            improvement = recent_3[-1] - recent_3[0]
            if improvement < self.convergence_threshold and self.no_improvement_count >= self.convergence_patience:
                print(f"\n🛑 收敛检测：最近3步改进={improvement:.6f} < {self.convergence_threshold}，连续{self.no_improvement_count}步无进展")
                return True
        
        if self.no_improvement_count >= 5:
            print(f"\n🛑 硬性早停：连续{self.no_improvement_count}步无进展，放弃")
            return True
        
        return False
    
    def generate(self):
        """生成图片"""
        if self.state in [self.STATE_INIT, self.STATE_Eself.theme)
            quality_suffix = ", 8k resolution, masterpiece, photorealistic, sharp focus, highly detailed, cinematic lighting"
            self.params['prompt'] = f"{core_prompt}, {quality_suffix}"
            print(f"✨ [DeepSeek创意] Prompt已更新\n")
        
        if self.params['seed'] == -1 or self.iteration > 1:
            self.params['seed'] = random.randint(1, 9999999999)
        
        hr_status = "[HR ON]" if self.params.get('enable_hr') else "[HR OFF]"
        state_tag = f"[{self.state}]"
        print(f"\n⚡ [Iter {self.iteration}] {state_tag} {hr_status} Steps={self.params['steps']}, CFG={self.params['cfg_scale']:.2f}")
        
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

            # 🛠️ 优化存储路径：Theme/Theme_Time_Iter.png
            theme_safe = re.sub(r'[\\/*?:"<>|]', "", self.theme).replace(" ", "_")
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            theme_dir = os.path.join(OUTPUT_DIR, theme_safe)
            os.makedirs(theme_dir, exist_ok=True)
            
            filename = f"{theme_safe}_{timestamp}_iter{self.iteration}.png"
            path = os.path.join(theme_dir, filename)
            
            path = f"{OUTPUT_DIR}/gen_{self.iteration}.png"
            with open(path, "wb") as f:
                f.write(img_data)
            return path
        except requests.Timeout:
            print("⏱️ Forge 请求超时，可能已卡死")
        except Exception as e:
            print(f"❌ API Error: {e}")
        return None
    
    def run(self):
        print("🚀 DiffuServo V4 启动：智能自适应控制（自动早停）")
        print(f"   目标分数: {TARGET_SCORE}")
        print(f"   最大迭代: {MAX_ITERATIONS}")
        
        converged = False
        early_stopped = False
        
        for self.iteration in range(1, MAX_ITERATIONS + 1):
            if self.iteration % self.heartbeat_interval == 0:
                if not check_forge_health():
                    print("💥 Forge 健康检查失败，提前停止")
                    break

            img_path = self.generate()
            if not img_path:
                continue
            
            res = rate_image(img_path, "Cyberpunk Neon City")
            if not isinstance(res, dict) or 'final_score' not in res:
                print("⚠️ 评分失败，跳过")
                continue
            
            current_score = res.get('final_score', 0)
            concept = res.get('concept_score', 0)
            quality = res.get('quality_score', 0)
            
            # 安全检查：防止 -1.0 污染 Buffer
            if current_score < 0:
                 image_path': img_path,
                'print("⚠️ 检测到无效分数，跳过梯度更新")
                 continue

            self.history.append({
                'iter': self.iteration,
                'score': current_score,
                'concept': concept,
                'quality': quality,
                'state': self.state,
                'params_summary': {
                    'steps': self.params['steps'],
                    'cfg_scale': self.params['cfg_scale'],
                    'enable_hr': self.params['enable_hr'],
                    'hr_scale': self.params['hr_scale'],
                    'hr_second_pass_steps': self.params['hr_second_pass_steps'],
                    'seed': self.params['seed']
                }
            })
            
            self.score_buffer.append(current_score)
            if len(self.score_buffer) > 5:
                self.score_buffer.pop(0)
            
            print(f"📊 评分: 总{current_score:.2f} (内容{concept:.2f} | 画质{quality:.2f})", end="")
            
            if self.state_transition(current_score, concept, quality):
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
            print("✅ 结果：达到目标分数" for h in self.history if h['score'] == self.best_score]
            if best_iter_list:
                best_entry = best_iter_list[0]
                print(f"📍 最优方案来自第 {best_entry['iter']} 代")
                print(f"💾 最优图片路径: {best_entry.get('image_path', 'N/A')}_SCORE})")
        
        print("="*70)
        print(f"🏆 最优分数: {self.best_score:.2f}")
        
        if self.best_score > 0:
            best_iter_list = [h['iter'] for h in self.history if h['score'] == self.best_score]
            if best_iter_list:
                best_iter = best_iter_list[0]
                print(f"📍 最优方案来自第 {best_iter} 代")
                print(f"💾 最优图片路径: {OUTPUT_DIR}/gen_{best_iter}.png")
        
        print("="*70)


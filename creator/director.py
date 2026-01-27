import os
import time
import random
from openai import OpenAI
from dotenv import load_dotenv
from config import DEEPSEEK_MODEL, DEEPSEEK_MAX_RETRIES, DEEPSEEK_TIMEOUT

# 加载环境变量
load_dotenv()
API_KEY = os.getenv("SILICON_KEY")

class CreativeDirector:
    def __init__(self):
        self.client = OpenAI(
            api_key=API_KEY,
            base_url="https://api.siliconflow.cn/v1"
        )
        self.model = DEEPSEEK_MODEL 

    def brainstorm_prompt(self, base_theme="cyberpunk city"):
        """
        通用版：通过'抽象艺术透镜'让 DeepSeek 适配任何主题
        """
        # 定义【通用】创意透镜 (Universal Creative Lenses)
        # 这些角度适用于任何主题（无论是赛博朋克、自然风光还是二次元人像）
        universal_lenses = [
            "Emphasis on Lighting & Atmosphere: (e.g., cinematic, volumetric, moody, golden hour, bioluminescent)",
            "Emphasis on Composition & Perspective: (e.g., wide angle, macro, dutch angle, symmetry, depth of field)",
            "Emphasis on Material & Texture: (e.g., organic, metallic, fluid, rough, intricate details)",
            "Emphasis on Color Palette: (e.g., monochromatic, vibrant contrast, pastel, dark & gritty)",
            "Emphasis on Dynamic Action/Flow: (e.g., motion blur, wind blowing, exploding, floating)",
            "Emphasis on Emotion/Vibe: (e.g., mysterious, peaceful, chaotic, horror, ethereal)"
        ]
        
        chosen_lens = random.choice(universal_lenses)
        print(f"🤖 [DeepSeek] 思考切入点: {base_theme} + [{chosen_lens.split(':')[0]}]")

        system_instructions = f"""
        Role: Expert Stable Diffusion Prompt Engineer.
        Task: Create a vivid, high-quality prompt for the user's concept, applying a specific artistic constraint.

        User Concept: "{base_theme}"
        Artistic Constraint: {chosen_lens}

        Response Rules:
        1. Output pure prompt text ONLY. No intros, no markdown code blocks (no ```text, no ``` symbols).
        2. Format: English keywords, comma-separated.
        3. ADAPTABILITY: You must interpret the 'Constraint' specifically for the 'User Concept'.
           - If concept is "Forest" + "Material": Focus on bark, moss, dew drops.
           - If concept is "Robot" + "Material": Focus on rust, chrome, oil.
        4. Length: Dense and rich (approx 40-70 words).
        """

        for attempt in range(DEEPSEEK_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": "Generate prompt."}
                    ],
                    temperature=1.2,  # 保持高创造性
                    max_tokens=200,
                    timeout=DEEPSEEK_TIMEOUT
                )

                creative_content = response.choices[0].message.content.strip()

                # 清洗数据
                creative_content = creative_content.replace("```text", "").replace("```", "").strip()

                print(f"✨ [灵感生成] {creative_content[:60]}...")
                return creative_content

            except Exception as e:
                if attempt < DEEPSEEK_MAX_RETRIES - 1:
                    wait = min(2 ** attempt, 10)
                    print(f"⚠️ DeepSeek 失败({attempt+1}/{DEEPSEEK_MAX_RETRIES}): {e}，{wait}s后重试")
                    time.sleep(wait)
                else:
                    print(f"❌ DeepSeek 耗尽重试次数")

        # 降级兜底：使用通用修饰词
        return f"cinematic shot of {base_theme}, highly detailed, masterpiece, 8k resolution, dynamic lighting"

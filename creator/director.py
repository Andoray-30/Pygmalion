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
        让 DeepSeek 把简单主题通过‘脑暴’变成 SDXL 提示词
        """
        focus_angles = [
            "Emphasis on atmosphere: heavy rain, fog, noir lighting, moody",
            "Emphasis on architecture: mega-structures, brutalism, holographic billboards",
            "Emphasis on chaos: crowded streets, vendors, cables everywhere, trash",
            "Emphasis on color: neon pink and cyan contrast, volumetric lighting",
            "Emphasis on tech: drones, cyborgs, futuristic vehicles"
        ]
        chosen_focus = random.choice(focus_angles)

        print(f"🤖 [DeepSeek] 正在思考创意方向: {chosen_focus} ...")

        system_instructions = f"""
        Role: Expert Stable Diffusion Prompt Engineer.
        Task: Expand the user's concept into a high-quality visual description prompt.
        
        Input Concept: "{base_theme}"
        Creative Constraint: {chosen_focus}
        
        Response Rules:
        1. Output pure prompt text ONLY. No "Here is the prompt", no markdown, no quotes.
        2. Format: English keywords, comma-separated.
        3. Content requirements: Detailed visual elements, lighting, style, composition.
        4. Length: Keep it dense and rich (approx 50-80 words).
        """

        for attempt in range(DEEPSEEK_MAX_RETRIES):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": "Generate now."}
                    ],
                    temperature=1.2,
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
                    print(f"❌ DeepSeek 连续失败 {DEEPSEEK_MAX_RETRIES} 次，使用降级Prompt")

        return f"cinematic shot of {base_theme}, highly detailed, neon lights, masterpiece"

import os
import time
import random
import httpx
from dotenv import load_dotenv
from pkg.infrastructure.config import DEEPSEEK_MODEL, DEEPSEEK_MAX_RETRIES, DEEPSEEK_TIMEOUT

# 加载环境变量
load_dotenv()
API_KEY = os.getenv("SILICON_KEY")

class CreativeDirector:
    def __init__(self):
        self.api_key = API_KEY
        self.base_url = "https://api.siliconflow.cn/v1"
        self.model = DEEPSEEK_MODEL
        self.recommended_model = None  # 缓存推荐的模型
        self.theme_category = None     # 缓存主题分类 

    def analyze_theme_and_recommend_model(self, theme):
        """
        使用 DeepSeek 分析主题意图并推荐最佳底模（三模型策略）。
        优先理解用户期望的艺术风格，而非简单分类主题内容。
        返回: {"intent": "...", "model": "PREVIEW/RENDER/ANIME", "reason": "..."}
        """
        system_prompt = """
You are an AI model selector for Stable Diffusion image generation.

🎯 CRITICAL: Your PRIMARY task is to understand the USER'S ARTISTIC INTENT (realistic vs stylized), NOT just the subject matter.

Available Models:
1. PREVIEW (SDXL Turbo): 
   - Ultra-fast 1-step generation
   - Use ONLY for: Initial exploration, simple test concepts
   - Limitation: Lower quality, use sparingly
   
2. RENDER (Juggernaut XL - Photorealistic):
   - 5-step photographic realism
   - Use when user wants: Realistic photos, professional product shots, nature photography, architectural renders
   - Strength: Lighting, textures, real-world accuracy
   - Keywords indicating this: "realistic", "photo", "cinematic", "professional", "lifelike", "detailed photography"
   
3. ANIME (Animagine XL - Stylized Art):
   - 28-step anime/illustration style
   - Use when user wants: Anime characters, manga art, game CG, cute/kawaii style, fantasy illustrations, cel-shaded art
   - Strength: Clean lines, vibrant colors, artistic expression
   - Keywords indicating this: "anime", "manga", "cartoon", "illustration", "cute", "chibi", "fantasy art", "game character"

🔍 Decision Logic:
- If theme mentions "anime/manga/cartoon/illustration/cute/chibi" → ANIME
- If theme implies photorealism/real-world accuracy → RENDER  
- If theme is ambiguous (e.g., "sunset", "dragon") → Infer from context:
  * "龙舌兰日出" (Tequila Sunrise cocktail) → RENDER (real product)
  * "魔法森林" (Magic Forest) → ANIME (fantasy illustration)
  * "女孩" (Girl) → Check if implies photo or anime style

Output JSON ONLY (no markdown):
{
  "intent": "realistic|anime|stylized|ambiguous",
  "model": "PREVIEW|RENDER|ANIME",
  "reason": "<25 words max explaining WHY this model fits the artistic intent>"
}
"""
        
        for attempt in range(3):  # 降低重试次数加快速度
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Theme: {theme}"}
                    ],
                    "temperature": 0.3,  # 低温度保证稳定输出
                    "max_tokens": 100
                }
                
                with httpx.Client(timeout=15) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()
                
                content = data['choices'][0]['message']['content'].strip()
                # 清理可能的markdown
                content = content.replace("```json", "").replace("```", "").strip()
                
                import json
                result = json.loads(content)
                
                # 验证结果格式
                if "model" in result and result["model"] in ["PREVIEW", "RENDER", "ANIME"]:
                    self.recommended_model = result["model"]
                    self.theme_category = result.get("intent", "unknown")
                    print(f"🤖 [模型推荐] {result.get('intent', 'N/A')} → {result['model']} | {result['reason']}")
                    return result
                    
            except Exception as e:
                if attempt < 2:
                    time.sleep(1)
                else:
                    print(f"⚠️ 模型推荐失败: {e}")
        
        # 降级：默认使用PREVIEW（快速模式）
        fallback = {"intent": "unknown", "model": "PREVIEW", "reason": "Fallback to fast mode"}
        self.recommended_model = "PREVIEW"
        return fallback

    def generate_project_name(self, base_theme=""):
        """
        使用 DeepSeek 生成简短英文项目名，用于文件命名。
        规则：2-4 个英文单词，短横线或下划线连接。
        """
        theme = (base_theme or "").strip()
        if not theme:
            return "untitled_project"

        system_instructions = f"""
        Role: Creative naming assistant.
        Task: Generate a short English project name for image generation.

        User Concept: "{theme}"

        Response Rules:
        1. Output name ONLY. No punctuation, no quotes.
        2. English words only, 2-4 words.
        3. Use simple, descriptive nouns/adjectives.
        4. Use space between words (no hyphen/underscore).
        """

        for attempt in range(DEEPSEEK_MAX_RETRIES):
            try:
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": "Generate a short project name."}
                    ],
                    "temperature": 0.6,
                    "max_tokens": 20
                }
                with httpx.Client(timeout=DEEPSEEK_TIMEOUT) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()

                name = data['choices'][0]['message']['content'].strip()
                name = name.replace("```", "").strip()
                # 仅保留英文与空格
                name = "".join(ch for ch in name if ch.isalpha() or ch == " ")
                name = " ".join(name.split())
                if name:
                    return name
            except Exception as e:
                if attempt < DEEPSEEK_MAX_RETRIES - 1:
                    wait = min(2 ** attempt, 10)
                    print(f"⚠️ DeepSeek 命名失败({attempt+1}/{DEEPSEEK_MAX_RETRIES}): {e}，{wait}s后重试")
                    time.sleep(wait)
                else:
                    print("❌ DeepSeek 命名耗尽重试次数")

        return "untitled_project"

    def brainstorm_prompt(self, base_theme="enchanted forest", feedback_context="", use_random=True):
        """
        通用版：通过'抽象艺术透镜'让 DeepSeek 适配任何主题
        Args:
            base_theme: 基础主题（由controller传入实际theme）
            feedback_context: 来自视觉模型的反馈信息 (用于持续优化)
            use_random: 是否使用随机镜头（OPTIMIZE阶段关闭以稳定收敛）
        """
        # 【改进】OPTIMIZE期间使用固定镜头，避免随机导致方向偏离
        if use_random:
            # EXPLORE阶段：使用权重随机镜头，优先主体相关镜头
            universal_lenses = [
                ("Emphasis on Lighting & Atmosphere: (e.g., cinematic, volumetric, moody, golden hour, bioluminescent)", 25),
                ("Emphasis on Material & Texture: (e.g., organic, metallic, fluid, rough, intricate details)", 25),
                ("Emphasis on Color Palette: (e.g., monochromatic, vibrant contrast, pastel, dark & gritty)", 20),
                ("Emphasis on Dynamic Action/Flow: (e.g., motion blur, wind blowing, exploding, floating)", 15),
                ("Emphasis on Emotion/Vibe: (e.g., mysterious, peaceful, chaotic, horror, ethereal)", 10),
                ("Emphasis on Composition & Perspective: (e.g., wide angle, macro, dutch angle, symmetry, depth of field)", 5)  # 降低权重，避免风景化
            ]
            # 加权随机选择
            lenses, weights = zip(*universal_lenses)
            chosen_lens = random.choices(lenses, weights=weights, k=1)[0]
        else:
            # OPTIMIZE阶段：固定使用"高质量"镜头组合
            chosen_lens = "Emphasis on Lighting & Atmosphere & Technical Excellence: Focus on cinematic volumetric lighting, sharp focus, intricate details, and professional-grade composition"
        
        print(f"🤖 [DeepSeek] 思考切入点: {base_theme} + [{chosen_lens.split(':')[0]}]")

        system_instructions = f"""
        Role: Expert Stable Diffusion Prompt Engineer.
        Task: Create a vivid, high-quality prompt for the user's concept, applying a specific artistic constraint.

        User Concept: "{base_theme}"
        Artistic Constraint: {chosen_lens}
        {feedback_context}

        Response Rules:
        1. Output pure prompt text ONLY. No intros, no markdown code blocks (no ```text, no ``` symbols).
        2. Format: English keywords, comma-separated.
        3. **CRITICAL: The prompt MUST explicitly include core elements from the User Concept as concrete nouns/objects.**
           - BAD: "sunrise colors" (too abstract)
           - GOOD: "tequila sunrise cocktail in glass" (specific object)
        4. ADAPTABILITY: Interpret the 'Constraint' specifically for the 'User Concept'.
           - If concept is "Forest" + "Material": Focus on bark, moss, dew drops.
           - If concept is "Robot" + "Material": Focus on rust, chrome, oil.
           - If concept is "Tequila Sunrise" + "Composition": Focus on cocktail glass, layered colors, NOT landscape.
        5. Length: Dense and rich (approx 40-70 words).
        6. If feedback provided: Incorporate suggestions or corrections. 
           - **CRITICAL**: If feedback identifies a PROBLEM (e.g. 'looks like a wall', 'blurry', 'bad eyes'), your prompt must EXPLICITLY solve it through descriptive keywords (e.g. 'deep depth of field', 'volumetric 3D space', 'razor sharp detail').
           - Never repeat negative feedback in the prompt; instead, provide the positive solution.
        """

        for attempt in range(DEEPSEEK_MAX_RETRIES):
            try:
                # 使用httpx直接调用API，避免OpenAI库的平台检测问题
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_instructions},
                        {"role": "user", "content": "Generate prompt."}
                    ],
                    "temperature": 1.2,
                    "max_tokens": 200
                }
                
                with httpx.Client(timeout=DEEPSEEK_TIMEOUT) as client:
                    response = client.post(
                        f"{self.base_url}/chat/completions",
                        headers=headers,
                        json=payload
                    )
                    response.raise_for_status()
                    data = response.json()

                creative_content = data['choices'][0]['message']['content'].strip()

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

import requests
import base64
import time

# 🛠️ 配置区
# 如果你在本机运行，用 127.0.0.1
# 如果你在 E5 上运行，请改成 4060 的局域网 IP (如 192.168.1.5)
API_URL = "http://127.0.0.1:7860" 

def save_encoded_image(b64_image, output_path):
    with open(output_path, "wb") as f:
        f.write(base64.b64decode(b64_image))

def first_contact():
    print(f"📡 正在呼叫 Pygmalion 节点: {API_URL} ...")
    
    # 1. 定义 payload (给画师的指令)
    # 针对 Juggernaut Lightning 的优化参数
    payload = {
        # ✅ 正面提示词：增加了光影、构图和画质描述
        "prompt": "cinematic shot of a cyberpunk street, rain, neon lights, reflection on wet ground, soft lighting, depth of field, 8k, photorealistic, masterpiece, highly detailed",
        
        # ✅ 负面提示词（关键！）：这是"去污粉"，能把画面擦干净
        "negative_prompt": "text, watermark, ugly, blurry, noise, distortion, messy, bad composition, low quality, jpeg artifacts, cartoon, 3d render, plastic",
        
        # ✅ Juggernaut Lightning 专用参数
        "steps": 4,           # Lightning 只需要 4-6 步
        "cfg_scale": 1.5,     # 保持低 CFG
        "width": 1024,        # 必须 1024
        "height": 1024,
        "sampler_name": "DPM++ SDE",  # 强烈建议换成这个采样器，比 Euler a 细腻
        "scheduler": "Karras",        # 配套调度器
        "batch_size": 1
    }

    try:
        # 2. 发送请求（添加超时设置）
        start_time = time.time()
        response = requests.post(f"{API_URL}/sdapi/v1/txt2img", json=payload, timeout=30)
        response.raise_for_status()  # 直接对非 2xx 状态码抛错
        
        # 3. 解析响应并验证数据
        data = response.json()
        images = data.get("images") or []
        
        if not images:
            print("❌ 响应中没有 images 字段或为空")
            print(f"响应内容: {data}")
            return
        
        # 4. 保存图片
        image_b64 = images[0]
        save_encoded_image(image_b64, "first_contact.png")
        print(f"✅ 成功！图片已保存为 first_contact.png")
        print(f"⚡ 耗时: {time.time() - start_time:.2f} 秒")
        
    except requests.Timeout:
        print("❌ 请求超时，请检查 Forge 是否在运行或网络连接")
    except requests.RequestException as e:
        print(f"❌ 网络/HTTP 错误: {e}")
    except (ValueError, KeyError, IndexError) as e:
        print(f"❌ 解析响应失败: {e}")
        print("请检查后端返回内容是否正确")
    except Exception as e:
        print(f"❌ 发生错误: {e}")
        print("请检查：\n1. Forge 黑框是否开着？\n2. IP地址填对了吗？\n3. 防火墙关了吗？")

if __name__ == "__main__":
    first_contact()
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Pygmalion DiffuServo V4 - Gradio Web UI
实时流式生成展示 - 边生成边显示图片
"""

import gradio as gr
from pathlib import Path
from PIL import Image
import os
import sys
from typing import Generator, Tuple, List
import threading
import time
import threading
import time

# 添加父目录到 Python 路径，使得能导入 core 模块
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core import DiffuServoV4
from core.state_manager import GenerationStateManager


def run_generation_stream(theme, target_score, max_iterations, quick_mode, progress=gr.Progress()):
    """
    运行图片生成 - 流式版本，实时返回中间结果
    每完成一个迭代就立即显示，而不是等待全部完成
    """
    try:
        # 验证输入
        if not theme or len(theme.strip()) == 0:
            yield None, 0.0, "❌ 错误：主题不能为空", []
            return
        
        target_score = float(target_score)
        max_iterations = int(max_iterations)
        
        if target_score < 0.7 or target_score > 0.95:
            yield None, 0.0, "❌ 错误：目标分数必须在 0.7-0.95 之间", []
            return
        
        if max_iterations < 5 or max_iterations > 30:
            yield None, 0.0, "❌ 错误：最大迭代数必须在 5-30 之间", []
            return
        
        # 模式策略
        effective_target = target_score
        effective_iters = max_iterations
        mode_label = "思考模式"
        if quick_mode:
            effective_iters = min(max_iterations, 8)
            effective_target = min(target_score, 0.88)
            mode_label = "快速模式"
        else:
            effective_iters = max(max_iterations, 15)
            effective_target = max(target_score, 0.90)
        
        print(f"\n🚀 启动生成：主题={theme}, 目标分数={effective_target}, 最大迭代={effective_iters}, 模式={mode_label}")
        
        # 初始化会话管理器
        state_manager = GenerationStateManager()
        session_id = state_manager.create_session(
            theme=theme,
            target_score=effective_target,
            max_iterations=effective_iters,
            quick_mode=(mode_label == "快速模式")
        )
        print(f"📋 会话已创建: {session_id}")
        
        # 创建控制器
        bot = DiffuServoV4(theme=theme)
        
        # 在后台线程中运行生成
        generation_error = [None]
        
        def run_generation():
            try:
                bot.run(target_score=effective_target, max_iterations=effective_iters)
            except Exception as e:
                print(f"⚠️ 后台生成错误: {e}")
                import traceback
                traceback.print_exc()
                generation_error[0] = e
        
        generation_thread = threading.Thread(target=run_generation, daemon=True)
        generation_thread.start()
        
        # 🎯 实时监听 history 更新
        ranked_images = []
        best_score = 0.0
        best_image_path = None
        last_history_len = 0
        monitor_timeout = 0
        max_wait_time = effective_iters * 120
        
        print(f"📡 开始监听实时更新...")
        
        # 实时监听模式：定期检查 bot.history 是否有新记录
        while True:
            current_history_len = len(bot.history)
            
            # 处理新的历史记录
            if current_history_len > last_history_len:
                print(f"📊 检测到 {current_history_len - last_history_len} 个新迭代")
                
                for i in range(last_history_len, current_history_len):
                    entry = bot.history[i]
                    
                    if 'image_path' in entry and entry.get('score') is not None:
                        score = float(entry['score'])
                        ranked_images.append((entry['image_path'], score))
                        ranked_images.sort(key=lambda x: x[1], reverse=True)
                        
                        if score > best_score:
                            best_score = score
                            best_image_path = ranked_images[0][0]
                        
                        print(f"  迭代 {i+1}: 分数={score:.2f}, 最优={best_score:.2f}")
                        
                        # 保存到会话状态
                        state_manager.add_iteration(
                            iteration_num=i + 1,
                            image_path=best_image_path,
                            score=best_score,
                            model=entry.get('model', 'unknown'),
                            prompt=entry.get('prompt', '')
                        )
                        
                        # 实时构建画廊
                        gallery_items = [(path, f"Score: {score:.2f}") for path, score in ranked_images]
                        
                        # 更新进度
                        progress((i + 1) / effective_iters, desc=f"迭代 {i+1}/{effective_iters}")
                        
                        # 构建实时状态信息
                        status_msg = f"⏳ 生成中...\n"
                        status_msg += f"模式: {mode_label}\n"
                        status_msg += f"当前最优: {best_score:.2f}\n"
                        status_msg += f"已完成: {i+1}/{effective_iters} 迭代\n"
                        status_msg += f"状态: 处理中"
                        
                        # 🎯 实时产出结果
                        yield best_image_path, best_score, status_msg, gallery_items
                
                last_history_len = current_history_len
                monitor_timeout = 0
            
            # 检查是否完成
            if not generation_thread.is_alive():
                print(f"📍 生成线程已完成")
                time.sleep(0.5)
                final_history_len = len(bot.history)
                if final_history_len > last_history_len:
                    continue
                break
            
            # 等待后再检查
            time.sleep(1)
            monitor_timeout += 1
            
            # 防止无限等待
            if monitor_timeout > max_wait_time:
                print(f"⚠️ 生成超时（{max_wait_time}秒），停止等待")
                break
        
        # 最终结果
        print(f"📋 保存会话...")
        state_manager.complete_session(session_id)
        gallery_items = [(path, f"Score: {score:.2f}") for path, score in ranked_images] if ranked_images else []
        final_status = f"✅ 完成！\n"
        final_status += f"模式: {mode_label}\n"
        final_status += f"最优分数: {best_score:.2f}\n"
        final_status += f"总迭代数: {len(bot.history)}\n"
        final_status += f"最终状态: 完成\n"
        final_status += f"📋 会话 ID: {session_id}"
        
        yield best_image_path, best_score, final_status, gallery_items
    
    except Exception as e:
        import traceback
        error_msg = f"❌ 错误: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        if 'session_id' in locals():
            state_manager.fail_session(session_id, error_msg)
        yield None, 0.0, error_msg, []


def get_session_history():
    """获取所有会话历史"""
    state_manager = GenerationStateManager()
    sessions = state_manager.list_sessions(limit=20)
    
    if not sessions:
        return "📭 暂无生成历史"
    
    history_text = "# 📜 生成历史\n\n"
    for session in sessions:
        history_text += f"## {session.get('theme', 'Unknown')} - {session.get('created_at', '')}\n"
        history_text += f"- 状态: {session.get('status', 'unknown')}\n"
        history_text += f"- 最优分数: {session.get('best_score', 0):.2f}\n"
        history_text += f"- 迭代数: {session.get('iterations', 0)}\n\n"
    
    return history_text


def recover_latest_session():
    """恢复最新的生成会话"""
    state_manager = GenerationStateManager()
    latest = state_manager.get_latest_session()
    
    if not latest:
        return "深色", 0.0, "❌ 暂无可恢复的会话", [], None, 0.0
    
    # 获取迭代数据
    iterations = latest.get('iterations', [])
    iterations.sort(key=lambda x: x.get('iteration', 0))
    
    # 构建画廊
    gallery_items = []
    best_image = None
    best_score = 0.0
    
    for it in iterations:
        path = it.get('image_path')
        score = it.get('score', 0)
        if path:
            gallery_items.append((path, f"Iteration {it.get('iteration', 0)}: {score:.2f}"))
            if score > best_score:
                best_score = score
                best_image = path
    
    # 构建状态信息（移到循环外面，避免重复定义）
    status = f"✅ 已恢复会话\n"
    status += f"主题: {latest.get('theme', 'Unknown')}\n"
    status += f"最优分数: {best_score:.2f}\n"
    status += f"总迭代数: {len(iterations)}\n"
    status += f"创建时间: {latest.get('created_at', '')}\n"
    status += f"状态: {latest.get('status', 'unknown')}"
    
    return "浅色", best_score, status, gallery_items, best_image, best_score


# 创建 Gradio 界面
with gr.Blocks(title="Pygmalion AI 图片生成工作台") as demo:
    
    gr.Markdown("""
    # 🎨 Pygmalion DiffuServo V4
    
    **智能自适应控制的 AI 图片生成系统 - 实时流式展示**
    
    ✨ 特性：
    - 🤖 DeepSeek 创意提示词生成
    - 🧠 Qwen 视觉评估反馈（4×72B+多模态模型轮换）
    - 🎯 自动化收敛优化
    - 📊 三模型智能选择 (PREVIEW / RENDER / ANIME)
    - 🔄 **实时流式显示** - 边生成边展示每一个迭代结果
    - 💾 **会话持久化** - 页面刷新不丢失进度
    
    """)
    
    with gr.Tabs():
        with gr.TabItem("🚀 新建生成"):
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### ⚙️ 参数配置")
                    
                    # 主题输入
                    theme_input = gr.Textbox(
                        label="🎭 生成主题",
                        placeholder="例如：enchanted forest, 动漫女孩, cyberpunk city...",
                        value="enchanted forest",
                        lines=2
                    )
                    
                    # 目标分数
                    target_score = gr.Slider(
                        minimum=0.7,
                        maximum=0.95,
                        step=0.01,
                        value=0.90,
                        label="🎯 目标分数"
                    )
                    
                    # 最大迭代次数
                    max_iterations = gr.Slider(
                        minimum=5,
                        maximum=30,
                        step=1,
                        value=15,
                        label="🔄 最大迭代次数"
                    )
                    
                    # 快速模式开关
                    quick_mode = gr.Checkbox(
                        label="⚡ 启用快速模式（速度优先）",
                        value=False
                    )
                    
                    # 运行按钮
                    run_btn = gr.Button(
                        "🚀 开始生成",
                        variant="primary",
                        size="lg"
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("### 📸 实时生成结果")
                    
                    # 输出图片（实时更新）
                    output_image = gr.Image(
                        label="🖼️ 最优结果",
                        type="filepath"
                    )
                    
                    # 结果统计
                    with gr.Row():
                        output_score = gr.Number(
                            label="📊 最优分数",
                            precision=2
                        )
                        output_status = gr.Textbox(
                            label="📝 实时状态",
                            lines=4,
                            interactive=False
                        )
                    
                    # 实时画廊（高分优先）
                    output_gallery = gr.Gallery(
                        label="🖼️ 结果画廊（高分优先 - 实时更新）",
                        columns=4,
                        height=400
                    )
            
            # 绑定按钮点击事件 - 使用流式生成
            run_btn.click(
                fn=run_generation_stream,
                inputs=[theme_input, target_score, max_iterations, quick_mode],
                outputs=[output_image, output_score, output_status, output_gallery]
            )
        
        with gr.TabItem("💾 会话恢复"):
            gr.Markdown("### 🔄 恢复上一次生成会话")
            gr.Markdown("如果网页刷新或中断，可以从这里恢复最近的生成过程")
            
            with gr.Row():
                recover_btn = gr.Button("📥 恢复最新会话", variant="primary", size="lg")
                clear_btn = gr.Button("🗑️ 清空历史", variant="secondary")
            
            with gr.Row():
                with gr.Column(scale=1):
                    gr.Markdown("### 📊 会话恢复数据")
                    recovery_status = gr.Textbox(
                        label="📝 会话状态",
                        lines=6,
                        interactive=False
                    )
                    recovery_score = gr.Number(
                        label="📈 最优分数",
                        precision=2
                    )
                
                with gr.Column(scale=2):
                    gr.Markdown("### 🖼️ 历史图库")
                    recovery_gallery = gr.Gallery(
                        label="📸 已生成的图片",
                        columns=4,
                        height=400
                    )
            
            recovery_image = gr.Image(
                label="🖼️ 最优结果",
                type="filepath",
                visible=False
            )
            
            # 恢复按钮事件
            recover_btn.click(
                fn=recover_latest_session,
                outputs=[gr.State(), recovery_score, recovery_status, recovery_gallery, recovery_image, gr.State()]
            )
            
            with gr.Accordion("📜 生成历史", open=False):
                history_display = gr.Markdown(get_session_history())
                refresh_history_btn = gr.Button("🔄 刷新历史")
                refresh_history_btn.click(fn=get_session_history, outputs=history_display)
    
    # 底部信息
    gr.Markdown("""
    ---
    
    ### 💡 使用提示
    
    1. **实时显示**：图片生成完成后会立即展示在画廊中，无需等待全部迭代完成
    2. **自动模型选择**：系统会根据主题自动选择最佳底模 (PREVIEW/RENDER/ANIME)
    3. **生成时间**：平均每次迭代 30-50 秒，请耐心等待实时更新
    4. **快速模式**：启用可加快速度但可能降低质量
    5. **会话恢复**：即使网页刷新，也能从上一次的进度继续或重新查看已生成的结果
    
    ### 📌 主题示例
    
    - **真实感**：`龙舌兰日出` → RENDER 模型
    - **动漫风格**：`动漫女孩` `魔法少女` → ANIME 模型  
    - **通用主题**：`enchanted forest` `cyberpunk city` → 自动选择
    
    ### 📊 API 配额说明
    
    - **ModelScope 免费 API**：2000次/天（4个模型 × 500次/天）
    - **自动轮换**：每150次调用切换一次模型，分散配额
    - **自动降级**：超配额时自动切换到 SiliconFlow 付费 API
    - **429 处理**：遇到速率限制立即切换 API，无重试等待
    
    """)


if __name__ == "__main__":
    server_port = 7861
    print("=" * 60)
    print("  Pygmalion AI Picture Generation Workspace")
    print(f"  URL: http://localhost:{server_port}")
    print("  Press Ctrl+C to exit")
    print("=" * 60)
    
    demo.launch(
        server_name="0.0.0.0",
        server_port=server_port,
        share=False,
        show_error=True,
        theme=gr.themes.Soft()
    )

"""
Pygmalion AI Web 应用后端 - WebSocket 增强版本
支持实时双向通信的对话式生成界面
"""

import os
import json
import uuid
import threading
import time
from datetime import datetime
from pathlib import Path

from flask import Flask, render_template, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
from werkzeug.exceptions import HTTPException
import logging

# 导入核心系统
import sys
# Ensure project root is in path: server.py -> interface -> pkg -> Pygmalion(Root)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

try:
    from pkg.system.engine import DiffuServoV4
    from pkg.infrastructure.config.settings import JUDGE_MODELS
    CORE_AVAILABLE = True
except ImportError as e:
    logger_temp = logging.getLogger(__name__)
    logger_temp.warning(f"⚠️ 核心模块加载失败: {e}，部分功能将不可用")
    CORE_AVAILABLE = False

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 初始化 Flask 应用
app = Flask(__name__, 
            template_folder='web/templates',
            static_folder='web/static',
            static_url_path='/static')

# 添加自定义目录服务：用于展示 evolution_history 下的生成图片
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
OUTPUT_DIR_PATH = os.path.join(ROOT_DIR, "evolution_history")
REFERENCE_UPLOAD_DIR = os.path.join(ROOT_DIR, "evolution_history", "references")
os.makedirs(REFERENCE_UPLOAD_DIR, exist_ok=True)

@app.route('/outputs/<path:filename>')
def serve_outputs(filename):
    """服务生成后的图片文件"""
    return send_from_directory(OUTPUT_DIR_PATH, filename)

@app.route('/api/upload_reference', methods=['POST'])
def upload_reference():
    """上传参考图接口"""
    try:
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '没有找到文件'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '文件名为空'}), 400
        
        # 生成安全的文件名
        import uuid
        from werkzeug.utils import secure_filename
        ext = os.path.splitext(secure_filename(file.filename))[1]
        safe_filename = f"ref_{uuid.uuid4().hex[:8]}{ext}"
        filepath = os.path.join(REFERENCE_UPLOAD_DIR, safe_filename)
        
        # 保存文件
        file.save(filepath)
        
        # 返回相对路径用于前端显示
        relative_path = f"references/{safe_filename}"
        
        logger.info(f"✅ 参考图上传成功: {safe_filename}")
        return jsonify({
            'success': True,
            'path': filepath,
            'url': f"/outputs/{relative_path}"
        })
    except Exception as e:
        logger.error(f"❌ 参考图上传失败: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

# 配置 SocketIO
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'pygmalion-secret-key-2025')
socketio = SocketIO(app, 
                   cors_allowed_origins="*",
                   ping_timeout=60,
                   ping_interval=25)

CORS(app)

# 全局变量
active_sessions = {}  # 存储活跃的生成会话
pygmalion_core = None  # DiffuServoV4 核心系统


class GenerationSession:
    """生成会话管理类"""
    
    def __init__(self, session_id, theme, target_score, max_iterations, quick_mode, reference_image_path=None):
        self.session_id = session_id
        self.theme = theme
        self.target_score = target_score
        self.max_iterations = max_iterations
        self.quick_mode = quick_mode
        self.reference_image_path = reference_image_path
        self.current_iteration = 0
        self.best_score = 0.0
        self.best_image = None
        self.images = []
        self.history = []
        self.is_running = False
        self.created_at = datetime.now()
        self.client_sid = None
        self.feedback = [] # 存储用户实时反馈
        
    def log_event(self, event_type, content):
        """记录事件"""
        self.history.append({
            'timestamp': datetime.now().isoformat(),
            'type': event_type,
            'content': content
        })
    
    def emit_message(self, msg_type, data):
        """向客户端发送消息"""
        if self.client_sid:
            socketio.emit('message', {
                'type': msg_type,
                'data': data
            }, room=self.client_sid)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'session_id': self.session_id,
            'theme': self.theme,
            'target_score': self.target_score,
            'max_iterations': self.max_iterations,
            'current_iteration': self.current_iteration,
            'best_score': self.best_score,
            'best_image': self.best_image,
            'image_count': len(self.images),
            'is_running': self.is_running,
            'created_at': self.created_at.isoformat()
        }


def init_pygmalion_core():
    """初始化 Pygmalion 核心系统"""
    global pygmalion_core
    if not CORE_AVAILABLE:
        logger.warning("⚠️ 核心模块不可用")
        return False
    
    try:
        pygmalion_core = DiffuServoV4()
        logger.info("✅ Pygmalion 核心系统已初始化")
        return True
    except Exception as e:
        logger.error(f"❌ 初始化失败: {e}")
        return False


# ==================== HTTP 路由 ====================

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')


@app.route('/api/status')
def get_status():
    """获取系统状态"""
    return jsonify({
        'status': 'running' if pygmalion_core else 'initializing',
        'active_sessions': len(active_sessions),
        'system_info': {
            'judgeModels': list(JUDGE_MODELS.keys()) if CORE_AVAILABLE else [],
        }
    })


@app.route('/api/sessions', methods=['GET'])
def list_sessions():
    """获取所有会话"""
    sessions = [s.to_dict() for s in active_sessions.values()]
    return jsonify({'sessions': sessions})


@app.route('/api/sessions/<session_id>', methods=['GET'])
def get_session(session_id):
    """获取特定会话信息"""
    if session_id not in active_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = active_sessions[session_id]
    return jsonify(session.to_dict())


@app.route('/api/sessions/<session_id>/history', methods=['GET'])
def get_session_history(session_id):
    """获取会话历史"""
    if session_id not in active_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = active_sessions[session_id]
    return jsonify({'history': session.history})


@app.route('/api/images/<session_id>', methods=['GET'])
def get_session_images(session_id):
    """获取会话的所有图片"""
    if session_id not in active_sessions:
        return jsonify({'error': '会话不存在'}), 404
    
    session = active_sessions[session_id]
    sorted_images = sorted(session.images, key=lambda x: x['score'], reverse=True)
    return jsonify({
        'images': sorted_images,
        'best_score': session.best_score,
        'best_image': session.best_image
    })


# ==================== WebSocket 事件处理 ====================

@socketio.on('connect')
def handle_connect():
    """客户端连接"""
    logger.info(f"👤 客户端已连接: {request.sid}")
    emit('connection_response', {'status': 'connected'})


@socketio.on('disconnect')
def handle_disconnect():
    """客户端断开连接"""
    logger.info(f"👤 客户端已断开: {request.sid}")


@socketio.on('start_generation')
def handle_start_generation(data):
    """处理生成启动请求"""
    try:
        # 参数验证和提取
        theme = data.get('theme', '').strip()
        target_score = float(data.get('target_score', 0.85))
        max_iterations = int(data.get('max_iterations', 5))
        quick_mode = data.get('quick_mode', True)
        
        if not theme:
            emit('error', {'message': '主题不能为空'})
            return
        
        # 创建新会话
        session_id = str(uuid.uuid4())
        session = GenerationSession(session_id, theme, target_score, max_iterations, quick_mode)
        session.client_sid = request.sid
        active_sessions[session_id] = session
        
        # 立即响应
        emit('session_created', {
            'session_id': session_id,
            'message': f'🚀 生成任务已启动，主题: {theme}'
        })
        
        logger.info(f"📝 新会话创建: {session_id} - 主题: {theme}")
        
        # 在后台线程中执行生成
        thread = threading.Thread(
            target=run_generation,
            args=(session_id, session, theme)
        )
        thread.daemon = True
        thread.start()
        
    except Exception as e:
        logger.error(f"❌ 启动生成失败: {e}")
        emit('error', {'message': f'启动失败: {str(e)}'})

@socketio.on('custom_message')
def handle_custom_message(data):
    """处理用户在生成过程中的实时反馈"""
    content = data.get('content', '').strip()
    session_id = data.get('session_id')
    
    if not content:
        return
        
    logger.info(f"📨 收到用户反馈: {content} (Session: {session_id})")
    
    # 查找关联的活跃会话
    session = None
    if session_id in active_sessions:
        session = active_sessions[session_id]
    else:
        # 如果没传 ID，尝试查找该客户端拥有的唯一会话
        for s in active_sessions.values():
            if s.client_sid == request.sid and s.is_running:
                session = s
                break
    
    if session:
        session.feedback.append(content)
        session.log_event('user_feedback', content)
        logger.info(f"📨 反馈已关联到会话: {content[:20]}... (Session: {session.session_id})")
        emit('message', {
            'type': 'status_update',
            'data': {'status': f'📥 已接收反馈: {content[:20]}...'}
        })
    else:
        # 如果当前没在生成，则视为启动新生成
        handle_start_generation({'theme': content})


def run_generation(session_id, session, theme):
    """运行生成任务（在后台线程执行）"""
    try:
        # 为本次生成创建或配置核心系统
        session_core = None
        if CORE_AVAILABLE:
            try:
                session_core = DiffuServoV4(theme=theme)
                session_core.target_score = session.target_score
                session_core.max_iterations = session.max_iterations
                # 传递参考图路径
                if session.reference_image_path:
                    session_core._session_reference_image = session.reference_image_path
                    logger.info(f"[{session_id}] 🖼️ 已加载参考图: {session.reference_image_path}")
                logger.info(f"[{session_id}] ✅ DiffuServoV4 已为主题 '{theme}' 初始化")
            except Exception as e:
                logger.warning(f"[{session_id}] ⚠️ 无法初始化 DiffuServoV4: {e}")
        
        session.is_running = True
        session.log_event('started', f'主题: {session.theme}')
        
        logger.info(f"[{session_id}] 📝 开始处理主题: {session.theme}")
        
        # 发送启动消息
        session.emit_message('status_update', {'status': '✨ 初始化中...'})
        
        # 第 1 步: 调用 Deepseek 获取创意建议
        session.emit_message('suggestion', {
            'sender': 'Deepseek 💡',
            'message': f'正在思考如何创意表现 "{session.theme}"...'
        })
        
        deepseek_suggestion = _get_deepseek_suggestion(session.theme)
        
        session.emit_message('suggestion', {
            'sender': 'Deepseek 💡',
            'message': deepseek_suggestion
        })
        
        session.log_event('deepseek_response', deepseek_suggestion)
        logger.info(f"[{session_id}] 💡 Deepseek 建议: {deepseek_suggestion[:100]}...")
        
        # 第 2-N 步: 迭代生成和评分
        for iteration in range(1, session.max_iterations + 1):
            session.current_iteration = iteration
            session.log_event('iteration_start', f'第 {iteration}/{session.max_iterations} 次迭代')
            
            session.emit_message('iteration_start', {
                'iteration': iteration,
                'total': session.max_iterations
            })
            
            logger.info(f"[{session_id}] 🎨 第 {iteration}/{session.max_iterations} 次迭代")
            
            # 生成图片（调用真实生成器）
            session.emit_message('status_update', {
                'status': f'🎨 正在生成第 {iteration} 张图片...'
            })
            
            # 处理实时反馈：如果有新需求，合并到当前的创意建议中
            current_feedback = ""
            if session.feedback:
                current_feedback = " ".join(session.feedback)
                session.feedback = [] # 处理完后清空
                logger.info(f"[{session_id}] 🆕 应用用户反馈到提示词: {current_feedback}")
                deepseek_suggestion = f"{deepseek_suggestion}\n用户最新需求: {current_feedback}"
                session.emit_message('suggestion', {
                    'sender': '系统 ⚙️',
                    'message': f'已将您的需求 "{current_feedback}" 加入生成规则'
                })

            image_path = _generate_image(session.theme, deepseek_suggestion, session_core)
            if not image_path:
                session.emit_message('status_update', {
                    'status': f'❌ 第 {iteration} 张图片生成失败'
                })
                session.log_event('error', '图片生成失败')
                continue
            
            session.emit_message('image_generated', {
                'iteration': iteration,
                'image_path': _path_to_url(image_path)
            })
            
            session.log_event('image_generated', image_path)
            
            # 评分
            session.emit_message('status_update', {
                'status': f'📊 正在评分第 {iteration} 张图片...'
            })
            
            scores = _evaluate_image(image_path, session_core)
            # 修复：不再取最大值，而是取 evaluator 返回的 final_score
            current_score = scores.get('final_score', 0.0) if scores else 0.0
            
            session.log_event('evaluation_complete', {
                'scores': scores,
                'current_score': current_score
            })
            
            # 更新会话
            session.images.append({
                'iteration': iteration,
                'path': image_path,
                'score': current_score,
                'scores_detail': scores
            })
            
            if current_score > session.best_score:
                session.best_score = current_score
                session.best_image = image_path
            
            # 发送评分结果
            model_names = list(scores.keys()) if scores else ['默认模型']
            for model, score in scores.items():
                session.emit_message('evaluation', {
                    'sender': f'评分模型 📊 ({model})',
                    'message': f'第 {iteration} 次迭代分数: {score:.3f}',
                    'score': score
                })
            
            session.emit_message('score_update', {
                'iteration': iteration,
                'current_score': current_score,
                'image_path': _path_to_url(image_path),
                'is_best': current_score == session.best_score,
                'max_iterations': session.max_iterations
            })
            
            logger.info(f"[{session_id}] 📊 迭代 {iteration} 完成，分数: {current_score:.3f}")
            
            # 检查是否达到目标分数
            if current_score >= session.target_score:
                session.emit_message('status_update', {
                    'status': f'✅ 已达到目标分数 {session.target_score} !'
                })
                session.log_event('target_reached', f'达到目标分数 {session.target_score}')
                logger.info(f"[{session_id}] ✅ 已达到目标分数!")
                break
            
            # 短暂延迟，避免过快轮询
            time.sleep(0.5)
        
        # 完成
        session.emit_message('completion', {
            'best_score': session.best_score,
            'best_image': session.best_image,
            'total_iterations': session.current_iteration,
            'total_images': len(session.images)
        })
        
        session.log_event('completed', f'最终分数: {session.best_score:.3f}')
        logger.info(f"[{session_id}] ✅ 生成完成，最优分数: {session.best_score:.3f}")
        
    except Exception as e:
        error_msg = f'生成过程出错: {str(e)}'
        session.emit_message('error', {'message': error_msg})
        session.log_event('error', error_msg)
        logger.error(f"[{session_id}] ❌ {error_msg}")
    
    finally:
        session.is_running = False


def _get_deepseek_suggestion(theme):
    """获取 Deepseek 的创意建议"""
    if not pygmalion_core:
        return f"关于 {theme} 的创意思考中..."
    
    try:
        # 这里应该调用真实的 Deepseek API
        # 目前返回模拟建议
        suggestion = f"根据主题 '{theme}'，我建议采用以下创意方向：\n" \
                    f"• 突出主题的独特特征\n" \
                    f"• 考虑色彩和构图的平衡\n" \
                    f"• 融入现代设计元素\n" \
                    f"• 保持视觉一致性"
        return suggestion
    except Exception as e:
        logger.error(f"Deepseek 调用失败: {e}")
        return f"获取建议时出错: {str(e)}"


def _path_to_url(path):
    """将本地文件路径转换为 Web 可访问的 URL"""
    if not path:
        return path
    try:
        # 统一为正斜杠
        rel_path = path.replace('\\', '/')
        if 'evolution_history/' in rel_path:
            filename = rel_path.split('evolution_history/')[-1]
            return f"/outputs/{filename}"
        elif 'static/' in rel_path:
            return "/" + rel_path.split('static/')[-1]
        return path
    except Exception as e:
        logger.warning(f"⚠️ 路径转换失败: {e}")
        return path


def _generate_image(theme, suggestion, core_system=None):
    """生成图片 - 调用真实的生成器"""
    if not core_system:
        logger.warning("⚠️ 核心系统不可用，使用模拟生成")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        # 返回一个本地模拟路径
        return f"static/images/generated_{timestamp}.png"
    
    try:
        logger.info(f"🎨 调用生成器: 主题='{theme}'")
        
        # 调用 DiffuServoV4 的 generate 方法生成图片，并传入创意建议和参考图
        image_path = core_system.generate(
            prev_score=None,
            prev_feedback=None,
            best_dimensions=None,
            external_suggestion=suggestion,
            reference_image_path=getattr(core_system, '_session_reference_image', None)
        )
        
        if image_path:
            logger.info(f"✅ 图片生成成功: {image_path} (本地路径)")
            return image_path
        else:
            logger.error("❌ 生成器返回空路径")
            return None
            
    except Exception as e:
        logger.error(f"❌ 图片生成失败: {e}", exc_info=True)
        return None


def _evaluate_image(image_path, core_system=None):
    """评估图片 - 调用真实的评分器"""
    if not core_system:
        logger.warning("⚠️ 核心系统不可用，使用模拟评分")
        import random
        return {
            'ModelScope': round(random.uniform(0.7, 0.95), 3),
            'SiliconFlow': round(random.uniform(0.7, 0.95), 3),
            'Backup': round(random.uniform(0.7, 0.95), 3)
        }
    
    try:
        logger.info(f"📊 调用评分器: 图片='{image_path}'")
        
        # 导入评分函数
        from pkg.system.modules.evaluator.core import rate_image
        
        # 调用评分器进行多模型评分
        result = rate_image(
            image_path=image_path,
            target_concept=core_system.theme,
            concept_weight=0.5,
            enable_smoothing=False
        )
        
        if result and result.get('final_score', 0) > 0:
            # 转换为分数字典格式
            scores = {
                'final_score': result.get('final_score', 0),
                'concept': result.get('concept_score', 0),
                'quality': result.get('quality_score', 0),
                'aesthetics': result.get('aesthetics_score', 0),
                'reasonableness': result.get('reasonableness_score', 0)
            }
            logger.info(f"✅ 评分完成: {scores}")
            return scores
        else:
            logger.error("❌ 评分器返回无效结果")
            return {}
            
    except Exception as e:
        logger.error(f"❌ 图片评分失败: {e}", exc_info=True)
        return {}


# ==================== 设置管理 ====================

@app.route('/api/settings', methods=['GET'])
def get_settings():
    """获取当前 API 设置"""
    from dotenv import dotenv_values
    env_path = os.path.join(ROOT_DIR, '.env')
    current_env = dotenv_values(env_path) if os.path.exists(env_path) else {}
    
    # 辅助函数：优先从 .env 读取，其次是当前环境变量
    def get_val(key, default=''):
        return current_env.get(key, os.environ.get(key, default))

    settings = {
        # 评分源 A
        'EVAL_A_NAME': get_val('EVAL_A_NAME', 'ModelScope'),
        'EVAL_A_KEY': get_val('EVAL_A_KEY', get_val('MODELSCOPE_API_KEY', '')),
        'EVAL_A_URL': get_val('EVAL_A_URL', get_val('MODELSCOPE_URL', 'https://api-inference.modelscope.cn/v1')),
        'EVAL_A_MODEL': get_val('EVAL_A_MODEL', 'Qwen/Qwen2.5-VL-72B-Instruct'),
        
        # 评分源 B
        'EVAL_B_NAME': get_val('EVAL_B_NAME', 'SiliconFlow'),
        'EVAL_B_KEY': get_val('EVAL_B_KEY', get_val('SILICON_KEY', '')),
        'EVAL_B_URL': get_val('EVAL_B_URL', get_val('SILICON_URL', 'https://api.siliconflow.cn/v1')),
        'EVAL_B_MODEL': get_val('EVAL_B_MODEL', 'Qwen/Qwen2.5-VL-72B-Instruct')
    }
    return jsonify(settings)

@app.route('/api/settings', methods=['POST'])
def save_settings():
    """保存 API 设置到 .env 并更新环境变量"""
    data = request.json
    if not data:
        return jsonify({'error': '无效的数据'}), 400
    
    keys_to_update = [
        'EVAL_A_NAME', 'EVAL_A_KEY', 'EVAL_A_URL', 'EVAL_A_MODEL',
        'EVAL_B_NAME', 'EVAL_B_KEY', 'EVAL_B_URL', 'EVAL_B_MODEL'
    ]
    
    # 为了向后兼容，同时更新旧的 Key
    if 'EVAL_A_KEY' in data: data['MODELSCOPE_API_KEY'] = data['EVAL_A_KEY']
    if 'EVAL_A_URL' in data: data['MODELSCOPE_URL'] = data['EVAL_A_URL']
    if 'EVAL_B_KEY' in data: data['SILICON_KEY'] = data['EVAL_B_KEY']
    if 'EVAL_B_URL' in data: data['SILICON_URL'] = data['EVAL_B_URL']
    
    keys_to_update.extend(['MODELSCOPE_API_KEY', 'MODELSCOPE_URL', 'SILICON_KEY', 'SILICON_URL'])
    
    # 逻辑：读取 .env，更新或添加新值
    env_path = os.path.join(ROOT_DIR, '.env')
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            env_lines = f.readlines()
            
    updated_keys = set()
    new_lines = []
    
    # 更新现有行
    for line in env_lines:
        line_stripped = line.strip()
        if not line_stripped or line_stripped.startswith('#'):
            new_lines.append(line)
            continue
            
        if '=' in line:
            parts = line.split('=', 1)
            key = parts[0].strip()
            if key in keys_to_update and key in data:
                new_lines.append(f"{key}={data[key]}\n")
                updated_keys.add(key)
                os.environ[key] = str(data[key])
            else:
                new_lines.append(line)
        else:
            new_lines.append(line)
            
    # 添加剩余的新键
    for key in keys_to_update:
        if key in data and key not in updated_keys:
            new_lines.append(f"{key}={data[key]}\n")
            os.environ[key] = str(data[key])
            
    # 写回文件
    try:
        with open(env_path, 'w', encoding='utf-8') as f:
            f.writelines(new_lines)
            
        # 尝试刷新评分器配置
        try:
            from pkg.system.modules.evaluator.core import api_manager
            api_manager.reload_config()
            logger.info("✅ 评分器 API 配置已刷新")
        except Exception as e:
            logger.warning(f"⚠️ 刷新评分器配置失败: {e}")
            
        return jsonify({'success': True, 'message': '设置已保存并同步到环境'})
    except Exception as e:
        logger.error(f"❌ 保存 .env 失败: {e}")
        return jsonify({'error': f'保存失败: {str(e)}'}), 500


# ==================== 错误处理 ====================

@app.errorhandler(400)
def bad_request(e):
    """400 错误处理"""
    return jsonify({'error': '请求参数错误'}), 400


@app.errorhandler(404)
def not_found(e):
    """404 错误处理"""
    return jsonify({'error': '资源不存在'}), 404


@app.errorhandler(500)
def server_error(e):
    """500 错误处理"""
    logger.error(f"服务器错误: {e}")
    return jsonify({'error': '服务器内部错误'}), 500


# ==================== 应用启动 ====================

if __name__ == '__main__':
    # 初始化核心系统（可选）
    if CORE_AVAILABLE:
        init_pygmalion_core()
    
    # 启动 Flask-SocketIO 应用
    print(r"""
    ╔════════════════════════════════════════╗
    ║   🚀 Pygmalion AI Web 界面              ║
    ║   Google 风格对话式生成                ║
    ║                                        ║
    ║   🌐 访问地址: http://localhost:5000   ║
    ║   📊 API 文档: /api/status              ║
    ║   💬 WebSocket: 已启用                  ║
    ╚════════════════════════════════════════╝
    """)
    
    socketio.run(
        app,
        host='0.0.0.0',
        port=5000,
        debug=True,
        use_reloader=False
    )

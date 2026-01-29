from pkg.interface.server import app, socketio
import os
import sys

# 确保项目根目录在 path 中
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

if __name__ == '__main__':
    print("🚀 Pygmalion System Launching...")
    # 允许所有 IP 访问，便于调试
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)

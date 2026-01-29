@echo off
REM Pygmalion Web UI - Windows 启动脚本
REM 启动 Flask-SocketIO Web 服务器

setlocal enabledelayedexpansion

echo.
echo ╔════════════════════════════════════════╗
echo ║   Pygmalion AI Web UI Launcher         ║
echo ║   Google Style Chat Interface          ║
echo ╚════════════════════════════════════════╝
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到 Python
    echo 请确保 Python 已安装并在 PATH 中
    pause
    exit /b 1
)

echo ✓ Python 已找到
echo.

REM 检查虚拟环境
if exist "..\venv\Scripts\activate.bat" (
    echo ✓ 虚拟环境已找到，正在激活...
    call ..\venv\Scripts\activate.bat
    echo ✓ 虚拟环境已激活
) else (
    echo ⚠ 虚拟环境未找到，使用系统 Python
)

echo.
echo 🚀 启动 Web 服务器...
echo.
echo 💡 提示：
echo   - 访问: http://localhost:5000
echo   - 关闭: Ctrl+C
echo.

python app_socketio.py

pause

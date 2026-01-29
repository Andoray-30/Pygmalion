@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

title Pygmalion System Launcher

echo.
echo =======================================================
echo   Pygmalion AI System Launcher
echo   清理环境 + 启动 Forge + Web UI
echo =======================================================
echo.

REM ==========================================
REM 第一步：停止所有旧进程
REM ==========================================
echo [1/4] 停止所有 Python 进程...
powershell -Command "Get-Process python,pythonw -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue"
timeout /t 2 /nobreak >nul
echo       [OK] 进程已清理

REM ==========================================
REM 第二步：清理缓存和日志
REM ==========================================
echo [2/4] 清理缓存和日志文件...

REM 清理 Python 缓存
for /d /r %%d in (__pycache__) do (
    if exist "%%d" rmdir /s /q "%%d" >nul 2>&1
)

REM 清理日志文件
if exist "pygmalion.log" del /f /q "pygmalion.log" >nul 2>&1
if exist "pkg" (
    del /f /q "pkg\*.log" >nul 2>&1
)

echo       [OK] 缓存和日志已清理

REM ==========================================
REM 第三步：启动 Forge 后端
REM ==========================================
echo [3/4] 启动 Forge WebUI 后端...
if exist "Forge\run.bat" (
    start "Forge Backend" cmd /c "cd /d Forge && run.bat"
    echo       [OK] Forge 启动中...
    echo       [WAIT] 等待 Forge 初始化...
    timeout /t 30 /nobreak >nul
) else (
    echo       [WARN] Forge 未找到，跳过启动
)

REM ==========================================
REM 第四步：启动 Pygmalion Web 服务
REM ==========================================
echo [4/4] 启动 Pygmalion Web 服务...
if exist "venv\Scripts\python.exe" (
    start "Pygmalion Web" cmd /k "venv\Scripts\python.exe launch.py"
) else (
    start "Pygmalion Web" cmd /k "python launch.py"
)
echo       [OK] Web 服务启动中...

echo.
echo =======================================================
echo   [SUCCESS] 系统启动完成！
echo =======================================================
echo   [URL] Forge Backend:   http://localhost:7860
echo   [URL] Pygmalion Web:   http://localhost:5000
echo.
echo   提示：两个服务窗口会自动打开
echo   按任意键关闭此窗口...
echo =======================================================
pause >nul

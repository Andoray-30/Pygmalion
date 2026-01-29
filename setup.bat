@echo off
chcp 65001 >nul
title Pygmalion 环境一键配置器

echo =======================================================
echo   Pygmalion AI 自动化安装程序
echo =======================================================
echo.
echo 此脚本将为您完成以下操作：
echo 1. 创建 Python 虚拟环境 (venv)
echo 2. 安装项目所需的所有库 (pip install)
echo 3. 克隆 Forge 图像生成后端 (git clone)
echo 4. [可选] 从 Hugging Face 下载必备 SDXL 底模 (约 15GB)
echo.
echo 注意：底模文件巨大，请确保硬盘空间充足 (建议预留 30GB+)。
echo.

set /p choice="确定要开始安装吗? (Y/N): "
if /i "%choice%" neq "Y" exit

echo.
echo [INFO] 正在调用 PowerShell 执行核心安装脚本...
powershell -NoProfile -ExecutionPolicy Bypass -File "setup_environment.ps1"

if %ERRORLEVEL% equ 0 (
    echo.
    echo [SUCCESS] 安装过程结束！
) else (
    echo.
    echo [ERROR] 安装过程中遇到了一些问题，请检查上方日志。
)

pause

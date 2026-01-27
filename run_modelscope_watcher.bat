@echo off
setlocal
REM 读取 .env（如果存在）
if exist "%~dp0\.env" (
  for /f "usebackq tokens=1,* delims==" %%A in ("%~dp0\.env") do (
    if /I "%%A"=="MODELSCOPE_API_KEY" set MODELSCOPE_API_KEY=%%B
    if /I "%%A"=="MODELSCOPE_ACCESS_TOKEN" set MODELSCOPE_ACCESS_TOKEN=%%B
    if /I "%%A"=="ACCESS_TOKEN" set ACCESS_TOKEN=%%B
  )
)

REM 激活 venv 并运行
call "%~dp0\venv\Scripts\activate.bat"
python "%~dp0\integrations\modelscope_watcher.py" --interval 1800 --output-dir "%~dp0\models_snapshot"
endlocal

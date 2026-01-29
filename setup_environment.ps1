# Pygmalion AI 自动化环境配置脚本 (PowerShell)
# 功能：安装 Python 环境、拉取 Forge、安装依赖、下载底模

# 设置控制台编码为 UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

function Show-Msg {
    param([string]$msg, [string]$color = "Cyan")
    Write-Host "`n==== $msg ====" -ForegroundColor $color
}

# 1. 检查 Python
Show-Msg "步骤 1: 检查 Python 环境"
if (Get-Command "python" -ErrorAction SilentlyContinue) {
    $version = python --version
    Write-Host "检测到 Python: $version" -ForegroundColor Green
} else {
    Write-Host "错误: 未检测到 Python，请先安装 Python 3.10 并添加到环境变量!" -ForegroundColor Red
    exit
}

# 2. 创建虚拟环境
Show-Msg "步骤 2: 创建虚拟环境 (venv)"
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "虚拟环境创建成功" -ForegroundColor Green
} else {
    Write-Host "虚拟环境已存在，跳过" -ForegroundColor Gray
}

# 3. 安装依赖项
Show-Msg "步骤 3: 安装项目仓库依赖"
& ".\venv\Scripts\python.exe" -m pip install --upgrade pip
& ".\venv\Scripts\python.exe" -m pip install -r requirements.txt
Write-Host "项目依赖安装完成" -ForegroundColor Green

# 4. 下载/检查 Forge
Show-Msg "步骤 4: 配置 Forge 后端"
if (-not (Test-Path "Forge")) {
    Write-Host "正在拉取 Stable Diffusion WebUI Forge (这可能需要一些时间)..."
    git clone https://github.com/lllyasviel/stable-diffusion-webui-forge Forge
} else {
    Write-Host "Forge 目录已存在，跳过克隆" -ForegroundColor Gray
}

# 5. 下载底模 (SDXL 系列)
Show-Msg "步骤 5: 检查并下载必备底模 (SDXL)"
$modelDir = "Forge\models\Stable-diffusion"
if (-not (Test-Path $modelDir)) {
    New-Item -ItemType Directory -Path $modelDir -Force | Out-Null
}

# 模型配置列表 (名称, 下载链接)
$models = @(
    @{
        name = "sd_xl_turbo_1.0_fp16.safetensors";
        url  = "https://huggingface.co/stabilityai/sdxl-turbo/resolve/main/sd_xl_turbo_1.0_fp16.safetensors"
    },
    @{
        name = "juggernautXL_ragnarokBy.safetensors";
        url  = "https://huggingface.co/RunDiffusion/Juggernaut-XL-v9/resolve/main/Juggernaut-XL-v9.safetensors"
    },
    @{
        name = "animagineXLV31_v31.safetensors";
        url  = "https://huggingface.co/cagliostrolab/animagine-xl-3.1/resolve/main/animagineXLV31_v31.safetensors"
    }
)

foreach ($m in $models) {
    $targetPath = Join-Path $modelDir $m.name
    if (-not (Test-Path $targetPath)) {
        Write-Host "正在下载模型: $($m.name)... (约 6GB+, 请保持网络畅通)" -ForegroundColor Yellow
        try {
            # 使用更现代的 WebRequest 方法，显示进度（虽然 Invoke-WebRequest 默认有，但这里确保可用）
            Invoke-WebRequest -Uri $m.url -OutFile $targetPath -ErrorAction Stop
            Write-Host "下载完成: $($m.name)" -ForegroundColor Green
        } catch {
            Write-Host "下载失败: $($m.name)。错误: $_" -ForegroundColor Red
            Write-Host "提示: 您可以稍后手动从 HuggingFace 下载并放入 $modelDir 目录下。" -ForegroundColor White
        }
    } else {
        Write-Host "模型已存在: $($m.name)" -ForegroundColor Gray
    }
}

Show-Msg "环境配置全部完成！" "Green"
Write-Host "您现在可以直接运行 run_system.bat 来启动系统。" -ForegroundColor White
pause

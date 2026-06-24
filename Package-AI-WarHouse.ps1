# AI-WarHouse 打包脚本
# 自动完成前端构建、后端打包、配置文件复制

$ErrorActionPreference = "Stop"
$ProjectRoot = "D:\Data\Trae\数仓AI助手-Trae1.0"
$BackendDir = "$ProjectRoot\backend"
$FrontendDir = "$ProjectRoot\frontend"
$OutputDir = "$ProjectRoot\AI-WarHouse\AI-WarHouse"

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "AI-WarHouse 自动打包脚本" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# 1. 构建前端
Write-Host "`n[步骤1] 构建前端..." -ForegroundColor Yellow
Set-Location $FrontendDir
npm.cmd run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "前端构建失败!" -ForegroundColor Red
    exit 1
}
Write-Host "前端构建完成" -ForegroundColor Green

# 2. 清理旧打包目录
Write-Host "`n[步骤2] 清理旧打包目录..." -ForegroundColor Yellow
Stop-Process -Name "AI-WarHouse" -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
Remove-Item -Path "$ProjectRoot\AI-WarHouse" -Recurse -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 1
Write-Host "旧目录已清理" -ForegroundColor Green

# 3. 打包后端
Write-Host "`n[步骤3] 打包后端..." -ForegroundColor Yellow
Set-Location $BackendDir
& "D:\ForWork\Python\python.exe" -m PyInstaller AI-WarHouse.spec --distpath "$ProjectRoot\AI-WarHouse" --clean
if ($LASTEXITCODE -ne 0) {
    Write-Host "后端打包失败!" -ForegroundColor Red
    exit 1
}
Write-Host "后端打包完成" -ForegroundColor Green

# 4. 复制前端文件
Write-Host "`n[步骤4] 复制前端文件..." -ForegroundColor Yellow
Copy-Item -Path "$FrontendDir\dist" -Destination "$OutputDir\frontend" -Recurse -Force
Write-Host "前端文件已复制" -ForegroundColor Green

# 5. 复制配置文件到可执行文件目录（关键步骤！）
Write-Host "`n[步骤5] 复制配置文件到正确位置..." -ForegroundColor Yellow
# 从 _internal 复制到可执行文件同级目录
Copy-Item -Path "$OutputDir\_internal\dev_standards.json" -Destination "$OutputDir\dev_standards.json" -Force
Copy-Item -Path "$OutputDir\_internal\custom_prompt.txt" -Destination "$OutputDir\custom_prompt.txt" -Force
Copy-Item -Path "$OutputDir\_internal\word_roots.json" -Destination "$OutputDir\word_roots.json" -Force
Copy-Item -Path "$OutputDir\_internal\builtin" -Destination "$OutputDir\builtin" -Recurse -Force
# 确保 standards 目录存在
if (-not (Test-Path "$OutputDir\standards")) {
    Copy-Item -Path "$OutputDir\_internal\standards" -Destination "$OutputDir\standards" -Recurse -Force
}
Write-Host "配置文件已复制到正确位置" -ForegroundColor Green

# 6. 验证打包结果
Write-Host "`n[步骤6] 验证打包结果..." -ForegroundColor Yellow
$RequiredFiles = @(
    "$OutputDir\AI-WarHouse.exe",
    "$OutputDir\frontend\index.html",
    "$OutputDir\dev_standards.json",
    "$OutputDir\custom_prompt.txt",
    "$OutputDir\word_roots.json",
    "$OutputDir\builtin\default_prompt.txt"
)
$AllExist = $true
foreach ($file in $RequiredFiles) {
    if (Test-Path $file) {
        Write-Host "  ✓ $file" -ForegroundColor Green
    } else {
        Write-Host "  ✗ $file (缺失)" -ForegroundColor Red
        $AllExist = $false
    }
}

if ($AllExist) {
    Write-Host "`n========================================" -ForegroundColor Cyan
    Write-Host "打包成功完成!" -ForegroundColor Green
    Write-Host "输出目录: $OutputDir" -ForegroundColor White
    Write-Host "========================================" -ForegroundColor Cyan
} else {
    Write-Host "`n打包验证失败，请检查缺失文件" -ForegroundColor Red
    exit 1
}
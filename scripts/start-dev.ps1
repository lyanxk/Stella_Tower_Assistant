param(
    [switch]$InstallDependencies
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiDir = Join-Path $repoRoot "apps\api"
$webDir = Join-Path $repoRoot "apps\web"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$backendArgs = '-NoExit', '-Command', "Set-Location '$apiDir'; `$env:PYTHONPATH='src'; & '$pythonExe' -m stellatowerassistant.cli serve"
$frontendArgs = '-NoExit', '-Command', "Set-Location '$webDir'; npm.cmd run dev"

if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found: $pythonExe"
}

if ($InstallDependencies) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    Push-Location $webDir
    try {
        npm.cmd install
    }
    finally {
        Pop-Location
    }
}

Write-Host "Starting backend API..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $apiDir -ArgumentList $backendArgs | Out-Null

Write-Host "Starting frontend dev server..." -ForegroundColor Green
Start-Process powershell -WorkingDirectory $webDir -ArgumentList $frontendArgs | Out-Null

Write-Host "Development services launched." -ForegroundColor Cyan
Write-Host "Backend:  http://127.0.0.1:8765" -ForegroundColor Cyan
Write-Host "Frontend: http://127.0.0.1:5173" -ForegroundColor Cyan

param(
    [switch]$InstallDependencies,
    [switch]$NoBackend
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiDir = Join-Path $repoRoot "apps\api"
$webDir = Join-Path $repoRoot "apps\web"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"
$backendUrl = "http://127.0.0.1:8765/health"
$frontendUrl = "http://127.0.0.1:5173"
$electronExe = Join-Path $webDir "node_modules\.bin\electron.cmd"
$electronRuntimeExe = Join-Path $webDir "node_modules\electron\dist\electron.exe"
$startedProcesses = @()

function Test-HttpReady {
    param([string]$Url)

    try {
        Invoke-WebRequest -Uri $Url -UseBasicParsing -TimeoutSec 2 | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

function Wait-HttpReady {
    param(
        [string]$Url,
        [string]$Name,
        [int]$TimeoutSeconds = 60
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        if (Test-HttpReady -Url $Url) {
            return
        }
        Start-Sleep -Seconds 1
    }

    throw "$Name did not become ready at $Url within $TimeoutSeconds seconds."
}

function Install-ElectronRuntime {
    $electronInstallScript = Join-Path $webDir "node_modules\electron\install.js"

    if (-not (Test-Path $electronInstallScript)) {
        throw "Electron install script was not found at $electronInstallScript. Run from apps\web: npm.cmd install"
    }

    Write-Host "Downloading Electron runtime..." -ForegroundColor Yellow
    $env:electron_config_cache = Join-Path $webDir ".electron-cache"
    if (-not $env:ELECTRON_MIRROR) {
        $env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
    }
    & node $electronInstallScript

    if (-not (Test-Path $electronRuntimeExe)) {
        throw "Electron runtime download did not finish. Run from apps\web: `$env:ELECTRON_MIRROR='https://npmmirror.com/mirrors/electron/'; node node_modules\electron\install.js"
    }
}

function Stop-ProcessTree {
    param([int]$ProcessId)

    try {
        $children = Get-CimInstance Win32_Process -Filter "ParentProcessId = $ProcessId"
        foreach ($child in $children) {
            Stop-ProcessTree -ProcessId $child.ProcessId
        }

        $process = Get-Process -Id $ProcessId -ErrorAction SilentlyContinue
        if ($process) {
            Stop-Process -Id $ProcessId -Force -ErrorAction SilentlyContinue
        }
    }
    catch {
        Write-Host "Failed to stop process tree rooted at PID ${ProcessId}: $_" -ForegroundColor DarkYellow
    }
}

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

if (-not (Test-Path $electronExe)) {
    throw "Electron was not found at $electronExe. Run from apps\web: npm.cmd install"
}

if (-not (Test-Path $electronRuntimeExe)) {
    Install-ElectronRuntime
}

try {
    if (-not $NoBackend) {
        if (Test-HttpReady -Url $backendUrl) {
            Write-Host "Backend API is already running." -ForegroundColor DarkGray
        }
        else {
            Write-Host "Starting backend API..." -ForegroundColor Green
            $backendCommand = "Set-Location '$apiDir'; `$env:PYTHONPATH='src'; & '$pythonExe' -m stellatowerassistant.cli serve"
            $backendProcess = Start-Process powershell -WindowStyle Hidden -WorkingDirectory $apiDir -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $backendCommand -PassThru
            $startedProcesses += $backendProcess
            Wait-HttpReady -Url $backendUrl -Name "Backend API"
        }
    }

    if (Test-HttpReady -Url $frontendUrl) {
        Write-Host "Frontend dev server is already running." -ForegroundColor DarkGray
    }
    else {
        Write-Host "Starting frontend dev server..." -ForegroundColor Green
        $frontendCommand = "Set-Location '$webDir'; npm.cmd run dev -- --host 127.0.0.1 --port 5173"
        $frontendProcess = Start-Process powershell -WindowStyle Hidden -WorkingDirectory $webDir -ArgumentList '-NoProfile', '-ExecutionPolicy', 'Bypass', '-Command', $frontendCommand -PassThru
        $startedProcesses += $frontendProcess
        Wait-HttpReady -Url $frontendUrl -Name "Frontend dev server"
    }

    $env:VITE_DEV_SERVER_URL = $frontendUrl

    Write-Host "Opening Stella Tower Assistant in an Electron window..." -ForegroundColor Cyan
    Push-Location $webDir
    try {
        & $electronExe .
    }
    finally {
        Pop-Location
    }
}
finally {
    if ($startedProcesses.Count -gt 0) {
        Write-Host "Stopping services started by this window session..." -ForegroundColor Yellow
        foreach ($process in @($startedProcesses | Sort-Object Id -Descending)) {
            Stop-ProcessTree -ProcessId $process.Id
        }
    }
}

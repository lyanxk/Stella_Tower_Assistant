param(
    [ValidateSet("auto", "small", "elevator")]
    [string]$Variant = "auto",

    [ValidateSet("auto", "screen", "emulator")]
    [string]$CaptureMode = "auto",

    [double]$Threshold = 0.98,

    [string]$CaptureHotkey = "f8",

    [string]$QuitHotkey = "esc"
)

$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $PSScriptRoot
$apiDir = Join-Path $repoRoot "apps\api"
$pythonExe = Join-Path $repoRoot ".venv\Scripts\python.exe"

if (-not (Test-Path $pythonExe)) {
    throw "Python virtual environment not found: $pythonExe"
}

Push-Location $apiDir
try {
    $env:PYTHONPATH = "src"
    & $pythonExe -m stellatowerassistant.ocr_capture `
        --variant $Variant `
        --capture-mode $CaptureMode `
        --threshold $Threshold `
        --capture-hotkey $CaptureHotkey `
        --quit-hotkey $QuitHotkey
}
finally {
    Pop-Location
}

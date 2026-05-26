# 金持ちの習慣 YouTube動画自動生成 — Windowsセットアップ＆実行スクリプト
# 右クリック →「PowerShellで実行」で起動してください

$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

function Write-Step($msg) { Write-Host "`n▶ $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "  ✓ $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "  ! $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "  ✗ $msg" -ForegroundColor Red }

Write-Host "================================================" -ForegroundColor Blue
Write-Host "  金持ちの習慣 YouTube動画 自動生成セットアップ" -ForegroundColor Blue
Write-Host "================================================" -ForegroundColor Blue

# ── 1. Python 確認・インストール ──────────────────────────
Write-Step "Python を確認中..."
$pythonOk = $false
try {
    $ver = python --version 2>&1
    if ($ver -match "Python 3\.(\d+)") {
        $minor = [int]$Matches[1]
        if ($minor -ge 9) {
            Write-OK "Python $ver"
            $pythonOk = $true
        }
    }
} catch {}

if (-not $pythonOk) {
    Write-Warn "Python 3.9以上が必要です。winget でインストールします..."
    winget install Python.Python.3.11 --accept-source-agreements --accept-package-agreements
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-OK "Python インストール完了"
}

# ── 2. ffmpeg 確認・インストール ─────────────────────────
Write-Step "ffmpeg を確認中..."
$ffmpegOk = $false
try {
    $null = ffmpeg -version 2>&1
    Write-OK "ffmpeg インストール済み"
    $ffmpegOk = $true
} catch {}

if (-not $ffmpegOk) {
    Write-Warn "ffmpeg をインストールします..."
    winget install Gyan.FFmpeg --accept-source-agreements --accept-package-agreements
    # PATH を更新
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-OK "ffmpeg インストール完了"
}

# ── 3. espeak-ng インストール ─────────────────────────────
Write-Step "espeak-ng を確認中..."
$espeakOk = $false
try {
    $null = espeak-ng --version 2>&1
    Write-OK "espeak-ng インストール済み"
    $espeakOk = $true
} catch {}

if (-not $espeakOk) {
    Write-Warn "espeak-ng をインストールします（フォールバック用音声エンジン）..."
    winget install eSpeak.eSpeakNG --accept-source-agreements --accept-package-agreements 2>&1 | Out-Null
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
    Write-OK "espeak-ng インストール完了"
}

# ── 4. Python パッケージインストール ─────────────────────
Write-Step "Python パッケージをインストール中..."
python -m pip install --upgrade pip --quiet
python -m pip install moviepy Pillow numpy openai httpx python-dotenv --quiet
Write-OK "パッケージインストール完了"

# ── 5. .env ファイルの設定 ────────────────────────────────
Write-Step "API キーを設定中..."
$envFile = Join-Path $ScriptDir ".env"
$envExample = Join-Path $ScriptDir ".env.example"

if (-not (Test-Path $envFile)) {
    Copy-Item $envExample $envFile
}

# 現在の OPENAI_API_KEY を読み込む
$currentKey = ""
if (Test-Path $envFile) {
    $lines = Get-Content $envFile
    foreach ($line in $lines) {
        if ($line -match "^OPENAI_API_KEY=(.+)$") {
            $currentKey = $Matches[1]
        }
    }
}

if ($currentKey -eq "" -or $currentKey -eq "sk-...") {
    Write-Host ""
    Write-Host "  OpenAI API キーを入力してください（高品質な音声・画像生成に使用）" -ForegroundColor Yellow
    Write-Host "  ※ スキップする場合はそのまま Enter を押してください" -ForegroundColor Gray
    Write-Host "  取得: https://platform.openai.com/api-keys" -ForegroundColor Gray
    $apiKey = Read-Host "  OPENAI_API_KEY"

    if ($apiKey -ne "") {
        $content = Get-Content $envFile -Raw
        $content = $content -replace "OPENAI_API_KEY=.*", "OPENAI_API_KEY=$apiKey"
        Set-Content $envFile $content -Encoding UTF8
        Write-OK "APIキーを .env に保存しました"
    } else {
        Write-Warn "APIキーなし。espeak-ng（機械音声）で続行します"
    }
} else {
    Write-OK "APIキー設定済み"
}

# ── 6. 動画生成 ───────────────────────────────────────────
Write-Step "動画を生成します..."
Write-Host ""
Set-Location $ScriptDir
python demo.py

# ── 7. 完了：動画を開く ───────────────────────────────────
$outputVideo = Join-Path $ScriptDir "output\demo\output.mp4"
if (Test-Path $outputVideo) {
    Write-Host ""
    Write-Host "================================================" -ForegroundColor Green
    Write-Host "  完成！動画を開きます..." -ForegroundColor Green
    Write-Host "================================================" -ForegroundColor Green
    Start-Process $outputVideo
} else {
    Write-Fail "動画ファイルが見つかりません: $outputVideo"
}

Write-Host ""
Write-Host "Enterキーを押すと終了します..."
Read-Host

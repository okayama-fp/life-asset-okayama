# Buffalo HDD 全自動復旧スクリプト
# 管理者権限が必要な場合は自動で昇格します

# 管理者権限チェック・自動昇格
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")) {
    Start-Process PowerShell -Verb RunAs -ArgumentList "-ExecutionPolicy Bypass -File `"$PSCommandPath`""
    Exit
}

Clear-Host
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "  Buffalo HDD ホームビデオ 全自動復旧" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# 保存先フォルダをデスクトップに作成
$dest = "$env:USERPROFILE\Desktop\Buffalo_Videos"
New-Item -ItemType Directory -Force -Path $dest | Out-Null
Write-Host "[OK] 保存先フォルダを作成: $dest" -ForegroundColor Green

# Buffalo HDD確認
Write-Host ""
Write-Host "[確認] Buffalo HDD を検出中..." -ForegroundColor Yellow
$buffalo = Get-Disk | Where-Object { $_.FriendlyName -like "*BUFFALO*" -or $_.FriendlyName -like "*Buffalo*" }
if (-not $buffalo) {
    Write-Host "[エラー] Buffalo HDDが見つかりません。USBケーブルを確認してください。" -ForegroundColor Red
    pause; exit
}
Write-Host "[OK] Buffalo HDD 検出: $($buffalo.FriendlyName) ($([math]::Round($buffalo.Size/1GB,0))GB)" -ForegroundColor Green
$diskNum = $buffalo.Number

# WSL確認
Write-Host ""
Write-Host "[確認] WSL (Windows Subsystem for Linux) を確認中..." -ForegroundColor Yellow
$wslCheck = wsl --status 2>&1
if ($LASTEXITCODE -ne 0 -or $wslCheck -like "*インストール*" -or $wslCheck -like "*install*") {
    Write-Host "[インストール] WSLをインストール中（数分かかります）..." -ForegroundColor Yellow
    wsl --install --no-distribution
    Write-Host ""
    Write-Host "[注意] PCを再起動後、このスクリプトをもう一度実行してください。" -ForegroundColor Red
    pause; exit
}
Write-Host "[OK] WSL 利用可能" -ForegroundColor Green

# 既存マウント解除
wsl --unmount "\\.\PHYSICALDRIVE$diskNum" 2>$null | Out-Null

# パーティション2にマウント試行（XFS → ext4 → ext3 の順）
$mounted = $false
$fsTypes = @("xfs", "ext4", "ext3")

Write-Host ""
Write-Host "[マウント] Buffalo HDD をマウント中..." -ForegroundColor Yellow

foreach ($fs in $fsTypes) {
    Write-Host "  → $fs で試行中..." -ForegroundColor Gray
    $result = wsl --mount "\\.\PHYSICALDRIVE$diskNum" --partition 2 --type $fs 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[OK] $fs でマウント成功!" -ForegroundColor Green
        $mounted = $true
        $mountedFs = $fs
        break
    }
}

if (-not $mounted) {
    Write-Host ""
    Write-Host "[別方法] パーティション1で試行中..." -ForegroundColor Yellow
    foreach ($fs in $fsTypes) {
        $result = wsl --mount "\\.\PHYSICALDRIVE$diskNum" --partition 1 --type $fs 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] パーティション1を $fs でマウント成功!" -ForegroundColor Green
            $mounted = $true
            $mountPoint = "/mnt/wsl/PHYSICALDRIVE${diskNum}p1"
            break
        }
    }
}

if (-not $mounted) {
    Write-Host ""
    Write-Host "[エラー] マウントに失敗しました。" -ForegroundColor Red
    Write-Host "HDDのファイルシステムがサポート外の可能性があります。" -ForegroundColor Red
    wsl --unmount "\\.\PHYSICALDRIVE$diskNum" 2>$null
    pause; exit
}

Start-Sleep -Seconds 3

# マウントポイント確認
$mountPoint = "/mnt/wsl/PHYSICALDRIVE${diskNum}p2"
$winUser = $env:USERNAME

Write-Host ""
Write-Host "[確認] ドライブの内容を確認中..." -ForegroundColor Yellow
$lsResult = wsl -e bash -c "ls '$mountPoint' 2>/dev/null" 2>&1
Write-Host $lsResult

# 動画ファイルをコピー
Write-Host ""
Write-Host "[コピー] ホームビデオファイルを検索・コピー中..." -ForegroundColor Yellow
Write-Host "  (ファイル数によっては数分かかります)" -ForegroundColor Gray

$winDest = $dest -replace "\\", "/" -replace "C:", "/mnt/c"
$copyScript = @"
find '$mountPoint' -type f \( -iname '*.mp4' -o -iname '*.mov' -o -iname '*.avi' -o -iname '*.mts' -o -iname '*.m2ts' -o -iname '*.mpg' -o -iname '*.mpeg' -o -iname '*.wmv' -o -iname '*.ts' -o -iname '*.mkv' -o -iname '*.MP4' -o -iname '*.MOV' \) 2>/dev/null | while read f; do echo "コピー: \$f"; cp "\$f" '$winDest/'; done
"@

wsl -e bash -c $copyScript

# 結果確認
$count = (Get-ChildItem $dest -File -ErrorAction SilentlyContinue).Count

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
if ($count -gt 0) {
    Write-Host "  完了! $count 個の動画ファイルを保存しました" -ForegroundColor Green
    Write-Host "  場所: $dest" -ForegroundColor Green
    Write-Host "==========================================" -ForegroundColor Cyan
    Start-Process explorer.exe $dest
} else {
    Write-Host "  動画ファイルが見つかりませんでした" -ForegroundColor Yellow
    Write-Host "  ドライブの全ファイル一覧:" -ForegroundColor Yellow
    Write-Host "==========================================" -ForegroundColor Cyan
    wsl -e bash -c "find '$mountPoint' -type f 2>/dev/null | head -50"
}

# マウント解除
wsl --unmount "\\.\PHYSICALDRIVE$diskNum" 2>$null
Write-Host ""
Write-Host "マウントを解除しました。" -ForegroundColor Gray
pause

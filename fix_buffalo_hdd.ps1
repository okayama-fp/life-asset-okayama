# Buffalo HDD 自動認識・修復スクリプト
# 管理者として実行してください

Write-Host "=== Buffalo HDD 自動修復ツール ===" -ForegroundColor Cyan
Write-Host ""

# 管理者確認
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]"Administrator")) {
    Write-Host "[エラー] 管理者として実行してください。" -ForegroundColor Red
    Write-Host "このファイルを右クリック → 「PowerShellで実行」→「管理者として実行」"
    pause
    exit
}

Write-Host "[1/4] 接続されているディスクを確認中..." -ForegroundColor Yellow

# 全ディスク一覧取得
$disks = Get-Disk | Where-Object { $_.BusType -eq "USB" -or $_.FriendlyName -like "*Buffalo*" -or $_.FriendlyName -like "*BUFFALO*" }

if ($disks.Count -eq 0) {
    Write-Host ""
    Write-Host "[注意] USB接続のディスクが見つかりません。" -ForegroundColor Red
    Write-Host "  → HDDのUSBケーブルがしっかり接続されているか確認してください。"
    Write-Host "  → 別のUSBポートに差し替えてみてください。"
    Write-Host ""
    Write-Host "すべてのディスク一覧："
    Get-Disk | Format-Table Number, FriendlyName, Size, PartitionStyle, OperationalStatus
    pause
    exit
}

Write-Host ""
Write-Host "Buffalo/USB ディスクが見つかりました：" -ForegroundColor Green
$disks | Format-Table Number, FriendlyName, @{N="Size(GB)";E={[math]::Round($_.Size/1GB,1)}}, PartitionStyle, OperationalStatus

# オフラインのディスクをオンラインに
Write-Host "[2/4] ディスクをオンラインに設定中..." -ForegroundColor Yellow
foreach ($disk in $disks) {
    if ($disk.OperationalStatus -eq "Offline") {
        Write-Host "  ディスク $($disk.Number) をオンラインにします..."
        Set-Disk -Number $disk.Number -IsOffline $false
        Set-Disk -Number $disk.Number -IsReadOnly $false
        Write-Host "  完了" -ForegroundColor Green
    }
}

# パーティション確認・ドライブレター割り当て
Write-Host ""
Write-Host "[3/4] パーティションとドライブレターを確認中..." -ForegroundColor Yellow

foreach ($disk in $disks) {
    $partitions = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue
    if ($partitions) {
        foreach ($part in $partitions) {
            $driveLetter = $part.DriveLetter
            if ([string]::IsNullOrEmpty($driveLetter) -or $driveLetter -eq "`0") {
                # ドライブレターを自動割り当て
                Write-Host "  パーティション $($part.PartitionNumber) にドライブレターを割り当て中..."
                try {
                    Add-PartitionAccessPath -DiskNumber $disk.Number -PartitionNumber $part.PartitionNumber -AssignDriveLetter
                    $part = Get-Partition -DiskNumber $disk.Number -PartitionNumber $part.PartitionNumber
                    Write-Host "  → ドライブ $($part.DriveLetter): に割り当てました" -ForegroundColor Green
                    $driveLetter = $part.DriveLetter
                } catch {
                    Write-Host "  → 自動割り当て失敗: $($_.Exception.Message)" -ForegroundColor Red
                }
            } else {
                Write-Host "  ドライブ $driveLetter`: は既に割り当て済み" -ForegroundColor Green
            }

            # ファイルシステム確認
            if ($driveLetter -and $driveLetter -ne "`0") {
                $vol = Get-Volume -DriveLetter $driveLetter -ErrorAction SilentlyContinue
                if ($vol) {
                    Write-Host "  ファイルシステム: $($vol.FileSystemType) / 状態: $($vol.HealthStatus)"
                    if ($vol.HealthStatus -ne "Healthy") {
                        Write-Host "  [修復] chkdsk を実行します..." -ForegroundColor Yellow
                        chkdsk "${driveLetter}:" /f
                    }
                }
            }
        }
    }
}

# 動画ファイルを自動検索
Write-Host ""
Write-Host "[4/4] ホームビデオファイルを検索中..." -ForegroundColor Yellow

$videoExtensions = @("*.mp4","*.mov","*.avi","*.mts","*.m2ts","*.mpg","*.mpeg","*.wmv","*.ts","*.mkv")
$foundFiles = @()

foreach ($disk in $disks) {
    $partitions = Get-Partition -DiskNumber $disk.Number -ErrorAction SilentlyContinue
    foreach ($part in $partitions) {
        $dl = $part.DriveLetter
        if ($dl -and $dl -ne "`0") {
            Write-Host "  ドライブ $dl`: を検索中..."
            foreach ($ext in $videoExtensions) {
                $files = Get-ChildItem -Path "${dl}:\" -Filter $ext -Recurse -ErrorAction SilentlyContinue
                $foundFiles += $files
            }
        }
    }
}

Write-Host ""
if ($foundFiles.Count -gt 0) {
    Write-Host "=== 動画ファイルが $($foundFiles.Count) 件見つかりました ===" -ForegroundColor Green
    $foundFiles | Select-Object FullName, @{N="Size(MB)";E={[math]::Round($_.Length/1MB,1)}}, LastWriteTime | Format-Table -AutoSize

    # 結果をデスクトップに保存
    $desktopPath = [Environment]::GetFolderPath("Desktop")
    $resultFile = "$desktopPath\buffalo_video_list.txt"
    $foundFiles | Select-Object FullName, @{N="Size(MB)";E={[math]::Round($_.Length/1MB,1)}}, LastWriteTime | Format-Table -AutoSize | Out-File $resultFile -Encoding UTF8
    Write-Host ""
    Write-Host "ファイル一覧をデスクトップに保存しました: buffalo_video_list.txt" -ForegroundColor Cyan

    # エクスプローラーで最初のファイルの場所を開く
    $firstFolder = Split-Path $foundFiles[0].FullName
    Write-Host "フォルダを開きます: $firstFolder" -ForegroundColor Cyan
    Start-Process explorer.exe $firstFolder
} else {
    Write-Host "動画ファイルが見つかりませんでした。" -ForegroundColor Red
    Write-Host ""
    Write-Host "考えられる原因："
    Write-Host "  1. ファイルシステムが破損している → chkdsk での修復が必要"
    Write-Host "  2. 録画ソフト専用の暗号化形式 → バッファローの専用ソフトが必要"
    Write-Host "  3. ドライブが正しくマウントされていない"
}

Write-Host ""
Write-Host "=== 完了 ===" -ForegroundColor Cyan
pause

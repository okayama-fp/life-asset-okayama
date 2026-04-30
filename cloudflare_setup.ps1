$TOKEN = "ここにAPIトークンを貼り付け"
$IP    = "160.251.71.29"
$DOM   = "assetguardians88338.com"
$API   = "https://api.cloudflare.com/client/v4"
$H     = @{"Authorization"="Bearer $TOKEN"; "Content-Type"="application/json"}

Write-Host "=== Cloudflare移行開始 ===" -ForegroundColor Cyan

# Zone取得
$Z = Invoke-RestMethod -Uri "$API/zones?name=$DOM" -Headers $H
if ($Z.result.Count -eq 0) {
    $B = "{`"name`":`"$DOM`",`"jump_start`":true}"
    $Z = Invoke-RestMethod -Uri "$API/zones" -Method POST -Headers $H -Body $B
    $ZID = $Z.result.id
    Write-Host "ドメインをCloudflareに追加しました" -ForegroundColor Green
} else {
    $ZID = $Z.result[0].id
    Write-Host "既存のZoneを使用します" -ForegroundColor Yellow
}
Write-Host "Zone ID: $ZID"

# Aレコード設定
$B1 = "{`"type`":`"A`",`"name`":`"$DOM`",`"content`":`"$IP`",`"proxied`":true,`"ttl`":1}"
$B2 = "{`"type`":`"A`",`"name`":`"www.$DOM`",`"content`":`"$IP`",`"proxied`":true,`"ttl`":1}"
try {
    Invoke-RestMethod -Uri "$API/zones/$ZID/dns_records" -Method POST -Headers $H -Body $B1 | Out-Null
    Invoke-RestMethod -Uri "$API/zones/$ZID/dns_records" -Method POST -Headers $H -Body $B2 | Out-Null
    Write-Host "DNSレコード設定完了" -ForegroundColor Green
} catch {
    Write-Host "DNSレコード: すでに存在する可能性があります（続行）" -ForegroundColor Yellow
}

# SSL設定
Invoke-RestMethod -Uri "$API/zones/$ZID/settings/ssl" -Method PATCH -Headers $H -Body '{"value":"full"}' | Out-Null
Write-Host "SSL設定完了" -ForegroundColor Green

# HTTPS強制
Invoke-RestMethod -Uri "$API/zones/$ZID/settings/always_use_https" -Method PATCH -Headers $H -Body '{"value":"on"}' | Out-Null
Write-Host "HTTPS強制リダイレクト設定完了" -ForegroundColor Green

# ネームサーバー表示
$NS = Invoke-RestMethod -Uri "$API/zones/$ZID" -Headers $H
Write-Host ""
Write-Host "==============================" -ForegroundColor Cyan
Write-Host "ConoHaで以下のネームサーバーを設定してください:" -ForegroundColor Yellow
$NS.result.name_servers | ForEach-Object { Write-Host "  → $_" -ForegroundColor White }
Write-Host "==============================" -ForegroundColor Cyan
Write-Host ""
Write-Host "移行設定完了！ネームサーバー変更後、最大48時間で反映されます。" -ForegroundColor Green
Read-Host "Enterキーで終了"

$T = "TOKEN_HERE"
$IP = "160.251.71.29"
$D = "assetguardians88338.com"
$A = "https://api.cloudflare.com/client/v4"
$H = @{Authorization="Bearer $T"; "Content-Type"="application/json"}

$r = Invoke-RestMethod "$A/zones?name=$D" -Headers $H
if ($r.result.Count -eq 0) {
    $b = @{name=$D;jump_start=$true} | ConvertTo-Json
    $r = Invoke-RestMethod "$A/zones" -Method POST -Headers $H -Body $b
    $z = $r.result.id
} else {
    $z = $r.result[0].id
}
Write-Host "Zone: $z"

$d1 = @{type="A";name=$D;content=$IP;proxied=$true;ttl=1} | ConvertTo-Json
$d2 = @{type="A";name="www.$D";content=$IP;proxied=$true;ttl=1} | ConvertTo-Json
Invoke-RestMethod "$A/zones/$z/dns_records" -Method POST -Headers $H -Body $d1 -ErrorAction SilentlyContinue | Out-Null
Invoke-RestMethod "$A/zones/$z/dns_records" -Method POST -Headers $H -Body $d2 -ErrorAction SilentlyContinue | Out-Null
Write-Host "DNS OK"

Invoke-RestMethod "$A/zones/$z/settings/ssl" -Method PATCH -Headers $H -Body '{"value":"full"}' | Out-Null
Invoke-RestMethod "$A/zones/$z/settings/always_use_https" -Method PATCH -Headers $H -Body '{"value":"on"}' | Out-Null
Write-Host "SSL OK"

$ns = (Invoke-RestMethod "$A/zones/$z" -Headers $H).result.name_servers
Write-Host "=============================="
Write-Host "NS1: $($ns[0])"
Write-Host "NS2: $($ns[1])"
Write-Host "=============================="

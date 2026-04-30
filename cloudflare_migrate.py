#!/usr/bin/env python3
"""
ConoHa WordPress → Cloudflare 移行スクリプト
使い方:
  1. 下の設定欄に情報を入力
  2. pip install requests
  3. python3 cloudflare_migrate.py
"""

import requests
import json
import sys

# ===== 設定欄（ここを入力してください） =====
CLOUDFLARE_EMAIL = "your-email@example.com"       # Cloudflareのメールアドレス
CLOUDFLARE_API_TOKEN = "your-api-token-here"      # CloudflareのAPIトークン
DOMAIN = "assetguardians88338.com"                 # ドメイン名
CONOHA_SERVER_IP = "xxx.xxx.xxx.xxx"              # ConoHaサーバーのIPアドレス
# ==========================================

BASE_URL = "https://api.cloudflare.com/client/v4"

HEADERS = {
    "X-Auth-Email": CLOUDFLARE_EMAIL,
    "Authorization": f"Bearer {CLOUDFLARE_API_TOKEN}",
    "Content-Type": "application/json",
}


def check(res, step):
    data = res.json()
    if not data.get("success"):
        print(f"[失敗] {step}: {data.get('errors')}")
        sys.exit(1)
    print(f"[成功] {step}")
    return data.get("result")


def add_zone():
    print("\n--- 1. ドメインをCloudflareに追加 ---")
    res = requests.post(
        f"{BASE_URL}/zones",
        headers=HEADERS,
        json={"name": DOMAIN, "jump_start": True},
    )
    # すでに追加済みの場合は既存のzoneを取得
    data = res.json()
    if not data.get("success"):
        err_code = data["errors"][0].get("code", 0) if data.get("errors") else 0
        if err_code == 1061:
            print("[情報] ドメインはすでに追加済み。既存のZoneを取得します。")
            return get_existing_zone()
        print(f"[失敗] ドメイン追加: {data.get('errors')}")
        sys.exit(1)
    print(f"[成功] ドメイン追加")
    return data["result"]


def get_existing_zone():
    res = requests.get(f"{BASE_URL}/zones?name={DOMAIN}", headers=HEADERS)
    result = check(res, "既存Zone取得")
    return result[0]


def set_dns_records(zone_id):
    print("\n--- 2. DNSレコード設定 ---")
    records = [
        {"type": "A", "name": DOMAIN, "content": CONOHA_SERVER_IP, "proxied": True, "ttl": 1},
        {"type": "A", "name": f"www.{DOMAIN}", "content": CONOHA_SERVER_IP, "proxied": True, "ttl": 1},
    ]
    for record in records:
        res = requests.post(
            f"{BASE_URL}/zones/{zone_id}/dns_records",
            headers=HEADERS,
            json=record,
        )
        data = res.json()
        if not data.get("success"):
            # 重複エラーは無視
            if any(e.get("code") == 81057 for e in data.get("errors", [])):
                print(f"[情報] {record['name']} のAレコードはすでに存在します。")
            else:
                print(f"[失敗] DNSレコード ({record['name']}): {data.get('errors')}")
        else:
            print(f"[成功] Aレコード追加: {record['name']} → {CONOHA_SERVER_IP}")


def enable_ssl(zone_id):
    print("\n--- 3. SSL設定（Full Strict） ---")
    res = requests.patch(
        f"{BASE_URL}/zones/{zone_id}/settings/ssl",
        headers=HEADERS,
        json={"value": "full"},
    )
    check(res, "SSL設定")


def enable_https_redirect(zone_id):
    print("\n--- 4. HTTP→HTTPSリダイレクト有効化 ---")
    res = requests.patch(
        f"{BASE_URL}/zones/{zone_id}/settings/always_use_https",
        headers=HEADERS,
        json={"value": "on"},
    )
    check(res, "HTTPS強制リダイレクト")


def set_cache_level(zone_id):
    print("\n--- 5. キャッシュ設定（標準） ---")
    res = requests.patch(
        f"{BASE_URL}/zones/{zone_id}/settings/cache_level",
        headers=HEADERS,
        json={"value": "aggressive"},
    )
    check(res, "キャッシュレベル設定")


def get_nameservers(zone):
    print("\n--- 6. ネームサーバー情報 ---")
    ns_list = zone.get("name_servers", [])
    print("以下のネームサーバーをドメイン登録会社で設定してください：")
    for ns in ns_list:
        print(f"  → {ns}")
    return ns_list


def main():
    print(f"=== Cloudflare移行スクリプト: {DOMAIN} ===")

    if "your-" in CLOUDFLARE_API_TOKEN or "xxx" in CONOHA_SERVER_IP:
        print("\n[エラー] 設定欄を入力してから実行してください。")
        print("  - CLOUDFLARE_EMAIL")
        print("  - CLOUDFLARE_API_TOKEN")
        print("  - CONOHA_SERVER_IP")
        sys.exit(1)

    zone = add_zone()
    zone_id = zone["id"]
    print(f"Zone ID: {zone_id}")

    set_dns_records(zone_id)
    enable_ssl(zone_id)
    enable_https_redirect(zone_id)
    set_cache_level(zone_id)
    ns_list = get_nameservers(zone)

    print("\n=== 完了 ===")
    print("次のステップ：")
    print("1. 上記ネームサーバーをConoHaまたはドメイン登録会社で設定")
    print("2. 反映まで最大48時間かかる場合があります")
    print("3. 確認: python3 check_dns.py")


if __name__ == "__main__":
    main()

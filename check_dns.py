#!/usr/bin/env python3
"""
DNS・Cloudflare移行確認スクリプト
使い方: python3 check_dns.py
"""

import socket
import subprocess
import sys

DOMAIN = "assetguardians88338.com"


def check_dns():
    print(f"=== DNS確認: {DOMAIN} ===\n")

    # Aレコード確認
    try:
        ip = socket.gethostbyname(DOMAIN)
        print(f"[Aレコード] {DOMAIN} → {ip}")
    except Exception as e:
        print(f"[失敗] DNS解決できません: {e}")

    # www確認
    try:
        ip_www = socket.gethostbyname(f"www.{DOMAIN}")
        print(f"[Aレコード] www.{DOMAIN} → {ip_www}")
    except Exception as e:
        print(f"[失敗] www DNS解決できません: {e}")

    # ネームサーバー確認
    print("\n--- ネームサーバー確認 ---")
    try:
        result = subprocess.run(
            ["nslookup", "-type=NS", DOMAIN],
            capture_output=True, text=True, timeout=10
        )
        for line in result.stdout.splitlines():
            if "nameserver" in line.lower() or "name server" in line.lower():
                print(f"  {line.strip()}")
    except FileNotFoundError:
        print("  nslookupが見つかりません（dig等で手動確認してください）")
    except Exception as e:
        print(f"  確認失敗: {e}")

    # Cloudflare経由かチェック
    print("\n--- Cloudflare経由チェック ---")
    try:
        import urllib.request
        req = urllib.request.Request(
            f"https://{DOMAIN}",
            headers={"User-Agent": "Mozilla/5.0"}
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            cf_ray = resp.headers.get("CF-RAY", None)
            server = resp.headers.get("Server", "不明")
            if cf_ray:
                print(f"[成功] Cloudflare経由で配信中 (CF-RAY: {cf_ray})")
            else:
                print(f"[情報] Cloudflare未経由 (Server: {server})")
            print(f"  HTTPステータス: {resp.status}")
    except Exception as e:
        print(f"[情報] HTTPSアクセス確認失敗: {e}")

    print("\n=== 確認完了 ===")


if __name__ == "__main__":
    check_dns()

#!/usr/bin/env python3
"""
Cloudflare APIトークン無効化スクリプト

チャットや公開の場所でトークンが漏洩した場合は、
すぐにこのスクリプトで無効化してください。

使い方:
  export CF_API_TOKEN="漏洩したトークン"
  python3 revoke_token.py

または直接引数で指定:
  python3 revoke_token.py <token>
"""

import os
import sys
import requests

BASE_URL = "https://api.cloudflare.com/client/v4"


def get_token_id(token: str) -> str:
    """トークン文字列からトークンIDを取得する"""
    res = requests.get(
        f"{BASE_URL}/user/tokens/verify",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = res.json()
    if not data.get("success"):
        print(f"[エラー] トークンの確認に失敗しました: {data.get('errors')}")
        sys.exit(1)
    token_id = data["result"]["id"]
    print(f"[確認] トークンID: {token_id} (status: {data['result']['status']})")
    return token_id


def revoke_token(token: str, token_id: str) -> None:
    """指定IDのトークンを無効化する"""
    res = requests.delete(
        f"{BASE_URL}/user/tokens/{token_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    data = res.json()
    if not data.get("success"):
        print(f"[エラー] トークンの無効化に失敗しました: {data.get('errors')}")
        sys.exit(1)
    print(f"[完了] トークン {token_id} を無効化しました。")


def main() -> None:
    if len(sys.argv) > 1:
        token = sys.argv[1]
    else:
        token = os.environ.get("CF_API_TOKEN", "")

    if not token:
        print("[エラー] トークンが指定されていません。")
        print("  CF_API_TOKEN 環境変数を設定するか、引数でトークンを指定してください。")
        sys.exit(1)

    print("=== Cloudflare APIトークン無効化ツール ===")
    print("[注意] この操作は元に戻せません。トークンは完全に無効化されます。")
    confirm = input("無効化を実行しますか？ (yes/no): ").strip().lower()
    if confirm != "yes":
        print("キャンセルしました。")
        sys.exit(0)

    token_id = get_token_id(token)
    revoke_token(token, token_id)
    print("\n次のステップ:")
    print("  1. 新しいAPIトークンを https://dash.cloudflare.com のAPIトークン設定から発行してください。")
    print("  2. 新しいトークンは環境変数 CF_API_TOKEN に設定して使用してください。")
    print("  3. トークンをコードやチャットに直接書かないよう注意してください。")


if __name__ == "__main__":
    main()

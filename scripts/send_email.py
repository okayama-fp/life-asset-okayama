#!/usr/bin/env python3
"""
Gmail SMTP でメール送信するスクリプト
環境変数 MAIL_MODE で動作を切り替え：
  success        → 毎日自動記事の完了通知
  failure        → 毎日自動記事の失敗通知
  manual_success → 手動記事の完了通知
  manual_failure → 手動記事の失敗通知
"""

import smtplib
import os
import sys
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

SITE_URL  = "https://lifeassetoffice.net"
NOTE_URL  = "https://note.com/lifeasset_fp"
TO_EMAIL  = "lifeassetpartners@gmail.com"
ACTIONS_URL = "https://github.com/okayama-fp/life-asset-okayama/actions"


def send(subject: str, body: str):
    from_email   = os.environ["GMAIL_USERNAME"]
    app_password = os.environ["GMAIL_APP_PASSWORD"]

    msg = MIMEMultipart()
    msg["From"]    = f"ライフアセット自動投稿 <{from_email}>"
    msg["To"]      = TO_EMAIL
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain", "utf-8"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
        server.starttls()
        server.login(from_email, app_password)
        server.send_message(msg)

    print(f"✅ メール送信完了: {TO_EMAIL}")


def read_note_draft() -> str:
    if os.path.exists("note_draft_for_email.txt"):
        with open("note_draft_for_email.txt", "r", encoding="utf-8") as f:
            return f.read()
    return "（note下書きの生成に失敗しました）"


def main():
    mode = os.environ.get("MAIL_MODE", "success")

    if mode == "success":
        title      = os.environ.get("MAIL_TITLE",     "（タイトルなし）")
        category   = os.environ.get("MAIL_CATEGORY",  "")
        filename   = os.environ.get("MAIL_FILENAME",  "")
        date       = os.environ.get("MAIL_DATE",      "")
        note_type  = os.environ.get("MAIL_NOTE_TYPE", "")
        note_body  = read_note_draft()

        subject = f"✅ [{note_type}] note下書き + ブログ自動投稿 [{date}]"
        body = f"""━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 note記事（{note_type}）下書き
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

↓↓ 以下をnoteにコピー＆ペーストしてください ↓↓

{note_body}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📰 ブログ自動投稿 完了
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

■ タイトル：{title}
■ カテゴリ：{category}
■ 投稿日時：{date} 07:00 JST
■ ブログURL：{SITE_URL}/blog/{filename}
■ note管理：{NOTE_URL}

─────────────────────
ライフアセットオフィス 自動投稿システム"""

    elif mode == "failure":
        subject = "⚠️ ブログ自動投稿が失敗しました"
        body = f"""本日の自動投稿でエラーが発生しました。

GitHub Actions のログを確認してください：
{ACTIONS_URL}

─────────────────────
ライフアセットオフィス 自動投稿システム"""

    elif mode == "manual_success":
        note_body = read_note_draft()
        subject = "📝 X投稿完了 + note下書き | 手動ブログ記事"
        body = f"""手動ブログ記事が公開されました。
X投稿は自動で完了しています。

以下のnote下書きをnoteにコピー＆ペーストしてください。

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📝 note下書き
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{note_body}

─────────────────────
ライフアセットオフィス 自動投稿システム"""

    elif mode == "manual_failure":
        subject = "⚠️ 手動記事の自動通知が失敗しました"
        body = f"""手動ブログ記事の自動通知でエラーが発生しました。

GitHub Actions のログを確認してください：
{ACTIONS_URL}

─────────────────────
ライフアセットオフィス 自動投稿システム"""

    else:
        print(f"未知のMAIL_MODE: {mode}")
        sys.exit(1)

    send(subject, body)


if __name__ == "__main__":
    main()

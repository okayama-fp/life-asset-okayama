"""
DistroKid 自動アップロードスクリプト
Playwright でブラウザを操作し、楽曲をアップロードします。

使用方法:
  pip install playwright
  playwright install chromium
  python upload_distrokid.py \
    --email "your@email.com" \
    --password "yourpassword" \
    --audio "morning_breeze.mp3" \
    --cover "cover.jpg" \
    --title "Morning Breeze" \
    --artist "Life Asset" \
    --genre "Pop"
"""

import argparse
import asyncio
import sys
from pathlib import Path


async def upload_to_distrokid(
    email: str,
    password: str,
    audio_path: str,
    cover_path: str,
    title: str,
    artist: str,
    genre: str = "Pop",
):
    from playwright.async_api import async_playwright

    audio_file = Path(audio_path).resolve()
    cover_file = Path(cover_path).resolve()

    if not audio_file.exists():
        print(f"❌ 音楽ファイルが見つかりません: {audio_path}")
        sys.exit(1)
    if not cover_file.exists():
        print(f"❌ ジャケット画像が見つかりません: {cover_path}")
        sys.exit(1)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 確認のため headless=False
        page = await browser.new_page()

        print("DistroKid にログイン中...")
        await page.goto("https://distrokid.com/signin/")
        await page.fill('input[name="email"]', email)
        await page.fill('input[name="password"]', password)
        await page.click('button[type="submit"]')
        await page.wait_for_load_state("networkidle")
        print("✅ ログイン完了")

        print("アップロードページへ移動中...")
        await page.goto("https://distrokid.com/new/")
        await page.wait_for_load_state("networkidle")

        # アーティスト名入力
        print(f"アーティスト名入力: {artist}")
        artist_input = page.locator('input[placeholder*="artist"], input[name*="artist"]').first
        await artist_input.fill(artist)

        # アルバム/曲名入力
        print(f"曲名入力: {title}")
        title_input = page.locator('input[placeholder*="title"], input[name*="title"], input[placeholder*="album"]').first
        await title_input.fill(title)

        # ジャンル選択
        print(f"ジャンル選択: {genre}")
        try:
            genre_select = page.locator('select[name*="genre"]').first
            await genre_select.select_option(label=genre)
        except Exception:
            print(f"  ⚠ ジャンル自動選択をスキップ（手動で選択してください）")

        # ジャケット画像アップロード
        print(f"ジャケット画像アップロード: {cover_file.name}")
        cover_input = page.locator('input[type="file"][accept*="image"], input[type="file"][name*="cover"]').first
        await cover_input.set_input_files(str(cover_file))
        await page.wait_for_timeout(2000)

        # 音楽ファイルアップロード
        print(f"音楽ファイルアップロード: {audio_file.name}")
        audio_input = page.locator('input[type="file"][accept*="audio"], input[type="file"][name*="audio"]').first
        await audio_input.set_input_files(str(audio_file))
        await page.wait_for_timeout(3000)

        print("\n✅ フォーム入力完了")
        print("⚠  送信前に画面を確認し、必要な項目（リリース日、価格等）を手動で確認してください。")
        print("   問題なければブラウザ上で「Submit」ボタンを押してください。")

        # ブラウザを開いたまま待機
        input("準備ができたらEnterキーを押してブラウザを閉じます: ")
        await browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="DistroKid 自動アップロード")
    parser.add_argument("--email", required=True, help="DistroKid メールアドレス")
    parser.add_argument("--password", required=True, help="DistroKid パスワード")
    parser.add_argument("--audio", required=True, help="音楽ファイルパス (MP3/WAV/FLAC)")
    parser.add_argument("--cover", required=True, help="ジャケット画像パス (JPG)")
    parser.add_argument("--title", required=True, help="曲名")
    parser.add_argument("--artist", required=True, help="アーティスト名")
    parser.add_argument("--genre", default="Pop", help="ジャンル (デフォルト: Pop)")
    args = parser.parse_args()

    asyncio.run(upload_to_distrokid(
        email=args.email,
        password=args.password,
        audio_path=args.audio,
        cover_path=args.cover,
        title=args.title,
        artist=args.artist,
        genre=args.genre,
    ))

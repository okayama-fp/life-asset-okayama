#!/usr/bin/env python3
"""
手動ブログ記事（post-*.html）の通知スクリプト
- 新規post-*.htmlを検出してGemini APIでX投稿文・note下書きを生成
- Xに自動投稿
- note下書きをファイルに保存（メール用）
"""

from google import genai
from bs4 import BeautifulSoup
import tweepy
import os
import time
from pathlib import Path

SITE_URL = "https://lifeassetoffice.net"


def extract_content(html_file: str) -> dict:
    with open(html_file, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')

    title = ''
    h1 = soup.find('h1')
    if h1:
        title = h1.get_text(strip=True)

    content_div = (
        soup.find(class_='article-content')
        or soup.find('article')
        or soup.find('main')
    )
    raw = content_div.get_text(separator='\n', strip=True) if content_div else soup.get_text(separator='\n', strip=True)
    text = '\n'.join(line for line in raw.split('\n') if line.strip())[:2000]

    return {'title': title, 'text': text}


def gemini_generate(client, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.0-flash-lite",
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            if attempt < retries - 1:
                wait = 30 * (attempt + 1)
                print(f"[Gemini] エラー: {e} → {wait}秒後リトライ")
                time.sleep(wait)
            else:
                raise


def generate_x_post(client, title: str, text: str, url: str) -> str:
    prompt = f"""あなたはライフアセットオフィスのFP（ファイナンシャルプランナー）です。
以下のブログ記事のX（旧Twitter）投稿文を作成してください。

ブログタイトル: {title}
ブログURL: {url}
記事内容（抜粋）:
{text[:500]}

【厳守ルール】
- 日本語1文字=2ウェイト、URL=23ウェイト、英数字・記号=1ウェイト
- 合計280ウェイト以内に必ず収める（超えたら絶対NG）
- 数字と具体的事例で読者の興味を引く
- 最後に「👇」と「{url}」を入れる
- ハッシュタグ2〜3個（#住宅ローン #FP #資産形成 など記事に合わせて）
- 絵文字と改行で読みやすく

投稿文のみ出力してください（説明不要）。"""
    return gemini_generate(client, prompt)


def generate_note_draft(client, title: str, text: str, blog_url: str) -> str:
    prompt = f"""あなたはライフアセットオフィスのFP資格者が運営するnoteマガジンのライターです。
以下のブログ記事をベースに、note用の無料記事を書いてください。

ブログタイトル: {title}
ブログURL: {blog_url}
記事内容（抜粋）:
{text[:800]}

【ルール】
- 800〜1200文字
- マークダウン形式（# タイトル、## 見出し、- 箇条書き）
- ブログと完全に同じにならず、note読者向けに書き直す
- FP目線の気づきやアドバイスを入れる
- 最後に「👉 詳しくはブログで\\n{blog_url}」を入れる
- 無料記事として書く

タイトルから本文まで完全なnote記事を出力してください。"""
    return gemini_generate(client, prompt)


def post_to_x(tweet: str) -> str:
    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )
    response = client.create_tweet(text=tweet)
    return f"https://x.com/i/web/status/{response.data['id']}"


def main():
    new_posts_file = 'new_posts.txt'
    if not os.path.exists(new_posts_file):
        print("new_posts.txt not found")
        return

    with open(new_posts_file) as f:
        new_posts = [line.strip() for line in f if line.strip()]

    if not new_posts:
        print("新規post-*.htmlなし。スキップ。")
        return

    gemini_client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    results = []

    for post_file in new_posts:
        if not os.path.exists(post_file):
            print(f"ファイルなし: {post_file}")
            continue

        filename = Path(post_file).name
        url = f"{SITE_URL}/blog/{filename}"

        print(f"\n処理中: {post_file}")
        content = extract_content(post_file)
        title = content['title']
        text = content['text']

        if not title:
            print(f"タイトル取得失敗: {post_file}")
            continue

        print(f"タイトル: {title}")

        print("X投稿文を生成中...")
        x_post = generate_x_post(gemini_client, title, text, url)
        print(f"X投稿文:\n{x_post}\n")

        try:
            x_url = post_to_x(x_post)
            print(f"✅ X投稿完了: {x_url}")
        except Exception as e:
            print(f"⚠️ X投稿エラー: {e}")
            x_url = "（投稿失敗）"

        print("note下書きを生成中...")
        note_draft = generate_note_draft(gemini_client, title, text, url)

        results.append({
            'title': title,
            'url': url,
            'x_post': x_post,
            'x_url': x_url,
            'note_draft': note_draft,
        })

    if results:
        with open('note_draft_for_email.txt', 'w', encoding='utf-8') as f:
            for item in results:
                f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
                f.write(f"📰 {item['title']}\n")
                f.write(f"🔗 ブログURL: {item['url']}\n")
                f.write(f"🐦 X投稿: {item['x_url']}\n")
                f.write("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n")
                f.write("【note下書き（コピー＆ペーストしてください）】\n\n")
                f.write(item['note_draft'])
                f.write("\n\n")

        print(f"\n✅ note下書き保存完了（{len(results)}件）")


if __name__ == '__main__':
    main()

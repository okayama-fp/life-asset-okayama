#!/usr/bin/env python3
"""ブログ記事をXに自動ポストするスクリプト"""

import tweepy
import os
import sys

def main():
    title    = sys.argv[1] if len(sys.argv) > 1 else "新着FP記事"
    filename = sys.argv[2] if len(sys.argv) > 2 else ""
    category = sys.argv[3] if len(sys.argv) > 3 else "FP"

    url = f"https://lifeassetoffice.net/blog/{filename}"

    hashtags = {
        "家計管理":    "#家計管理 #節約 #お金の管理",
        "NISA・投資":  "#NISA #新NISA #投資初心者",
        "節税・控除":  "#節税 #確定申告 #ふるさと納税",
        "ライフプラン": "#ライフプラン #FP #資産形成",
        "保険":        "#保険 #生命保険 #医療保険",
        "住宅・ローン": "#住宅ローン #マイホーム #不動産",
        "老後・年金":   "#老後資金 #年金 #iDeCo",
    }
    tags = hashtags.get(category, "#FP #資産形成 #家計管理")

    tweet = f"""📊【本日のFP解説】

{title}

資産形成・節税・老後資金について、FP資格者がわかりやすく解説します。

🔗 {url}

{tags} #ライフアセット"""

    # 280文字制限チェック
    if len(tweet) > 280:
        tweet = f"📊【FP解説】{title}\n\n🔗 {url}\n\n{tags} #ライフアセット"

    client = tweepy.Client(
        consumer_key=os.environ["X_API_KEY"],
        consumer_secret=os.environ["X_API_SECRET"],
        access_token=os.environ["X_ACCESS_TOKEN"],
        access_token_secret=os.environ["X_ACCESS_TOKEN_SECRET"],
    )

    response = client.create_tweet(text=tweet)
    print(f"✅ Xに投稿しました: https://x.com/i/web/status/{response.data['id']}")

if __name__ == "__main__":
    main()

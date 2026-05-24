#!/usr/bin/env python3
"""
ライフアセットオフィス 自動ブログ記事生成スクリプト
- Gemini API でFP専門記事を生成（3000〜5000文字）
- blog/YYYY-MM-DD.html として保存
- blog/index.html の先頭に記事カードを追加
- GitHub Actions の GITHUB_OUTPUT に結果を出力
"""

from google import genai
import feedparser
import os
import json
import re
import random
import time
from datetime import datetime
import pytz

# ───────────────────────────────────────────
# 設定
# ───────────────────────────────────────────
JST = pytz.timezone('Asia/Tokyo')
NOW = datetime.now(JST)
DATE_STR   = NOW.strftime('%Y-%m-%d')
DATE_JP    = NOW.strftime('%Y年%-m月%-d日')
TIME_STR   = NOW.strftime('%H:%M')
YEAR_MONTH = NOW.strftime('%Y年%-m月')

ARTICLE_FILENAME = f"{DATE_STR}.html"
ARTICLE_PATH     = f"blog/{ARTICLE_FILENAME}"
BLOG_INDEX_PATH  = "blog/index.html"
NOTE_DRAFT_PATH  = f"note-drafts/{DATE_STR}.md"

CONTACT_EMAIL = "yamakaze8000@gmail.com"
SITE_URL      = "https://lifeassetoffice.net"
NOTE_URL      = "https://note.com/lifeasset_fp"

# 月の日付が3の倍数なら有料記事（月に約10回有料）
IS_PAID_NOTE  = (NOW.day % 3 == 0)

# 日替わり記事フォーマット
ARTICLE_FORMATS = [
    ("ランキング", "「〇〇ベスト5」「やってはいけない〇つのこと」など順位・番号で構成する"),
    ("ケーススタディ", "実在しそうな家庭の具体例（例：35歳・年収500万・子2人）をもとにシミュレーションで解説する"),
    ("Q&A", "読者がよく抱く疑問を3〜5つ立てて、FP目線でズバリ答える形式にする"),
    ("比較", "「A vs B どちらがお得？」の形式で2つの選択肢を数字で比較する"),
    ("チェックリスト", "「今すぐ確認すべき〇項目」の形式で読者が自分でチェックできる内容にする"),
    ("失敗事例", "「実はやってはいけない〇つのこと」「多くの人が損している理由」の切り口で問題提起する"),
    ("シミュレーション", "「今〇万円を積み立てると〇年後にいくらになる？」など具体的な数字で未来を見せる"),
]
ARTICLE_FORMAT_NAME, ARTICLE_FORMAT_RULE = ARTICLE_FORMATS[NOW.day % len(ARTICLE_FORMATS)]

# 日替わり読者ペルソナ
TARGET_PERSONAS = [
    "20代・社会人1〜5年目（初めて貯金・投資を始めようとしている）",
    "30代・共働き夫婦（子育て費用と将来の老後資金を同時に悩んでいる）",
    "40代・教育費のピークと老後準備が重なって不安な会社員",
    "50代・定年が近づき退職金の使い方やiDeCoをどうするか迷っている人",
    "シングル女性・独身の方（一人で老後2000万円を準備しなければならない不安）",
]
TARGET_PERSONA = TARGET_PERSONAS[(NOW.day + NOW.month) % len(TARGET_PERSONAS)]

# カテゴリとスタイルの対応
CATEGORY_STYLES = {
    "家計管理":   {"tag_class": "tag-life",      "bg": "bg-green",  "emoji_bg": "💰"},
    "NISA・投資": {"tag_class": "tag-nisa",      "bg": "bg-blue",   "emoji_bg": "📈"},
    "節税・控除": {"tag_class": "tag-tax",       "bg": "bg-indigo", "emoji_bg": "💡"},
    "ライフプラン":{"tag_class": "tag-life",      "bg": "bg-amber",  "emoji_bg": "🗺️"},
    "保険":       {"tag_class": "tag-insurance", "bg": "bg-pink",   "emoji_bg": "🛡️"},
    "住宅・ローン":{"tag_class": "tag-loan",      "bg": "bg-green",  "emoji_bg": "🏠"},
    "老後・年金": {"tag_class": "tag-nisa",      "bg": "bg-blue",   "emoji_bg": "👴"},
}

# ───────────────────────────────────────────
# ニュース取得
# ───────────────────────────────────────────
def fetch_news():
    rss_feeds = [
        ("NHK経済",   "https://www3.nhk.or.jp/rss/news/cat3.xml"),
        ("NHK社会",   "https://www3.nhk.or.jp/rss/news/cat5.xml"),
        ("NHK政治",   "https://www3.nhk.or.jp/rss/news/cat4.xml"),
    ]
    items = []
    for name, url in rss_feeds:
        try:
            d = feedparser.parse(url)
            for e in d.entries[:4]:
                title   = e.get('title', '').strip()
                summary = re.sub(r'<[^>]+>', '', e.get('summary', '')).strip()[:120]
                if title:
                    items.append(f"【{name}】{title}：{summary}")
        except Exception:
            pass
    return "\n".join(items[:10]) if items else "本日の経済・政治ニュースを確認中"


# ───────────────────────────────────────────
# Gemini で note 記事生成
def gemini_generate(client, prompt: str, retries: int = 3) -> str:
    for attempt in range(retries):
        try:
            response = client.models.generate_content(model="gemini-2.0-flash-lite", contents=prompt)
            return response.text.strip()
        except Exception as e:
            if attempt < retries - 1:
                wait = 65 * (attempt + 1)
                print(f"[Gemini] エラー: {e} → {wait}秒後リトライ ({attempt+1}/{retries})")
                time.sleep(wait)
            else:
                raise

# ───────────────────────────────────────────
def generate_note_article(news_text: str, blog_title: str, blog_body: str) -> str:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    if IS_PAID_NOTE:
        note_type = "有料記事（深掘り・実践編）"
        length_req = "2000〜3000文字"
        extra_req = """
- 具体的な数字・シミュレーション例を必ず含める
- 「すぐに使えるチェックリスト」か「穴埋め式ワークシート」を1つ含める
- 読者が行動できるような具体的なアクションプランで締める
- 有料記事にふさわしい深い内容にすること"""
    else:
        note_type = "無料記事（入門・気づき編）"
        length_req = "800〜1200文字"
        extra_req = """
- 読みやすく短くまとめる
- 最後に「続きは有料マガジンで詳しく解説」と誘導する
- フォロワーが増えるよう、役立つ豆知識か気づきを1つ入れる"""

    prompt = f"""あなたはFP資格者が運営するnoteマガジン「ライフアセットFP通信」のライターです。
今日は{DATE_JP}です。

以下のブログ記事をベースに、note用の記事を書いてください。
ブログと完全に同じにならず、note読者向けに書き直してください。

【参考ブログタイトル】{blog_title}
【参考ブログ内容（抜粋）】
{blog_body[:800]}

【記事種別】{note_type}
【文字数】{length_req}
【要件】{extra_req}

【出力形式】
タイトル行（# から始める）を最初に書き、その後に本文を書いてください。
見出しは ## を使い、箇条書きは - を使ってください。
"""

    return gemini_generate(client, prompt)


def save_note_draft(content: str) -> str:
    os.makedirs("note-drafts", exist_ok=True)
    note_type_label = "【有料】" if IS_PAID_NOTE else "【無料】"
    note_type_str   = 'paid' if IS_PAID_NOTE else 'free'
    header = f"---\ndate: {DATE_JP}\ntype: {note_type_str}\nlabel: {note_type_label}\nnote_url: {NOTE_URL}\n---\n\n"
    full_content = header + content
    with open(NOTE_DRAFT_PATH, "w", encoding="utf-8") as f:
        f.write(full_content)
    return full_content


# ───────────────────────────────────────────
# Gemini で記事生成
# ───────────────────────────────────────────
def generate_article(news_text: str) -> dict:
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""あなたはライフアセットオフィスの人気FPブログライターです。
今日は{DATE_JP}です。

【今日の記事フォーマット】{ARTICLE_FORMAT_NAME}形式
{ARTICLE_FORMAT_RULE}

【今日のターゲット読者】
{TARGET_PERSONA}

【参考にする最新ニュース】
{news_text}

【記事作成ルール】
1. タイトルは「数字」か「疑問形」か「〜してはいけない」を含める魅力的なものにする
   良い例：「新NISAで月3万円積み立てると30年後どうなる？35歳からシミュレーション」
   良い例：「保険料を年20万円節約した人がやった3つのこと」
   悪い例：「NISAについて解説します」「家計管理の基本」

2. 導入は必ずターゲット読者の「悩み・不安」への共感から始める
   例：「毎月頑張って働いているのに、なぜかお金が貯まらない…そんな悩みを抱えていませんか？」

3. 本文には必ず以下を含める：
   - 具体的な金額（例：月3万円、年収500万円、退職金2000万円など）
   - 具体的な年数・年齢（例：35歳から20年間、65歳までに）
   - 比較できる数字（積み立てた場合 vs しなかった場合など）

4. 見出しも魅力的にする
   良い例：「## 月1万円の差が30年で1000万円になる理由」
   悪い例：「## NISAの概要」

5. 最後に「今日からできる3つのアクション」で締める

6. 文字数：3000〜4000文字
7. ニュースをFP視点で家計・資産形成に自然に結びつける

【出力形式】
まず以下のJSONを1行で出力し、その次の行から本文を書いてください：
{{"title":"記事タイトル","category":"カテゴリ","emoji":"絵文字1文字","description":"記事説明（100文字以内）","reading_time":"読了時間（数字のみ）"}}

カテゴリ候補：家計管理, NISA・投資, 節税・控除, ライフプラン, 保険, 住宅・ローン, 老後・年金

本文の見出しは ## 見出しテキスト の形式で書いてください。
"""

    raw = gemini_generate(client, prompt)

    # JSON を抽出
    meta = {
        "title": f"{DATE_JP}のFP解説",
        "category": "家計管理",
        "emoji": "💡",
        "description": f"{DATE_JP}の経済ニュースをFPの視点で解説します。",
        "reading_time": "8",
    }
    body_text = raw

    for i, line in enumerate(raw.split("\n")):
        line = line.strip()
        if line.startswith("{") and line.endswith("}"):
            try:
                meta = {**meta, **json.loads(line)}
                body_text = "\n".join(raw.split("\n")[i + 1:]).strip()
                break
            except json.JSONDecodeError:
                pass

    return {"meta": meta, "body": body_text}


# ───────────────────────────────────────────
# Markdown → HTML 変換
# ───────────────────────────────────────────
def md_to_html(text: str) -> tuple[str, list[tuple[str, str]]]:
    lines  = text.split("\n")
    parts  = []
    toc    = []
    sec_n  = 0
    ul_buf: list[str] = []

    def flush_ul():
        if ul_buf:
            parts.append("  <ul>\n" + "\n".join(f"    <li>{item}</li>" for item in ul_buf) + "\n  </ul>")
            ul_buf.clear()

    for line in lines:
        stripped = line.strip()
        if not stripped:
            flush_ul()
            continue

        if stripped.startswith("## "):
            flush_ul()
            sec_n += 1
            heading = stripped[3:].strip()
            sid = f"sec{sec_n}"
            toc.append((sid, heading))
            parts.append(f'  <h2 id="{sid}">{heading}</h2>')

        elif stripped.startswith("### "):
            flush_ul()
            parts.append(f'  <h3 style="font-size:1rem;font-weight:700;color:var(--navy);margin:20px 0 10px">{stripped[4:].strip()}</h3>')

        elif stripped.startswith(("- ", "* ", "・")):
            item = stripped[2:].strip() if stripped[:2] in ("- ", "* ") else stripped[1:].strip()
            item = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", item)
            ul_buf.append(item)

        else:
            flush_ul()
            para = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", stripped)
            parts.append(f"  <p>{para}</p>")

    flush_ul()
    return "\n".join(parts), toc


# ───────────────────────────────────────────
# HTML テンプレート生成
# ───────────────────────────────────────────
def build_html(meta: dict, body_html: str, toc: list) -> str:
    title       = meta["title"]
    category    = meta["category"]
    emoji       = meta["emoji"]
    description = meta["description"]
    reading_time= meta["reading_time"]

    style_info  = CATEGORY_STYLES.get(category, CATEGORY_STYLES["家計管理"])
    tag_class   = style_info["tag_class"]
    post_id     = DATE_STR

    # 目次 HTML
    toc_html = "\n".join(
        f'      <li><a href="#{sid}">{heading}</a></li>'
        for sid, heading in toc
    )

    # アフィリエイト枠
    affiliate_html = """
<div style="background:#fff7ed;border:2px solid #fed7aa;border-radius:16px;padding:24px;margin:32px 0">
  <h3 style="font-size:1rem;font-weight:700;color:#92400e;margin-bottom:4px">📊 資産形成の第一歩はこちら</h3>
  <p style="font-size:0.78rem;color:#b45309;margin-bottom:16px">※アフィリエイトリンクを設定してください（A8.net / バリューコマース）</p>
  <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:12px">
    <a href="#" data-affiliate="sbi-nisa" target="_blank" rel="noopener sponsored"
       style="display:block;background:#fff;border:1.5px solid #fed7aa;border-radius:10px;padding:14px;text-align:center;color:#92400e;font-size:0.85rem;font-weight:700;transition:box-shadow .2s">
      📈 SBI証券<br><span style="font-size:0.75rem;font-weight:400">新NISA口座を開く</span>
    </a>
    <a href="#" data-affiliate="rakuten-nisa" target="_blank" rel="noopener sponsored"
       style="display:block;background:#fff;border:1.5px solid #fed7aa;border-radius:10px;padding:14px;text-align:center;color:#92400e;font-size:0.85rem;font-weight:700">
      💳 楽天証券<br><span style="font-size:0.75rem;font-weight:400">iDeCo・NISA対応</span>
    </a>
    <a href="#" data-affiliate="insurance" target="_blank" rel="noopener sponsored"
       style="display:block;background:#fff;border:1.5px solid #fed7aa;border-radius:10px;padding:14px;text-align:center;color:#92400e;font-size:0.85rem;font-weight:700">
      🛡️ 保険見直し<br><span style="font-size:0.75rem;font-weight:400">無料相談サービス</span>
    </a>
  </div>
</div>"""

    # AdSense 枠
    adsense_html = """
<ins class="adsbygoogle"
     style="display:block"
     data-ad-client="ca-pub-1266918303152498"
     data-ad-slot="auto"
     data-ad-format="auto"
     data-full-width-responsive="true"></ins>
<script>(adsbygoogle = window.adsbygoogle || []).push({});</script>"""

    return f"""<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <link rel="canonical" href="{SITE_URL}/blog/{ARTICLE_FILENAME}">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title}｜Life Asset ブログ</title>
  <meta name="description" content="{description}">
  <meta http-equiv="Referrer-Policy" content="strict-origin-when-cross-origin">
  <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-1266918303152498" crossorigin="anonymous"></script>
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
  <style>
    :root{{--sky:#0ea5e9;--sl:#38bdf8;--sb:#f0f9ff;--sp:#e0f2fe;--navy:#0f3460;--nl:#1e4d8c;--w:#fff;--gb:#f8fafc;--t:#1e293b;--tl:#64748b;--b:#e2e8f0}}
    *,*::before,*::after{{box-sizing:border-box;margin:0;padding:0}}
    html{{scroll-behavior:smooth}}
    body{{font-family:'Noto Sans JP','Hiragino Kaku Gothic ProN',sans-serif;color:var(--t);background:var(--gb);line-height:1.8}}
    a{{color:inherit;text-decoration:none}}
    img{{max-width:100%}}
    #pb{{position:fixed;top:0;left:0;height:3px;width:0%;background:linear-gradient(90deg,var(--sky),var(--sl));z-index:9999;transition:width .1s linear}}
    header{{position:sticky;top:0;z-index:200;background:rgba(255,255,255,0.96);backdrop-filter:blur(8px);border-bottom:1px solid var(--b);box-shadow:0 1px 8px rgba(14,165,233,0.07)}}
    .header-inner{{max-width:1100px;margin:0 auto;padding:0 24px;height:64px;display:flex;align-items:center;gap:24px}}
    .logo{{display:flex;align-items:center;gap:10px;flex-shrink:0}}
    .logo-text .name{{font-size:1.25rem;font-weight:700;background:linear-gradient(90deg,#4facfe,#00f2fe);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;line-height:1.1}}
    .logo-text .tagline{{font-size:0.62rem;color:var(--tl);white-space:nowrap}}
    nav{{display:flex;gap:4px;margin-left:auto}}
    nav a{{padding:6px 14px;border-radius:20px;font-size:0.875rem;font-weight:500;color:var(--t);transition:all .2s}}
    nav a:hover,nav a.active{{background:var(--sp);color:var(--sky)}}
    .btn-cta{{padding:8px 20px;border-radius:22px;background:linear-gradient(90deg,var(--sky),var(--sl));color:#fff;font-size:0.875rem;font-weight:600;white-space:nowrap;box-shadow:0 2px 8px rgba(14,165,233,0.3);transition:opacity .2s}}
    .btn-cta:hover{{opacity:.85}}
    .breadcrumb{{max-width:760px;margin:0 auto;padding:16px 24px 0;font-size:0.8rem;color:var(--tl);display:flex;align-items:center;gap:6px;flex-wrap:wrap}}
    .breadcrumb a{{color:var(--sky)}}
    .article-header{{max-width:760px;margin:0 auto;padding:20px 24px 16px}}
    .article-tag{{display:inline-block;padding:4px 14px;border-radius:14px;font-size:0.78rem;font-weight:700;margin-bottom:14px;background:var(--sp);color:var(--sky)}}
    .article-title{{font-size:clamp(1.4rem,3.5vw,2rem);font-weight:700;color:var(--navy);line-height:1.35;margin-bottom:16px}}
    .article-meta{{display:flex;align-items:center;gap:16px;font-size:0.82rem;color:var(--tl);flex-wrap:wrap}}
    .toc{{max-width:760px;margin:24px auto 32px;padding:0 24px}}
    .toc-box{{background:#fff;border:1.5px solid var(--sp);border-radius:14px;padding:20px 24px;border-left:4px solid var(--sky)}}
    .toc-box h2{{font-size:0.9rem;font-weight:700;color:var(--navy);margin-bottom:12px}}
    .toc-list{{list-style:none;display:flex;flex-direction:column;gap:6px}}
    .toc-list li a{{font-size:0.875rem;color:var(--sky);display:flex;align-items:baseline;gap:7px;transition:opacity .2s}}
    .toc-list li a:hover{{opacity:.7;text-decoration:underline}}
    .toc-list li a::before{{content:'▸';font-size:0.7rem;flex-shrink:0}}
    .article-content{{max-width:760px;margin:0 auto;padding:0 24px 48px}}
    .article-content h2{{font-size:1.2rem;font-weight:700;color:var(--navy);margin:36px 0 14px;padding:10px 16px;border-left:4px solid var(--sky);background:var(--sb);border-radius:0 8px 8px 0;line-height:1.4}}
    .article-content h3{{font-size:1rem;font-weight:700;color:var(--navy);margin:20px 0 10px}}
    .article-content p{{margin-bottom:16px;font-size:0.97rem;line-height:1.85}}
    .article-content ul{{padding-left:1.4em;margin-bottom:16px}}
    .article-content li{{font-size:0.97rem;margin-bottom:6px;line-height:1.7}}
    .share-section{{max-width:760px;margin:0 auto 40px;padding:0 24px}}
    .share-section h2{{font-size:0.95rem;font-weight:700;color:var(--navy);margin-bottom:12px}}
    .share-btns{{display:flex;gap:12px;flex-wrap:wrap}}
    .share-btn{{display:inline-flex;align-items:center;gap:8px;padding:10px 20px;border-radius:22px;font-size:0.875rem;font-weight:600;color:#fff;cursor:pointer;transition:opacity .2s;border:none;font-family:inherit}}
    .share-btn:hover{{opacity:.85}}
    .share-x{{background:#000}}
    .share-line{{background:#06c755}}
    .share-copy{{background:#64748b}}
    footer{{background:var(--navy);color:rgba(255,255,255,0.85);padding:40px 24px 28px;margin-top:24px}}
    .footer-inner{{max-width:1100px;margin:0 auto;text-align:center}}
    .footer-logo{{display:flex;align-items:center;justify-content:center;gap:10px;margin-bottom:12px;font-size:1.1rem;font-weight:700}}
    .footer-logo-icon{{width:36px;height:36px;border-radius:50%;background:linear-gradient(135deg,var(--sky),var(--sl));display:flex;align-items:center;justify-content:center;font-size:0.8rem;font-weight:700;color:#fff}}
    .footer-contact{{margin:10px 0}}
    .footer-contact a{{font-size:0.85rem;color:var(--sl);text-decoration:underline}}
    footer p{{font-size:0.78rem;opacity:.6;margin-top:16px}}
  </style>
</head>
<body>
<div id="pb"></div>

<header>
  <div class="header-inner">
    <a href="../index.html" class="logo">
      <div class="logo-text">
        <div class="name">Life Asset</div>
        <div class="tagline">あなたの未来に、確かな安心と成長を。</div>
      </div>
    </a>
    <nav>
      <a href="../index.html">ホーム</a>
      <a href="../index.html#services">サービス</a>
      <a href="index.html" class="active">ブログ</a>
    </nav>
    <a href="../index.html#contact" class="btn-cta">お問い合わせ</a>
  </div>
</header>

<div class="breadcrumb">
  <a href="../index.html">ホーム</a>
  <span>›</span>
  <a href="index.html">ブログ</a>
  <span>›</span>
  <span>{title}</span>
</div>

<div class="article-header">
  <div class="article-tag">{emoji} {category}</div>
  <h1 class="article-title">{title}</h1>
  <div class="article-meta">
    <span>📅 {DATE_JP}</span>
    <span>⏱ 約{reading_time}分で読めます</span>
    <span>🤖 自動投稿</span>
  </div>
</div>

{adsense_html}

<div class="toc">
  <div class="toc-box">
    <h2>📋 目次</h2>
    <ul class="toc-list">
{toc_html}
    </ul>
  </div>
</div>

<div class="article-content">
{body_html}
</div>

{affiliate_html}

<div class="share-section">
  <h2>この記事をシェアする</h2>
  <div class="share-btns">
    <a class="share-btn share-x" href="https://twitter.com/intent/tweet?text={title}&url={SITE_URL}/blog/{ARTICLE_FILENAME}" target="_blank" rel="noopener noreferrer">𝕏 Xでシェア</a>
    <a class="share-btn share-line" href="https://social-plugins.line.me/lineit/share?url={SITE_URL}/blog/{ARTICLE_FILENAME}" target="_blank" rel="noopener noreferrer">💬 LINEで送る</a>
    <button class="share-btn share-copy" onclick="copyLink()">🔗 リンクをコピー</button>
  </div>
</div>

<div style="background:linear-gradient(135deg,#fffbeb,#fef3c7);border-top:2px solid #fde68a;padding:40px 24px;text-align:center">
  <div style="max-width:640px;margin:0 auto">
    <p style="font-size:0.75rem;font-weight:700;color:#d97706;margin-bottom:8px">📓 NOTE 有料マガジン</p>
    <h2 style="font-size:1.3rem;font-weight:900;color:#92400e;margin-bottom:10px">ライフアセットFP通信</h2>
    <p style="font-size:0.88rem;color:#78350f;margin-bottom:20px;line-height:1.7">ブログでは語れない深掘り解説・家計診断シート・読者限定Q&amp;Aを月額980円でお届け</p>
    <a href="https://note.com/lifeasset_fp" target="_blank" rel="noopener noreferrer" style="display:inline-flex;align-items:center;gap:8px;background:#000;color:#fff;font-size:0.9rem;font-weight:700;padding:12px 28px;border-radius:8px;text-decoration:none">
      📓 noteマガジンを見る
    </a>
  </div>
</div>

<footer>
  <div class="footer-inner">
    <div class="footer-logo">
      <div class="footer-logo-icon"><span>LA</span></div>
      Life Asset
    </div>
    <div class="footer-contact">
      <a href="https://mail.google.com/mail/?view=cm&fs=1&to={CONTACT_EMAIL}" target="_blank" rel="noopener noreferrer">{CONTACT_EMAIL}</a>
      ｜<a href="../contact.html">お問い合わせ</a>
      ｜<a href="../privacy.html">プライバシーポリシー</a>
    </div>
    <p>© 2026 Life Asset Partners. 本記事はAIによる自動生成コンテンツです。</p>
  </div>
</footer>

<script>
  function copyLink() {{
    navigator.clipboard.writeText(location.href).then(function(){{ alert('リンクをコピーしました！'); }});
  }}
  window.addEventListener('scroll', function(){{
    const el = document.documentElement;
    const pct = (el.scrollTop / (el.scrollHeight - el.clientHeight)) * 100;
    document.getElementById('pb').style.width = pct + '%';
  }});
</script>
</body>
</html>"""


# ───────────────────────────────────────────
# blog/index.html を更新
# ───────────────────────────────────────────
def update_blog_index(meta: dict):
    if not os.path.exists(BLOG_INDEX_PATH):
        return

    title    = meta["title"]
    category = meta["category"]
    emoji    = meta["emoji"]
    style    = CATEGORY_STYLES.get(category, CATEGORY_STYLES["家計管理"])
    bg       = style["bg"]

    # 既存の記事数を取得してカウントアップ
    with open(BLOG_INDEX_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # 記事件数を更新
    count_match = re.search(r'id="articles-count">(\d+)件', content)
    if count_match:
        old_count = int(count_match.group(1))
        content = content.replace(
            f'id="articles-count">{old_count}件',
            f'id="articles-count">{old_count + 1}件'
        )

    # 今日の記事を更新
    today_pattern = r'<!-- TODAY\'S ARTICLE -->.*?</div>\s*</div>'
    today_new = f"""<!-- TODAY'S ARTICLE -->
<div class="today-section">
  <div class="today-label">🔥 本日の記事</div>
  <a href="{ARTICLE_FILENAME}" class="today-card">
    <div class="today-thumb">{emoji}</div>
    <div class="today-body">
      <span class="tag">{category}</span>
      <h2>{title}</h2>
      <p>{meta.get('description', '')}　</p>
      <span class="read-link">今日の記事を読む →</span>
    </div>
  </a>
</div>"""
    content = re.sub(today_pattern, today_new, content, flags=re.DOTALL)

    # 新しいカードを article-grid の先頭に挿入
    new_card = f"""
      <!-- 記事: {title} {DATE_STR} -->
      <article class="card" data-cat="{style['tag_class'].replace('tag-','')}" data-date="{DATE_STR}" data-pop="0" data-id="{DATE_STR}" data-title="{title}">
        <a href="{ARTICLE_FILENAME}">
          <div class="card-thumb {bg}">{emoji}<span class="card-new">🆕NEW</span></div>
        </a>
        <div class="card-body">
          <div class="card-meta"><span class="card-tag">{category}</span><span class="card-date">{DATE_STR}</span></div>
          <h3><a href="{ARTICLE_FILENAME}">{title}</a></h3>
          <a href="{ARTICLE_FILENAME}" class="card-link">続きを読む →</a>
        </div>
      </article>
"""

    insert_marker = '<div class="article-grid" id="article-grid">'
    content = content.replace(insert_marker, insert_marker + new_card, 1)

    with open(BLOG_INDEX_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"blog/index.html を更新しました（記事: {title}）")


# ───────────────────────────────────────────
# GitHub Actions 出力
# ───────────────────────────────────────────
def set_github_output(meta: dict):
    github_output = os.environ.get("GITHUB_OUTPUT", "")
    if not github_output:
        return
    with open(github_output, "a", encoding="utf-8") as f:
        f.write(f"title={meta['title']}\n")
        f.write(f"category={meta['category']}\n")
        f.write(f"filename={ARTICLE_FILENAME}\n")
        f.write(f"date={DATE_JP}\n")


# ───────────────────────────────────────────
# メイン
# ───────────────────────────────────────────
def main():
    print(f"[{DATE_JP} {TIME_STR}] 記事生成開始...")

    # シークレット確認
    api_key = os.environ.get("GEMINI_API_KEY", "")
    print(f"GEMINI_API_KEY: {'✅ 設定済み (' + str(len(api_key)) + '文字)' if api_key else '❌ 未設定'}")
    if not api_key:
        raise SystemExit("エラー: GEMINI_API_KEY が設定されていません。\n"
                         "GitHub リポジトリの Settings > Secrets > Actions に追加してください。\n"
                         "取得先: https://aistudio.google.com/app/apikey")

    # ニュース取得
    print("ニュースを取得中...")
    news = fetch_news()
    print(f"取得したニュース数: {len(news.splitlines())} 件")

    # 記事生成
    print("Gemini API で記事を生成中...")
    result = generate_article(news)
    meta   = result["meta"]
    body   = result["body"]

    print(f"タイトル: {meta['title']}")
    print(f"カテゴリ: {meta['category']}")
    print(f"文字数: {len(body)} 文字")

    # HTML 変換
    body_html, toc = md_to_html(body)

    # ファイル保存
    os.makedirs("blog", exist_ok=True)
    html = build_html(meta, body_html, toc)
    with open(ARTICLE_PATH, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"保存: {ARTICLE_PATH}")

    # blog/index.html 更新
    update_blog_index(meta)

    # GitHub Actions 出力（note生成の前に書いておく）
    set_github_output(meta)

    # note 記事生成（失敗してもブログ投稿は続行）
    print("note記事を生成中...")
    note_type = "有料" if IS_PAID_NOTE else "無料"
    print(f"note種別: {note_type}記事")
    try:
        note_content = generate_note_article(news, meta["title"], body)
        note_draft   = save_note_draft(note_content)
        print(f"note下書き保存: {NOTE_DRAFT_PATH}")

        # note情報もGITHUB_OUTPUTに追加
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write(f"note_type={note_type}\n")
                f.write(f"note_draft_path={NOTE_DRAFT_PATH}\n")

        # note本文をファイルに書き出し（メール用）
        with open("note_draft_for_email.txt", "w", encoding="utf-8") as f:
            f.write(note_draft)
    except Exception as e:
        print(f"⚠️ note記事生成をスキップしました: {e}")
        github_output = os.environ.get("GITHUB_OUTPUT", "")
        if github_output:
            with open(github_output, "a", encoding="utf-8") as f:
                f.write(f"note_type=（生成失敗）\n")

    print("✅ 完了")


if __name__ == "__main__":
    main()

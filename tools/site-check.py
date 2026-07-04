#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ライフアセットオフィス サイトヘルスチェック
使い方: python3 tools/site-check.py
リポジトリルートで実行すると、優先度つきの問題レポートを出力する。
"""
import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GA4_ID = "G-PKDH2DR522"

# 本文に書いてはいけない表現（ユーザー指示による規約）
FORBIDDEN_WORDS = ["中立", "売り込みなし", "登録無料", "登録不要", "非営利"]

# チェック対象外（テンプレート・部品など）
EXCLUDE_FILES = {"google3a26dd3b04d70cbf.html"}


def is_excluded(name):
    """Google Search Console 確認ファイル（google[token].html）等は検査対象外"""
    import re as _re
    return name in EXCLUDE_FILES or bool(_re.match(r"google[0-9a-f]+\.html$", name))

issues = {"高": [], "中": [], "低": []}


def add(sev, path, msg):
    issues[sev].append(f"{path}: {msg}")


def strip_noise(html):
    """base64画像・script/styleの中身を除去して本文だけ残す"""
    html = re.sub(r"data:image/[^;]+;base64,[A-Za-z0-9+/=]+", "", html)
    return html


def visible_text(html):
    """タグを外して表示テキストに近いものを得る（禁止ワード検査用）"""
    html = strip_noise(html)
    html = re.sub(r"<script[\s\S]*?</script>", "", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", "", html, flags=re.I)
    html = re.sub(r"<!--[\s\S]*?-->", "", html)
    return html


def collect_html_files():
    files = []
    for p in sorted(ROOT.glob("*.html")):
        if not is_excluded(p.name):
            files.append(p)
    for p in sorted(ROOT.glob("blog/*.html")):
        files.append(p)
    for p in sorted(ROOT.glob("blog/*/index.html")):
        files.append(p)
    return files


def rel(p):
    return str(p.relative_to(ROOT))


def check_head_elements(path, html):
    r = rel(path)
    head_end = html.find("</head>")
    head = html[:head_end] if head_end != -1 else html

    # noindex ページ（404・確認中の告知等）は canonical/OGP を求めない
    is_noindex = "noindex" in head
    if is_noindex:
        return

    if '<link rel="canonical"' not in head:
        add("中", r, "canonical が無い")
    # GA4 は cookie-consent.js が同意後に注入する設計。両方無い場合のみ計測ゼロ
    if GA4_ID not in html and "cookie-consent.js" not in html:
        add("高", r, "GA4 も cookie-consent.js も無い → アクセス計測されない")
    elif "cookie-consent.js" not in html:
        add("中", r, "cookie-consent.js が読み込まれていない（Cookie同意なしでGA4が動く状態）")
    if '<link rel="icon"' not in head:
        add("低", r, "favicon が無い")
    if 'property="og:title"' not in head:
        add("低", r, "OGP (og:title) が無い")


def check_forbidden_words(path, html):
    r = rel(path)
    text = visible_text(html)
    for w in FORBIDDEN_WORDS:
        if w in text:
            # 前後の文脈を1つだけ表示
            i = text.find(w)
            ctx = re.sub(r"\s+", " ", text[max(0, i - 20):i + 25]).strip()
            add("高", r, f"禁止ワード「{w}」が本文にある（…{ctx}…）")


def check_bare_nav_selector(path, html):
    r = rel(path)
    styles = re.findall(r"<style[\s\S]*?</style>", html, flags=re.I)
    for s in styles:
        if re.search(r"(?:^|[}\s;])nav\s*\{", s):
            add("中", r, "裸の nav{} セレクタ（.topnav{} にスコープすること・CLAUDE.md規約）")
            return


def check_relative_image_paths(path, html):
    r = rel(path)
    # ルート直下のページのみ対象（blog/ 配下は相対パスの意味が変わるため個別確認）
    if "/" in r:
        return
    m = re.findall(r'src="(images/[^"]+)"', strip_noise(html))
    if m:
        add("低", r, f"先頭スラッシュなし画像パス {len(m)}件（例: {m[0]}）→ /images/ に統一")


def check_internal_links(path, html):
    r = rel(path)
    # script内のJS文字列連結を誤検知しないよう、scriptを除去してから検査
    body = re.sub(r"<script[\s\S]*?</script>", "", strip_noise(html), flags=re.I)
    hrefs = re.findall(r'(?:href|src)="(/[^"#?]+|[^":/#?][^":#?]*)"', body)
    seen = set()
    for h in hrefs:
        if h.startswith(("http", "mailto:", "tel:", "javascript:", "data:", "//")):
            continue
        if h in seen:
            continue
        seen.add(h)
        # 絶対パス → ルート基準 / 相対パス → ファイルのディレクトリ基準
        if h.startswith("/"):
            target = ROOT / h.lstrip("/")
        else:
            target = path.parent / h
        # ディレクトリリンクは index.html を見る
        t = str(target)
        if t.endswith("/"):
            target = Path(t) / "index.html"
        if not target.exists() and not Path(str(target) + "index.html").exists():
            # ディレクトリとして存在するか
            if target.is_dir() and (target / "index.html").exists():
                continue
            add("高", r, f"壊れた内部リンク: {h}")


def check_sitemap():
    sm_path = ROOT / "sitemap.xml"
    if not sm_path.exists():
        add("高", "sitemap.xml", "ファイルが存在しない")
        return
    sm = sm_path.read_text(encoding="utf-8")
    locs = re.findall(r"<loc>https://lifeassetoffice\.net(/[^<]*)</loc>", sm)

    # sitemap → 実ファイル
    for loc in locs:
        if loc == "/":
            target = ROOT / "index.html"
        elif loc.endswith("/"):
            target = ROOT / loc.lstrip("/") / "index.html"
        else:
            target = ROOT / loc.lstrip("/")
        if not target.exists():
            add("高", "sitemap.xml", f"存在しないページを登録: {loc}")

    # 実ファイル → sitemap（ルート直下の公開HTMLのみ・noindexは除外）
    registered = set(locs)
    for p in sorted(ROOT.glob("*.html")):
        if is_excluded(p.name) or p.name == "404.html":
            continue
        try:
            head = p.read_text(encoding="utf-8")[:2000]
        except Exception:
            head = ""
        if "noindex" in head:
            continue  # 非公開・補助ページは sitemap 登録不要
        loc = "/" + p.name
        if loc not in registered and (loc != "/index.html" or "/" not in registered):
            if p.name == "index.html":
                continue
            add("中", "sitemap.xml", f"未登録の公開ページ: {loc}")


def main():
    files = collect_html_files()
    print(f"チェック対象: {len(files)} HTMLファイル\n")

    for p in files:
        try:
            html = p.read_text(encoding="utf-8")
        except Exception as e:
            add("高", rel(p), f"読み込み失敗: {e}")
            continue
        check_head_elements(p, html)
        check_forbidden_words(p, html)
        check_bare_nav_selector(p, html)
        check_relative_image_paths(p, html)
        check_internal_links(p, html)

    check_sitemap()

    total = sum(len(v) for v in issues.values())
    for sev in ["高", "中", "低"]:
        if issues[sev]:
            print(f"■ 深刻度: {sev}（{len(issues[sev])}件）")
            for i in issues[sev]:
                print(f"  - {i}")
            print()

    if total == 0:
        print("✅ 問題は見つかりませんでした。")
    else:
        print(f"合計 {total} 件の問題が見つかりました。")
    return 1 if issues["高"] else 0


if __name__ == "__main__":
    sys.exit(main())

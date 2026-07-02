# サイト管理ダッシュボード — ライフアセットオフィス

> このファイルはサイトの健康状態と改善バックログを一元管理する。
> チェックの実行: リポジトリルートで `python3 tools/site-check.py`
> 更新ルール: サイトに変更を加えたセッションでは必ずチェックを再実行し、このファイルを最新化する。

**最終チェック: 2026-07-02 ｜ 状態: 🟡 深刻度「高」0件・「中」67件・「低」14件**

---

## 🔴 深刻度：高（今すぐ対応）

なし（2026-07-02 全件解消済み）

---

## 🟡 深刻度：中（計画的に対応）

### 1. 裸の `nav{}` セレクタ — 約55ファイル
- CLAUDE.md 規約違反（`.topnav{}` にスコープすべき）。現状バグは顕在化していないが、目次 `<nav class="toc">` を導入した瞬間にスティッキー化バグが再現する時限爆弾。
- 対象: `blog/post-411〜557.html` のほぼ全て、`index.html`、`contact.html`、`privacy.html`、`lifeplan.html`、`loan-check.html`、`couples-sim.html`、`fire.html`、`nisa.html`、`fp-tools.html`、`404.html`、`app.html` など
- 対応方針: 一括置換スクリプトで `nav{` → `.topnav{`＋`<nav>` → `<nav class="topnav">`。1PRでまとめて実施可能（機械的変更）。

### 2. canonical 欠落 — 8ファイル
- `404.html`（※404は不要・除外してよい）、`app.html`、`fire.html`、`fp-tools.html`、`future-plans.html`、`loan.html`、`nisa.html`、`blog/asset-building-beginner/index.html`

### 3. sitemap.xml 未登録の公開ページ — 4件
- `/app.html`・`/fp-tools.html`・`/mypage.html`・`/tools.html`
- ※意図的な非公開（マイページ等）なら sitemap 登録せず `noindex` を付ける方が正しい。**ユーザーに公開意図を確認してから対応。**

---

## 🟢 深刻度：低（余裕があれば）

- favicon 欠落: `app.html`、`fire.html`、`fp-tools.html`、`nisa.html`、`blog/index.html`、`blog/asset-building-beginner/index.html`
- OGP (og:title) 欠落: `404.html`、`contact.html`、`couples-sim.html`、`future-plans.html`、`loan.html`、`mypage.html`、`privacy.html`、`blog/asset-building-beginner/index.html`

---

## 💡 改善アイデア（バグではないが効果が見込めるもの）

| 優先度 | 項目 | 理由 |
|--------|------|------|
| 高 | ブログ記事の定期追加（post-558以降） | SEO流入の柱。テンプレート規約に従うこと |
| 高 | 記事間の内部リンク強化（関連記事セクション） | 回遊率・SEO向上。現状ツールCTAのみの記事が多い |
| 中 | 画像の alt 属性充実・WebP統一 | SEO・表示速度 |
| 中 | `fire.html`・`nisa.html`・`loan.html` の位置づけ整理 | `*-sim.html` と重複気味。リダイレクトか統合を検討 |
| 低 | 404.html のデザイン改善（人気ページへの誘導） | 離脱防止 |

---

## 📋 効率化メモ（作業のしかた）

- **マージ後の同期を忘れない**: `git fetch origin gh-pages && git merge origin/gh-pages`（忘れると次のPRで必ずコンフリクト）
- **一括テキスト修正**: Python の `str.replace()` ループが安全（sed より事故が少ない）
- **base64埋め込み画像入りのHTML**: grep 結果が巨大化するので `data:image` を除去してから検査（site-check.py は対応済み）
- **新規ページ追加時の3点セット**: ①ページ本体 ②`blog/index.html` or `simulation.html` へのカード追加 ③`sitemap.xml` 登録

---

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-07-02 | 初版作成。深刻度「高」14件を全件修正（禁止ワード5件・GA4/cookie-consent 1件・チェッカー誤検知調整） |

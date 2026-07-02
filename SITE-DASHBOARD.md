# サイト管理ダッシュボード — ライフアセットオフィス

> このファイルはサイトの健康状態と改善バックログを一元管理する。
> チェックの実行: リポジトリルートで `python3 tools/site-check.py`
> 更新ルール: サイトに変更を加えたセッションでは必ずチェックを再実行し、このファイルを最新化する。

**最終チェック: 2026-07-02（シミュレーター監査後） ｜ 状態: 🟡 深刻度「高」0件・「中」67件・「低」14件**

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

## 🔧 シミュレーター監査（2026-07-02・計算ロジックの検算監査）

**修正済み（利用者が損する系の重大バグ3本）:**
- `furusato-sim.html`: 上限計算式の分母誤り＋2,000円加算欠落＋社会保険料控除欠落 → 総務省の正式式に全面修正（修正前は上限が13〜32%過大＝上限超過寄附で自己負担増の実害）。総務省目安表と±4%以内で一致を検算済み。内訳表示も限界税率ベースに修正。住宅ローン控除の一律20%減額（根拠なし）を廃止
- `tedori-sim.html`: 所得税の基礎控除が旧48万円のまま → 2025年改正の段階制（88万等）に修正。給与所得控除最低65万円に更新。扶養ラベルに「16歳未満は含めない」を明記
- `nisa-ideco-sim.html`: 公務員iDeCo限度額が旧1.2万円 → 月2.0万円（2024年12月改正）。節税額計算が「年収に税率表を直接適用」で約1.5倍過大 → 概算課税所得ベースに修正。URLパラメータの不正値対策
- `souzoku-sim.html`: 子がいない場合（親・兄弟相続）は計算対象外である旨を免責に明記

**残バックログ（監査所見・中〜低）:**
- nisa-ideco-sim: NISA生涯枠1,800万超の扱い／iDeCo受取時課税の未反映（比較が過大）／つみたて枠ゲージの1,200万表記
- furusato-sim: 住宅ローン控除入力UIの注記整備
- tedori-sim: 健保の標準報酬上限・調整控除の精緻化
- souzoku-sim: 親・兄弟相続パターンの実装（現在は免責で対応）
- **未実施の監査4グループ**（セッション上限で中断）: retirement-gap等5ツール／student-sim-app.js／lifeplan・couples-sim／診断・子ども・紹介ページ → 再実行予定

## 更新履歴

| 日付 | 内容 |
|------|------|
| 2026-07-02 | 初版作成。深刻度「高」14件を全件修正（禁止ワード5件・GA4/cookie-consent 1件・チェッカー誤検知調整） |
| 2026-07-02 | シミュレーター計算ロジック監査（4ツール完了）。furusato/tedori/nisa-ideco の重大バグ修正・souzoku免責追記 |

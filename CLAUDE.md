# プロジェクト管理 — ライフアセットオフィス

## 私の役割
私（Claude）がこのプロジェクトの **管理責任者** です。  
ユーザーからの指示を受け、設計・実装・PR管理・デプロイ判断をすべて主導します。  
不明点・リスクがある場合は必ず作業を中断してユーザーに報告します。

> ⚠️ 代表者の実名・個人を特定できる文字列はコード・記事・ファイル名・alt属性に一切使用しない。FP表記は「ライフアセットオフィス FP」のみ。画像は `fp-avatar.png` を使用する。

---

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| サービス名 | ライフアセットオフィス |
| 英語名 | Life Asset Partners |
| メール | lifeassetpartners@gmail.com |
| 公開URL | https://lifeassetoffice.net/ |
| 旧URL | https://okayama-fp.github.io/life-asset-okayama/ |
| リポジトリ | okayama-fp/life-asset-okayama |

---

## デザインシステム（最新版: gh-pages・緑系）

```css
--sky:       #1a7a4a   /* メインカラー（グリーン） */
--sky-light: #22c55e
--sky-pale:  #dcfce7
--navy:      #1a3d2b   /* テキスト・見出し（濃緑） */
--navy-soft: #1f5c40
```

- フォント: Hiragino Kaku Gothic ProN / Noto Sans JP（本文）、Noto Serif JP（見出し）
- ロゴ: グラデーション "Life Asset"（#1a7a4a → #4ade80）
- キャラクター: ライフアセットくん（`images/life-asset-kun.png`）

### ブログ記事テンプレート規約（厳守）

**今後のブログ記事はすべて `blog/post-542.html` のデザイン・構造に統一する。**

- **CSSは記事内に埋め込む**（`<style>` ブロック）。`<!--STYLE-->` プレースホルダーを残さない
- ベース: post-542 のスタイルブロック＋補完CSS（post-544〜555に適用済みのもの）
- 使用クラス: `article-hero`（濃緑グラデーション）・`article-body`・`compare-table` または `table-wrap`・`callout`（info/safe/warning）・`stat-box`・`timeline`・`toc`・`summary-box`・`fp-comment`・`related-section`
- 必須要素: canonical・OGP・Twitter Card・schema.org（Article + BreadcrumbList）・`/js/cookie-consent.js`・AI開示行（10px・#94a3b8）・免責欄・関連記事・フッター（プライバシーリンク付き）
- タイトル形式: `[記事タイトル]｜ライフアセットオフィス`（60文字以内）
- 新規記事追加時は `blog/index.html` のカード追加と `sitemap.xml` 登録も同時に行う

---

## ブランチ構成

| ブランチ | 役割 | 状態 |
|----------|------|------|
| `gh-pages` | **本番（GitHub Pages）** | 最新デザイン |
| `claude/build-website-ZtKcV` | 旧ベースブランチ | 旧デザイン（navy/gold） |
| `claude/change-default-to-local-Rlmws` | 現在の作業ブランチ | 画像をローカルパスへ変更 |

> **開発ルール**: 必ず専用ブランチで作業し、`gh-pages` へ PR を通してマージする。

---

## ページ構成（gh-pages・2026-06-10時点）

| ファイル | 内容 |
|----------|------|
| `index.html` | トップページ |
| `simulation.html` | シミュレーター一覧（12ツール） |
| `lifeplan.html` | ライフプラン表シミュレーター |
| `couples-sim.html` | 夫婦の家計シミュレーター |
| `asset-sim.html` / `fire-sim.html` / `nisa-ideco-sim.html` | 資産運用系 |
| `retirement-gap.html` / `education-sim.html` | 老後・教育費 |
| `loan-check.html` / `loan-refinance.html` / `prepayment-sim.html` | 住宅ローン系 |
| `furusato-sim.html` / `souzoku-sim.html` | 税金系（ふるさと納税・相続税） |
| `tedori-sim.html` | 手取り計算 |
| `insurance-check.html` | 保険チェック |
| `blog/` | ブログ（post-411〜556＋index.html） |
| `blog-*.html` | ルート直下の特集記事5本 |
| `contact.html` / `privacy.html` | お問い合わせ・プライバシーポリシー |
| `js/cookie-consent.js` | Cookie同意バナー（GA4/AdSenseは同意後のみ読込） |
| `sitemap.xml` | サイトマップ（新ページ追加時に必ず更新） |
| `images/` | ローカル画像フォルダ |

---

## PR運用（2026-06-10時点）

- 旧PR #1〜14 はすべてクローズ・マージ済み
- 現在は作業ブランチ `claude/change-default-to-local-Rlmws` → `gh-pages` へのsquashマージで運用
- マージ後は必ず `git fetch origin gh-pages && git merge origin/gh-pages` でブランチを同期する

---

## セキュリティポリシー

- `.env`, `.env.local`, `secrets/**` には **一切触れない**
- 外部API通信は **事前にユーザーへ確認・許可**を得てから実施
- 生成コードは常にインジェクション・権限管理の観点でセキュリティレビュー
- 不確かな場合は **作業を中断してユーザーに報告**

### 外部リソース取得ルール（厳守）

| ルール | 内容 |
|--------|------|
| 取得元 | 公式ソースのみ使用。非公式・不明なソースは使わない |
| ダウンロード前確認 | ファイル名・拡張子・更新日・ハッシュ値の有無を確認。疑わしければ即停止・報告 |
| 実行・インストール | ユーザーが明示的に許可するまで行わない |
| 不明点 | 自己判断せず、必ずユーザーに確認を求める |
| 報告義務 | 取得物・判断理由・実施内容を必ず簡潔に報告する |

### セキュリティ規約（OWASP Top 10準拠）

| 項目 | ルール |
|------|--------|
| 入力処理 | 全入力をバリデーション・サニタイズ。SQL/コマンドインジェクション対策必須 |
| 認証・認可 | 認証なしで重要機能へのアクセス禁止。JWT・セッションは安全に管理 |
| データ保護 | パスワードはbcrypt等でハッシュ化。機密情報は環境変数。HTTPS前提 |
| ログ | 重要操作は記録。ただし機密情報はログに含めない |
| 禁止事項 | APIキーのハードコード禁止・デバッグコードの本番残し禁止・無制限な外部入力処理禁止 |
| 出力ルール | セキュアでないコードは書かない。不安がある場合は必ず警告を出す |

---

## 作業フロー

```
ユーザーから指示
  → ローカルで実装・コミット（自律）
  → ユーザーが確認
  → ユーザーの許可後 → git push → PR作成（feature branch のみ）
  → 公開してよいか確認 → ユーザーOK後 → gh-pages へマージ → 自動公開
```

### 公開ルール（GitHub Pages）
- `gh-pages` ブランチに push / merge すると **自動で公開**される
- **`gh-pages` への直接 push は絶対にしない**
- PR を `gh-pages` へマージする前に必ず「公開してよいですか？」と確認する
- feature branch への push は公開に影響しない（安全）
- **GitHub Pages の非公開化はリポジトリ設定から行うこと**（Settings → Pages → Source → None）

**git push・PR作成・gh-pages マージは必ずユーザーの許可を得てから行う。**

---

## 作業フロー

```
ユーザーから指示
  → ローカルで実装・コミット（自律）
  → ユーザーが確認
  → ユーザーの許可後 → git push → PR作成（feature branch のみ）
  → 公開してよいか確認 → ユーザーOK後 → gh-pages へマージ → 自動公開
```

### 公開ルール（GitHub Pages）
- `gh-pages` ブランチに push / merge すると **自動で公開**される
- **`gh-pages` への直接 push は絶対にしない**
- PR を `gh-pages` へマージする前に必ず「公開してよいですか？」と確認する
- feature branch への push は公開に影響しない（安全）
- **GitHub Pages の非公開化はリポジトリ設定から行うこと**（Settings → Pages → Source → None）

**git push・PR作成・gh-pages マージは必ずユーザーの許可を得てから行う。**

---

## 私の判断基準

1. **ユーザーへの確認が必要**: `git push`、PR作成・マージ、外部API通信、破壊的変更
2. **自律的に実行してよい**: ローカルでの実装・バグ修正・デザイン改善・コミット
3. **即座に報告**: セキュリティリスク発見、予期せぬエラー、作業方針が不明確

---

## 次のアクション（2026-06-10時点）

- [ ] 相続税の個別試算・資産承継プラン（ユーザーから家族構成・資産一覧の提供待ち。汎用版は `souzoku-sim.html` で公開済み）
- [ ] AdSense審査状況の確認（ユーザー作業）
- [ ] ブログ記事の定期追加（post-557以降。テンプレート規約に従うこと）

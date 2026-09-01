# セキュリティ運用メモ — ライフアセットオフィス

最終監査日: **2026-09-01**（5系統の並列監査を実施）

---

## 1. 監査結果サマリー（2026-09-01）

**結論: サイト乗っ取り・マルウェア混入・情報漏洩の痕跡はいずれも検出されませんでした。**

| 監査系統 | 判定 | 主な確認内容 |
|---|---|---|
| マルウェア・不審スクリプト | ✅ クリーン | HTML100/JS5ファイル。`eval`/`atob`/`document.write`/iframe/難読化コードすべて0件 |
| Git履歴・改ざん痕跡 | ✅ クリーン | 全56コミットの作者は本人とClaudeの2名のみ。強制push・履歴改変の痕跡なし |
| 機密情報漏洩 | ✅ クリーン | APIキー・トークン・秘密鍵は履歴含め0件。個人メール・電話・住所も0件 |
| 外部リソース・リンク先 | ✅ クリーン | 外部ドメイン31個すべて正当。偽ドメイン（タイポスクワッティング）0件 |
| インフラ・設定ファイル | ✅ クリーン | CNAME改変なし。ads.txtへの第三者ID追記なし。GA4/AdSense IDの差し替えなし |

### 特に重要な確認項目（乗っ取りの直接経路）

- **CNAME**: `lifeassetoffice.net`。**初回コミット以降1度も変更されていない**（書き換えられるとドメインごと乗っ取られる最重要ファイル）
- **ads.txt**: 正規の1行のみ。第三者の広告事業者IDの追記なし（＝広告収益の横取りなし）
- **GA4測定ID**: `G-PKDH2DR522` の1種類のみ（101箇所すべて一致）。別プロパティへの計測横流しなし
- **AdSense発行者ID**: `ca-pub-1266918303152498` の1種類のみ。`ads.txt` の記載と一致
- **canonical**: 96件すべて自ドメイン。別ドメインへのSEO評価移転なし
- **共同編集者**: リポジトリ管理者1名（本人）のみ。第三者アカウントなし
- **Service Worker / manifest.json**: 存在しない → 最も危険な永続化経路が構造的に存在しない

### この監査でカバーできない範囲（要注意）

- このリポジトリは **shallow clone** のため、履歴検査は2026-06-26以降の56コミットに限られる
- **Cloudflare / DNS / ドメインレジストラ側の設定はリポジトリから検証不能**
- GitHubアカウント・Googleアカウントの2要素認証の有効性は検証不能

---

## 2. セキュリティヘッダーは「どこで」効いているのか（誤認防止）

**この項目は非常に間違えやすいため、変更する前に必ず読むこと。**

静的サイトのセキュリティヘッダーは、**HTTPレスポンスヘッダーでしか機能しません**。
HTML内の `<meta>` タグに書いても、以下のものは**ブラウザに完全に無視されます**。

| 書き方 | 効くか | 備考 |
|---|---|---|
| `<meta http-equiv="X-Frame-Options" ...>` | ❌ **効かない** | HTTPヘッダー専用。97ページに記載があるが**すべて無効** |
| `<meta http-equiv="X-Content-Type-Options" ...>` | ❌ **効かない** | 同上 |
| `<meta http-equiv="Referrer-Policy" ...>` | ❌ **効かない** | HTML仕様の許可リストに含まれない |
| `<meta name="referrer" content="...">` | ✅ **効く** | これが正しい形式（2026-09-01に全96ページへ整備済み） |
| `<meta http-equiv="Content-Security-Policy" ...>` | ✅ **効く** | ただし `frame-ancestors` は meta では無効（HTTPヘッダー専用） |
| `.htaccess` の `Header always set ...` | ❌ **効かない** | GitHub Pages はApache設定を一切処理しない |

### 結論: クリックジャッキング対策は Cloudflare 側のヘッダーに完全依存している

`X-Frame-Options` と `CSP: frame-ancestors` は、どちらもリポジトリ側からは設定できません。
したがって **Cloudflare の Transform Rules（Modify Response Header）が唯一の防御線**です。

**定期確認の方法（3か月に1回を推奨）:**

1. ブラウザで https://lifeassetoffice.net/ を開く
2. `F12`（開発者ツール）→ `Network` タブ → ページを再読み込み
3. 一番上のドキュメント（`lifeassetoffice.net`）をクリック → `Headers` → `Response Headers`
4. 以下が**実際に存在するか**を目視確認する:
   - `x-frame-options: DENY`（または `SAMEORIGIN`）
   - `x-content-type-options: nosniff`
   - `referrer-policy: strict-origin-when-cross-origin`
   - `strict-transport-security: max-age=31536000; includeSubDomains`
   - `permissions-policy: camera=(), microphone=(), geolocation=()`

**これらが無い場合、サイトはクリックジャッキングに対して無防備です。**
その場合は Cloudflare ダッシュボード → 対象ドメイン → **Rules → Transform Rules → Modify Response Header** で再設定してください（無料プランで10ルールまで利用可）。

---

## 3. 未対応の防御項目（優先度順）

### 🔴 高: `gh-pages` にブランチ保護が未設定

現在、本番ブランチ `gh-pages` は `protected: false` です。
CLAUDE.md の「gh-pages への直接 push 禁止」は**運用ルールのみで、技術的な強制がありません**。
またワークフロー `manual-blog-notify.yml` は `gh-pages` への push で起動し、X・Gemini・Gmail の全シークレットを持つため、
万一アカウントが侵害されると、スクリプト1行の書き換えとpushだけで全シークレットを外部送信できます。

**設定方法**: GitHub → リポジトリ → Settings → Branches → Add branch protection rule
→ Branch name pattern に `gh-pages` → 「Require a pull request before merging」にチェック

### 🟡 中: Google Apps Script エンドポイントが無認証で書き込み可能

`js/sim-tracker.js` がシミュレーター利用統計を Google Apps Script へ送信しています。
送信内容は匿名化済み（年代・年収レンジ等）でCookie同意後のみ発火するため**利用者への危害はありません**が、
URLが公開ソースに露出しているため、第三者が任意データをスプレッドシートへ書き込める状態です（データ汚染・クォータ消費のリスク）。

**対処案**: GAS側で Origin/Referer チェックとレート制限を実装する。または GA4 イベントで代替できるなら GAS ルートを廃止する。

### 🟡 中: `student-sim.html` の React を unpkg.com から読み込み

```html
<script src="https://unpkg.com/react@18/umd/react.production.min.js" crossorigin></script>
```
**サイト内で唯一「Google以外から実行コードを読み込む」箇所**です。
`@18` は浮動バージョン指定のため配信内容が随時変わり、SRI（改ざん検知ハッシュ）を付けられません。

**対処案**: `js/chart.umd.min.js` と同様に React を `/js/` へローカル配置する（方針が一貫する）。
または `react@18.3.1` のように完全固定＋`integrity=` 付与。

### 🟢 低: GitHub Actions のバージョン固定

- `actions/checkout@v4` / `actions/setup-python@v5` がタグ指定（コミットSHA未固定）
- `pip install google-genai beautifulsoup4 tweepy` がバージョン未固定

いずれもGitHub公式Action・主要パッケージのため実現可能性は低いものの、
侵害された場合は全シークレットが流出します。`requirements.txt` でのハッシュ固定を推奨します。

### 🟢 低: Dependabot / CODEOWNERS が未設定

- `.github/dependabot.yml` がないため、依存関係の脆弱性通知を受け取れない
- CODEOWNERS がないため、`CNAME` や `.github/workflows/` の改変時にレビューを強制できない

---

## 4. リポジトリ外（ユーザー側）で確認すべき項目

コードでは守れない領域です。**過去のサイト乗っ取りの大半はこの領域で起きます。**

| 項目 | 確認内容 |
|---|---|
| **ドメインの有効期限** | `lifeassetoffice.net` の自動更新が有効か。**期限切れは乗っ取りの最大要因** |
| **GitHubアカウントの2要素認証** | Settings → Password and authentication → Two-factor authentication |
| **Googleアカウントの2要素認証** | GA4・AdSense・Google Apps Script の管理権限を持つため重要 |
| **Cloudflareアカウントの2要素認証** | DNS を握られると、サイト全体を別サーバーへ向けられる |
| **各アカウントのパスワード使い回し** | 他サービスからの漏洩パスワードによる侵入が典型的な経路 |
| **Cloudflareのセキュリティヘッダー** | 上記「2.」の定期確認手順を参照 |

---

## 5. 変更履歴

| 日付 | 内容 |
|------|------|
| 2026-09-01 | 5系統の並列セキュリティ監査を実施。本ファイルを新規作成。あわせて以下を実施:<br>①ワークフローに `permissions: contents: read`（最小権限）を明示<br>②32ファイルに有効な `<meta name="referrer">` を追加（http-equiv版は無効なため）<br>③作業ブランチを gh-pages に同期し、個人名ファイル削除と強化版 .gitignore を取り込み |

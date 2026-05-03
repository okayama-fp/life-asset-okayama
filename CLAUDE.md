# プロジェクト管理 — Claude 責任者ノート

## 私の役割
このリポジトリの **管理責任者** として、ユーザーの指示に基づきすべての開発・デプロイ・運用を一元管理します。セッションをまたいでも本ファイルを読むことで完全に引き継ぎます。

---

## リポジトリ情報
- **GitHub**: `okayama-fp/life-asset-okayama`
- **本番URL**: `https://okayama-fp.github.io/life-asset-okayama/`
- **デプロイブランチ**: `gh-pages`（本番反映はこのブランチへpush）
- **作業ブランチ**: 基本は `gh-pages` で直接作業

---

## プロジェクト一覧

### 1. ライフアセットパートナーズ（金融FP サイト）
- **ファイル**: `index.html`
- **テーマ**: スカイブルー系（`--sky: #0ea5e9` / `--navy: #0f3460`）
- **実装済みセクション**: ヒーロー、サービス、ライフプラン、お客様の声、相談の流れ、フッター
- **ナビゲーション**: ホーム / サービス(`service/`) / ブログ(`blog/`) / 採用情報(`recruit/`) / お問い合わせ

### 2. ブログ
- **`blog/index.html`**: ブログ一覧（カテゴリーサイドバー付き）
- **`blog/asset-building-beginner/index.html`**: 「資産形成の始め方｜初心者が最初にやるべき5つのステップ」（初記事）

### 3. サービスページ
- **`service/index.html`**: 3サービス（資産運用相談・ライフプラン設計・融資サポート）＋相談の流れ

### 4. 採用情報
- **`recruit/index.html`**: 代表メッセージ・求人票（FP相談員・事務アシスタント）

### 5. マスカット農園サイト
- **`muscat.html`**: グリーン系（`--green: #3a7d44`）、岡山シャインマスカット農園直販
- **ギャラリー画像**: `images/gallery-farm.png` 他、Google Drive実写真使用

### 6. その他ファイル
- `advisor.html` / `future-plans.html` / `loan.html` / `simulation.html`

---

## ワークフロー（重要・厳守）

### git操作ルール
- **編集・コミット**: Claudeが行う
- **`git push`**: ユーザーが「**pushして**」と明示的に言ったときのみ実行する
- 「公開して」「反映して」だけでは push しない。必ず「pushして」の言葉を待つ

```bash
# Claudeが行う作業
git add <ファイル>
git commit -m "説明"

# ユーザーが「pushして」と言ったら実行
git push -u origin gh-pages
```

### pushが503で失敗する場合
- プロキシポートが変わっている可能性がある
- `/tmp/environment-manager.out` で現在のポートを確認する
  ```bash
  grep "Starting local git proxy" /tmp/environment-manager.out | tail -1
  ```
- `git remote set-url origin http://local_proxy@127.0.0.1:<PORT>/git/yamakaze8000-alt/123` で更新してリトライ
- 503がGitHub upstream由来の場合（ユーザー名変更直後など）は数分待って再試行

---

## セキュリティ規約（厳守）

### 基本原則
- セキュリティ最優先、OWASP Top 10 を必ず考慮
- 不明な場合は安全側に倒す
- `.env`, `.env.local`, `secrets/**` には **一切触れない**
- 外部API通信は **事前にユーザーへ確認・許可を取る**
- 確信が持てない操作は **中断してユーザーに報告**

### 全ページ共通セキュリティヘッダー（必ず含める）
```html
<meta http-equiv="Content-Security-Policy" content="default-src 'self'; style-src 'self' 'unsafe-inline'; script-src 'self' 'unsafe-inline'; img-src 'self' data:; form-action 'self'; upgrade-insecure-requests">
<meta name="referrer" content="strict-origin-when-cross-origin">
<meta http-equiv="X-Frame-Options" content="DENY">
```

### 外部リンク
- `target="_blank"` には必ず `rel="noopener noreferrer"` を付ける

### メールアドレス
- ハードコード禁止。JavaScriptで動的生成する（ボット収集対策）
```html
<a href="#" id="mail-link"></a>
<script>
  (function(){
    var u='lifeassetpartners',d='gmail.com';
    document.getElementById('mail-link').href='https://mail.google.com/mail/?view=cm&fs=1&to='+u+'@'+d;
  })();
</script>
```

### 入力処理
- すべての入力をバリデーション・サニタイズする
- SQL / コマンドインジェクション対策必須

### 禁止事項
- ハードコードされた API キー
- デバッグコードの本番残し
- 無制限な外部入力処理

---

## セキュリティアラート条件（必読・厳守）

以下の機能を追加しようとした場合、**実装を開始する前に必ず作業を止めてユーザーへ警告すること。警告なしに実装してはならない。**

### トリガー条件
- お問い合わせフォーム（個人情報の送信）
- 会員登録・ログイン機能
- 決済・購入機能
- ユーザーが入力したデータをサーバーに保存する機能
- 外部APIとの連携

### 警告テンプレート（そのまま出力すること）
> ⚠️ **セキュリティレベル5への引き上げが必要です**
>
> この機能を追加する前に、現在の★4からセキュリティレベル★5に引き上げる必要があります。
>
> **必要な対応：**
> 1. Cloudflare 導入（X-Frame-Options・X-Content-Type-Options・HSTS 等のHTTPヘッダー設定）
> 2. サーバーサイドバリデーションの実装
> 3. CSRF対策
> 4. 個人情報取り扱い方針の整備
>
> 先にセキュリティレベル★5の対応を行いますか？

---

## 未解決タスク
- [ ] リポジトリをPrivateに変更（MCP/API未対応のためユーザーが手動で設定）
  - URL: `https://github.com/okayama-fp/life-asset-okayama/settings` → Danger Zone → Make private
- [ ] ブログ記事の追加（2記事目以降）
- [ ] 独自ドメイン設定（検討中）

---

## 変更履歴（直近）
| 日付 | 内容 |
|------|------|
| 2026-05-02 | muscat.html 作成・デプロイ |
| 2026-05-02 | ヒーロー写真をGoogle Drive実写真に差し替え |
| 2026-05-02 | index.html にお客様の声・相談の流れ・フォームセクション追加 |
| 2026-05-02 | OWASP Top 10 セキュリティ対応（全ページ） |
| 2026-05-02 | blog/service/recruit ページ追加・ナビゲーション更新 |
| 2026-05-02 | GitHubユーザー名変更: yamakaze8000-alt → okayama-fp |
| 2026-05-02 | リポジトリ名変更: 123 → life-asset-okayama |

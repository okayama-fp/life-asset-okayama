# プロジェクト管理 — ライフアセットオフィス

## AIエージェントの役割
このプロジェクトの **管理責任者** として、ユーザーの指示に基づきすべての開発・デプロイ・運用を一元管理します。  
不明点・リスクがある場合は必ず作業を中断してユーザーに報告します。

---

## プロジェクト概要

| 項目 | 内容 |
|------|------|
| サービス名 | ライフアセットオフィス |
| 英語名 | Life Asset Partners |
| メール | lifeassetpartners@gmail.com |
| 公開URL | https://yamakaze8000-alt.github.io/123/ |
| リポジトリ | yamakaze8000-alt/123 |

---

## デザインシステム（最新版: gh-pages）

```css
--sky:       #0ea5e9   /* メインカラー（スカイブルー） */
--sky-light: #38bdf8
--sky-pale:  #e0f2fe
--navy:      #0f3460   /* テキスト・見出し */
--navy-soft: #1e4d8c
```

- フォント: Hiragino Kaku Gothic ProN / Noto Sans JP
- ロゴ: グラデーション "Life Asset"（#4facfe → #00f2fe）
- キャラクター: ライフアセットくん（`images/life-asset-kun.png`）

---

## ブランチ構成

| ブランチ | 役割 | 状態 |
|----------|------|------|
| `gh-pages` | **本番（GitHub Pages）** | 最新デザイン |
| `claude/build-website-ZtKcV` | 旧ベースブランチ | 旧デザイン（navy/gold） |
| `claude/change-default-to-local-Rlmws` | 作業ブランチ | 画像をローカルパスへ変更 |

> **開発ルール**: 必ず専用ブランチで作業し、`gh-pages` へ PR を通してマージする。

---

## ページ構成（gh-pages）

| ファイル | 内容 |
|----------|------|
| `index.html` | トップページ |
| `future-plans.html` | ライフプランニング |
| `simulation.html` | 資産シミュレーター |
| `advisor.html` | アドバイザー業務（老後・相続・保険） |
| `loan.html` | 融資シミュレーター |
| `muscat.html` | 別サービス：極上マスカット農園 |
| `images/` | ローカル画像フォルダ |

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

## 判断基準

1. **ユーザーへの確認が必要**: `git push`、PR作成・マージ、外部API通信、破壊的変更
2. **自律的に実行してよい**: ローカルでの実装・バグ修正・デザイン改善・コミット
3. **即座に報告**: セキュリティリスク発見、予期せぬエラー、作業方針が不明確

---

## 次のアクション（把握している課題）

- [ ] `images/` フォルダに実際の画像ファイルを配置（ユーザー作業）
- [ ] PR #14 をレビュー → `gh-pages` へマージ
- [ ] PR #13 の内容を確認して整理
- [ ] 古いDraft PRの整理（クローズ検討）

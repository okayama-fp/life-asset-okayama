# AI Music Auto Pipeline

## セットアップ

```bash
cd auto-pipeline
npm install
npx playwright install chromium
```

## .envを作成

```
cp .env.example .env
```

`.env`を開いて以下を入力：
- `DISTRO_EMAIL` — DistroKidのメールアドレス
- `DISTRO_PASSWORD` — DistroKidのパスワード
- `OPENAI_API_KEY` — OpenAI APIキー

## 音声・画像ファイルを配置

```
input/
├── song.wav   （または .mp3）
└── cover.jpg  （または .png）
```

## 実行

```bash
npm start
```

## 動作

1. OpenAI でタイトル・説明・タグを自動生成
2. Playwright でブラウザを起動してDistroKidにログイン
3. フォームに自動入力・ファイルをアップロード
4. ブラウザを開いたまま停止 → **最終確認は手動で送信**
5. `uploaded/` フォルダにファイルを移動

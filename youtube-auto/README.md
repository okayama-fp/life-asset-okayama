# 金持ちの習慣 — YouTube 動画自動生成ツール

Claude API × VOICEVOX × DALL-E 3 × MoviePy で  
「金持ちの習慣」YouTube 動画を全自動生成します。

## 機能

| ステップ | 使用技術 | 内容 |
|----------|----------|------|
| 台本生成 | Claude API (claude-sonnet-4-6) | テーマから台本・テロップ・画像プロンプトを自動生成 |
| 音声生成 | VOICEVOX（ローカル） | 無料・高品質な日本語 TTS |
| 画像生成 | DALL-E 3 (OpenAI API) | 各シーンの背景画像を自動生成 |
| 動画合成 | MoviePy + FFmpeg | 画像＋音声＋テロップを 1080p MP4 に合成 |

## セットアップ

### 1. 依存パッケージのインストール

```bash
cd youtube-auto
pip install -r requirements.txt
```

FFmpeg も必要です:
```bash
# Ubuntu/Debian
sudo apt install ffmpeg

# macOS
brew install ffmpeg
```

### 2. VOICEVOX の起動

**方法 A: VOICEVOX アプリ**  
[公式サイト](https://voicevox.hiroshiba.jp/) からダウンロードして起動。

**方法 B: Docker（推奨）**
```bash
docker run -d -p 50021:50021 voicevox/voicevox_engine:latest
```

### 3. 環境変数の設定

```bash
cp .env.example .env
# .env を編集して API キーを設定
```

必須:
- `OPENAI_API_KEY` — OpenAI API キー（DALL-E 3 使用）
- `ANTHROPIC_API_KEY` — Anthropic API キー（台本生成使用）

### 4. 動画生成の実行

```bash
# デフォルトテーマで生成
python main.py

# テーマを指定
python main.py --topic "億万長者の朝活ルーティン"

# 画像生成のみスキップ（テスト時）
python main.py --skip-images

# 音声生成のみスキップ
python main.py --skip-voice
```

## 出力ファイル

```
output/
└── {動画タイトル}/
    ├── output.mp4        ← YouTube にアップロードする動画
    ├── thumbnail.png     ← サムネイル画像
    ├── script.json       ← 生成された台本
    ├── scene_01.wav      ← 各シーンの音声
    ├── scene_01.png      ← 各シーンの画像
    └── ...
```

## YouTube アップロード手順

1. [YouTube Studio](https://studio.youtube.com/) にアクセス
2. 「作成」→「動画をアップロード」
3. `output.mp4` を選択
4. `thumbnail.png` をサムネイルに設定
5. `script.json` の `title` と `description` をコピペ
6. 公開設定を選択して完了

## カスタマイズ

| ファイル | 変更できること |
|----------|--------------|
| `generate_script.py` | 台本のトーン・構成・シーン数 |
| `generate_voice.py` | 話者ID・読み上げ速度 |
| `generate_images.py` | 画像スタイル・サイズ |
| `create_video.py` | テロップフォント・位置・動画解像度 |
| `.env` | API キー・出力フォルダ・話者 |

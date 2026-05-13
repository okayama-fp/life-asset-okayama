#!/bin/bash
# ============================================================
# Life Asset BGMリリース 自動化スクリプト
# ============================================================
# 使い方:
#   1. SUNOで音楽を生成してダウンロード（例: morning_breeze.mp3）
#   2. 以下の変数を編集して実行
#   chmod +x run_all.sh && ./run_all.sh
# ============================================================

# ===== 設定 =====
OPENAI_API_KEY="sk-ここにOpenAI APIキーを入力"
DISTROKID_EMAIL="ここにDistroKidのメールアドレスを入力"
DISTROKID_PASSWORD="ここにDistroKidのパスワードを入力"

TITLE="Morning Breeze"
ARTIST="Life Asset"
GENRE="Pop"
AUDIO_FILE="morning_breeze.mp3"   # SUNOからダウンロードした音楽ファイル
COVER_FILE="cover.jpg"             # 生成されるジャケット画像

# ===== 依存パッケージのインストール =====
echo "📦 依存パッケージをインストール中..."
pip install openai pillow requests playwright -q
playwright install chromium -q

# ===== Step 1: ジャケット画像生成 =====
echo ""
echo "🎨 Step 1: ジャケット画像を生成中..."
export OPENAI_API_KEY="${OPENAI_API_KEY}"
python generate_cover.py \
  --title "${TITLE}" \
  --artist "${ARTIST}" \
  --output "${COVER_FILE}"

if [ ! -f "${COVER_FILE}" ]; then
  echo "❌ ジャケット画像の生成に失敗しました"
  exit 1
fi
echo "✅ ジャケット画像生成完了: ${COVER_FILE}"

# ===== Step 2: 音楽ファイル確認 =====
echo ""
echo "🎵 Step 2: 音楽ファイル確認..."
if [ ! -f "${AUDIO_FILE}" ]; then
  echo "❌ 音楽ファイルが見つかりません: ${AUDIO_FILE}"
  echo ""
  echo "【SUNOでの生成手順】"
  echo "  1. https://suno.com にアクセス"
  echo "  2. 以下のプロンプトで生成:"
  echo "     'uplifting acoustic pop, morning vibes, cheerful, gentle guitar,"
  echo "      bright piano, no vocals, fresh and airy atmosphere'"
  echo "  3. 生成後「Download」→ MP3/WAV でダウンロード"
  echo "  4. このフォルダに ${AUDIO_FILE} として保存"
  echo ""
  exit 1
fi
echo "✅ 音楽ファイル確認完了: ${AUDIO_FILE}"

# ===== Step 3: DistroKid アップロード =====
echo ""
echo "🚀 Step 3: DistroKid にアップロード中..."
python upload_distrokid.py \
  --email "${DISTROKID_EMAIL}" \
  --password "${DISTROKID_PASSWORD}" \
  --audio "${AUDIO_FILE}" \
  --cover "${COVER_FILE}" \
  --title "${TITLE}" \
  --artist "${ARTIST}" \
  --genre "${GENRE}"

echo ""
echo "🎉 完了！"

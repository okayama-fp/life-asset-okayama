import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
VOICEVOX_URL = os.getenv("VOICEVOX_URL", "http://localhost:50021")
VOICEVOX_SPEAKER = int(os.getenv("VOICEVOX_SPEAKER", "1"))
OUTPUT_DIR = os.getenv("OUTPUT_DIR", "output")
VIDEO_TITLE_PREFIX = os.getenv("VIDEO_TITLE_PREFIX", "【金持ちの習慣】")

VIDEO_WIDTH = 1920
VIDEO_HEIGHT = 1080
FPS = 30

# 各シーンの表示秒数（音声終了後に +1秒 のバッファを加算）
SCENE_BUFFER_SEC = 1.0

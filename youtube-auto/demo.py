"""
APIキー不要のデモ版 — 金持ちの習慣 YouTube動画生成

必要なもの:
  pip install gtts moviepy Pillow numpy

使い方:
  python demo.py
"""
import os
import sys
import subprocess
from pathlib import Path


# ── 台本（ハードコード済み） ────────────────────────────────────
SCRIPT = {
    "title": "金持ちの習慣 トップ7",
    "description": "富裕層が実践する7つの習慣を解説。今日から取り入れられる実践的なヒントをご紹介します。",
    "scenes": [
        {
            "narration": "今日は、お金持ちが毎日実践している7つの習慣をご紹介します。これを知るだけで、あなたの人生は大きく変わるかもしれません。",
            "caption": "金持ちの習慣 トップ7",
            "image_prompt": "luxury penthouse living room golden sunrise cityscape cinematic 4K",
            "color": "#0f3460",
            "accent": "#0ea5e9",
        },
        {
            "narration": "習慣その1。早起きです。富裕層の90パーセントは、朝5時から6時の間に起床します。静かな朝の時間を使って、思考を整え、一日の計画を立てます。",
            "caption": "習慣1: 早起き（朝5〜6時）",
            "image_prompt": "successful businessman waking up early sunrise window golden light modern bedroom cinematic",
            "color": "#0a2240", "accent": "#38bdf8",
        },
        {
            "narration": "習慣その2。毎日読書をすること。お金持ちは平均して月に4冊以上の本を読みます。ビジネス書・自己啓発・歴史書など、知識への投資を欠かしません。",
            "caption": "習慣2: 毎日読書（月4冊以上）",
            "image_prompt": "wealthy person reading books luxury home library wood shelves warm light cinematic 4K",
            "color": "#1a1a2e", "accent": "#f59e0b",
        },
        {
            "narration": "習慣その3。運動を継続することです。富裕層の76パーセントが毎日30分以上の有酸素運動をしています。体を動かすことで、頭も冴え、集中力が上がります。",
            "caption": "習慣3: 毎日30分以上の運動",
            "image_prompt": "fit businessman running morning park sunrise motivation healthy lifestyle cinematic",
            "color": "#0f3460", "accent": "#10b981",
        },
        {
            "narration": "習慣その4。複数の収入源を持つこと。お金持ちは平均7つの収入源を持っています。給料だけに頼らず、投資・副業・不動産など多角化します。",
            "caption": "習慣4: 収入源を複数持つ",
            "image_prompt": "stock market investment portfolio gold coins real estate multiple income streams cinematic 4K",
            "color": "#1a1a2e", "accent": "#f59e0b",
        },
        {
            "narration": "習慣その5。お金の記録をつけることです。支出を管理し、毎月の収支を把握することで、無駄遣いをなくし、投資に回せるお金を増やします。",
            "caption": "習慣5: 毎月の収支を記録する",
            "image_prompt": "businessman reviewing financial charts laptop modern office wealth management cinematic",
            "color": "#0a2240", "accent": "#0ea5e9",
        },
        {
            "narration": "習慣その6。優れた人脈を築くこと。成功者の周りには成功者が集まります。メンターを持ち、自分より優秀な人と積極的に交流しましょう。",
            "caption": "習慣6: 良い人脈への投資",
            "image_prompt": "successful business people networking luxury event handshake professional cinematic 4K",
            "color": "#0f3460", "accent": "#a855f7",
        },
        {
            "narration": "習慣その7。感謝の気持ちを持つことです。毎朝・毎晩、感謝できることを3つ書き出す習慣が、ポジティブな思考を育て、チャンスを引き寄せます。",
            "caption": "習慣7: 毎日3つの感謝を書く",
            "image_prompt": "person writing gratitude journal peaceful morning sunlight notebook zen mindfulness cinematic",
            "color": "#1a1a2e", "accent": "#f59e0b",
        },
        {
            "narration": "以上が、金持ちの7つの習慣でした。どれか一つでも今日から始めてみてください。チャンネル登録と高評価もよろしくお願いします！",
            "caption": "チャンネル登録をお願いします！",
            "image_prompt": "luxury success wealth achievement gold trophy celebration motivation cinematic 4K",
            "color": "#0f3460", "accent": "#0ea5e9",
        },
    ],
}

WORK_DIR = Path("output/demo")
VIDEO_W, VIDEO_H = 1280, 720


def check_and_install():
    """必要なパッケージを確認してインストールする。"""
    packages = {
        "moviepy": "moviepy",
        "PIL": "Pillow",
        "numpy": "numpy",
        "openai": "openai",
        "httpx": "httpx",
        "dotenv": "python-dotenv",
        "pyttsx3": "pyttsx3",
    }
    missing = []
    for module, pkg in packages.items():
        try:
            __import__(module)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"▶ 必要なパッケージをインストール中: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing, stdout=subprocess.DEVNULL)
        print("✓ インストール完了")


def _tts_openai(text: str, output_path: str):
    """OpenAI TTS（高品質）で音声を生成する。OPENAI_API_KEY が必要。"""
    import requests
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    api_key = api_key.encode("ascii", errors="ignore").decode("ascii")
    resp = requests.post(
        "https://api.openai.com/v1/audio/speech",
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        json={"model": "tts-1", "voice": "nova", "input": text, "response_format": "wav"},
        timeout=60,
    )
    resp.raise_for_status()
    with open(output_path, "wb") as f:
        f.write(resp.content)


def _tts_espeak(text: str, output_path: str):
    """Windows: pyttsx3（SAPI）/ Linux: espeak-ng でオフライン音声生成。"""
    import platform
    if platform.system() == "Windows":
        import pyttsx3
        engine = pyttsx3.init()
        # 日本語音声を探して設定
        for voice in engine.getProperty("voices"):
            name = (voice.name or "").lower()
            vid = (voice.id or "").lower()
            if any(k in name or k in vid for k in ["japanese", "haruka", "ja-jp", "keita"]):
                engine.setProperty("voice", voice.id)
                break
        engine.setProperty("rate", 150)
        engine.save_to_file(text, output_path)
        engine.runAndWait()
    else:
        wav_path = output_path if output_path.endswith(".wav") else output_path + ".wav"
        result = subprocess.run(
            ["espeak-ng", "-v", "jpx/ja", "-s", "140", "-p", "55", "-w", wav_path, text],
            capture_output=True,
        )
        if result.returncode != 0:
            raise RuntimeError(f"espeak-ng failed: {result.stderr.decode()}")
        if output_path != wav_path:
            os.rename(wav_path, output_path)


def _tts_voicevox(text: str, output_path: str, speaker: int = 1):
    """VOICEVOX（無料・高品質日本語）で音声生成。事前にVOICEVOXを起動しておくこと。"""
    import urllib.request, json, urllib.parse
    base = "http://localhost:50021"
    # クエリ生成
    params = urllib.parse.urlencode({"text": text, "speaker": speaker})
    req = urllib.request.Request(f"{base}/audio_query?{params}", method="POST")
    with urllib.request.urlopen(req, timeout=10) as r:
        query = r.read()
    # 音声合成
    req2 = urllib.request.Request(
        f"{base}/synthesis?speaker={speaker}",
        data=query,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req2, timeout=30) as r:
        wav = r.read()
    with open(output_path, "wb") as f:
        f.write(wav)


def _voicevox_running() -> bool:
    import urllib.request
    try:
        urllib.request.urlopen("http://localhost:50021/version", timeout=2)
        return True
    except Exception:
        return False


def generate_voice(text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    # 優先順位: VOICEVOX → OpenAI TTS → pyttsx3
    if _voicevox_running():
        _tts_voicevox(text, output_path)
        return
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    api_key = api_key.encode("ascii", errors="ignore").decode("ascii")
    if api_key and not api_key.startswith("sk-ここ"):
        _tts_openai(text, output_path)
    else:
        _tts_espeak(text, output_path)


def generate_image(scene: dict, scene_num: int, output_path: str):
    """Pollinations.ai（無料・APIキー不要）でAI画像を生成し、テロップを重ねる。"""
    import urllib.request, urllib.parse
    from PIL import Image, ImageDraw, ImageFont
    import io

    # ── 写真取得（Unsplash Source → フォールバック） ────────
    prompt = scene.get("image_prompt", scene["caption"])
    # キーワードを英単語のみ抽出してUnsplashクエリに使用
    keywords = ",".join(w for w in prompt.split() if w.isascii())[:60]
    url = f"https://source.unsplash.com/{VIDEO_W}x{VIDEO_H}/?{urllib.parse.quote(keywords)}&sig={scene_num}"
    ai_ok = False
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=20) as r:
            img_data = r.read()
        img = Image.open(io.BytesIO(img_data)).convert("RGB").resize((VIDEO_W, VIDEO_H), Image.LANCZOS)
        ai_ok = True
    except Exception:
        # AI生成失敗時はカラーカードにフォールバック
        accent_hex = scene.get("accent", "#0ea5e9")
        accent = tuple(int(accent_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
        img = Image.new("RGB", (VIDEO_W, VIDEO_H), scene.get("color", "#0f3460"))
        draw_bg = ImageDraw.Draw(img)
        for i in range(8):
            draw_bg.line([(0, VIDEO_H - 80 + i * 2), (VIDEO_W, VIDEO_H - 80 + i * 2)],
                         fill=accent + (int(255 * (1 - i / 8)),), width=2)

    # ── テロップを重ねる ────────────────────────────────────
    draw = ImageDraw.Draw(img)
    caption = scene["caption"]
    font_size = 52
    try:
        font = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", font_size)
        font_small = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 28)
    except OSError:
        try:
            font = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", font_size)
            font_small = ImageFont.truetype("C:/Windows/Fonts/msgothic.ttc", 28)
        except OSError:
            font = font_small = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), caption, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = (VIDEO_W - tw) // 2
    y = VIDEO_H - th - 50
    pad = 18

    # 半透明背景
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    odraw = ImageDraw.Draw(overlay)
    odraw.rectangle([x - pad, y - pad, x + tw + pad, y + th + pad], fill=(0, 0, 0, 170))
    img = Image.alpha_composite(img.convert("RGBA"), overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # テキスト（影＋本文）
    draw.text((x + 2, y + 2), caption, font=font, fill=(0, 0, 0))
    draw.text((x, y), caption, font=font, fill=(255, 255, 255))

    # ロゴ
    logo = "Life Asset Partners"
    lbbox = draw.textbbox((0, 0), logo, font=font_small)
    draw.text((VIDEO_W - (lbbox[2] - lbbox[0]) - 20, VIDEO_H - (lbbox[3] - lbbox[1]) - 20),
              logo, font=font_small, fill=(200, 200, 200))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)
    status = "AI画像" if ai_ok else "カラーカード（フォールバック）"
    print(f"    → {status}")

    # グラデーション風の装飾ライン
    accent = tuple(int(scene["accent"].lstrip("#")[i:i+2], 16) for i in (0, 2, 4))
    for i in range(8):
        draw.line([(0, VIDEO_H - 80 + i * 2), (VIDEO_W, VIDEO_H - 80 + i * 2)],
                  fill=accent + (int(255 * (1 - i / 8)),), width=2)

    # シーン番号の丸バッジ
    if scene_num > 0:
        r = 45
        cx, cy = 100, 100
        draw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent)

    # テキスト描画
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 52)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 32)
        font_num = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 40)
    except OSError:
        font_large = font_small = font_num = ImageFont.load_default()

    # キャプション（中央）
    caption = scene["caption"]
    bbox = draw.textbbox((0, 0), caption, font=font_large)
    tw = bbox[2] - bbox[0]
    draw.text(((VIDEO_W - tw) // 2 + 2, VIDEO_H // 2 - 26 + 2), caption, font=font_large, fill=(0, 0, 0))
    draw.text(((VIDEO_W - tw) // 2, VIDEO_H // 2 - 26), caption, font=font_large, fill=(255, 255, 255))

    # ロゴ（右下）
    logo = "Life Asset Partners"
    bbox2 = draw.textbbox((0, 0), logo, font=font_small)
    lw = bbox2[2] - bbox2[0]
    draw.text((VIDEO_W - lw - 30, VIDEO_H - 55), logo, font=font_small, fill=accent)

    # シーン番号（左上バッジ内）
    if scene_num > 0:
        num_text = str(scene_num)
        bbox3 = draw.textbbox((0, 0), num_text, font=font_num)
        nw = bbox3[2] - bbox3[0]
        nh = bbox3[3] - bbox3[1]
        draw.text((100 - nw // 2, 100 - nh // 2), num_text, font=font_num, fill=(255, 255, 255))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)


def create_video(scenes_data: list, output_path: str):
    from moviepy import ImageClip, AudioFileClip, concatenate_videoclips
    import numpy as np

    clips = []
    for s in scenes_data:
        audio = AudioFileClip(s["audio"])
        duration = audio.duration + 0.8
        clip = ImageClip(s["image"], duration=duration).with_fps(24).with_audio(audio)
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final.write_videofile(
        output_path,
        fps=24,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile=str(WORK_DIR / "temp_audio.m4a"),
        remove_temp=True,
        threads=4,
        preset="fast",
        logger=None,
    )


def main():
    print("=" * 55)
    print("  金持ちの習慣 YouTube動画 自動生成（デモ版）")
    print("=" * 55)

    check_and_install()
    WORK_DIR.mkdir(parents=True, exist_ok=True)

    scenes_data = []
    total = len(SCRIPT["scenes"])

    # ── 音声生成 ───────────────────────────────────────
    print(f"\n▶ 音声を生成中... (gTTS / 無料)")
    for i, scene in enumerate(SCRIPT["scenes"], 1):
        audio_path = str(WORK_DIR / f"scene_{i:02d}.wav")
        print(f"  [{i}/{total}] {scene['caption']}")
        generate_voice(scene["narration"], audio_path)
    print("✓ 音声生成完了")

    # ── 画像生成 ───────────────────────────────────────
    print(f"\n▶ 画像を生成中... (Pillow / APIキー不要)")
    for i, scene in enumerate(SCRIPT["scenes"], 1):
        image_path = str(WORK_DIR / f"scene_{i:02d}.png")
        print(f"  [{i}/{total}] {scene['caption']}")
        generate_image(scene, i - 1, image_path)
        scenes_data.append({
            "audio": str(WORK_DIR / f"scene_{i:02d}.wav"),
            "image": image_path,
        })
    print("✓ 画像生成完了")

    # ── 動画合成 ───────────────────────────────────────
    print(f"\n▶ 動画を合成中... (MoviePy)")
    output_video = str(WORK_DIR / "output.mp4")
    create_video(scenes_data, output_video)

    # ── 完了 ───────────────────────────────────────────
    size_mb = os.path.getsize(output_video) / 1024 / 1024
    print("\n" + "=" * 55)
    print("✅ 動画生成完了！")
    print(f"  ファイル : {output_video}  ({size_mb:.1f} MB)")
    print(f"  タイトル : {SCRIPT['title']}")
    print(f"  概要欄  : {SCRIPT['description']}")
    print()
    print("📺 YouTube Studio にアクセスしてアップロードしてください。")
    print("   https://studio.youtube.com/")
    print("=" * 55)


if __name__ == "__main__":
    main()

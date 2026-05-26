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
            "color": "#0f3460",
            "accent": "#0ea5e9",
        },
        {
            "narration": "習慣その1。早起きです。富裕層の90パーセントは、朝5時から6時の間に起床します。静かな朝の時間を使って、思考を整え、一日の計画を立てます。",
            "caption": "習慣1: 早起き（朝5〜6時）",
            "color": "#0a2240",
            "accent": "#38bdf8",
        },
        {
            "narration": "習慣その2。毎日読書をすること。お金持ちは平均して月に4冊以上の本を読みます。ビジネス書・自己啓発・歴史書など、知識への投資を欠かしません。",
            "caption": "習慣2: 毎日読書（月4冊以上）",
            "color": "#1a1a2e",
            "accent": "#f59e0b",
        },
        {
            "narration": "習慣その3。運動を継続することです。富裕層の76パーセントが毎日30分以上の有酸素運動をしています。体を動かすことで、頭も冴え、集中力が上がります。",
            "caption": "習慣3: 毎日30分以上の運動",
            "color": "#0f3460",
            "accent": "#10b981",
        },
        {
            "narration": "習慣その4。複数の収入源を持つこと。お金持ちは平均7つの収入源を持っています。給料だけに頼らず、投資・副業・不動産など多角化します。",
            "caption": "習慣4: 収入源を複数持つ",
            "color": "#1a1a2e",
            "accent": "#f59e0b",
        },
        {
            "narration": "習慣その5。お金の記録をつけることです。支出を管理し、毎月の収支を把握することで、無駄遣いをなくし、投資に回せるお金を増やします。",
            "caption": "習慣5: 毎月の収支を記録する",
            "color": "#0a2240",
            "accent": "#0ea5e9",
        },
        {
            "narration": "習慣その6。優れた人脈を築くこと。成功者の周りには成功者が集まります。メンターを持ち、自分より優秀な人と積極的に交流しましょう。",
            "caption": "習慣6: 良い人脈への投資",
            "color": "#0f3460",
            "accent": "#a855f7",
        },
        {
            "narration": "習慣その7。感謝の気持ちを持つことです。毎朝・毎晩、感謝できることを3つ書き出す習慣が、ポジティブな思考を育て、チャンスを引き寄せます。",
            "caption": "習慣7: 毎日3つの感謝を書く",
            "color": "#1a1a2e",
            "accent": "#f59e0b",
        },
        {
            "narration": "以上が、金持ちの7つの習慣でした。どれか一つでも今日から始めてみてください。チャンネル登録と高評価もよろしくお願いします！",
            "caption": "チャンネル登録をお願いします！",
            "color": "#0f3460",
            "accent": "#0ea5e9",
        },
    ],
}

WORK_DIR = Path("output/demo")
VIDEO_W, VIDEO_H = 1280, 720


def check_and_install():
    """必要なパッケージを確認してインストールする。"""
    packages = {"gtts": "gTTS", "moviepy": "moviepy", "PIL": "Pillow", "numpy": "numpy"}
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
    import httpx
    from openai import OpenAI
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    client = OpenAI(api_key=api_key, http_client=httpx.Client(verify=False))
    response = client.audio.speech.create(
        model="tts-1",
        voice="nova",
        input=text,
        response_format="wav",
    )
    with open(output_path, "wb") as f:
        f.write(response.content)


def _tts_espeak(text: str, output_path: str):
    """espeak-ng（オフライン）で音声を生成する。APIキー不要。"""
    wav_path = output_path if output_path.endswith(".wav") else output_path + ".wav"
    result = subprocess.run(
        ["espeak-ng", "-v", "jpx/ja", "-s", "140", "-p", "55", "-w", wav_path, text],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RuntimeError(f"espeak-ng failed: {result.stderr.decode()}")
    if output_path != wav_path:
        os.rename(wav_path, output_path)


def generate_voice(text: str, output_path: str):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    from dotenv import load_dotenv
    load_dotenv()
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if api_key and api_key != "sk-...":
        _tts_openai(text, output_path)
    else:
        _tts_espeak(text, output_path)


def generate_image(scene: dict, scene_num: int, output_path: str):
    from PIL import Image, ImageDraw, ImageFont
    import textwrap

    img = Image.new("RGB", (VIDEO_W, VIDEO_H), scene["color"])
    draw = ImageDraw.Draw(img)

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

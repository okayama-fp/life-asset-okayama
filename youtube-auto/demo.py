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

GHIBLI_PALETTES = [
    {"sky_top": (255, 100, 50),  "sky_bot": (255, 200, 120), "hill1": (34, 100, 34),   "hill2": (60, 140, 50),   "mood": "dawn"},
    {"sky_top": (30, 120, 210),  "sky_bot": (160, 220, 255), "hill1": (30, 130, 30),   "hill2": (70, 170, 60),   "mood": "day"},
    {"sky_top": (200, 60, 20),   "sky_bot": (255, 160, 60),  "hill1": (60, 40, 20),    "hill2": (90, 70, 20),    "mood": "dusk"},
    {"sky_top": (60, 150, 220),  "sky_bot": (180, 230, 255), "hill1": (40, 170, 40),   "hill2": (80, 210, 70),   "mood": "meadow"},
    {"sky_top": (200, 150, 40),  "sky_bot": (255, 210, 90),  "hill1": (110, 80, 20),   "hill2": (150, 120, 30),  "mood": "autumn"},
    {"sky_top": (190, 210, 240), "sky_bot": (235, 248, 255), "hill1": (90, 140, 90),   "hill2": (120, 170, 120), "mood": "fog"},
    {"sky_top": (10, 15, 70),    "sky_bot": (25, 40, 110),   "hill1": (10, 50, 10),    "hill2": (20, 70, 20),    "mood": "night"},
    {"sky_top": (255, 175, 200), "sky_bot": (255, 220, 235), "hill1": (70, 140, 55),   "hill2": (100, 180, 75),  "mood": "spring"},
    {"sky_top": (40, 140, 220),  "sky_bot": (140, 205, 255), "hill1": (195, 175, 125), "hill2": (215, 195, 145), "mood": "coast"},
]


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


def _draw_ghibli_background(scene_num: int):
    """ジブリ風の水彩タッチ背景をPillow+numpyで生成する。"""
    import math
    import random
    from PIL import Image, ImageDraw, ImageFilter
    import numpy as np

    palette = GHIBLI_PALETTES[scene_num % len(GHIBLI_PALETTES)]
    mood = palette["mood"]
    rng = random.Random(scene_num * 7919)

    # ── 空のグラデーション ──────────────────────────────────
    img = Image.new("RGB", (VIDEO_W, VIDEO_H))
    pixels = img.load()
    st = palette["sky_top"]
    sb = palette["sky_bot"]
    for y in range(VIDEO_H):
        t = y / VIDEO_H
        r = int(st[0] + (sb[0] - st[0]) * t)
        g = int(st[1] + (sb[1] - st[1]) * t)
        b = int(st[2] + (sb[2] - st[2]) * t)
        for x in range(VIDEO_W):
            pixels[x, y] = (r, g, b)

    draw = ImageDraw.Draw(img, "RGBA")

    # ── 星（夜モード） ──────────────────────────────────────
    if mood == "night":
        num_stars = rng.randint(25, 45)
        for _ in range(num_stars):
            sx = rng.randint(0, VIDEO_W)
            sy = rng.randint(0, int(VIDEO_H * 0.65))
            sr = rng.randint(1, 3)
            alpha = rng.randint(160, 255)
            draw.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 255, 240, alpha))

    # ── 太陽/光線（dawn・dusk） ──────────────────────────────
    if mood in ("dawn", "dusk"):
        horizon_y = int(VIDEO_H * 0.58)
        sun_x = VIDEO_W // 2 + rng.randint(-80, 80)
        sun_r = 48
        if mood == "dawn":
            sun_color = (255, 240, 160, 200)
            ray_color = (255, 220, 80, 30)
        else:
            sun_color = (255, 140, 40, 200)
            ray_color = (255, 100, 20, 25)
        # 光線
        num_rays = 12
        for ri in range(num_rays):
            angle = math.radians(ri * (360 / num_rays))
            ray_len = rng.randint(180, 320)
            ex = int(sun_x + math.cos(angle) * ray_len)
            ey = int(horizon_y + math.sin(angle) * ray_len)
            draw.line([(sun_x, horizon_y), (ex, ey)], fill=ray_color, width=rng.randint(3, 10))
        # 太陽
        draw.ellipse(
            [sun_x - sun_r, horizon_y - sun_r, sun_x + sun_r, horizon_y + sun_r],
            fill=sun_color,
        )

    # ── 雲（3〜5個） ──────────────────────────────────────
    num_clouds = rng.randint(3, 5)
    for _ in range(num_clouds):
        cx = rng.randint(80, VIDEO_W - 80)
        cy = rng.randint(30, int(VIDEO_H * 0.4))
        num_puffs = rng.randint(3, 6)
        for pi in range(num_puffs):
            px = cx + rng.randint(-80, 80)
            py = cy + rng.randint(-20, 20)
            pw = rng.randint(60, 130)
            ph = rng.randint(35, 70)
            alpha = rng.randint(160, 220)
            cloud_color = (255, 252, 245, alpha) if mood != "night" else (200, 210, 240, 80)
            draw.ellipse([px - pw, py - ph, px + pw, py + ph], fill=cloud_color)

    # ── 丘（2層、サイン波輪郭） ───────────────────────────
    hill_y_base1 = int(VIDEO_H * 0.72)
    hill_y_base2 = int(VIDEO_H * 0.82)

    def make_hill_polygon(base_y, amplitude, freq_mult, x_offset, color):
        pts = [(0, VIDEO_H)]
        for xi in range(0, VIDEO_W + 1, 4):
            wave = math.sin((xi + x_offset) * freq_mult * math.pi / VIDEO_W)
            yi = int(base_y - amplitude * (0.5 + 0.5 * wave))
            pts.append((xi, yi))
        pts.append((VIDEO_W, VIDEO_H))
        draw.polygon(pts, fill=color + (255,))

    amp1 = rng.randint(55, 100)
    amp2 = rng.randint(35, 65)
    freq1 = rng.uniform(1.5, 3.0)
    freq2 = rng.uniform(2.0, 4.0)
    xoff1 = rng.randint(0, 300)
    xoff2 = rng.randint(0, 300)

    make_hill_polygon(hill_y_base1, amp1, freq1, xoff1, palette["hill2"])
    make_hill_polygon(hill_y_base2, amp2, freq2, xoff2, palette["hill1"])

    # ── 木（3〜8本） ──────────────────────────────────────
    num_trees = rng.randint(3, 8)
    for _ in range(num_trees):
        tx = rng.randint(30, VIDEO_W - 30)
        # 木は丘の上あたりに配置
        ty_base = int(hill_y_base2 - amp2 * 0.5 - rng.randint(0, 40))
        trunk_h = rng.randint(30, 70)
        trunk_w = rng.randint(6, 14)
        leaf_rx = rng.randint(20, 45)
        leaf_ry = rng.randint(25, 55)
        # 幹色
        trunk_color = (
            max(0, palette["hill1"][0] - 30),
            max(0, palette["hill1"][1] - 50),
            max(0, palette["hill1"][2] - 20),
            220,
        )
        # 葉色
        leaf_color = palette["hill2"] + (200,)
        # 幹
        draw.rectangle(
            [tx - trunk_w // 2, ty_base - trunk_h, tx + trunk_w // 2, ty_base],
            fill=trunk_color,
        )
        # 葉
        leaf_cy = ty_base - trunk_h - leaf_ry // 2
        draw.ellipse(
            [tx - leaf_rx, leaf_cy - leaf_ry, tx + leaf_rx, leaf_cy + leaf_ry],
            fill=leaf_color,
        )

    # ── 水彩テクスチャ: ガウスぼかし ────────────────────
    img = img.filter(ImageFilter.GaussianBlur(radius=1.5))

    # ── numpy ノイズ（std=8）でテクスチャ感 ────────────
    arr = np.array(img).astype(np.int16)
    noise = np.random.RandomState(scene_num).normal(0, 8, arr.shape)
    arr = np.clip(arr + noise, 0, 255).astype(np.uint8)
    img = Image.fromarray(arr, "RGB")

    return img


def generate_image(scene: dict, scene_num: int, output_path: str):
    """ジブリ風水彩背景を生成し、テロップを重ねる。外部APIは使用しない。"""
    from PIL import Image, ImageDraw, ImageFont

    # ── ジブリ背景生成 ──────────────────────────────────────
    img = _draw_ghibli_background(scene_num)
    print(f"    → ジブリ風背景（{GHIBLI_PALETTES[scene_num % len(GHIBLI_PALETTES)]['mood']}）")

    # ── テキスト描画 ──────────────────────────────────────
    draw = ImageDraw.Draw(img, "RGBA")
    accent_hex = scene.get("accent", "#0ea5e9")
    accent = tuple(int(accent_hex.lstrip("#")[i:i+2], 16) for i in (0, 2, 4))

    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 52)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc", 32)
        font_num = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", 40)
    except OSError:
        try:
            font_large = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 52)
            font_small = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 32)
            font_num = ImageFont.truetype("C:/Windows/Fonts/meiryo.ttc", 40)
        except OSError:
            font_large = font_small = font_num = ImageFont.load_default()

    # シーン番号バッジ（左上）
    if scene_num > 0:
        r = 45
        cx, cy = 100, 100
        badge_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
        bdraw = ImageDraw.Draw(badge_overlay)
        bdraw.ellipse([cx - r, cy - r, cx + r, cy + r], fill=accent + (210,))
        img = Image.alpha_composite(img.convert("RGBA"), badge_overlay).convert("RGB")
        draw = ImageDraw.Draw(img, "RGBA")

        num_text = str(scene_num)
        bbox3 = draw.textbbox((0, 0), num_text, font=font_num)
        nw = bbox3[2] - bbox3[0]
        nh = bbox3[3] - bbox3[1]
        draw.text((100 - nw // 2, 100 - nh // 2), num_text, font=font_num, fill=(255, 255, 255, 255))

    # キャプション（画面中央下寄り）
    caption = scene["caption"]
    bbox = draw.textbbox((0, 0), caption, font=font_large)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    tx = (VIDEO_W - tw) // 2
    ty = int(VIDEO_H * 0.72) - th - 20
    pad = 16
    # 半透明背景
    cap_overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    cdraw = ImageDraw.Draw(cap_overlay)
    cdraw.rectangle([tx - pad, ty - pad, tx + tw + pad, ty + th + pad], fill=(0, 0, 0, 160))
    img = Image.alpha_composite(img.convert("RGBA"), cap_overlay).convert("RGB")
    draw = ImageDraw.Draw(img)

    # テキスト影＋本文（温かいクリーム色）
    draw.text((tx + 2, ty + 2), caption, font=font_large, fill=(0, 0, 0))
    draw.text((tx, ty), caption, font=font_large, fill=(255, 245, 180))

    # ロゴ（右下）
    logo = "Life Asset Partners"
    bbox2 = draw.textbbox((0, 0), logo, font=font_small)
    lw = bbox2[2] - bbox2[0]
    draw.text((VIDEO_W - lw - 30, VIDEO_H - 55), logo, font=font_small, fill=accent)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    img.save(output_path)


EFFECTS = ["zoom_in", "pan_right", "zoom_out", "pan_left", "zoom_pan"]


def _split_phrases(text: str) -> list:
    """ナレーションを句読点で短いフレーズに分割する。"""
    import re
    parts = re.split(r'(?<=[。、！？!?,．，])', text)
    phrases = []
    buf = ""
    for p in parts:
        buf += p
        if len(buf) >= 8 and buf.strip():
            phrases.append(buf.strip())
            buf = ""
    if buf.strip():
        phrases.append(buf.strip())
    return [p for p in phrases if p]


def _get_font(size: int):
    from PIL import ImageFont
    for path in [
        "C:/Windows/Fonts/meiryo.ttc",
        "C:/Windows/Fonts/msgothic.ttc",
        "C:/Windows/Fonts/YuGothB.ttc",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except OSError:
            pass
    return ImageFont.load_default()


def _draw_phrase_overlay(frame_np, phrases, timings, t):
    """現在時刻 t に合わせてフレーズをフレームに描画する。ジブリ風テキストと輝く粒子付き。"""
    import random
    from PIL import Image, ImageDraw
    import numpy as np

    overlay = Image.new("RGBA", (VIDEO_W, VIDEO_H), (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    font_big = _get_font(54)
    font_small = _get_font(38)

    # 現在・直前のフレーズを特定
    current_idx = -1
    for i, (s, e) in enumerate(timings):
        if s <= t < e:
            current_idx = i
            break
    if current_idx == -1 and t >= timings[-1][1]:
        current_idx = len(phrases) - 1

    # 表示: 現在フレーズ（クリーム色・大）＋ 直前（白・小・薄）
    show = []
    if current_idx > 0:
        show.append((phrases[current_idx - 1], False, timings[current_idx - 1]))
    if current_idx >= 0:
        show.append((phrases[current_idx], True, timings[current_idx]))

    line_h = 64
    base_y = VIDEO_H - line_h * len(show) - 70

    for i, (phrase, is_current, (s, e)) in enumerate(show):
        y = base_y + i * line_h
        font = font_big if is_current else font_small

        # フェードイン
        if is_current:
            fade = min((t - s) / 0.25, 1.0)
            # ウォームクリーム色（harsh yellowからソフトなクリームへ）
            color = (255, 245, 180, int(255 * fade))
            shadow = (0, 0, 0, int(220 * fade))
            glow = (200, 150, 20, int(80 * fade))
        else:
            color = (200, 200, 200, 140)
            shadow = (0, 0, 0, 80)
            glow = None

        bbox = draw.textbbox((0, 0), phrase, font=font)
        tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        x = (VIDEO_W - tw) // 2
        pad = 12
        draw.rectangle([x - pad, y - pad, x + tw + pad, y + th + pad], fill=(0, 0, 0, 120))
        draw.text((x + 2, y + 2), phrase, font=font, fill=shadow)

        # ウォームグロー（現在フレーズのみ、4方向オフセットで柔らかい輝き）
        if glow is not None:
            for ox, oy in [(-2, -2), (2, -2), (-2, 2), (2, 2)]:
                draw.text((x + ox, y + oy), phrase, font=font, fill=glow)

        draw.text((x, y), phrase, font=font, fill=color)

    # ── 浮かび上がる輝く粒子（ジブリのすすたまり・ホタル風） ──
    rng = random.Random(int(t * 30))  # 時間で変化するシード
    num_particles = rng.randint(15, 25)
    for _ in range(num_particles):
        px = rng.randint(0, VIDEO_W)
        # 時間とともに上昇: y = H - (t * 40) % H
        base_py = VIDEO_H - (t * 40) % VIDEO_H
        py = int(base_py + rng.randint(-30, 30)) % VIDEO_H
        pr = rng.randint(2, 4)
        alpha = rng.randint(80, 200)
        # 温かい黄色〜クリーム色
        pr_color_choices = [
            (255, 240, 100, alpha),
            (255, 220, 60, alpha),
            (255, 255, 200, alpha),
            (255, 200, 80, alpha),
        ]
        pcolor = rng.choice(pr_color_choices)
        draw.ellipse([px - pr, py - pr, px + pr, py + pr], fill=pcolor)

    base = Image.fromarray(frame_np).convert("RGBA")
    result = Image.alpha_composite(base, overlay)
    return np.array(result.convert("RGB"))


def _make_ken_burns_frame(img_big, effect, progress):
    """Ken Burns エフェクトの1フレームを生成する。イーズイン・アウト曲線適用。"""
    import math
    import numpy as np
    from PIL import Image
    big_h, big_w = img_big.shape[:2]

    # イーズイン・アウト（コサイン補間）
    eased = 0.5 - 0.5 * math.cos(math.pi * progress)
    progress = eased

    if effect == "zoom_in":
        s = 1.0 + 0.25 * progress
        sw, sh = int(VIDEO_W / s), int(VIDEO_H / s)
        x, y = (big_w - sw) // 2, (big_h - sh) // 2
    elif effect == "zoom_out":
        s = 1.25 - 0.25 * progress
        sw, sh = int(VIDEO_W / s), int(VIDEO_H / s)
        x, y = (big_w - sw) // 2, (big_h - sh) // 2
    elif effect == "pan_right":
        sw, sh = VIDEO_W, VIDEO_H
        x = int((big_w - VIDEO_W) * progress)
        y = (big_h - VIDEO_H) // 2
    elif effect == "pan_left":
        sw, sh = VIDEO_W, VIDEO_H
        x = int((big_w - VIDEO_W) * (1 - progress))
        y = (big_h - VIDEO_H) // 2
    else:  # zoom_pan
        s = 1.0 + 0.2 * progress
        sw, sh = int(VIDEO_W / s), int(VIDEO_H / s)
        x = int((big_w - sw) * progress * 0.5)
        y = (big_h - sh) // 2

    x = max(0, min(x, big_w - sw))
    y = max(0, min(y, big_h - sh))
    crop = img_big[y:y+sh, x:x+sw]
    return np.array(Image.fromarray(crop).resize((VIDEO_W, VIDEO_H), Image.LANCZOS))


def create_video(scenes_data: list, output_path: str):
    from moviepy import VideoClip, AudioFileClip, concatenate_videoclips
    from PIL import Image
    import numpy as np

    clips = []
    for idx, s in enumerate(scenes_data):
        audio = AudioFileClip(s["audio"])
        duration = audio.duration + 0.8
        effect = EFFECTS[idx % len(EFFECTS)]
        narration = s.get("narration", "")

        # Ken Burns 用に画像を 1.3 倍に拡大
        img_pil = Image.open(s["image"]).convert("RGB")
        big = img_pil.resize((int(VIDEO_W * 1.3), int(VIDEO_H * 1.3)), Image.LANCZOS)
        img_big = np.array(big)

        # フレーズ分割とタイミング計算（文字数比例）
        phrases = _split_phrases(narration) if narration else [s.get("caption", "")]
        total_chars = max(sum(len(p) for p in phrases), 1)
        timings = []
        cur = 0.2
        for phrase in phrases:
            span = (len(phrase) / total_chars) * (duration - 0.5)
            timings.append((cur, cur + span))
            cur += span

        def make_frame(t, _img=img_big, _dur=duration, _eff=effect,
                       _phrases=phrases, _timings=timings):
            progress = min(t / _dur, 1.0)
            bg = _make_ken_burns_frame(_img, _eff, progress)
            return _draw_phrase_overlay(bg, _phrases, _timings, t)

        clip = VideoClip(make_frame, duration=duration).with_fps(24).with_audio(audio)
        clips.append(clip)
        print(f"  シーン {idx+1}: {effect} / {len(phrases)}フレーズ")

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
            "narration": scene["narration"],
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

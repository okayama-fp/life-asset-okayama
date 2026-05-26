"""画像・音声・テロップを合成して MP4 動画を生成する。"""
import os
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np
from moviepy import (
    ImageClip,
    AudioFileClip,
    TextClip,
    CompositeVideoClip,
    concatenate_videoclips,
)
from config import VIDEO_WIDTH, VIDEO_HEIGHT, FPS, SCENE_BUFFER_SEC


def add_caption_overlay(image_path: str, caption: str) -> np.ndarray:
    """Pillow で画像にテロップを描画して numpy 配列を返す。"""
    img = Image.open(image_path).convert("RGB")
    img = img.resize((VIDEO_WIDTH, VIDEO_HEIGHT), Image.LANCZOS)

    draw = ImageDraw.Draw(img)

    # フォントサイズを動的に設定（幅に応じて調整）
    font_size = 56
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansCJK-Bold.ttc", font_size)
    except OSError:
        try:
            font = ImageFont.truetype("/usr/share/fonts/opentype/noto/NotoSansCJKjp-Bold.otf", font_size)
        except OSError:
            font = ImageFont.load_default()

    bbox = draw.textbbox((0, 0), caption, font=font)
    text_w = bbox[2] - bbox[0]
    text_h = bbox[3] - bbox[1]

    padding = 20
    x = (VIDEO_WIDTH - text_w) // 2
    y = VIDEO_HEIGHT - text_h - padding * 3

    # 半透明の背景ボックス
    box_img = Image.new("RGBA", img.size, (0, 0, 0, 0))
    box_draw = ImageDraw.Draw(box_img)
    box_draw.rectangle(
        [x - padding, y - padding, x + text_w + padding, y + text_h + padding],
        fill=(0, 0, 0, 160),
    )
    img = Image.alpha_composite(img.convert("RGBA"), box_img).convert("RGB")
    draw = ImageDraw.Draw(img)

    # テキスト描画（影 + 本文）
    draw.text((x + 2, y + 2), caption, font=font, fill=(0, 0, 0))
    draw.text((x, y), caption, font=font, fill=(255, 255, 255))

    return np.array(img)


def build_scene_clip(image_path: str, audio_path: str, caption: str) -> CompositeVideoClip:
    """1シーン分のクリップ（画像＋音声＋テロップ）を生成する。"""
    audio = AudioFileClip(audio_path)
    duration = audio.duration + SCENE_BUFFER_SEC

    frame = add_caption_overlay(image_path, caption)
    image_clip = ImageClip(frame, duration=duration).with_fps(FPS).with_audio(audio)

    return image_clip


def create_video(scenes: list, output_path: str) -> str:
    """全シーンを結合して MP4 ファイルを生成する。

    scenes: [{"image": path, "audio": path, "caption": str}, ...]
    """
    clips = []
    for scene in scenes:
        clip = build_scene_clip(
            scene["image"],
            scene["audio"],
            scene["caption"],
        )
        clips.append(clip)

    final = concatenate_videoclips(clips, method="compose")

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    final.write_videofile(
        output_path,
        fps=FPS,
        codec="libx264",
        audio_codec="aac",
        temp_audiofile="temp_audio.m4a",
        remove_temp=True,
        threads=4,
        preset="fast",
    )

    return output_path

"""
ジャケット画像生成スクリプト
DALL-E 3 API で 3000×3000 JPG を生成し、テキストを合成します。

使用方法:
  pip install openai pillow requests
  export OPENAI_API_KEY="sk-..."
  python generate_cover.py --title "Morning Breeze" --artist "Life Asset" --output cover.jpg
"""

import argparse
import os
import io
import requests
from pathlib import Path

def generate_cover(title: str, artist: str, output_path: str):
    from openai import OpenAI
    from PIL import Image, ImageDraw, ImageFont

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

    print(f"DALL-E 3 でジャケット画像を生成中...")
    prompt = (
        "A refreshing and uplifting album cover art. "
        "Bright morning sky with soft golden sunlight, light blue gradient background, "
        "gentle abstract wave patterns in white and sky blue, "
        "minimalist modern design, clean and airy feel, "
        "no text, no people, suitable for music release, "
        "3000x3000 pixel quality, professional album artwork"
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1024x1024",
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url
    print(f"画像URL取得: {image_url[:60]}...")

    # ダウンロード
    img_data = requests.get(image_url).content
    img = Image.open(io.BytesIO(img_data))

    # 3000×3000にリサイズ
    img = img.resize((3000, 3000), Image.LANCZOS)

    # テキスト合成
    draw = ImageDraw.Draw(img)

    # フォントサイズ設定（システムフォントを使用）
    try:
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 160)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 90)
    except:
        font_large = ImageFont.load_default()
        font_small = ImageFont.load_default()

    # 半透明の帯をテキスト背景に追加
    overlay = Image.new("RGBA", img.size, (0, 0, 0, 0))
    overlay_draw = ImageDraw.Draw(overlay)
    overlay_draw.rectangle([(0, 2400), (3000, 3000)], fill=(0, 0, 0, 140))
    img = img.convert("RGBA")
    img = Image.alpha_composite(img, overlay)
    img = img.convert("RGB")
    draw = ImageDraw.Draw(img)

    # タイトル（曲名）
    title_bbox = draw.textbbox((0, 0), title, font=font_large)
    title_w = title_bbox[2] - title_bbox[0]
    draw.text(
        ((3000 - title_w) // 2, 2450),
        title,
        font=font_large,
        fill=(255, 255, 255),
    )

    # アーティスト名
    artist_bbox = draw.textbbox((0, 0), artist, font=font_small)
    artist_w = artist_bbox[2] - artist_bbox[0]
    draw.text(
        ((3000 - artist_w) // 2, 2680),
        artist,
        font=font_small,
        fill=(200, 230, 255),
    )

    # 推奨文字（サブテキスト）
    sub_text = "Original BGM  |  Instrumental"
    sub_bbox = draw.textbbox((0, 0), sub_text, font=font_small)
    sub_w = sub_bbox[2] - sub_bbox[0]
    draw.text(
        ((3000 - sub_w) // 2, 2810),
        sub_text,
        font=font_small,
        fill=(160, 200, 240),
    )

    # 保存
    img.save(output_path, "JPEG", quality=95)
    print(f"✅ ジャケット画像を保存しました: {output_path}")
    print(f"   サイズ: {img.size[0]}×{img.size[1]} px")
    return output_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="アルバムジャケット画像生成")
    parser.add_argument("--title", default="Morning Breeze", help="曲名")
    parser.add_argument("--artist", default="Life Asset", help="アーティスト名")
    parser.add_argument("--output", default="cover.jpg", help="出力ファイルパス")
    args = parser.parse_args()

    generate_cover(args.title, args.artist, args.output)

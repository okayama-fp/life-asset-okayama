"""DALL-E 3 でシーン画像を生成して PNG として保存する。"""
import os
import requests
from openai import OpenAI
from config import OPENAI_API_KEY, VIDEO_WIDTH, VIDEO_HEIGHT


client = OpenAI(api_key=OPENAI_API_KEY)


def generate_scene_image(prompt: str, output_path: str) -> str:
    """DALL-E 3 で画像を生成して output_path に保存する。"""

    full_prompt = (
        f"{prompt}, "
        "professional photography, cinematic lighting, 4K ultra HD, "
        "no text, no watermark, clean composition"
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=full_prompt,
        size="1792x1024",  # 16:9 に近いサイズ
        quality="standard",
        n=1,
    )

    image_url = response.data[0].url
    img_data = requests.get(image_url, timeout=30).content

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_data)

    return output_path


def generate_thumbnail(title: str, output_path: str) -> str:
    """サムネイル用画像を DALL-E 3 で生成する。"""
    prompt = (
        f"YouTube thumbnail for a video about wealthy people habits, "
        f"topic: {title}, "
        "luxury lifestyle, successful businessman, gold and dark background, "
        "eye-catching, high contrast, professional, cinematic, 4K"
    )

    response = client.images.generate(
        model="dall-e-3",
        prompt=prompt,
        size="1792x1024",
        quality="hd",
        n=1,
    )

    image_url = response.data[0].url
    img_data = requests.get(image_url, timeout=30).content

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(img_data)

    return output_path


if __name__ == "__main__":
    out = generate_scene_image(
        "wealthy businessman reading books in a modern library at sunrise",
        "output/test_image.png",
    )
    print(f"画像生成完了: {out}")

"""
金持ちの習慣 YouTube 動画自動生成ツール

使い方:
  python main.py                        # デフォルトテーマで生成
  python main.py --topic "朝活の習慣"   # テーマ指定
  python main.py --skip-images          # 画像生成をスキップ（既存画像を使用）
"""
import argparse
import json
import os
import sys
from pathlib import Path

from config import OUTPUT_DIR, VIDEO_TITLE_PREFIX
from generate_script import generate_script
from generate_voice import text_to_wav, check_voicevox
from generate_images import generate_scene_image, generate_thumbnail
from create_video import create_video


def main():
    parser = argparse.ArgumentParser(description="金持ちの習慣 YouTube 動画自動生成")
    parser.add_argument("--topic", default="金持ちの習慣 トップ7", help="動画テーマ")
    parser.add_argument("--skip-images", action="store_true", help="DALL-E 画像生成をスキップ")
    parser.add_argument("--skip-voice", action="store_true", help="VOICEVOX 音声生成をスキップ")
    args = parser.parse_args()

    # ── 1. VOICEVOX 起動確認 ──────────────────────────────
    if not args.skip_voice:
        print("▶ VOICEVOXサーバーを確認中...")
        if not check_voicevox():
            print("✗ VOICEVOXが起動していません。")
            print("  以下のいずれかで起動してください:")
            print("  - VOICEVOX アプリを起動")
            print("  - Docker: docker run -p 50021:50021 voicevox/voicevox_engine:latest")
            print("  --skip-voice オプションで音声生成をスキップできます。")
            sys.exit(1)
        print("✓ VOICEVOXサーバー接続OK")

    # ── 2. 台本生成 ──────────────────────────────────────
    print(f"\n▶ 台本を生成中... テーマ: {args.topic}")
    script = generate_script(args.topic)

    title = VIDEO_TITLE_PREFIX + script["title"]
    print(f"✓ タイトル: {title}")
    print(f"  シーン数: {len(script['scenes'])}")

    # 作業フォルダを作成
    safe_title = "".join(c for c in script["title"] if c.isalnum() or c in "ぁ-ん亜-熙ァ-ン_ ")[:30]
    work_dir = Path(OUTPUT_DIR) / safe_title
    work_dir.mkdir(parents=True, exist_ok=True)

    # 台本を保存
    script_path = work_dir / "script.json"
    with open(script_path, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    print(f"✓ 台本保存: {script_path}")

    # ── 3. 音声生成 ──────────────────────────────────────
    audio_paths = []
    if not args.skip_voice:
        print("\n▶ 音声を生成中...")
        for i, scene in enumerate(script["scenes"], 1):
            audio_path = str(work_dir / f"scene_{i:02d}.wav")
            print(f"  シーン {i}/{len(script['scenes'])}: {scene['narration'][:30]}...")
            text_to_wav(scene["narration"], audio_path)
            audio_paths.append(audio_path)
        print(f"✓ 音声生成完了: {len(audio_paths)} ファイル")
    else:
        # スキップ時は既存ファイルを探す
        for i in range(1, len(script["scenes"]) + 1):
            audio_paths.append(str(work_dir / f"scene_{i:02d}.wav"))
        print("  （音声生成スキップ）")

    # ── 4. 画像生成 ──────────────────────────────────────
    image_paths = []
    if not args.skip_images:
        print("\n▶ 画像を生成中（DALL-E 3）...")
        for i, scene in enumerate(script["scenes"], 1):
            image_path = str(work_dir / f"scene_{i:02d}.png")
            print(f"  シーン {i}/{len(script['scenes'])}: {scene['image_prompt'][:50]}...")
            generate_scene_image(scene["image_prompt"], image_path)
            image_paths.append(image_path)

        # サムネイル生成
        thumb_path = str(work_dir / "thumbnail.png")
        print("  サムネイル生成中...")
        generate_thumbnail(script["title"], thumb_path)
        print(f"✓ 画像生成完了: {len(image_paths)} シーン + サムネイル")
    else:
        for i in range(1, len(script["scenes"]) + 1):
            image_paths.append(str(work_dir / f"scene_{i:02d}.png"))
        print("  （画像生成スキップ）")

    # ── 5. 動画合成 ──────────────────────────────────────
    print("\n▶ 動画を合成中...")

    scenes_data = []
    for i, scene in enumerate(script["scenes"]):
        scenes_data.append({
            "image": image_paths[i],
            "audio": audio_paths[i],
            "caption": scene["caption"],
        })

    output_video = str(work_dir / "output.mp4")
    create_video(scenes_data, output_video)

    # ── 6. 完了レポート ──────────────────────────────────
    print("\n" + "=" * 60)
    print("✅ 動画生成完了！")
    print(f"  動画ファイル : {output_video}")
    print(f"  サムネイル  : {work_dir / 'thumbnail.png'}")
    print(f"  台本JSON    : {script_path}")
    print()
    print("📺 YouTube アップロード用情報:")
    print(f"  タイトル: {title}")
    print(f"  概要欄: {script['description']}")
    print("=" * 60)


if __name__ == "__main__":
    main()

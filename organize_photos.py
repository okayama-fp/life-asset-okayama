#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E:\\ の写真・動画を西暦年月日フォルダへ自動整理するスクリプト
対象期間: 2026年1月31日まで

フォルダ構成:
  E:\整理済み\
    写真\
      2024年\
        2024-01月\
          2024-01-15\
            IMG_001.jpg
    動画\
      2024年\
        2024-01月\
          2024-01-15\
            VID_001.mp4

使い方:
  確認のみ（移動しない）:  python organize_photos.py --dry-run
  実際に整理する        :  python organize_photos.py

依存ライブラリ (EXIFを正確に読む場合):
  pip install Pillow
  ※ Pillowがなくてもファイル日付で動作します
"""

from __future__ import annotations
import os
import shutil
import sys
from datetime import datetime
from pathlib import Path

# ===================== 設定 =====================
SOURCE_DIR = Path(r"E:\\")          # 整理元フォルダ
DEST_DIR   = Path(r"E:\整理済み")   # 整理先フォルダ
CUTOFF     = datetime(2026, 1, 31, 23, 59, 59)  # この日時までのファイルを対象

DRY_RUN    = "--dry-run" in sys.argv  # --dry-run で確認のみ（実際には移動しない）

# 対象の拡張子
PHOTO_EXT = {
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".tif",
    ".heic", ".heif", ".raw", ".arw", ".nef", ".cr2", ".cr3",
    ".orf", ".rw2", ".dng", ".webp",
}
VIDEO_EXT = {
    ".mp4", ".mov", ".avi", ".mkv", ".m4v", ".3gp", ".mts",
    ".m2ts", ".wmv", ".flv", ".ts", ".mpg", ".mpeg",
}
# ================================================


def get_exif_date(path: Path) -> datetime | None:
    """JPG / PNG / HEIC 等の EXIF 撮影日時を取得する"""
    try:
        from PIL import Image, ExifTags  # type: ignore
        with Image.open(path) as img:
            exif = img._getexif()
            if not exif:
                return None
            for tag_id, val in exif.items():
                tag = ExifTags.TAGS.get(tag_id, "")
                if tag in ("DateTimeOriginal", "DateTimeDigitized", "DateTime"):
                    try:
                        return datetime.strptime(str(val), "%Y:%m:%d %H:%M:%S")
                    except ValueError:
                        pass
    except Exception:
        pass
    return None


def get_file_date(path: Path) -> datetime:
    """ファイルの日付を取得する（EXIF → 作成日 → 更新日 の優先順）"""
    date = get_exif_date(path)
    if date:
        return date

    stat = path.stat()
    # Windows では st_ctime が作成日時、st_mtime が更新日時
    ctime = datetime.fromtimestamp(stat.st_ctime)
    mtime = datetime.fromtimestamp(stat.st_mtime)
    # 古い方（より元の日付に近い）を採用
    return min(ctime, mtime)


def build_dest_path(file: Path, date: datetime) -> Path:
    """整理先のフルパスを生成する
    例: E:\整理済み\写真\2024年\2024-01月\2024-01-15\IMG_001.jpg
        E:\整理済み\動画\2024年\2024-01月\2024-01-15\VID_001.mp4
    """
    kind_dir = "写真" if file.suffix.lower() in PHOTO_EXT else "動画"
    folder = (
        DEST_DIR
        / kind_dir
        / f"{date.year}年"
        / f"{date.year}-{date.month:02d}月"
        / f"{date.year}-{date.month:02d}-{date.day:02d}"
    )
    return folder / file.name


def unique_dest(path: Path) -> Path:
    """同名ファイルが既にある場合、連番を付けて衝突を回避する"""
    if not path.exists():
        return path
    stem   = path.stem
    suffix = path.suffix
    i = 1
    while True:
        candidate = path.parent / f"{stem}_{i:03d}{suffix}"
        if not candidate.exists():
            return candidate
        i += 1


def is_inside_dest(file: Path) -> bool:
    """整理済みフォルダ内のファイルは再処理しない"""
    try:
        file.relative_to(DEST_DIR)
        return True
    except ValueError:
        return False


def main() -> None:
    target_exts = PHOTO_EXT | VIDEO_EXT

    moved   = 0
    skipped = 0
    errors  = 0

    print("=" * 60)
    print(f"  写真・動画 日付別整理スクリプト")
    print(f"  {'[確認モード / 移動しません] ' if DRY_RUN else '[実行モード]'}")
    print("=" * 60)
    print(f"  整理元 : {SOURCE_DIR}")
    print(f"  整理先 : {DEST_DIR}")
    print(f"  対象期間: ～ {CUTOFF.strftime('%Y年%m月%d日')}")
    print()

    for file in SOURCE_DIR.rglob("*"):
        if not file.is_file():
            continue

        # 対象外の拡張子をスキップ
        if file.suffix.lower() not in target_exts:
            continue

        # 整理済みフォルダ内はスキップ
        if is_inside_dest(file):
            continue

        # ファイル日付を取得
        try:
            date = get_file_date(file)
        except Exception as e:
            print(f"  [エラー] 日付取得失敗: {file.name}  ({e})")
            errors += 1
            continue

        # 2026年1月以降のファイルはスキップ
        if date > CUTOFF:
            skipped += 1
            continue

        dst = unique_dest(build_dest_path(file, date))

        # 表示
        try:
            rel_src = file.relative_to(SOURCE_DIR)
        except ValueError:
            rel_src = file
        try:
            rel_dst = dst.relative_to(DEST_DIR)
        except ValueError:
            rel_dst = dst

        kind = "写真" if file.suffix.lower() in PHOTO_EXT else "動画"
        print(f"  [{kind}] {rel_src}  →  {rel_dst}")

        if not DRY_RUN:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(file), str(dst))

        moved += 1

    # 空フォルダを削除（DRY_RUN 以外）
    if not DRY_RUN and moved > 0:
        _remove_empty_dirs(SOURCE_DIR)

    print()
    print("=" * 60)
    print(f"  完了: 整理 {moved} 件 / 期間外スキップ {skipped} 件 / エラー {errors} 件")
    if DRY_RUN:
        print()
        print("  ※ 確認モードのため実際には移動していません。")
        print("     実際に整理するには: python organize_photos.py")
    print("=" * 60)


def _remove_empty_dirs(root: Path) -> None:
    """整理後に空になったフォルダを削除する（整理先フォルダは対象外）"""
    for dirpath in sorted(root.rglob("*"), reverse=True):
        if not dirpath.is_dir():
            continue
        if is_inside_dest(dirpath):
            continue
        try:
            dirpath.rmdir()  # 空でなければ失敗するので安全
        except OSError:
            pass


if __name__ == "__main__":
    main()

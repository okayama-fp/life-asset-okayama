"""VOICEVOX ローカルサーバーを使って日本語音声 WAV を生成する。"""
import os
import requests
from config import VOICEVOX_URL, VOICEVOX_SPEAKER


def text_to_wav(text: str, output_path: str, speaker: int = VOICEVOX_SPEAKER) -> str:
    """テキストを音声ファイル（WAV）に変換して output_path に保存する。"""

    # 1. 音声合成クエリを作成
    query_res = requests.post(
        f"{VOICEVOX_URL}/audio_query",
        params={"text": text, "speaker": speaker},
        timeout=30,
    )
    query_res.raise_for_status()
    query = query_res.json()

    # 読み上げ速度を少し上げる（1.1倍）
    query["speedScale"] = 1.1

    # 2. 音声合成を実行
    synth_res = requests.post(
        f"{VOICEVOX_URL}/synthesis",
        params={"speaker": speaker},
        json=query,
        timeout=60,
    )
    synth_res.raise_for_status()

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "wb") as f:
        f.write(synth_res.content)

    return output_path


def check_voicevox() -> bool:
    """VOICEVOX サーバーが起動しているか確認する。"""
    try:
        res = requests.get(f"{VOICEVOX_URL}/version", timeout=5)
        return res.status_code == 200
    except requests.exceptions.ConnectionError:
        return False


if __name__ == "__main__":
    if check_voicevox():
        out = text_to_wav("こんにちは！金持ちの習慣をご紹介します。", "output/test_voice.wav")
        print(f"音声ファイル生成完了: {out}")
    else:
        print("VOICEVOXサーバーが起動していません。先に起動してください。")
        print(f"起動URL: {VOICEVOX_URL}")

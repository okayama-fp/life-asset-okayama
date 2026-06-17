#!/usr/bin/env python3
"""Microsoft Edge TTS（ニューラル音声）でナレーションを生成"""
import asyncio
import base64
import json
import edge_tts

# 利用可能な日本語音声（高品質ニューラル）
# Nanami: 女性 / Keita: 男性
VOICE = "ja-JP-NanamiNeural"

narrations = [
    "お金のことを考えるのが怖いあなたへ。でも実は、考えないことの方が、ずっと危険です。",
    "日本FP協会の調査によると、将来のお金が不安と感じる人の約7割が、家計をまったく把握していないと回答しています。",
    "デメリット、1つ目。不安が慢性化します。脳は、見えない脅威を最も恐れます。家計を見ないことで、最悪いくらヤバいかもわからないという、最大の不安が生まれてしまいます。",
    "デメリット、2つ目。将来への無力感が育ちます。お金を見ない習慣は、やればできるという自己効力感を、じわじわと奪っていきます。これは仕事や人間関係にも影響します。",
    "デメリット、3つ目。人間関係にも亀裂が入ります。パートナーとのすれ違い、子どもへのイライラ、友人の誘いを断り続けることでの孤立感。お金の問題は、人間関係にも広がっていきます。",
    "デメリット、4つ目。衝動買いが増えます。不安からストレス発散でショッピングをして、お金が減り、またより不安になる。この悪循環が、止まらなくなります。",
    "まとめです。知らないことは、逃げではなくリスクです。不安の慢性化、無力感、人間関係への悪影響、そして衝動買いの悪循環。これらが静かに積み重なっていきます。",
    "解決策は、月に10分だけ、お金と向き合うことです。今月の収入はいくらか。支出はいくらか。貯金は増えたか減ったか。この3つを確認するだけでいいんです。始めることが、すべてのスタートです。",
    "ライフアセットオフィスでは、ファイナンシャルプランナーによる無料相談を受け付けています。岡山、そしてオンラインにも対応しています。お金の不安、一緒に解消しましょう。"
]

async def generate():
    results = []
    for i, text in enumerate(narrations):
        print(f"生成中 [{i+1}/{len(narrations)}]: {text[:30]}...")
        communicate = edge_tts.Communicate(text, VOICE, rate="-5%", pitch="+0Hz")
        chunks = []
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                chunks.append(chunk["data"])
        audio_bytes = b"".join(chunks)
        b64 = base64.b64encode(audio_bytes).decode("utf-8")
        results.append(b64)
        print(f"  完了 ({len(audio_bytes):,} bytes)")

    with open("/home/user/life-asset-okayama/tools/tts_audio.json", "w") as f:
        json.dump(results, f)
    print(f"\n完了！{len(results)}件の音声ファイルを生成しました。")

asyncio.run(generate())

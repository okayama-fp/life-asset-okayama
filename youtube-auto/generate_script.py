"""Claude API で「金持ちの習慣」台本を自動生成する。"""
import json
import anthropic
from config import ANTHROPIC_API_KEY


SYSTEM_PROMPT = """あなたはYouTube動画の台本ライターです。
「金持ちの習慣」をテーマに、視聴者を引き込む短い動画台本を作成します。

以下のJSON形式で必ず返答してください:
{
  "title": "動画タイトル（30文字以内）",
  "description": "YouTube概要欄テキスト（100文字以内）",
  "scenes": [
    {
      "scene_number": 1,
      "narration": "ナレーション本文（50〜80文字）",
      "image_prompt": "DALL-E用の英語プロンプト（具体的・写実的）",
      "caption": "画面下部に表示するテロップ（20文字以内）"
    }
  ]
}

ルール:
- シーンは7〜10個
- ナレーションは自然な日本語で、聴いて分かりやすい文体
- image_prompt は必ず英語で「professional, cinematic, 4K」を含める
- 内容は実践的な富裕層の習慣（朝のルーティン・読書・投資思考など）
"""


def generate_script(topic: str = "金持ちの習慣 トップ7") -> dict:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=2048,
        system=SYSTEM_PROMPT,
        messages=[
            {"role": "user", "content": f"テーマ: {topic}\n\n台本を作成してください。"}
        ],
    )

    raw = message.content[0].text.strip()

    # JSON ブロックを抽出
    if "```json" in raw:
        raw = raw.split("```json")[1].split("```")[0].strip()
    elif "```" in raw:
        raw = raw.split("```")[1].split("```")[0].strip()

    script = json.loads(raw)
    return script


if __name__ == "__main__":
    script = generate_script()
    print(json.dumps(script, ensure_ascii=False, indent=2))

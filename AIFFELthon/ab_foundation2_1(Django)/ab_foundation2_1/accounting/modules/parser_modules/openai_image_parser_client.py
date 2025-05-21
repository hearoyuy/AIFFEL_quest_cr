"""
OpenAI Vision (GPT-4o) 로 인보이스 이미지를 분석해
프롬프트에 명시된 JSON 스키마로 추출한다.
"""
import base64, json, mimetypes
import openai
from django.conf import settings
from utils.token_counter import count_tokens, count_message_tokens
from PIL import Image
from io import BytesIO

openai.api_key = settings.OPENAI_API_KEY
DEFAULT_MODEL = "o3"             # 필요하면 인자로 덮어쓰기

def call_openai_vision(
    file_path: str,
    *,
    prompt: str,
    model: str | None = None,
    json_mode: bool = False,
    max_tokens: int = 10000,
    temperature: float = 0.2,
) -> dict:
    """
    Vision 모델 1장 → JSON 추출.
    • o3 계열(=GPT-4o) ↔ GPT-4.x 파라미터 차이를 자동 처리.
    """
    model = model or DEFAULT_MODEL

    # ── 이미지 로드 ───────────────────────────────
    mime, _ = mimetypes.guess_type(file_path)
    if not (mime and mime.startswith("image/")):
        raise ValueError("지원 형식: 이미지(JPG·PNG)만 가능")

    # ── 흑백 변환 후 base64 인코딩 ──────────────
    with Image.open(file_path) as img:
        gray = img.convert("L")
        buffer = BytesIO()
        gray.save(buffer, format="PNG")  # 흑백 이미지를 PNG로 메모리에 저장
        img_b64 = base64.b64encode(buffer.getvalue()).decode()

    messages = [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": prompt},
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime};base64,{img_b64}"
                    },
                },
            ],
        }
    ]

    # ── 공통 옵션 ────────────────────────────────
    kwargs = {"model": model, "messages": messages}

    if json_mode:                       # JSON 강제
        kwargs["response_format"] = {"type": "json_object"}

    # ── 모델별 파라미터 분기 ─────────────────────
    if model == "o3":                   # GPT-4o(o3) → max_completion_tokens, no temperature
        kwargs["max_completion_tokens"] = max_tokens
    else:                               # GPT-4.x 계열
        kwargs["max_tokens"] = max_tokens
        kwargs["temperature"] = temperature

    resp = openai.chat.completions.create(**kwargs)

    raw = resp.choices[0].message.content.strip()

    # ── 토큰 카운트 (문자열만) ─────────────────────
    tok_in = count_tokens(prompt)

    tok_out = count_tokens(json.dumps(raw, ensure_ascii=False)) \
        if isinstance(raw, (dict, list)) else count_tokens(raw)
    print(f"입력 토큰: {tok_in},  출력 토큰: {tok_out}")

    # 코드블록 마커 제거
    for tag in ("```json", "```"):
        if raw.startswith(tag):
            raw = raw[len(tag):]
        if raw.endswith("```"):
            raw = raw[:-3]


    return json.loads(raw)

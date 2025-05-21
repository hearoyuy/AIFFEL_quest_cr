import json, re, logging, os
from django.conf import settings
from openai import OpenAI
from utils.token_counter import count_tokens, count_message_tokens

logger = logging.getLogger(__name__)
client = OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL_ID = getattr(settings, "GPT_MATCH_MODEL", "o3")

def call_gpt(system: str, user: str) -> dict | None:
    messages = [
        {"role": "system", "content": system},
        {"role": "user", "content": user},
    ]
    tok_in = count_message_tokens(messages)

    params = {
        "model": MODEL_ID,
        "messages": messages,
        "timeout": 60,
    }
    if MODEL_ID == "o3":
        params["max_completion_tokens"] = 10000
    else:
        params["max_tokens"] = 10000
        params["temperature"] = 0.2

    try:
        resp = client.chat.completions.create(**params)
        content = resp.choices[0].message.content
        tok_out = count_tokens(content)
        print(f"🪙 GPT-call  prompt={tok_in}  resp={tok_out}")

        os.makedirs("logs", exist_ok=True)
        with open("logs/full_gpt_resp.json", "w", encoding="utf-8") as f:
            f.write(content)

        result = _safe_json(content)
        return result
    except Exception as e:
        logger.error("GPT 호출 실패: %s", e)
        return None

def _safe_json(raw: str):
    s = re.sub(r"```(?:json)?|```", "", raw, flags=re.I).strip()
    if "{" in s and "}" in s:
        s = s[s.find("{"): s.rfind("}") + 1]
    elif "[" in s and "]" in s:
        s = s[s.find("["): s.rfind("]") + 1]
    try:
        return json.loads(s)
    except Exception as e:
        logger.warning("JSON 파싱 실패: %s", e)
        return None

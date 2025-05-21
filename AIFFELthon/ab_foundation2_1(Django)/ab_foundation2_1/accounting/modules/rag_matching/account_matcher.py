import os, json, math
from typing import List, Dict
from django.conf import settings
from openai import OpenAI
from .vector_store import vector_store          # search([query], top_k)

# ── OpenAI 초기화 ─────────────────────────────────────────────
client   = OpenAI(api_key=settings.OPENAI_API_KEY)
MODEL_ID = getattr(settings, "GPT_MATCH_MODEL", "o3")   # gpt-4o

SYSTEM = (
    "You are a certified public accountant.\n"
    "The purchase is tagged: 'office supplies expense'.\n"
    "For each candidate GL account, assign a probability 0-100.\n"
    "Look for phrases like 'office supplies', 'input VAT', 'stationery'.\n"
    "You will receive UP TO 1000 lines in the form '<code> – <desc>'.\n"
    "Return ONLY JSON:\n"
    '{ "scores":[{"code":"XXXX","prob":NN}],'
    '  "result":{"primary":{"code":"XXXX","prob":NN},'
    '            "secondary":{"code":"XXXX","prob":NN|null}} }'
)

# ────────────────── GPT 호출 (1회로 1000줄 처리) ──────────────
def _ask_gpt(query: str, cands: List[Dict]) -> List[Dict]:
    # 설명을 자르지 않고 그대로
    cand_text = "\n".join(f"{c['code']} – {c['desc']}" for c in cands[:1000])

    messages = [
        {"role": "system", "content": SYSTEM},
        {"role": "user",
         "content": f"query: {query}\n\ncandidates:\n{cand_text}"},
    ]

    common = {
        "model": MODEL_ID,
        "messages": messages,
        "response_format": {"type": "json_object"},
        "timeout": 60,
    }
    if MODEL_ID == "o3":                       # temperature 지정 금지!
        common["max_completion_tokens"] = 2048
    else:                                      # GPT-4.x 계열
        common["max_tokens"]  = 2048
        common["temperature"] = 0

    resp     = client.chat.completions.create(**common)
    raw_json = resp.choices[0].message.content

    # ─ 디버그: 원본 JSON 저장 ────────────────────────────────
    os.makedirs("logs", exist_ok=True)
    with open("logs/full_gpt_resp.json", "w", encoding="utf-8") as f:
        f.write(raw_json)
    print("[GPT-raw] saved → logs/full_gpt_resp.json")

    # ─ JSON 파싱 & 어떤 포맷이든 scores 리스트로 정규화 ────
    try:
        data = json.loads(raw_json)
    except Exception:
        return []

    scores_raw = data.get("scores", data)       # list | dict | fallback

    if isinstance(scores_raw, list):
        return scores_raw

    if isinstance(scores_raw, dict):            # {"3100":15,…}
        return [{"code": k, "prob": v} for k, v in scores_raw.items()]

    # {"3100 – desc": 12, …}
    return [
        {"code": k.split(" –")[0].strip(), "prob": v}
        for k, v in data.items() if " – " in k
    ]

# ────────────────── 메인 엔트리 ─────────────────────────────
def match_accounts(query_sentence: str,
                   top_k: int = 1000) -> Dict:
    """
    • query_sentence : build_rag_query() 결과 문자열
    • top_k          : 벡터 후보 개수 (기본 1,000)
    """
    cands = vector_store.search([query_sentence], top_k=top_k)

    print("\n── RAG 후보 상위 10 /", len(cands), "──")
    for c in cands[:1000]:
        print(f"{c['code']:>6}  {c['prob']:>5.1f}  «{c['desc'][:60]}»")
    print("────────────────────────────────────")

    scores = _ask_gpt(query_sentence, cands)

    # GPT 실패 시 거리 기반 soft-max fallback
    if not scores:
        dists = [c["prob"] for c in cands]
        exps  = [2.71828 ** (-d) for d in dists]
        tot   = sum(exps) or 1
        scores = [
            {"code": c["code"], "prob": round(x / tot * 100)}
            for c, x in zip(cands, exps)
        ]

    scores.sort(key=lambda x: x["prob"], reverse=True)
    primary   = scores[0]
    secondary = scores[1] if len(scores) > 1 and primary["prob"] < 95 else None
    return {"primary": primary, "secondary": secondary}

# accounting/modules/parser_modules/utils.py
from datetime import datetime
import re, json
from typing import Dict, List
from django.conf import settings
from openai import OpenAI

# ── OpenAI ───────────────────────────────────────────────
client = OpenAI(api_key=settings.OPENAI_API_KEY)
KW_MODEL  = "gpt-4o-mini"
CAT_MODEL = "gpt-4o-mini"

# ── 정규식: ‘7자리↑ 금액’ & 통화 기호만 제거 ───────────────
_NUM_RE = re.compile(r"\b[0-9]{7,}([.,][0-9]+)?\b")
_CCY_RE = re.compile(r"[€$£¥₹₩]")

def _strip_big_amount(text: str) -> str:
    return _CCY_RE.sub("", _NUM_RE.sub("", text)).strip()

# ── 안전 dict 탐색 ────────────────────────────────────────
def _dig(d: Dict, *keys):
    if not isinstance(d, dict):
        return None
    for k in keys:
        v = d.get(k)
        if v not in (None, "", [], {}):
            return v
    return None

def _dig_any(obj: Dict, *keys):
    if not isinstance(obj, dict):
        return None
    for k in keys:
        v = obj.get(k)
        if v not in (None, "", [], {}):
            return v
    for v in obj.values():
        r = _dig_any(v, *keys)
        if r is not None:
            return r
    return None

# ── LLM: 키워드 추출 ─────────────────────────────────────
def _extract_keywords(text: str) -> List[str]:
    prompt = (
        "Extract 3-5 key ITEM keywords (English nouns only) and return ONLY JSON:\n"
        '{"keywords":["copy paper","stapler","coffee filter"]}\n'
        f"text: {text}"
    )
    resp = client.chat.completions.create(
        model=KW_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "json_object"},
        temperature=0,
        timeout=10,
    )
    data = json.loads(resp.choices[0].message.content)
    return data.get("keywords", [])

# ── LLM: 카테고리 문장 ───────────────────────────────────
def _make_category_sentence(kws: List[str]) -> str:
    prompt = (
        "Given the keywords, output ONE English sentence that classifies the purchase "
        "into an accounting expense category (e.g., Office supplies expense). "
        "Return ONLY the sentence.\n"
        f"keywords: {', '.join(kws)}"
    )
    resp = client.chat.completions.create(
        model=CAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        response_format={"type": "text"},
        temperature=0,
        timeout=10,
    )
    return resp.choices[0].message.content.strip()

# ── 메인 ────────────────────────────────────────────────
def build_rag_query(parsed: Dict) -> str:
    """Invoice 파싱 결과 → RAG 검색용 단일 문장"""
    inv   = parsed.get("invoice", {})
    ent   = parsed.get("entity", {})
    items = parsed.get("article", [])

    # 1) 헤더
    seller = (_dig(ent, "seller_name", "company_name", "name", "cp_name")
              or _dig_any(parsed, "seller", "supplier", "vendor")
              or "Unknown seller")
    raw_dt = (_dig(inv, "invoice_date", "date", "issuance_date")
              or _dig_any(parsed, "invoice_date", "date", "issued") or "")
    try:
        dt = datetime.strptime(raw_dt[:10], "%Y-%m-%d").strftime("%d %b %Y")
    except Exception:
        dt = raw_dt
    header = f"{seller} invoice dated {dt}.".strip()

    # 2) 품목 요약 (단가·통화 포함)
    currency = (_dig(inv, "currency", "cur") or "EUR").strip()
    segs = []
    for r in items:
        qty   = str(_dig(r, "quantity", "qty") or "")
        desc  = str(_dig(r, "article_name", "description", "item_name", "name") or "")
        price = str(_dig(r, "unit_price", "price", "amount") or "")
        if desc:
            seg = " ".join(filter(None, [qty, "of", desc]))
            if price:
                seg += f" at {price} {currency} each"
            segs.append(seg)
    body = " ; ".join(segs)

    # 3) 합계 + VAT
    total = _dig(inv, "grand_total", "total_due", "total") or ""
    tail  = f"Total {total} {currency}." if total else ""
    vat   = _dig(inv, "vat_amount", "tax_amount") or ""
    if vat:
        tail += f" VAT {vat} {currency}."

    # 4) 금액 제거 후 LLM 태그
    base_sent = _strip_big_amount(" ".join(filter(None, [header, body, tail])))
    kws       = _extract_keywords(base_sent)
    cat_sent  = _make_category_sentence(kws)

    return " ".join(filter(None, [base_sent, cat_sent]))

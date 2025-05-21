from accounting.modules.parser_modules.gpt_client import call_gpt # 실제 환경에서는 이 줄을 사용하세요.

import json
import logging
import re  # query_sentence 파싱을 위해 re 모듈 추가
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)


# --- query_sentence 파싱을 위한 헬퍼 함수들 ---
def _parse_vat_rate_from_query(query_sentence: str) -> Optional[float]:
    # query_sentence 구조: "... | Total ... VAT ... (VAT_RATE%) | ..."
    # 또는 라인 아이템 "... VAT RATE% | ..."
    # 가장 확실한 헤더의 VAT 비율을 먼저 찾습니다.
    match_header = re.search(r"Total [^\|]+ VAT [^\|]+ \(([\d\.]+)\s*%\)", query_sentence, re.IGNORECASE)
    if match_header:
        try:
            return float(match_header.group(1)) / 100.0
        except ValueError:
            pass

    # 헤더에서 못 찾으면 라인 아이템에서 찾아봅니다 (첫 번째 라인 아이템의 VAT를 대표로 가정).
    # build_query_sentence 구조상 라인아이템은 뒤쪽에 위치합니다.
    parts = query_sentence.split(" | ")
    for part in reversed(parts):  # 뒤에서부터 탐색
        match_line = re.search(r"VAT\s+([\d\.]+)\s*%", part, re.IGNORECASE)
        if match_line:
            try:
                # 이 VAT가 전체 VAT rate인지, 라인 아이템 특정 VAT rate인지 구분 필요
                # 여기서는 일단 찾으면 반환
                return float(match_line.group(1)) / 100.0  # 0.19% 와 같은 경우를 위해 /100은 보류.
                # build_query_sentence에서 % 앞의 숫자가 실제 비율(0.19)인지,
                # 백분율 숫자(19)인지 확인 필요.
                # 현재 build_query_sentence는 (doc.get('vat_rate') or 'n/a'}%) 이므로 0.19와 같은 소수점 비율.
                # 라인 아이템은 {it.get('vat_rate') or doc.get('vat_rate') or '-'}% 이므로 이것도 소수점 비율.
                # 따라서 /100 하지 않음. -> 다시 확인: (0.19%) 이므로 0.19가 맞음. %가 붙으면 19가 되어야 함.
                # build_query_sentence는 vat_rate를 그대로 넣으므로 0.19. GPT 프롬프트에서는 19%로 변환.
                # 여기서는 float(0.19)를 반환하는 것이 맞음.
                raw_rate_str = match_line.group(1)
                # "0.19" 같은 문자열을 float 0.19로 변환
                return float(raw_rate_str)

            except ValueError:
                pass
    return None


def _parse_line_items_from_query(query_sentence: str) -> List[Dict[str, Any]]:
    items = []
    parts = query_sentence.split(" | ")
    # build_query_sentence 구조상 라인 아이템은 특정 포맷을 가짐
    # 예: "HP EliteBook Laptop, 5 × 1270.0 EUR VAT 0.19%"
    for part in parts:
        # 정규식: 설명, 수량, 단가 추출 시도
        # (desc), (qty) × (price) CURRENCY VAT RATE%
        # 좀 더 견고한 정규식이 필요할 수 있습니다.
        m = re.match(r"^(?P<desc>.+?),\s*(?P<qty>[\d\.]+)\s*[xX×]\s*(?P<price>[\d\.]+)\s*([A-Z]{3})?\s*(VAT.*)?$",
                     part.strip())
        if m:
            item_data = m.groupdict()
            items.append({
                "article_description": item_data["desc"].strip(),
                "quantity": item_data.get("qty"),
                "unit_price": item_data.get("price"),
                # "amount"는 query_sentence에서 직접 추출하기 어려움 (qty*price로 계산 가능)
            })
    return items


def _parse_currency_from_query(query_sentence: str) -> Optional[str]:
    # query_sentence 구조: "... | Total NET_AMOUNT CURRENCY VAT ... | ..."
    match = re.search(r"Total\s+[\d\.]+\s+([A-Z]{3})\s+VAT", query_sentence, re.IGNORECASE)
    if match:
        return match.group(1).upper()

    # 라인 아이템에서도 찾아볼 수 있음
    parts = query_sentence.split(" | ")
    for part in parts:
        m = re.search(r"[\d\.]+\s+([A-Z]{3})\s+VAT", part, re.IGNORECASE)
        if m:
            return m.group(1).upper()
    return None


def _parse_doc_type_hint_from_query(query_sentence: str) -> Optional[str]:
    # build_query_sentence는 "Invoice INV_NO dated ..." 와 같이 시작
    if "invoice" in query_sentence.lower():  # 매우 기본적인 힌트
        return "Invoice"
    # "Debit Note" 등의 정보는 build_query_sentence 결과에 명시적으로 포함되지 않음
    return None


# --- 헬퍼 함수 끝 ---


def match_accounts(
        query_sentence: str,
        cand_rows: List[Dict[str, Any]]
) -> Dict[str, Optional[Dict[str, Any]]]:
    """
    query_sentence와 cand_rows를 입력으로 받아 GPT를 호출하여 계정을 매칭합니다.
    GPT가 각 추천 계정의 코드와 신뢰도 점수를 반환하도록 요청합니다.
    """

    doc_label = None
    doc_group = None
    doc_vat_rate = _parse_vat_rate_from_query(query_sentence)
    doc_line_items = _parse_line_items_from_query(query_sentence)
    doc_type = _parse_doc_type_hint_from_query(query_sentence)
    currency = _parse_currency_from_query(query_sentence)

    logger.info(
        f"Parsed from query_sentence for GPT: VAT Rate={doc_vat_rate}, Items Count={len(doc_line_items)}, Currency={currency}, DocType Hint={doc_type}")

    # GPT 프롬프트 수정: 신뢰도(confidence) 점수 요청 추가
    system_prompt = """
You are an expert AI accounting assistant. Your task is to analyze invoice data and a list of candidate Chart of Account (COA) entries, then select the three most appropriate COA entries for journalizing the invoice. These three accounts should represent the main expense/revenue (primary), VAT/tax (secondary), and payable/receivable (tertiary) aspects of the transaction.

I will provide:
1.  **Invoice Details**: Key information extracted from an invoice summary string.
2.  **Candidate COA Entries**: A list of available COA entries (code, desc, category).

Your response MUST be a JSON object with three keys: "primary", "secondary", and "tertiary".
-   Each key should correspond to an object containing:
    -   "code": The 'code' (string) of the selected candidate COA entry.
    -   "confidence": Your confidence score (integer, 0-100) for this specific selection.
-   If you cannot find a suitable match for a role (e.g., no VAT is applicable or found), the value for that role's key (e.g., "secondary") should be `null`.

Example of desired JSON output:
{
    "primary": {"code": "6815", "confidence": 95},
    "secondary": {"code": "1406", "confidence": 90},
    "tertiary": null
}

Selection Guidelines:
-   **Primary Account**: Main expense/revenue. Base this on line item descriptions if an overall label is not provided.
-   **Secondary Account (VAT/Tax)**: Related to VAT. If a VAT rate is specified, find a corresponding VAT account. If no VAT or no suitable account, this role should be `null`.
-   **Tertiary Account (Payable/Receivable)**: Contra-account. 'Accounts Payable' for purchases, 'Accounts Receivable' for sales.

General Instructions:
-   Analyze all provided details carefully.
-   Return ONLY the JSON object as specified. No other text or markdown.
"""

    invoice_details_parts = []
    invoice_details_parts.append(f"- Overall Label: {doc_label if doc_label else 'Not directly available'}")
    invoice_details_parts.append(f"- Overall Group/Category: {doc_group if doc_group else 'Not directly available'}")
    if doc_type: invoice_details_parts.append(f"- Document Type Hint: {doc_type}")
    if doc_vat_rate is not None:
        invoice_details_parts.append(f"- VAT Rate: {doc_vat_rate * 100:.2f}%")  # GPT에게는 %로 변환된 값 전달
    if currency: invoice_details_parts.append(f"- Currency: {currency}")

    if doc_line_items:
        invoice_details_parts.append("- Line Items (parsed from summary):")
        for i, item in enumerate(doc_line_items[:5]):
            desc = item.get('article_description', 'N/A')
            qty = item.get('quantity', 'N/A')
            price = item.get('unit_price', 'N/A')
            invoice_details_parts.append(
                f"  - Item {i + 1}: Description: '{desc}', Quantity: {qty}, Unit Price: {price}")
        if len(doc_line_items) > 5:
            invoice_details_parts.append(f"  - ... and {len(doc_line_items) - 5} more line items.")
    else:
        invoice_details_parts.append("- Line Items: Could not be reliably parsed or none were present.")

    invoice_details_str = "\n".join(invoice_details_parts)

    cand_rows_for_prompt = [{"code": r.get("code"), "desc": r.get("desc"), "category": r.get("category")} for r in
                            cand_rows]
    cand_rows_str = json.dumps(cand_rows_for_prompt, indent=2, ensure_ascii=False)

    user_prompt = f"""
Invoice Details (parsed from a summary sentence):
{invoice_details_str}

Full Invoice Summary Sentence (for context):
"{query_sentence}"

Candidate Chart of Account Entries:
{cand_rows_str}

Based on these details, select the most appropriate primary, secondary, and tertiary accounts. For each, provide its 'code' and your 'confidence' score (0-100).
Return your answer strictly in the JSON format specified in the system instructions.
"""
    logger.debug("--- GPT System Prompt (match_accounts with prob) ---\n%s", system_prompt)
    logger.debug("--- GPT User Prompt (match_accounts with prob) ---\n%s", user_prompt)

    gpt_response_dict = call_gpt(system_prompt, user_prompt)

    final_match_result = {
        "primary": None,
        "secondary": None,
        "tertiary": None
    }

    if gpt_response_dict and isinstance(gpt_response_dict, dict):
        cand_map = {str(row["code"]): row for row in cand_rows if "code" in row}

        for role in ["primary", "secondary", "tertiary"]:
            selection = gpt_response_dict.get(role)
            if selection and isinstance(selection, dict):
                code = selection.get("code")
                confidence = selection.get("confidence")

                if code and str(code) in cand_map:
                    # 원본 cand_row 데이터를 복사하여 prob 키 추가
                    account_data = cand_map[str(code)].copy()
                    # confidence가 정수형인지 확인, 아니면 기본값(예: 0 또는 None) 설정
                    account_data["prob"] = int(confidence) if isinstance(confidence, (int, float)) else None
                    final_match_result[role] = account_data
                    logger.info(
                        f"GPT suggested for {role}: Code={code}, Confidence={confidence}. Matched to: {account_data}")
                elif code:
                    logger.warning(
                        f"{role.capitalize()} code '{code}' (Confidence: {confidence}) suggested by GPT not found in candidate rows.")
            elif selection is not None:  # null이 아닌데 dict 형태가 아닐 경우
                logger.warning(
                    f"GPT response for '{role}' was not in the expected format (object with code and confidence): {selection}")
    else:
        logger.error(f"Failed to get a valid structured JSON response from GPT. Response: %s",
                     str(gpt_response_dict)[:500])

    return final_match_result
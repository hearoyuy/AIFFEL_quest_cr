import os, json
import re
import time  # 시간 측정을 위해 time 모듈 임포트
import django
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.views.decorators.http import require_POST
from django.template.loader import render_to_string

from accounting.models import UploadedFile
from accounting.modules.parser_modules.invoice_parser import InvoiceParser
from accounting.models.coa_classification import COAClassification
from django.db.models import F
from accounting.models.coa import ChartOfAccount
import pprint, logging
from accounting.modules.parser_modules.gpt_matching import match_accounts
from typing import Dict, List, Tuple, Optional, Any
from django_countries import countries as django_countries_db
from django.db.models import Subquery, OuterRef, CharField
from accounting.modules.parser_modules.invoice_data_saver import save_parsed_invoice_data

logger = logging.getLogger(__name__)


# ───────────────────────── 메인 화면 ─────────────────────────
@login_required
def parser_view(request):
    unprocessed = (UploadedFile.objects
                   .filter(uploaded_by=request.user, is_processed=False)
                   .order_by("-uploaded_at"))
    return render(request, "accounting/parser.html",
                  {"unprocessed_files": unprocessed})


countries_tuple: Tuple[Tuple[str, str], ...] = tuple(django_countries_db)


# _guess_country 함수 (이전과 동일)
def _guess_country(parsed: Dict) -> Optional[str]:
    vat_no_issuer = parsed.get("issuer", {}).get("vat_no", "") or ""
    vat_no_receiver = parsed.get("receiver", {}).get("vat_no", "") or ""
    vat_no_to_check = ""
    if vat_no_issuer and re.match(r"^[A-Z]{2}", vat_no_issuer.strip()):
        vat_no_to_check = vat_no_issuer.strip()
    elif vat_no_receiver and re.match(r"^[A-Z]{2}", vat_no_receiver.strip()):
        vat_no_to_check = vat_no_receiver.strip()

    if vat_no_to_check:
        iso = vat_no_to_check[:2].upper()
        return dict(countries_tuple).get(iso, iso)

    addr_issuer = parsed.get("issuer", {}).get("address", "") or ""
    addr_receiver = parsed.get("receiver", {}).get("address", "") or ""
    full_address = f"{addr_issuer} {addr_receiver}".lower()
    for code, name in countries_tuple:
        if name and name.lower() in full_address:
            return name
    return None


# build_query_sentence 함수 (이전과 동일)
def build_query_sentence(parsed: Dict) -> str:
    doc = parsed.get("transaction_document", {})
    issuer = parsed.get("issuer", {})
    receiver = parsed.get("receiver", {})
    items: List[Dict] = parsed.get("transaction_line_items", [])
    main_partner_role = parsed.get("main_trading_partner_role")
    partner_obj = {}
    partner_label = "Trading Partner (Undetermined)"

    if main_partner_role == "issuer":
        partner_obj = issuer
        partner_label = "Trading Partner (Issuer/Supplier)"
    elif main_partner_role == "receiver":
        partner_obj = receiver
        partner_label = "Trading Partner (Receiver/Customer)"
    else:
        partner_obj = receiver
        partner_label = f"Trading Partner (Receiver - Role: {main_partner_role or 'Default'})"

    country = partner_obj.get("country")
    if not country and isinstance(receiver, dict): country = receiver.get("country")
    if not country: country = _guess_country(parsed)

    parts = [
        f"{partner_label}: {partner_obj.get('name', 'N/A')} (VAT: {partner_obj.get('vat_no', 'N/A')})",
        f"Invoice {doc.get('invoice_no', 'N/A')} dated {doc.get('issuance_date', 'N/A')}",
        f"Total {doc.get('net_amount', 'N/A')} {doc.get('currency', '')} VAT {doc.get('vat_amount', 'N/A')} ({doc.get('vat_rate', 'N/A')}%)",
        f"Country: {country or 'N/A'}",
    ]
    for it in items:
        desc = it.get("article_description") or it.get("article_name") or ""
        parts.append(
            f"{desc}, qty: {it.get('quantity', 'N/A')} × unit_price: {it.get('unit_price', 'N/A')} {doc.get('currency', '')} VAT {it.get('vat_rate') or doc.get('vat_rate') or '-'}%"
        )
    return " | ".join(filter(None, parts))


@require_POST
@login_required
def parse_invoice_view(request):
    file_id = request.POST.get("file_id")
    if not file_id: return JsonResponse({"error": "파일 선택이 필요합니다."}, status=400)
    uf = get_object_or_404(UploadedFile, id=file_id, uploaded_by=request.user)
    original_filepath = uf.original_filepath.path
    new_filepath = uf.new_filepath.path
    if not os.path.exists(new_filepath):
        logger.error(f"File not found at path: {new_filepath} for UploadedFile ID: {uf.id}")
        raise Http404("변환 이미지가 서버에 존재하지 않습니다.")
    coa_rows = list(COAClassification.objects.values("code", "group", "label"))

    parsed_data_for_template: Dict[str, Any] = {}
    view_debug_info: Dict[str, Any] = {}

    total_analysis_time_taken = 0.0
    analysis_duration_parser_val = "N/A"
    analysis_duration_matching_val = "N/A" # 이 변수는 matching_duration_str로 대체될 수 있음
    match = {} # match 변수 초기화

    try:
        parser_start_time = time.perf_counter()
        parser = InvoiceParser(extra_json={"coa_classifications": coa_rows})
        parser_output = parser.parse(original_filepath, new_filepath) #1차 파싱
        parser_end_time = time.perf_counter()
        parser_duration = parser_end_time - parser_start_time
        total_analysis_time_taken += parser_duration
        analysis_duration_parser_val = f"{parser_duration:.2f}"

        parsed_data_for_template = parser_output.get("parsed_data", {})
        parser_internal_debug_messages = parser_output.get("debug_messages", {})
        view_debug_info.update(parser_internal_debug_messages)

        line_items_list = parsed_data_for_template.get("transaction_line_items", [])
        if isinstance(line_items_list, list):
            for li in line_items_list:
                if not isinstance(li, dict): continue
                if not li.get("article_description"):
                    li["article_description"] = li.get("article_name") or ""
                # 'net_amount'를 'amount'로 복사하는 로직은 OUTPUT_SCHEMA 준수 및 additional_data 활용에 따라 제거 또는 수정 가능
                # 현재는 LLM이 amount를 채우고, net_amount를 additional_data로 넣도록 유도하므로 아래 로직은 불필요할 수 있음
                # if "net_amount" not in li and "amount" in li:
                #     li["net_amount"] = li.get("amount", 0)
                # elif "amount" not in li and "net_amount" in li:
                #     li["amount"] = li.get("net_amount", 0)

        parsed_codes_data = parsed_data_for_template.get("codes", [])
        codes = []
        if isinstance(parsed_codes_data, list):
            for item in parsed_codes_data:
                if isinstance(item, dict) and item.get("code"): # 이전 형식 대비
                    codes.append(item.get("code"))
                elif isinstance(item, str): # 프롬프트 수정 후 기대 형식
                    codes.append(item)
        codes = codes[:3] # 최대 3개

        cand_rows_qs = ChartOfAccount.objects.filter(activation=True)
        if codes: cand_rows_qs = cand_rows_qs.filter(coa_classification__code__in=codes)
        cand_rows = list(cand_rows_qs.values("code", desc=F("desc_long_en"), category=F("coa_classification__group")))

        query_sentence = build_query_sentence(parsed_data_for_template)

        matching_start_time = time.perf_counter()
        match = match_accounts(query_sentence, cand_rows) # match 변수 할당
        matching_end_time = time.perf_counter()
        matching_duration = matching_end_time - matching_start_time
        total_analysis_time_taken += matching_duration
        analysis_duration_matching_val = f"{matching_duration:.2f}" # 수정: matching_duration_str 대신 사용
        view_debug_info["matching_duration_seconds"] = analysis_duration_matching_val


        for k_match in ("primary", "secondary", "tertiary"):
            item_match = match.get(k_match) # item -> item_match로 변경 (컨텍스트 변수 line_items의 item과 구분)
            if not item_match or not item_match.get("code"): continue
            coa = ChartOfAccount.objects.filter(code=str(item_match["code"])).only("desc_long_en").first()
            if coa: item_match["desc"] = coa.desc_long_en

    except Exception as e:
        logger.error("Error in parse_invoice_view: %s", e, exc_info=True)
        if "parser_end_time" not in locals() and "parser_start_time" in locals():
            parser_end_time = time.perf_counter()
            total_analysis_time_taken = parser_end_time - parser_start_time
        # matching_duration_val이 아니라 analysis_duration_matching_val를 사용하거나, matching_duration을 직접 사용
        # analysis_duration_matching_val = f"{matching_duration:.2f}" # 에러 시 matching_duration이 없을 수 있음

        view_debug_info["view_level_exception"] = str(e)
        view_debug_info["view_level_exception_type"] = type(e).__name__
        parsed_data_for_template.setdefault("transaction_document", {}).setdefault("cp_memo", f"View Error: {str(e)}")

    analysis_duration_total_val = f"{total_analysis_time_taken:.2f}" if total_analysis_time_taken > 0 else "N/A"

    # line_items 중 additional_data가 있는 항목만 필터링하여 템플릿에 전달
    line_items_with_additional_data = []
    for item in parsed_data_for_template.get("transaction_line_items", []):
        if isinstance(item, dict) and item.get("additional_data"):
            line_items_with_additional_data.append({
                "line_item_id": item.get("line_item_id"),
                "article_name": item.get("article_name"),
                "additional_data": item.get("additional_data")
            })

    transaction_doc, duplicate_reason = save_parsed_invoice_data(uf, parsed_data_for_template, match)

    if transaction_doc is None:
        if duplicate_reason:
            if isinstance(duplicate_reason, list):
                reason_str = "<br>".join(duplicate_reason)
            else:
                reason_str = str(duplicate_reason)
            save_status = "중복된 인보이스로 저장이 되지 않았습니다.<br>" \
                          f"<span style='font-size:0.97em; color:#b38a00;'>중복 사유:<br>{reason_str}</span>"
        else:
            save_status = "저장 실패(원인 불명)"
        save_result = "duplicate"
    else:
        save_status = "인보이스가 정상적으로 저장되었습니다."
        save_result = "success"

    context = {
        "doc": parsed_data_for_template.get("transaction_document", {}),
        "issuer": parsed_data_for_template.get("issuer", {}),
        "receiver": parsed_data_for_template.get("receiver", {}),
        "main_trading_partner_role": parsed_data_for_template.get("main_trading_partner_role"),
        "line_items": parsed_data_for_template.get("transaction_line_items", []),
        "codes": codes, # 정제된 codes 리스트 사용
        "match": match, # 초기화된 match 사용
        "parsed_data_json": json.dumps(parsed_data_for_template, indent=2, ensure_ascii=False),
        "analysis_duration_parser": analysis_duration_parser_val,
        "analysis_duration_matching": analysis_duration_matching_val, # 일관된 변수명 사용
        "analysis_duration_total": analysis_duration_total_val,
        "cand_rows": cand_rows if 'cand_rows' in locals() else [], # cand_rows가 정의되지 않았을 경우 대비
        "debug_info": view_debug_info,
        "line_items_with_additional_data": line_items_with_additional_data, # 새로 추가
        "save_status": save_status,  # 여기 추가!
        "save_result": save_result,
    }

    html_snippet = render_to_string("accounting/_invoice_result.html", context, request=request)
    return HttpResponse(html_snippet)


# FIELD_MAP, _dig, find_key, _flatten 함수 (이전과 동일)
FIELD_MAP: dict[str, tuple[str, ...]] = {
    "invoice_number": ("transaction_document.invoice_no",),
    "date": ("transaction_document.issuance_date",),
    "company_name": ("receiver.name",),
    "company_address": ("receiver.address",),
    "billing_name": ("receiver.contact_person_name",),
    "billing_addr": ("receiver.address",),
    "items": ("transaction_line_items",),
    "subtotal": ("transaction_document.net_amount",),
    "tax_rate": ("transaction_document.vat_rate",),
    "tax_amount": ("transaction_document.vat_amount",),
    "total_due": ("transaction_document.total_due",),
    "bank": ("receiver.bank_name",),
    "iban": ("receiver.bank_iban",),
    "bic": ("receiver.bank_bic",),
}


def _dig(obj: dict, path):
    if isinstance(path, (list, tuple)):
        for p in path:
            val = _dig(obj, p)
            if val not in (None, "", [], {}): return val
        return None
    cur = obj
    for key in path.split("."):
        if not isinstance(cur, dict): return None
        cur = cur.get(key)
        if cur is None: return None
    return cur


def find_key(obj, key):
    if not isinstance(obj, dict): return None
    if key in obj: return obj[key]
    for v in obj.values():
        if isinstance(v, dict):
            res = find_key(v, key)
            if res is not None: return res
    return None


def _flatten(src: Dict) -> Dict:
    flat_dict = {}
    for k, paths in FIELD_MAP.items():
        value = _dig(src, paths)
        flat_dict[k] = value
    return flat_dict
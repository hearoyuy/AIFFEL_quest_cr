# accounting/modules/parser_modules/invoice_parser.py

from __future__ import annotations
import json
import re
import logging
import pprint
from typing import Dict, Any, Optional, List
from django.conf import settings

log = logging.getLogger(__name__)

# OpenAI API 클라이언트 (실제 파일에서 임포트)
try:
    from .openai_file_parser_client import call_openai_vision_or_file
except ImportError:
    log.warning("openai_file_parser_client not found. Mocking will be attempted in __main__ if run directly.")


    def call_openai_vision_or_file(*args, **kwargs):
        raise NotImplementedError("call_openai_vision_or_file is not available")

try:
    from .openai_image_parser_client import call_openai_vision
except ImportError:
    log.warning("openai_image_parser_client not found. Mocking will be attempted in __main__ if run directly.")


    def call_openai_vision(*args, **kwargs):
        raise NotImplementedError("call_openai_vision is not available")

import os


class BaseParser:
    def validate(self, data: dict) -> dict:
        date_fields = ["issuance_date", "service_date", "delivery_date", "due_date"]
        for field in date_fields:
            if field in data and data.get(field) and not re.match(r"^\d{4}-\d{2}-\d{2}$", str(data[field])):
                log.warning(f"Invalid {field} format: {data[field]}. Expected YYYY-MM-DD.")
        return data


OUTPUT_SCHEMA = (
    "{\n"
    "  \"transaction_document\": {\n"
    "    \"tran_doc_id\": null,\n"
    "    \"document_type\": null,\n"
    "    \"invoice_no\": null,\n"
    "    \"reference_no\": null,\n"
    "    \"internal_order_no\": null,\n"
    "    \"external_order_no\": null,\n"
    "    \"issuance_date\": null, /* Format:YYYY-MM-DD */\n"
    "    \"service_date\": null, /* Format:YYYY-MM-DD */\n"
    "    \"delivery_date\": null, /* Format:YYYY-MM-DD */\n"
    "    \"cp_memo\": null,\n"
    "    \"payment_terms\": null,\n"
    "    \"due_date\": null, /* Format:YYYY-MM-DD */\n"
    "    \"currency\": null,\n"
    "    \"net_amount\": null,\n"
    "    \"vat_amount\": null,\n"
    "    \"vat_rate\": null, /* Example: For 7% VAT, return 7.0 or 7.00 */\n"
    "    \"total_due\": null,\n"
    "    \"prepayment\": false,\n"
    "    \"prepaid_amount\": null,\n"
    "    \"price_discount\": null,\n"
    "    \"price_discount_terms\": null,\n"
    "    \"transaction_summary\": null,\n"
    "    \"anomaly_memo\": null,\n"
    "    \"additional_data\": {}\n"
    "  },\n"
    "  \"issuer\": {\n"
    "    \"name\": null,\n"
    "    \"regi_no\": null,\n"
    "    \"vat_no\": null,\n"
    "    \"tax_no\": null,\n"
    "    \"address\": null,\n"
    "    \"postcode\": null,\n"
    "    \"country\": null,\n"
    "    \"phone\": null,\n"
    "    \"email\": null,\n"
    "    \"contact_person_name\": null,\n"
    "    \"contact_person_phone\": null,\n"
    "    \"contact_person_email\": null,\n"
    "    \"bank_name\": null,\n"
    "    \"bank_address\": null,\n"
    "    \"bank_account_no\": null,\n"
    "    \"bank_iban\": null,\n"
    "    \"bank_bic\": null,\n"
    "    \"bank_owner\": null,\n"
    "    \"additional_data\": {}\n"
    "  },\n"
    "  \"receiver\": {\n"
    "    \"name\": null,\n"
    "    \"regi_no\": null,\n"
    "    \"vat_no\": null,\n"
    "    \"tax_no\": null,\n"
    "    \"address\": null,\n"
    "    \"postcode\": null,\n"
    "    \"country\": null,\n"
    "    \"phone\": null,\n"
    "    \"email\": null,\n"
    "    \"contact_person_name\": null,\n"
    "    \"contact_person_phone\": null,\n"
    "    \"contact_person_email\": null,\n"
    "    \"bank_name\": null,\n"
    "    \"bank_address\": null,\n"
    "    \"bank_account_no\": null,\n"
    "    \"bank_iban\": null,\n"
    "    \"bank_bic\": null,\n"
    "    \"bank_owner\": null,\n"
    "    \"additional_data\": {}\n"
    "  },\n"
    "  \"main_trading_partner_role\": null,\n"
    "  \"transaction_line_items\": [\n"
    "    {\n"
    "      \"line_item_id\": null,\n"
    "      \"article_no\": null,\n"
    "      \"article_name\": null,\n"
    "      \"article_description\": null,\n"
    "      \"quantity\": null,\n"
    "      \"unit_price\": null,\n"
    "      \"amount\": null,\n"
    "      \"additional_data\": {}\n"
    "    }\n"
    "  ],\n"
    "  \"codes\": [],\n"
    "  \"group\": null,\n"
    "  \"label\": null\n"
    "}"
)

our_company_settings_name = settings.OUR_COMPANY_INFO.get("name")

COMMAND_PROMPT: str = (
    f"You are an invoice parser for {our_company_settings_name}.\n"
    "Your SOLE task is to return a JSON object based on the provided invoice text.\n"
    "Strictly follow the Output Schema Structure and all field definitions below.\n"
    "Use null for missing or unrecognized values.\n"
    "**All date fields (issuance_date, service_date, delivery_date, due_date) MUST be in 'YYYY-MM-DD' format.** For example, 'May 14, 2025' should be '2025-05-14'. If year is missing, assume current year (2025). If conversion is impossible, use null.\n"
    "If you find relevant data in the invoice that does not fit into a predefined schema field for `transaction_document`, `issuer`, `receiver`, or a `transaction_line_item`, "
    "place that extra data as a key-value pair within the `additional_data` object of the respective parent object.\n"
    "ONLY output the JSON. NO other text, comments, or explanations outside the specified `cp_memo` and `anomaly_memo` fields.\n"
    "\n"
    "Output Schema Structure:\n"  # (스키마 정의는 이전과 동일)
    "{\n"
    "  \"transaction_document\": { /* All keys MUST be present. See details below. */ },\n"
    "  \"issuer\": { /* All keys MUST be present. See details below. */ },\n"
    "  \"receiver\": { /* All keys MUST be present. See details below. */ },\n"
    "  \"main_trading_partner_role\": \"[ 'issuer' or 'receiver' or null ]\",\n"
    "  \"transaction_line_items\": [ /* Array of objects. Each item MUST contain all specified keys. See details below. */ ],\n"
    "  \"codes\": [], /* Array of EXACTLY 3 STRING codes like \"PL_X_Y\". Example: [\"PL_3_11\", \"FP_1_10\", \"FP_4_10\"]. DO NOT use objects here. */\n"
    "  \"group\": null, /* The 'group' from COA for the FIRST code in the \"codes\" array. */\n"
    "  \"label\": null  /* The 'label' from COA for the FIRST code in the \"codes\" array. */\n"
    "}\n"
    "\n"
    "'transaction_document' object structure:\n"  # (세부 구조 정의는 이전과 동일)
    "{\n"
    "  \"tran_doc_id\": null, \"document_type\": null, \"invoice_no\": null, \"reference_no\": null,\n"
    "  \"internal_order_no\": null, \"external_order_no\": null, \"issuance_date\": null, /* Date format:YYYY-MM-DD */\n"
    "  \"service_date\": null, /* Date format:YYYY-MM-DD */\n"
    "  \"delivery_date\": null, /* Date format:YYYY-MM-DD */\n"
    f"  \"cp_memo\": null, /* MANDATORY: Reason for 'main_trading_partner_role' from {our_company_settings_name}'s view. Example: \"Role 'issuer': {our_company_settings_name} is receiver (purchase invoice).\" */\n"
    "  \"payment_terms\": null, \"due_date\": null, /* Date format:YYYY-MM-DD */\n"
    "  \"currency\": null, \"net_amount\": null,\n"
    "  \"vat_amount\": null, \"vat_rate\": null, /* For 7% VAT, return 7.0 or 7.00. NOT 0.07 */\n"
    "  \"total_due\": null, \"prepayment\": false, /* Default to false if not specified */\n"
    "  \"prepaid_amount\": null, \"price_discount\": null, \"price_discount_terms\": null,\n"
    "  \"transaction_summary\": null, /* Brief one-sentence summary. */\n"
    "  \"anomaly_memo\": null, /* CRITICAL: Document line item auto-corrections. Format: 'Line Item Amount Auto-Correction: Item \"[name/id]\" amount changed from [original] to [corrected] (Qty:[Q], UnitPrice:[UP]).'. Null if no corrections/anomalies. */\n"
    "  \"additional_data\": {} /* For any other relevant document-level data not in schema. Key-value pairs. */\n"
    "}\n"
    "\n"
    "'issuer' AND 'receiver' object structure (use for both):\n"  # (세부 구조 정의는 이전과 동일)
    "{\n"
    "  \"name\": null, \"regi_no\": null, \"vat_no\": null, \"tax_no\": null, \"address\": null,\n"
    "  \"postcode\": null, \"country\": null, \"phone\": null, \"email\": null,\n"
    "  \"contact_person_name\": null, \"contact_person_phone\": null, \"contact_person_email\": null,\n"
    "  \"bank_name\": null, \"bank_address\": null, \"bank_account_no\": null, \"bank_iban\": null,\n"
    "  \"bank_bic\": null, \"bank_owner\": null,\n"
    "  \"additional_data\": {} /* For any other relevant issuer/receiver data not in schema. Key-value pairs. */\n"
    "}\n"
    "\n"
    "Structure for EACH object in 'transaction_line_items' array:\n"  # (세부 구조 정의는 이전과 동일)
    "{\n"
    "  \"line_item_id\": null,\n"
    "  \"article_no\": null,\n"
    "  \"article_name\": null,\n"
    "  \"article_description\": null,\n"
    "  \"quantity\": null,\n"
    "  \"unit_price\": null,\n"
    "  \"amount\": null, /* This is the primary total for the line item. */\n"
    "  \"additional_data\": {} /* For any other relevant line-item-specific data not in schema (e.g., if a separate 'net_amount' or 'item_discount' is found). Key-value pairs. */\n"
    "}\n"
    "\n"
    "**CRITICAL PROCESSING STEPS - FOLLOW EXACTLY:**\n"  # (처리 단계 지침은 이전과 동일)
    "\n"
    "**1. 'main_trading_partner_role' ({our_company_settings_name} is 'Our Company'):**\n"
    f"   - If \"{our_company_settings_name}\" is 'receiver': `main_trading_partner_role` = **\"issuer\"**. `cp_memo` = \"Role 'issuer': {our_company_settings_name} is receiver (purchase invoice).\"\n"
    f"   - If \"{our_company_settings_name}\" is 'issuer': `main_trading_partner_role` = **\"receiver\"**. `cp_memo` = \"Role 'receiver': {our_company_settings_name} is issuer (sales invoice).\"\n"
    "   - Else: `main_trading_partner_role` = null. `cp_memo` = \"Role for AB Foundation GmbH unclear.\"\n"
    "\n"
    "**2. 'transaction_line_items' (VALIDATE AND AUTO-CORRECT `amount` - MANDATORY):**\n"
    "   - For EACH line item:\n"
    "     - Extract `quantity` (Q), `unit_price` (UP), and original `amount` (A_orig). Treat as numbers.\n"
    "     - If Q and UP are numbers, calculate `expected_amount = Q * UP`.\n"
    "     - **Compare `expected_amount` with `A_orig`:**\n"
    "       - If `expected_amount` != `A_orig` (and A_orig is a number):\n"
    "         - Set this line item's `amount` in JSON to `expected_amount`.\n"
    "         - **ADD to `transaction_document.anomaly_memo`:** \"Line Item Amount Auto-Correction: Item '[line_item_id or article_name]' amount changed from [A_orig] to [expected_amount] (Qty:[Q], UnitPrice:[UP]).\"\n"
    "       - Else: Set `amount` to `expected_amount` (or `A_orig` if calculation not possible).\n"
    "     - If you find other relevant line item data not fitting the main keys (e.g., a distinct 'net_amount' or 'item_discount'), place it in this line item's `additional_data` object.\n"
    "\n"
    "**3. EXTRACT OTHER DATA (Follow Schema):**\n"
    "   - Populate all fields in `transaction_document`, `issuer`, `receiver` as per their structures. Use null for missing.\n"
    "   - **Dates:** Ensure `issuance_date`, `service_date`, `delivery_date`, and `due_date` are formatted as **'YYYY-MM-DD'**. If the year is ambiguous (e.g., '01.02.25'), assume the current century (e.g., for 2025, '2025-02-01'). If only day and month are present and year cannot be clearly inferred from context or other dates in the document, use null. If the original date is partial (e.g. 'May 2025') and cannot be resolved to a specific day, use null.\n"
    "   - If relevant data is found that does not fit predefined fields, place it in the `additional_data` object of the corresponding parent (`transaction_document`, `issuer`, or `receiver`).\n"
    "   - `receiver.regi_no`: Use Customer ID (e.g., \"DEABC12345\").\n"
    "   - `issuer.bank_bic`: Use BLZ (e.g., \"37040044\") if BIC not separate.\n"
    "   - `transaction_document.vat_rate`: If invoice says \"7%\", output `7.0` (number).\n"
    "   - `transaction_document.prepayment`: Default `false`.\n"
    "\n"
    "**4. SELECT COA CODES (Use provided COA list: code – group – label).**\n"
    "   - `codes` array MUST be a list of **EXACTLY 3 STRING codes** (e.g., `[\"PL_X_Y\", \"FP_A_B\", \"FP_C_D\"]`).\n"
    "   - **1st Code (Primary `PL_*`):** Based on `main_trading_partner_role` (Expense for purchase, Revenue for sale).\n"
    "   - **2nd Code (VAT `FP_*` if `vat_amount > 0`):** 'Input VAT' (purchase) or 'Output VAT' (sale).\n"
    "   - **3rd Code (Payable/Receivable `FP_*`):** 'Trade payables' (purchase) or 'Trade receivables' (sale).\n"
    "   - *If <3 codes, add relevant distinct codes to make 3.*\n"
    "   - Set top-level `group` & `label` from the 1st PL_* code.\n"
    "\n"
    "**5. OTHER ANOMALIES (Report in `anomaly_memo` ONLY. NO auto-correction for these totals):**\n"
    "   - After line item `amount`s are finalized:\n"
    "     - Check: (sum of line item `amount`s) vs `net_amount`.\n"
    "     - Check: (`net_amount * vat_rate / 100`) vs `vat_amount`.\n"
    "     - Check: (`net_amount + vat_amount`) vs `total_due`.\n"
    "   - Report significant discrepancies in `anomaly_memo`.\n"
    "\n"
    "Strictly follow all schema and instructions. ONLY return the JSON object.\n"
)

COMMAND_PROMPT_FOR_SECOND_PASS_TEMPLATE: str = (
    "You are an invoice parser for {our_company_settings_name} performing a second-pass analysis.\n"
    "You will be given the results of a first pass (`first_pass_data`) and a new document image.\n"
    "Your task is to:\n"
    "1. Review the `first_pass_data` provided below (especially any existing `anomaly_memo`).\n"
    "2. Analyze the new document image thoroughly.\n"
    "3. Populate ANY fields in the overall schema that are `null` or empty in `first_pass_data`, using information from the new document image.\n"
    "4. CRITICALLY, you MUST re-evaluate and populate the following fields based on the new document image, "
    "REGARDLESS of their values in `first_pass_data`:\n"
    "   - `codes` (array of 3 strings)\n"
    "   - `group` (string, from the first code)\n"
    "   - `label` (string, from the first code)\n"
    "   - `additional_data` (object, within `transaction_document`, `issuer`, `receiver`, and EACH `transaction_line_item`).\n"
    "   - `transaction_document.payment_terms` (string)\n"  # NEW: Explicitly for 2nd pass
    "   - `transaction_document.transaction_summary` (string)\n"  # NEW: Explicitly for 2nd pass
    "   - All fields within `transaction_line_items` should be re-evaluated for accuracy and completeness.\n"
    "5. Refine `transaction_document.anomaly_memo`: The `first_pass_data` may contain an initial `anomaly_memo`. Review it. Using the new document, perform all anomaly checks again (line item calculations, totals consistency as per original guidelines). Generate a new, final `anomaly_memo` that is comprehensive and accurate. If the first pass memo had valid points, incorporate or confirm them. If it was empty or incorrect, create the new memo from scratch based on your detailed analysis of the new document.\n"  # NEW: anomaly_memo refinement instruction
    "Follow all general instructions, schema definitions, and critical processing steps from the original guidelines (provided below for completeness).\n"
    "\n"
    "**Original Guidelines (Apply these to the new document image, considering `first_pass_data` for context):**\n"
    "--- START ORIGINAL GUIDELINES ---\n"
    "{original_command_prompt}"
    "--- END ORIGINAL GUIDELINES ---\n\n"
    "**COA List (Use for `codes`, `group`, `label`):**\n{coa_list_json}\n\n"
    "**First Pass Data (Use as a base; fill nulls; re-evaluate specified fields, especially note the `anomaly_memo` if present):**\n"
    "```json\n{first_pass_json_string}\n```\n\n"
    "Analyze the new document image and return the COMPLETE, FINAL JSON object adhering to the schema. "
    "ONLY output the JSON. NO other text."
)


def extract_potential_party_from_footer(footer_text: str) -> dict:
    # (이전과 동일)
    party_info = {}
    if not isinstance(footer_text, str):
        return party_info
    match_name = re.search(r"(?i)\b([A-Za-z&\s]+(GmbH|Co\.|Company|Inc\.|Ltd|LLC))\b", footer_text)
    if match_name: party_info["name"] = match_name.group(1).strip()
    match_phone = re.search(r"(?i)(?:phone|tel|fax)[^:\d]*[:\s]*([\d\-]+)", footer_text)
    if match_phone: party_info["phone"] = match_phone.group(1).strip()
    match_vat = re.search(r"(?i)(VAT|Tax ID|Steuernummer|USt-IdNr\.)[^\w]*([A-Z]{0,2}\s?[\d\s\/\-]+[A-Z\d]*)",
                          footer_text)
    if match_vat:
        if "vat" in match_vat.group(1).lower() or "ust-id" in match_vat.group(1).lower():
            party_info["vat_no"] = match_vat.group(2).strip()
        else:
            party_info["tax_no"] = match_vat.group(2).strip()
    match_iban = re.search(r"\b([A-Z]{2}\d{2}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{4}\s?\d{0,2})\b", footer_text)
    if match_iban: party_info["bank_iban"] = match_iban.group(0).replace(" ", "")
    match_bank = re.search(r"(?i)(ING-DIBA|Sparkasse|Deutsche\s*Bank|Commerzbank|Postbank|Volksbank)[^\n]*",
                           footer_text)
    if match_bank: party_info["bank_name"] = match_bank.group(1).strip()
    match_addr_city_zip = re.search(r"(\d{4,5})\s+([A-Za-zÀ-ÖØ-öø-ÿ\s\-]+(?:Stadt|Dorf|Markt)?)", footer_text)
    if match_addr_city_zip: party_info["postcode"] = match_addr_city_zip.group(1).strip()
    match_email = re.search(r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", footer_text)
    if match_email: party_info["email"] = match_email.group(0).strip()
    return party_info


def second_stage_llm_parse_issuer(image_path_for_ocr: str) -> dict:
    # (이전과 동일, 오류 처리 강화)
    if not isinstance(image_path_for_ocr, str) or not os.path.exists(image_path_for_ocr):
        log.warning(f"second_stage_llm_parse_issuer: Invalid or non-existent image path '{image_path_for_ocr}'.")
        return {}
    try:
        raw_text_for_fallback = call_openai_vision(image_path_for_ocr, prompt="OCR_ONLY", json_mode=False)
    except Exception as e:
        log.error(f"Error during OCR_ONLY call in second_stage_llm_parse_issuer for {image_path_for_ocr}: {e}")
        return {}

    if not isinstance(raw_text_for_fallback, str) or not raw_text_for_fallback.strip():
        log.warning("second_stage_llm_parse_issuer: OCR_ONLY did not return usable text.")
        return {}
    log.info(f"[Parser] Fallback OCR text for issuer (first 500 chars): {str(raw_text_for_fallback)[:500]}")

    issuer_fields_str = (
        "\"name\": null, \"regi_no\": null, \"vat_no\": null, \"tax_no\": null, \"address\": null, "
        "\"postcode\": null, \"country\": null, \"phone\": null, \"email\": null, "
        "\"contact_person_name\": null, \"contact_person_phone\": null, \"contact_person_email\": null, "
        "\"bank_name\": null, \"bank_address\": null, \"bank_account_no\": null, "
        "\"bank_iban\": null, \"bank_bic\": null, \"bank_owner\": null"
    )
    parse_prompt = (
        "You are an invoice parser. Extract the details for the INVOICE ISSUER (seller) "
        f"from the following text. Return JSON only, with this exact structure: {{{issuer_fields_str}}}\n\n"
        f"Invoice text:\n{raw_text_for_fallback}"
    )
    try:
        resp = call_openai_vision(None, prompt=parse_prompt, json_mode=True)
    except Exception as e:
        log.error(f"Error during LLM call in second_stage_llm_parse_issuer: {e}")
        return {}

    if isinstance(resp, dict):
        return resp
    elif isinstance(resp, str):
        try:
            return json.loads(resp)
        except json.JSONDecodeError:
            log.warning("Second stage LLM parse for issuer failed to parse JSON string.")
            return {}
    else:
        log.warning(f"Second stage LLM parse for issuer received unexpected response type: {type(resp)}")
        return {}


def _safe_load(txt: Any) -> dict:
    # (이전과 동일)
    log.debug(f"_safe_load received input of type: {type(txt)}")
    if not txt:
        log.debug("_safe_load received empty or None input, returning empty dict.")
        return {}
    if isinstance(txt, dict):
        log.debug("_safe_load received a dict, returning it directly.")
        return txt
    if not isinstance(txt, (str, bytes)):
        log.warning(
            f"_safe_load received unexpected type: {type(txt)}. Value (first 100 chars): {str(txt)[:100]}. Returning empty dict.")
        return {}

    original_txt_for_log = str(txt)[:500] if isinstance(txt, str) else txt.decode("utf-8", "ignore")[:500]
    if isinstance(txt, bytes):
        txt = txt.decode("utf-8", "ignore")

    cleaned_txt = txt.strip()
    if cleaned_txt.startswith("```json"):
        cleaned_txt = cleaned_txt[len("```json"):].strip()
    elif cleaned_txt.startswith("```"):
        cleaned_txt = cleaned_txt[len("```"):].strip()
    if cleaned_txt.endswith("```"):
        cleaned_txt = cleaned_txt[:-len("```")].strip()

    log.debug(f"_safe_load: Cleaned text (first 500 chars): '{cleaned_txt[:500]}'")
    if not cleaned_txt:
        log.debug("_safe_load resulted in empty string after cleaning, returning empty dict.")
        return {}
    try:
        loaded_json = json.loads(cleaned_txt)
        log.debug("_safe_load successfully parsed JSON.")
        return loaded_json
    except json.JSONDecodeError as e:
        log.warning(
            f"JSONDecodeError in _safe_load: {e}. Cleaned text (first 500 chars): '{cleaned_txt[:500]}'")
        try:
            match = re.search(r'\{.*\}', cleaned_txt, re.DOTALL)
            if match:
                potential_json = match.group(0)
                log.info(f"Attempting to parse potential JSON object found within string: {potential_json[:200]}...")
                loaded_json = json.loads(potential_json)
                log.info("_safe_load successfully parsed JSON object found within string.")
                return loaded_json
        except json.JSONDecodeError as inner_e:
            log.warning(f"Still failed to parse JSON after attempting to find object within string: {inner_e}")
        return {}
    except Exception as e:
        log.error(
            f"Unexpected error in _safe_load: {e}. Cleaned text (first 500 chars): '{cleaned_txt[:500]}'",
            exc_info=True)
        return {}


TOP_LEVEL_FIELDS_FOR_SECOND_PASS_OVERWRITE = ["codes", "group", "label"]
TRANSACTION_DOC_FIELDS_FOR_SECOND_PASS_OVERWRITE = ["payment_terms", "transaction_summary", "anomaly_memo",
                                                    "additional_data"]


class InvoiceParser(BaseParser):
    REQUIRED_FIELDS = ["invoice_no", "issuance_date"]

    def __init__(self, *, extra_json: dict | None = None):
        self.extra_json = extra_json or {}

    def _build_prompt_1st_pass(self) -> str:
        prompt = COMMAND_PROMPT + "\n\nOutput Format Schema:\n" + OUTPUT_SCHEMA
        prompt += ("\n\nIMPORTANT: This is the first pass. Focus on extracting primary fields. "
                   "Do NOT fill 'codes', 'group', 'label', or any 'additional_data' in this pass. "
                   "Also, do NOT fill 'payment_terms' or 'transaction_summary' in this pass. "  # NEW
                   "You MAY populate 'anomaly_memo' based on initial line item checks.")

        return prompt

    def _build_prompt_2nd_pass(self, first_pass_data: dict) -> str:
        coa_list = self.extra_json.get("coa_classifications", [])
        coa_list_json_str = json.dumps(coa_list, ensure_ascii=False, indent=2) if coa_list else "[]"

        prompt = COMMAND_PROMPT_FOR_SECOND_PASS_TEMPLATE.format(
            our_company_settings_name=our_company_settings_name,  # <-- 네 번째 인자로 우리 회사 이름 전달
            original_command_prompt=COMMAND_PROMPT,
            coa_list_json=coa_list_json_str,
            first_pass_json_string=json.dumps(first_pass_data or {}, indent=2, ensure_ascii=False)
        )
        return prompt

    def _merge_results(self, base_data: dict, new_data: dict) -> dict:
        if not base_data and not new_data: return _safe_load(OUTPUT_SCHEMA)
        if not new_data: return base_data.copy() if base_data else _safe_load(OUTPUT_SCHEMA)
        if not base_data: return new_data.copy()

        merged_data = base_data.copy()

        for key in TOP_LEVEL_FIELDS_FOR_SECOND_PASS_OVERWRITE:
            merged_data[key] = new_data.get(key, [] if key == "codes" else None)

        for section_key in ["transaction_document", "issuer", "receiver"]:
            merged_data_section = merged_data.get(section_key, {})
            new_data_section = new_data.get(section_key, {})  # Ensure new_data_section is a dict
            if not isinstance(new_data_section, dict):  # If new_data doesn't have this section or it's not a dict
                new_data_section = {}

            # Fields to always overwrite from new_data for transaction_document
            if section_key == "transaction_document":
                for field_to_overwrite in TRANSACTION_DOC_FIELDS_FOR_SECOND_PASS_OVERWRITE:
                    if field_to_overwrite in new_data_section:
                        merged_data_section[field_to_overwrite] = new_data_section[field_to_overwrite]
                    elif field_to_overwrite == "additional_data":  # Ensure additional_data is at least {}
                        merged_data_section[field_to_overwrite] = {}
            elif section_key in ["issuer",
                                 "receiver"]:  # For issuer/receiver, only additional_data is explicit overwrite
                if "additional_data" in new_data_section:
                    merged_data_section["additional_data"] = new_data_section["additional_data"]
                elif "additional_data" not in merged_data_section:  # Ensure it exists
                    merged_data_section["additional_data"] = {}

            # For other fields in the section, update if null in base or if field is new
            for field, value in new_data_section.items():
                is_overwrite_field = (
                                                 section_key == "transaction_document" and field in TRANSACTION_DOC_FIELDS_FOR_SECOND_PASS_OVERWRITE) or \
                                     (section_key in ["issuer", "receiver"] and field == "additional_data")

                if not is_overwrite_field:  # If not already handled by specific overwrite logic
                    if merged_data_section.get(field) is None and value is not None:
                        merged_data_section[field] = value
                    elif field not in merged_data_section and value is not None:
                        merged_data_section[field] = value

            merged_data[section_key] = merged_data_section

        if "transaction_line_items" in new_data and new_data["transaction_line_items"] is not None:
            merged_data["transaction_line_items"] = new_data["transaction_line_items"]
        elif not merged_data.get("transaction_line_items"):
            merged_data["transaction_line_items"] = []

        # Final check for existence of additional_data
        for section_obj_key in ["transaction_document", "issuer", "receiver"]:
            section_obj = merged_data.get(section_obj_key)
            if isinstance(section_obj, dict) and "additional_data" not in section_obj:
                section_obj["additional_data"] = {}
        for item in merged_data.get("transaction_line_items", []):
            if isinstance(item, dict) and "additional_data" not in item:
                item["additional_data"] = {}

        return merged_data

    def parse(self, original_filepath: Optional[str], new_filepath: str) -> dict:
        parser_debug_messages: Dict[str, Any] = {}
        first_pass_data: Dict[str, Any] = {}
        final_parsed_data: Dict[str, Any] = {}
        default_structure = _safe_load(OUTPUT_SCHEMA)

        try:
            if original_filepath and os.path.exists(original_filepath):
                log.info(f"[InvoiceParser] Starting 1st pass for file: {original_filepath}")
                prompt_1st = self._build_prompt_1st_pass()
                # log.debug(f"[InvoiceParser] 1st pass prompt: {prompt_1st}") # Full prompt can be very long
                log.debug(
                    f"[InvoiceParser] 1st pass prompt (first 300, last 100 chars): {prompt_1st[:300]}...{prompt_1st[-100:]}")

                raw_resp_1st = call_openai_vision_or_file(original_filepath, prompt=prompt_1st, json_mode=True)
                parser_debug_messages["api_response_1st_pass_snippet"] = (
                            str(raw_resp_1st)[:500] + "...") if raw_resp_1st else "N/A"
                log.info(f"[InvoiceParser] 1st pass response: {parser_debug_messages['api_response_1st_pass_snippet']}")

                loaded_1st_pass = _safe_load(raw_resp_1st)
                if not loaded_1st_pass or not isinstance(loaded_1st_pass, dict):
                    log.warning(
                        "1st pass failed to obtain a valid dictionary. Using default structure for 1st pass base.")
                    first_pass_data = default_structure.copy()
                else:
                    first_pass_data = loaded_1st_pass
                    first_pass_data["codes"] = []  # Always clear for 2nd pass
                    first_pass_data["group"] = None  # Always clear for 2nd pass
                    first_pass_data["label"] = None  # Always clear for 2nd pass

                    # Clear fields designated for 2nd pass, keep anomaly_memo from 1st pass for reference
                    for section_key_fp in ["transaction_document", "issuer", "receiver"]:
                        if section_key_fp in first_pass_data and isinstance(first_pass_data[section_key_fp], dict):
                            first_pass_data[section_key_fp]["additional_data"] = {}  # Clear additional_data
                            if section_key_fp == "transaction_document":
                                first_pass_data[section_key_fp]["payment_terms"] = None
                                first_pass_data[section_key_fp]["transaction_summary"] = None
                                # anomaly_memo is kept from 1st pass for 2nd pass to reference

                    if "transaction_line_items" in first_pass_data and isinstance(
                            first_pass_data["transaction_line_items"], list):
                        for item in first_pass_data["transaction_line_items"]:
                            if isinstance(item, dict):
                                item["additional_data"] = {}  # Clear additional_data
                parser_debug_messages["parsed_data_1st_pass_after_cleanup"] = pprint.pformat(first_pass_data)
            else:
                log.info(
                    f"[InvoiceParser] No original_filepath provided or file does not exist ('{original_filepath}'). Skipping 1st pass.")
                first_pass_data = default_structure.copy()  # Start with default, including empty anomaly_memo

            if not new_filepath or not os.path.exists(new_filepath):
                log.error(f"New filepath '{new_filepath}' is missing or does not exist. Cannot proceed.")
                # Ensure first_pass_data is used if it exists, otherwise return error with default structure
                final_error_data = first_pass_data if first_pass_data and any(
                    first_pass_data.values()) else default_structure.copy()
                if "transaction_document" not in final_error_data: final_error_data["transaction_document"] = {}
                final_error_data["transaction_document"]["cp_memo"] = (
                            final_error_data["transaction_document"].get("cp_memo",
                                                                         "") + f" Critical error: New filepath '{new_filepath}' missing.").strip()
                final_error_data["error_message"] = f"New filepath '{new_filepath}' missing."
                return {
                    "parsed_data": final_error_data,
                    "debug_messages": parser_debug_messages
                }

            log.info(f"[InvoiceParser] Starting 2nd pass for image file: {new_filepath}")
            prompt_2nd = self._build_prompt_2nd_pass(first_pass_data)
            # log.debug(f"[InvoiceParser] 2nd pass prompt: {prompt_2nd}") # Can be very long
            log.debug(
                f"[InvoiceParser] 2nd pass prompt (template part, first 300, last 300 of first_pass_json): {COMMAND_PROMPT_FOR_SECOND_PASS_TEMPLATE.split('{original_command_prompt}')[0][:300]}...{json.dumps(first_pass_data or {}, indent=2, ensure_ascii=False)[-300:]}")

            raw_resp_2nd = call_openai_vision(new_filepath, prompt=prompt_2nd, json_mode=True)
            parser_debug_messages["api_response_2nd_pass_snippet"] = (
                        str(raw_resp_2nd)[:500] + "...") if raw_resp_2nd else "N/A"
            log.info(f"[InvoiceParser] 2nd pass response: {parser_debug_messages['api_response_2nd_pass_snippet']}")

            second_pass_data = _safe_load(raw_resp_2nd)
            parser_debug_messages["parsed_data_2nd_pass"] = pprint.pformat(second_pass_data)

            if not second_pass_data or not isinstance(second_pass_data, dict):
                log.warning(
                    "2nd pass failed to obtain valid dictionary. Attempting to use 1st pass data if available and not just an empty default structure.")
                # Use 1st pass data only if it's not just the default empty structure
                if first_pass_data and first_pass_data != default_structure:
                    final_parsed_data = first_pass_data
                    log.info("Using 1st pass data as 2nd pass failed.")
                else:
                    log.error("Both 1st and 2nd pass resulted in empty or invalid data.")
                    raise ValueError("Both 1st and 2nd pass resulted in empty or invalid data after _safe_load.")
            else:
                final_parsed_data = self._merge_results(first_pass_data, second_pass_data)

            parser_debug_messages["data_before_issuer_fallback"] = pprint.pformat(final_parsed_data)

            current_issuer_info = final_parsed_data.get("issuer", {})
            if not self._is_party_info_sufficient(current_issuer_info):
                log.info(
                    "[Parser] Issuer details after merge seem insufficient. Attempting fallback using new_filepath.")
                issuer_fallback_result = second_stage_llm_parse_issuer(new_filepath)
                parser_debug_messages["issuer_fallback_result"] = pprint.pformat(issuer_fallback_result)
                if self._is_party_info_sufficient(issuer_fallback_result):
                    log.info("[Parser] Fallback (second_stage_llm_parse_issuer) provided issuer details.")
                    final_parsed_data["issuer"] = self._merge_party_info(current_issuer_info, issuer_fallback_result)

            parser_debug_messages["data_after_issuer_fallback"] = pprint.pformat(final_parsed_data)

            if "transaction_document" in final_parsed_data and isinstance(final_parsed_data["transaction_document"],
                                                                          dict):
                final_parsed_data["transaction_document"] = self.validate(final_parsed_data["transaction_document"])
            else:  # Ensure validation happens even if transaction_document was missing
                validated_td = self.validate(final_parsed_data.get("transaction_document", {}))
                if "transaction_document" not in final_parsed_data: final_parsed_data["transaction_document"] = {}
                final_parsed_data["transaction_document"].update(validated_td)

            log.info(
                f"[InvoiceParser] Parse completed. Final 'main_trading_partner_role': {final_parsed_data.get('main_trading_partner_role')}")
            parser_debug_messages["final_merged_data"] = pprint.pformat(final_parsed_data)

            return {
                "parsed_data": final_parsed_data,
                "debug_messages": parser_debug_messages
            }

        except Exception as e:
            log.error(f"InvoiceParser failed in main parse method: {e}", exc_info=True)
            parser_debug_messages["parser_exception"] = str(e)
            parser_debug_messages["parser_exception_type"] = type(e).__name__

            error_data_payload = default_structure.copy()
            temp_data_for_error = {}  # Start with empty
            if first_pass_data and first_pass_data != default_structure:
                temp_data_for_error = self._merge_results(temp_data_for_error, first_pass_data)
            if final_parsed_data and final_parsed_data != default_structure:  # If final_parsed_data got populated partially
                temp_data_for_error = self._merge_results(temp_data_for_error, final_parsed_data)

            # Ensure the error payload is based on default_structure and then updated
            for key, value in temp_data_for_error.items():
                if value is not None and value != [] and value != {}:  # only update if temp has something meaningful
                    error_data_payload[key] = value

            if "transaction_document" not in error_data_payload or not isinstance(
                    error_data_payload.get("transaction_document"), dict):
                error_data_payload["transaction_document"] = {}

            current_cp_memo = error_data_payload["transaction_document"].get("cp_memo", "")
            error_message = f"Parser failed: {str(e)}"
            error_data_payload["transaction_document"][
                "cp_memo"] = f"{current_cp_memo} {error_message}".strip() if current_cp_memo else error_message
            error_data_payload["error_message"] = error_message  # Top level error message

            return {
                "parsed_data": error_data_payload,
                "debug_messages": parser_debug_messages
            }

    def _is_party_info_sufficient(self, party_data: Dict[str, Any]) -> bool:
        if not isinstance(party_data, dict): return False
        return bool(party_data.get("name") or party_data.get("address") or party_data.get("vat_no") or party_data.get(
            "regi_no"))

    def _merge_party_info(self, base_party: dict, fallback_party: dict) -> dict:
        """Helper to merge fallback party data into base, only filling nulls in base."""
        merged = base_party.copy() if isinstance(base_party, dict) else {}
        if not isinstance(fallback_party, dict): return merged

        for key, value in fallback_party.items():
            if merged.get(key) is None and value is not None:
                merged[key] = value
            # Ensure additional_data is a dict if it wasn't before
            if key == "additional_data" and not isinstance(merged.get(key), dict) and value is not None:
                merged[key] = value if isinstance(value, dict) else {}
            elif key == "additional_data" and merged.get(
                    key) is None:  # if fallback_party has no additional_data, ensure it's a dict
                merged[key] = {}

        if "additional_data" not in merged:  # ensure additional_data always exists
            merged["additional_data"] = {}
        return merged


if __name__ == '__main__':
    # (테스트 코드는 이전 답변과 동일하게 유지하거나, 필요에 따라 새 필드 테스트 로직 추가)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


    # --- Dummy API call functions for testing ---
    def mock_call_openai_vision_or_file(filepath: str, prompt: str, json_mode: bool = False):
        log.info(f"MOCK call_openai_vision_or_file for: {filepath}")
        # Simulate 1st pass result
        return {
            "transaction_document": {
                "invoice_no": "INV-1STPASS", "issuance_date": "2025-01-01", "net_amount": 100.0,
                "cp_memo": "1st pass memo",
                "anomaly_memo": "Initial anomaly: Item A amount seems high."  # 1차 anomaly_memo
                # payment_terms, transaction_summary는 1차에서 생성 안되거나, 생성돼도 parser가 None으로 만듦
            },
            "issuer": {"name": "Issuer From 1st Pass"},
            "receiver": {"name": "Receiver From 1st Pass"},
            "main_trading_partner_role": "issuer",
            "transaction_line_items": [{"article_name": "Item Alpha", "amount": 100.0}],
        }


    def mock_call_openai_vision(filepath: Optional[str], prompt: str, json_mode: bool = False):
        if filepath is None and "INVOICE ISSUER" in prompt:
            log.info(f"MOCK call_openai_vision for ISSUER OCR PARSE (text prompt)")
            return {"name": "Fallback Issuer Name", "vat_no": "DE_FallbackVAT", "address": "Fallback Address"}
        elif filepath is None and "OCR_ONLY" in prompt:
            log.info(f"MOCK call_openai_vision for OCR_ONLY (text prompt)")
            return "OCR Text for fallback issuer parsing if needed by second_stage_llm_parse_issuer directly."

        log.info(
            f"MOCK call_openai_vision for: {filepath if filepath else 'None (text-only for issuer fallback likely)'}")
        first_pass_data_sim = {}
        if "first_pass_json_string" in prompt:  # Check if it's a 2nd pass prompt
            try:
                # Extract the JSON string for first_pass_data from the prompt
                json_str_match = re.search(r"```json\s*(\{.*?\})\s*```", prompt.split("**First Pass Data")[1],
                                           re.DOTALL)
                if json_str_match:
                    first_pass_data_sim = json.loads(json_str_match.group(1))
            except Exception as e:
                log.error(f"Error parsing first_pass_data_sim from mock prompt: {e}")

        # Simulate 2nd pass response
        response = {
            "transaction_document": {
                "invoice_no": first_pass_data_sim.get("transaction_document", {}).get("invoice_no", "INV-2NDPASS"),
                "issuance_date": first_pass_data_sim.get("transaction_document", {}).get("issuance_date", "2025-02-02"),
                "service_date": "2025-02-10",
                "due_date": "2025-03-02",
                "currency": "EUR",
                "net_amount": first_pass_data_sim.get("transaction_document", {}).get("net_amount", 200.0),
                "vat_amount": 14.0,
                "vat_rate": 7.0,
                "total_due": 214.0,
                "cp_memo": first_pass_data_sim.get("transaction_document", {}).get("cp_memo", "2nd pass memo"),
                "payment_terms": "Net 30 days from 2nd pass",  # NEW: Filled in 2nd pass
                "transaction_summary": "Summary from 2nd pass.",  # NEW: Filled in 2nd pass
                "anomaly_memo": (first_pass_data_sim.get("transaction_document", {}).get("anomaly_memo",
                                                                                         "") + " Further check: All totals consistent.").strip(),
                # NEW: Refined anomaly_memo
                "additional_data": {"source": "2nd_pass_document", "verified_by": "AI_v2"}
            },
            "issuer": {
                "name": first_pass_data_sim.get("issuer", {}).get("name", "Issuer From 2nd Pass"),
                "vat_no": "DE123456789",
                "address": "Vendor Street 1, 12345 City",
                "additional_data": {"category": "supplier_final"}
            },
            "receiver": {
                "name": first_pass_data_sim.get("receiver", {}).get("name", "Receiver From 2nd Pass"),
                "regi_no": "CUST999",
                "additional_data": {"department": "finance"}
            },
            "main_trading_partner_role": first_pass_data_sim.get("main_trading_partner_role", "issuer"),
            "transaction_line_items": [
                {"line_item_id": "L1", "article_name": "Item Bravo", "quantity": 2, "unit_price": 100.0,
                 "amount": 200.0, "additional_data": {"tax_info": "standard_final"}}
            ],
            "codes": ["PL_EXP_01", "FP_VAT_IN", "FP_PAY_TR"],
            "group": "General Expenses",
            "label": "External Services"
        }
        return response


    import sys

    current_module = sys.modules[__name__]
    current_module.call_openai_vision_or_file = mock_call_openai_vision_or_file
    current_module.call_openai_vision = mock_call_openai_vision

    parser = InvoiceParser(extra_json={"coa_classifications": [
        {"code": "PL_EXP_01", "group": "General Expenses", "label": "External Services"},
        {"code": "FP_VAT_IN", "group": "VAT", "label": "Input VAT"},
        {"code": "FP_PAY_TR", "group": "Liabilities", "label": "Trade Payables"}
    ]})

    dummy_files_created = []


    def create_dummy_file(name):
        if not os.path.exists(name):
            with open(name, "w") as f: f.write(f"dummy content for {name}")
            dummy_files_created.append(name)


    dummy_original_pdf = "dummy_original.pdf";
    create_dummy_file(dummy_original_pdf)
    dummy_new_image_jpg = "dummy_new_image.jpg";
    create_dummy_file(dummy_new_image_jpg)

    print("\n--- Test Case 1: With original_filepath (2-pass) ---")
    result1 = parser.parse(original_filepath=dummy_original_pdf, new_filepath=dummy_new_image_jpg)
    print("\nParsed Data (2-pass):")
    pprint.pprint(result1.get("parsed_data"))

    print("\n--- Test Case 2: Without original_filepath (effectively 2nd pass logic only) ---")
    result2 = parser.parse(original_filepath=None, new_filepath=dummy_new_image_jpg)
    print("\nParsed Data (1-pass to 2nd logic):")
    pprint.pprint(result2.get("parsed_data"))

    print("\n--- Test Case 3: new_filepath does not exist ---")
    result3 = parser.parse(original_filepath=None, new_filepath="non_existent_image.jpg")
    print("\nParsed Data (new_filepath non-existent):")
    pprint.pprint(result3.get("parsed_data"))

    for fname in dummy_files_created:
        if os.path.exists(fname): os.remove(fname)
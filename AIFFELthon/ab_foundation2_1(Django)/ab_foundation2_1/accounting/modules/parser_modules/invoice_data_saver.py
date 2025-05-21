# accounting/modules/parser_modules/invoice_data_saver.py

from django.db import transaction
from decimal import Decimal, InvalidOperation
import logging
from typing import Dict, List, Optional
from accounting.modules.parser_modules.filename_generator import generate_invoice_filename

# 수정된 모델 임포트
from accounting.models import (
    UploadedFile,
    TransactionDocument,
    Entity,  # Counterparty 대신 Entity 사용
    TransactionLineItem,
    TransactionDetail
)

logger = logging.getLogger(__name__)


def safe_decimal(value, default=None, max_digits=19, decimal_places=4) -> Optional[Decimal]:
    """Helper function to safely convert a value to Decimal."""
    if value is None:
        return default
    try:
        cleaned_value = str(value)
        # 추가적인 문자열 정리 로직 (예: 통화 기호, 천단위 콤마 제거)은 필요에 따라 강화
        # cleaned_value = re.sub(r'[€$,]', '', cleaned_value).strip()
        # cleaned_value = cleaned_value.replace(',', '') # For locales using . as decimal separator

        d_value = Decimal(cleaned_value)
        # Django DecimalField는 자동으로 반올림/자릿수 처리를 하지만,
        # 여기서 명시적으로 하고 싶다면 quantize 등을 사용할 수 있습니다.
        # 예: return d_value.quantize(Decimal('0.1') ** decimal_places)
        return d_value
    except (InvalidOperation, ValueError, TypeError) as e:
        cleaned_value_str = cleaned_value if 'cleaned_value' in locals() else str(value)
        logger.warning(
            f"Could not convert '{str(value)}' (cleaned: '{cleaned_value_str}') to Decimal: {e}. Returning default.")
        return default


def _get_or_create_entity(entity_data: Optional[Dict], entity_type_role_value: Optional[str] = None) -> Optional[Entity]:
    """
    Helper function to get or create an Entity instance from parsed data.
    Uses 'regi_no' as the primary unique identifier, falls back to 'name' if regi_no is not available.
    More sophisticated duplicate checks might be needed for production.
    """
    if not entity_data:
        return None

    identifier_kwargs = {}
    if entity_data.get('regi_no'):
        identifier_kwargs['regi_no'] = entity_data['regi_no']

    entity_fields_to_save = {
        'name': entity_data.get('name'),
        'regi_no': entity_data.get('regi_no'),
        'vat_no': entity_data.get('vat_no'),
        'tax_no': entity_data.get('tax_no'),
        'address': entity_data.get('address'),
        'postcode': entity_data.get('postcode'),
        'country': entity_data.get('country'),
        'phone': entity_data.get('phone'),
        'email': entity_data.get('email'),
        'contact_person_name': entity_data.get('contact_person_name'),
        'contact_person_phone': entity_data.get('contact_person_phone'),
        'contact_person_email': entity_data.get('contact_person_email'),
        'bank_name': entity_data.get('bank_name'),
        'bank_address': entity_data.get('bank_address'),
        'bank_account_no': entity_data.get('bank_account_no'),
        'bank_iban': entity_data.get('bank_iban'),
        'bank_bic': entity_data.get('bank_bic'),
        'bank_owner': entity_data.get('bank_owner'),
    }
    if entity_type_role_value and hasattr(Entity, 'entity_general_role'):
        entity_fields_to_save['entity_general_role'] = entity_type_role_value

    defaults = {k: v for k, v in entity_fields_to_save.items() if v is not None}

    # regi_no가 없고 이름만 있는 경우(주의)
    if not identifier_kwargs and defaults.get('name'):
        identifier_kwargs['name'] = defaults['name']

    if identifier_kwargs:
        # 여러 개면 가장 오래된 것(최초 1개)만 사용
        qs = Entity.objects.filter(**identifier_kwargs)
        if qs.count() > 1:
            logger.warning(
                f"Entity 중복({qs.count()}개)! identifiers: {identifier_kwargs} -- 최초 Entity만 사용, 나머지는 병합 필요"
            )
            entity = qs.first()
            # 필요하다면 defaults로 업데이트
            for k, v in defaults.items():
                setattr(entity, k, v)
            entity.save()
            return entity
        elif qs.count() == 1:
            entity = qs.first()
            # 필요하다면 defaults로 업데이트
            for k, v in defaults.items():
                setattr(entity, k, v)
            entity.save()
            return entity
        else:
            entity = Entity.objects.create(**defaults)
            logger.info(f"Created Entity (ID: {entity.id}) with identifiers: {identifier_kwargs}. Role hint: {entity_type_role_value or 'N/A'}")
            return entity
    elif defaults:
        logger.warning(f"Attempting to create Entity with data but no reliable unique identifier. Data: {defaults}. Role hint: {entity_type_role_value or 'N/A'}")
        # 중복 방지 위해 생성은 하지 않고 None만 반환
        return None
    else:
        logger.warning(f"No valid data provided to get or create an Entity. Role hint: {entity_type_role_value or 'N/A'}")
        return None

def find_duplicate_transaction_document(doc_data: dict, issuer_data: dict):
    invoice_no = doc_data.get('invoice_no')
    total_due = safe_decimal(doc_data.get('total_due'))
    issuance_date = doc_data.get('issuance_date')
    issuer_name = issuer_data.get('name') if issuer_data else None

    qs = TransactionDocument.objects.filter(
        invoice_no=invoice_no,
        total_due=total_due,
        issuance_date=issuance_date,
        issuer__name=issuer_name
    )
    if qs.exists():
        duplicate = qs.first()
        reason = [
            f"invoice_no: {duplicate.invoice_no} == {invoice_no}",
            f"total_due: {duplicate.total_due} == {total_due}",
            f"issuance_date: {duplicate.issuance_date} == {issuance_date}",
            f"issuer_name: {duplicate.issuer.name if duplicate.issuer else None} == {issuer_name}",
        ]
        return duplicate, reason
    return None, None

    # 부분 일치 후보(아래는 예시. 필요하면 좀 더 섬세하게)
    partial_reasons = []
    base_qs = TransactionDocument.objects.filter(invoice_no=invoice_no)
    for doc in base_qs:
        # 각 필드별 비교
        if doc.total_due != total_due:
            partial_reasons.append(f"total_due: {doc.total_due} != {total_due}")
        if str(doc.issuance_date) != str(issuance_date):
            partial_reasons.append(f"issuance_date: {doc.issuance_date} != {issuance_date}")
        if (doc.issuer and doc.issuer.name != issuer_name) or (doc.issuer is None and issuer_name is not None):
            partial_reasons.append(f"issuer_name: {doc.issuer.name if doc.issuer else None} != {issuer_name}")
    if base_qs.exists():
        return None, partial_reasons

    return None, None



@transaction.atomic
def save_parsed_invoice_data(uploaded_file_instance: UploadedFile, parsed_data: Dict, match_data: dict | None = None):
    try:
        print("[save_parsed_invoice_data] 호출됨")
        print("  uploaded_file_instance:", uploaded_file_instance)
        print("  parsed_data keys:", list(parsed_data.keys()))

        uploaded_file_instance.parsed_json = parsed_data

        # 1. Entity 저장 정책 변경
        main_role = parsed_data.get("main_trading_partner_role")
        issuer_data = parsed_data.get("issuer")
        receiver_data = parsed_data.get("receiver")
        print("  main_trading_partner_role:", main_role)

        issuer_entity = None
        receiver_entity = None

        if main_role == "issuer":
            issuer_entity = _get_or_create_entity(issuer_data, 'issuer')
            print("  issuer_entity:", issuer_entity)
        elif main_role == "receiver":
            receiver_entity = _get_or_create_entity(receiver_data, 'receiver')
            print("  receiver_entity:", receiver_entity)
        else:
            print("  main_trading_partner_role이 명확하지 않아, 둘 다 저장 안 함")

        # 2. TransactionDocument 저장
        doc_data = parsed_data.get("transaction_document", {})
        print("  doc_data:", doc_data)

        # 중복 검사 먼저!
        duplicate_doc, duplicate_reason = find_duplicate_transaction_document(doc_data, issuer_data)
        print("  duplicate_doc:", duplicate_doc)
        print("  duplicate_reason:", duplicate_reason)
        if duplicate_doc:
            print("[RETURN] 중복 발견, 저장 중단")
            return None, duplicate_reason
        elif duplicate_reason:
            print("[INFO] 부분 중복 의심:", duplicate_reason)

        prepayment_val = doc_data.get('prepayment', False)
        if prepayment_val is None:
            prepayment_val = False

        company_code = 'DE000001'
        doc_type = doc_data.get('document_type')
        filename, doc_type_code = generate_invoice_filename(company_code, doc_type)
        transaction_doc_fields = {
            'uploaded_file': uploaded_file_instance,
            'issuer': issuer_entity,
            'receiver': receiver_entity,
            'main_trading_partner_role': main_role,
            'tran_doc_id_parsed': doc_data.get('tran_doc_id'),
            'document_type': doc_type,
            'accounting_transaction_doc_type': doc_type_code,
            'invoice_no': doc_data.get('invoice_no'),
            'reference_no': doc_data.get('reference_no'),
            'internal_order_no': doc_data.get('internal_order_no'),
            'external_order_no': doc_data.get('external_order_no'),
            'issuance_date': doc_data.get('issuance_date') or None,
            'service_date': doc_data.get('service_date') or None,
            'delivery_date': doc_data.get('delivery_date') or None,
            'cp_memo': doc_data.get('cp_memo'),
            'payment_terms': doc_data.get('payment_terms'),
            'due_date': doc_data.get('due_date') or None,
            'currency': doc_data.get('currency'),
            'net_amount': safe_decimal(doc_data.get('net_amount')),
            'vat_amount': safe_decimal(doc_data.get('vat_amount')),
            'vat_rate': safe_decimal(doc_data.get('vat_rate'), decimal_places=2),
            'total_due': safe_decimal(doc_data.get('total_due')),
            'prepayment': prepayment_val,
            'prepaid_amount': safe_decimal(doc_data.get('prepaid_amount')),
            'price_discount': safe_decimal(doc_data.get('price_discount')),
            'price_discount_terms': doc_data.get('price_discount_terms'),
            'transaction_summary': doc_data.get('transaction_summary'),
            'booking_document_no': doc_data.get('booking_document_no'),
            'booking_date': doc_data.get('booking_date'),
            'closing_period': doc_data.get('closing_period'),
            'ledger_standard': doc_data.get('ledger_standard'),
            'anomaly_memo': doc_data.get('anomaly_memo')
        }
        closing_period_raw = doc_data.get('closing_period')
        if closing_period_raw is not None:
            try:
                transaction_doc_fields['closing_period'] = int(closing_period_raw)
            except (ValueError, TypeError):
                print("  closing_period 변환 실패:", closing_period_raw)
                transaction_doc_fields['closing_period'] = None

        print("  transaction_doc_fields 준비됨:", transaction_doc_fields)
        transaction_doc, created = TransactionDocument.objects.update_or_create(
            uploaded_file=uploaded_file_instance,
            defaults=transaction_doc_fields
        )
        print("  transaction_doc 생성/업데이트:", transaction_doc, "created:", created)

        # 4. TransactionLineItems 저장
        transaction_doc.line_items.all().delete()
        line_items_data = parsed_data.get("transaction_line_items", [])
        print("  line_items_data 길이:", len(line_items_data))
        for item_data in line_items_data:
            print("    저장할 item_data:", item_data)
            TransactionLineItem.objects.create(
                document=transaction_doc,
                line_item_id_parsed=item_data.get('line_item_id'),
                article_no=item_data.get('article_no'),
                article_name=item_data.get('article_name'),
                article_description=item_data.get('article_description'),
                quantity=safe_decimal(item_data.get('quantity')),
                unit_price=safe_decimal(item_data.get('unit_price')),
                amount=safe_decimal(item_data.get('amount'))
            )
        print(f"Saved {len(line_items_data)} line items for TransactionDocument ID: {transaction_doc.id}")

        # ③ ▶ 새로 추가 ◀  매칭된 계정코드를 TransactionDetail 로 저장
        if match_data:
            # 매핑 규칙: 어느 금액을 쓰고 차/대변 어느 쪽으로 넣을지
            amount_map = {
                "primary": ("net_amount", "credit"),  # 매출액
                "secondary": ("vat_amount", "credit"),  # 부가세
                "tertiary": ("total_due", "debit"),  # 미수금
            }

            currency = parsed_data.get("transaction_document", {}).get("currency")

            for idx, level in enumerate(("primary", "secondary", "tertiary"), start=1):
                item = match_data.get(level)
                if not item or not item.get("code"):
                    continue

                amount_field, drcr = amount_map[level]
                raw_amount = parsed_data.get("transaction_document", {}).get(amount_field)
                if raw_amount is None:
                    continue  # 금액이 없으면 건너뜀

                TransactionDetail.objects.create(
                    transaction_document=transaction_doc,
                    gl_account_no=item["code"],
                    gl_account_description=item.get("desc"),
                    position_no=idx,
                    position="credit" if drcr == "credit" else "debit",
                    currency=currency,
                    amount=Decimal(str(raw_amount)),
                    tax_code=item["code"] if level == "secondary" else None,
                    description=f"Auto-matched {level} ({item.get('category')})",
                )

        # 5. UploadedFile 상태 업데이트
        uploaded_file_instance.is_processed = True
        uploaded_file_instance.abf_filename = filename

        fields = ['abf_filename', 'is_processed', 'parsed_json']

        if hasattr(uploaded_file_instance, 'processing_status'):
            uploaded_file_instance.processing_status = 'COMPLETED'
            fields.append('processing_status')
        uploaded_file_instance.save(update_fields=fields)

        print(f"[RETURN] 정상 저장. transaction_doc: {transaction_doc}")
        return transaction_doc, None

    except Exception as e:
        print("[ERROR] Exception 발생:", str(e))
        if uploaded_file_instance and hasattr(UploadedFile, 'processing_status'):
            try:
                uploaded_file_instance.processing_status = 'ERROR'
                uploaded_file_instance.save(update_fields=['processing_status'])
            except Exception as e_save:
                print("[ERROR] UploadedFile status update 실패:", str(e_save))
        return None, str(e)


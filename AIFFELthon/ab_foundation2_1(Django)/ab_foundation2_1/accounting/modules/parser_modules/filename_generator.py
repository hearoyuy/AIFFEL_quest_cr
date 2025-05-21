#accounting/modules/parser_modules/filename_generator.py
from datetime import datetime
from accounting.models import TransactionDocument

# 문서 유형을 약어로 매핑
DOC_TYPE_MAP = {
    "invoice": "CI",                # 상업용 인보이스
    "bank statements": "BS",        # 은행 명세서
    "commercial contracts": "CC",   # 상업 계약서
}

def generate_invoice_filename(company_code: str, doc_type: str):
    today = datetime.today()
    year = today.year  # int로!
    month = today.month  # int로!

    doc_type_code = DOC_TYPE_MAP.get(doc_type, 'CI')

    # class_serial은 특정 조건 기준 순번
    class_serial_count = TransactionDocument.objects.filter(
        created_at__year=year,
        created_at__month=month,
        accounting_transaction_doc_type=doc_type_code  # 원문 기준 필터
    ).count()
    class_serial = class_serial_count + 1

    filename = f"{company_code}_{year}_{month:02}_{doc_type_code}_{class_serial:06}"

    return filename, doc_type_code
from django.db import models
from django.conf import settings # for User model if needed, or use get_user_model()
from .uploaded_file import UploadedFile # Assuming relation to UploadedFile

# Python 3.9+ type hinting, for older versions remove or use from typing import ...
from typing import Optional, List
from django.utils.translation import gettext_lazy as _ # 다국어 지원을 위해
from django.core.validators import MinValueValidator, MaxValueValidator

class Entity(models.Model):
    ROLE_CHOICES = [
        ('issuer', _('Issuer')),
        ('receiver', _('Receiver')),
        ('both', _('Both Issuer and Receiver')), # 발행자 및 수신자 역할 모두 가능
        ('other', _('Other/Not Specified')),   # 기타 또는 역할 미지정
    ]

    # 기존 필드들
    name = models.CharField(max_length=255, blank=True, null=True, help_text=_("Company or person name"))
    regi_no = models.CharField(max_length=100, blank=True, null=True, unique=True, help_text=_("Registration number (e.g., business registration number), should be unique if possible"))
    vat_no = models.CharField(max_length=100, blank=True, null=True, help_text=_("VAT number"))
    tax_no = models.CharField(max_length=100, blank=True, null=True, help_text=_("Tax number"))
    address = models.TextField(blank=True, null=True)
    postcode = models.CharField(max_length=20, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=50, blank=True, null=True)
    email = models.EmailField(max_length=254, blank=True, null=True)
    contact_person_name = models.CharField(max_length=255, blank=True, null=True)
    contact_person_phone = models.CharField(max_length=50, blank=True, null=True)
    contact_person_email = models.EmailField(max_length=254, blank=True, null=True)
    bank_name = models.CharField(max_length=255, blank=True, null=True)
    bank_address = models.CharField(max_length=255, blank=True, null=True)
    bank_account_no = models.CharField(max_length=100, blank=True, null=True)
    bank_iban = models.CharField(max_length=100, blank=True, null=True)
    bank_bic = models.CharField(max_length=50, blank=True, null=True)
    bank_owner = models.CharField(max_length=255, blank=True, null=True, help_text=_("Bank account holder name"))

    # Entity 자체의 역할을 나타내는 필드 (사용자 요청 사항 반영)
    # 이 필드는 해당 Entity가 시스템에 등록될 때 또는 정보가 업데이트될 때
    # 어떤 유형의 거래 파트너로 주로 간주되는지를 나타냅니다.
    entity_general_role = models.CharField(
        max_length=15, # 'both' 와 같은 값을 고려하여 길이 조절
        choices=ROLE_CHOICES,
        blank=True, # 파싱 데이터에서 직접 이 정보가 오지 않을 수 있으므로
        null=True,  # 데이터베이스에서 NULL을 허용하거나, default 값을 설정할 수 있습니다.
                    # 예: default='other'
        help_text=_("The general role of this entity (e.g., primarily an issuer, receiver, or can be both). This is a characteristic of the entity itself.")
    )
    # 이 필드 값 설정 로직:
    # - 파싱된 데이터에서 'issuer'로 등장한 Entity는 이 필드를 'issuer'로 설정.
    # - 'receiver'로 등장한 Entity는 'receiver'로 설정.
    # - 만약 동일 Entity가 여러 문서에서 다른 역할로 등장하는 경우,
    #   'both'로 업데이트하거나, 가장 최근 역할 또는 첫 번째 역할 유지 등 정책 필요.

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name or self.regi_no or str(self.id)

    class Meta:
        verbose_name = _("Entity")
        verbose_name_plural = _("Entities")
        # db_table = 'accounting_entity' # 주석 처리된 테이블명. Django는 기본적으로 '앱이름_모델명소문자' (accounting_entity)로 생성.
                                         # 만약 'accounting_entities'와 같이 복수형을 원하면 주석 해제하고 이름 지정.
                                         # 현재는 issuer/receiver 표시 필드가 모델 필드로 추가되었습니다.

class TransactionDocument(models.Model):
    # --- 기존 필드들 시작 ---
    uploaded_file = models.OneToOneField(
        UploadedFile,
        on_delete=models.CASCADE,
        related_name='parsed_document',
        help_text=_("The uploaded file from which this document was parsed.")
    )
    tran_doc_id_parsed = models.CharField(max_length=255, blank=True, null=True, help_text=_("Parsed transaction document ID, if any."))
    document_type = models.CharField(max_length=100, blank=True, null=True, help_text=_("Type of the document (e.g., invoice, credit_note) from OCR/parsing.")) # 기존 문서 유형
    invoice_no = models.CharField(max_length=255, blank=True, null=True, help_text=_("Invoice number."))
    reference_no = models.CharField(max_length=255, blank=True, null=True, help_text=_("Reference number."))
    internal_order_no = models.CharField(max_length=255, blank=True, null=True)
    external_order_no = models.CharField(max_length=255, blank=True, null=True)
    issuance_date = models.DateField(blank=True, null=True, help_text=_("Date when the document was issued (e.g., invoice date).")) # 기존 발행일
    service_date = models.DateField(blank=True, null=True, help_text=_("Date when the service was rendered."))
    delivery_date = models.DateField(blank=True, null=True)
    cp_memo = models.TextField(blank=True, null=True, help_text=_("Counterparty memo."))
    payment_terms = models.CharField(max_length=255, blank=True, null=True)
    due_date = models.DateField(blank=True, null=True)
    currency = models.CharField(max_length=10, blank=True, null=True)
    net_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, help_text=_("Total net amount of the document."))
    vat_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, help_text=_("Total VAT amount of the document."))
    vat_rate = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text=_("VAT rate (e.g., 10.00 for 10%)."))
    total_due = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, help_text=_("Total amount due."))
    prepayment = models.BooleanField(blank=True, null=True)
    prepaid_amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    price_discount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    price_discount_terms = models.CharField(max_length=255, blank=True, null=True)
    transaction_summary = models.TextField(blank=True, null=True)
    issuer = models.ForeignKey(
        Entity,
        related_name='issued_documents',
        on_delete=models.PROTECT,
        blank=True, null=True,
        help_text=_("The issuer of this document.")
    )
    receiver = models.ForeignKey(
        Entity,
        related_name='received_documents',
        on_delete=models.PROTECT,
        blank=True, null=True,
        help_text=_("The receiver of this document.")
    )
    main_trading_partner_role = models.CharField(
        max_length=10,
        choices=Entity.ROLE_CHOICES, # Entity 모델에 정의된 ROLE_CHOICES 사용
        blank=True, null=True,
        help_text=_("Indicates which party is considered the main trading partner.")
    )
    # --- 기존 필드들 끝 ---

    # --- 요청하신 추가 필드들 시작 ---
    booking_document_no = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Booking Document Number, assigned during accounting entry.")
    )

    # 'Transaction Doc. Type' 필드 (기존 document_type과 구분)
    # 만약 기존 document_type이 이 역할을 한다면 이 필드는 필요 없을 수 있습니다.
    # 여기서는 사용자의 요청대로 별도 필드로 추가합니다.
    accounting_transaction_doc_type = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text=_("Specific type of the transaction document for accounting purposes (e.g., Standard Invoice, Debit Memo).")
        # choices=[(...)] 등을 사용하여 선택지를 제공할 수 있습니다.
    )

    booking_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date when the transaction was booked into the accounting system.")
    )

    closing_period = models.IntegerField(
        blank=True,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text=_("The accounting closing period (month, 1-12) for this transaction.")
    )

    # 회계 기준 선택지를 위한 예시 (실제 필요한 기준으로 수정/추가 가능)
    LEDGER_STANDARD_CHOICES = [
        ('IFRS', _('International Financial Reporting Standards')),
        ('K-GAAP', _('Korean Generally Accepted Accounting Principles')),
        ('US-GAAP', _('United States Generally Accepted Accounting Principles')),
        ('OTHER', _('Other')),
    ]
    ledger_standard = models.CharField(
        max_length=50, # 선택지 값의 길이에 맞춰 조정
        choices=LEDGER_STANDARD_CHOICES,
        blank=True,
        null=True,
        help_text=_("The accounting ledger standard applied to this transaction.")
    )
    # --- 요청하신 추가 필드들 끝 ---

    # 'To confirm'이 'Confirmed'보다 먼저 정렬되도록 키 값 조정
    STATUS_CHOICES = [
        ('1_TO_CONFIRM', _('To confirm')),  # 키 값을 변경하여 정렬 순서 제어
        ('2_CONFIRMED', _('Confirmed')),
    ]
    status = models.CharField(
        max_length=15,  # '1_TO_CONFIRM' 길이에 맞춰 조정
        choices=STATUS_CHOICES,
        default='1_TO_CONFIRM',  # 기본 상태를 'To confirm'으로 설정
        blank=True,  # 필요에 따라 False로 변경 가능
        null=True,  # 필요에 따라 False로 변경 가능
        help_text=_("Status of the transaction document.")
    )
    confirmation_date = models.DateField(
        blank=True,
        null=True,
        help_text=_("Date when the document was confirmed.")
    )

    # OUTPUT_SCHEMA에 추가된 anomaly_memo 필드
    anomaly_memo = models.TextField(
        blank=True,
        null=True,
        help_text=_(
            "Notes on any detected anomalies, exceptions, or inconsistencies found during invoice processing. Max 255 chars advised for prompt, but TextField allows more.")
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        doc_identifier = self.invoice_no or self.tran_doc_id_parsed or str(self.id)
        doc_type = self.document_type or "Document"
        # get_status_display()를 사용하여 사람이 읽기 좋은 형태로 상태 표시
        return f"{doc_type} {doc_identifier} ({self.get_status_display()})"

    class Meta:
        verbose_name = _("Transaction Document")
        verbose_name_plural = _("Transaction Documents")
        # status: 'To confirm' (1_TO_CONFIRM)이 'Confirmed' (2_CONFIRMED) 보다 먼저 오도록 정렬
        # -confirmation_date: 최신 확인일 순
        # -issuance_date: 최신 발행일 순
        # -created_at: 최신 생성일 순
        ordering = ['status', '-confirmation_date', '-issuance_date', '-created_at']


class TransactionLineItem(models.Model):
    document = models.ForeignKey(
        TransactionDocument,
        related_name='line_items',
        on_delete=models.CASCADE, # 문서 삭제 시 관련 항목들도 삭제. 필요에 따라 PROTECT 등으로 변경 가능
        null=True,  # <<< 이 부분을 추가하여 null 값을 허용합니다.
        blank=True, # <<< 폼 유효성 검사 시 비워둘 수 있도록 보통 함께 추가합니다.
        help_text=_("The transaction document this line item belongs to.")
    )
    # ... (line_item_id_parsed 등 TransactionLineItem의 나머지 필드들은 그대로 유지) ...
    line_item_id_parsed = models.CharField(max_length=255, blank=True, null=True, help_text=_("Parsed line item ID, if any."))
    article_no = models.CharField(max_length=255, blank=True, null=True, help_text=_("Article number or code."))
    article_name = models.CharField(max_length=255, blank=True, null=True, help_text=_("Name of the article or service."))
    article_description = models.TextField(blank=True, null=True, help_text=_("Detailed description of the article/service."))
    quantity = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True)
    unit_price = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, help_text=_("Price per unit."))
    amount = models.DecimalField(max_digits=19, decimal_places=4, blank=True, null=True, help_text=_("Total amount for this line item (quantity * unit_price)."))
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        item_identifier = self.article_name if self.article_name else self.article_no
        # document가 null일 수 있으므로, document_id 대신 self.document.id 접근 시 주의
        doc_id_str = str(self.document.id) if self.document else "N/A"
        return f"Line Item {self.id} for Doc {doc_id_str}: {item_identifier}"

    class Meta:
        verbose_name = _("Transaction Line Item")
        verbose_name_plural = _("Transaction Line Items")
        ordering = ['id']

class TransactionDetail(models.Model):
    """
    Stores detailed accounting entries or lines related to a TransactionDocument.
    For example, GL posting lines (debits/credits).
    """
    transaction_document = models.ForeignKey(
        'TransactionDocument',  # 문자열로 참조하여 정의 순서에 덜 민감하게 만듦
        related_name='details', # TransactionDocument 객체에서 .details.all() 등으로 접근 가능
        on_delete=models.CASCADE, # 주 문서가 삭제되면 상세 정보도 함께 삭제
        help_text=_("The main transaction document this detail line belongs to.")
    )

    gl_account_no = models.CharField(
        max_length=50, # 계정 번호의 일반적인 길이에 맞춰 조정 가능
        help_text=_("GL Account No. (General Ledger Account Number).")
    )
    gl_account_description = models.CharField(
        max_length=255,
        blank=True, # 계정 번호로 조회가 가능하다면 설명은 선택적일 수 있음
        null=True,
        help_text=_("GL Account Description.")
    )
    position_no = models.PositiveIntegerField( # 항목 순번, 양수
        blank=True,
        null=True,
        help_text=_("Position or line number for ordering within the document's details.")
    )

    # 요청하신 'position' 필드: 차변(Debit) 또는 대변(Credit)을 나타냄
    ENTRY_TYPE_CHOICES = [
        ('debit', _('Debit')),
        ('credit', _('Credit')),
    ]
    position = models.CharField(  # 필드명을 사용자 요청대로 'position'으로 사용
        max_length=10,  # 'credit'이 6자이므로 약간의 여유
        choices=ENTRY_TYPE_CHOICES,
        # 일반적으로 차변/대변 구분은 필수이므로 blank=False, null=False가 적절할 수 있습니다.
        # 데이터 제공 방식에 따라 blank=True, null=True로 두거나, default 값을 설정할 수 있습니다.
        # 여기서는 우선 blank=True, null=True로 두겠습니다. 필요시 조정해주세요.
        blank=True,
        null=True,
        help_text=_("Indicates if this line is a Debit or Credit entry.")
    )

    currency = models.CharField(
        max_length=3, # 예: "KRW", "USD"
        blank=True, # 비워두면 상위 TransactionDocument의 통화를 따를 수 있음
        null=True,
        help_text=_("Currency for the amount in this line. If blank, may inherit from parent document.")
    )
    amount = models.DecimalField(
        max_digits=19, # 총 자릿수
        decimal_places=4, # 소수점 이하 자릿수 (필요에 따라 조정)
        help_text=_("Amount for this detail line. Could be debit or credit.")
    )
    # 참고: 실제 회계 분개라면 차변(Debit)/대변(Credit)을 구분하는 필드가 필요할 수 있습니다.
    # 예: entry_type = models.CharField(max_length=1, choices=[('D', 'Debit'), ('C', 'Credit')])

    tax_code = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text=_("Tax code relevant to this line item.")
    )
    description = models.TextField( # 여러 줄의 상세 설명을 위해 TextField 사용
        blank=True,
        null=True,
        help_text=_("Additional description for this transaction detail line.")
    )

    # 타임스탬프
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        # self.transaction_document가 로드되지 않았거나 없을 경우를 대비
        doc_id_str = str(self.transaction_document.id) if self.transaction_document_id else "N/A"
        return f"Detail for Doc {doc_id_str} - GL: {self.gl_account_no}, Amount: {self.amount}"

    class Meta:
        verbose_name = _("Transaction Detail")
        verbose_name_plural = _("Transaction Details")
        ordering = ['transaction_document', 'position_no', 'id'] # 기본 정렬 순서 예시
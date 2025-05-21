# accounting/models/coa.py
from django.db import models
from accounting.models.coa_classification import COAClassification

class ChartOfAccount(models.Model):
    code                 = models.CharField(max_length=20, unique=True)   # GL Account No.
    ledger               = models.CharField(max_length=30, blank=True, null=True)
    statement            = models.CharField(max_length=30, blank=True, null=True)

    # 변경 부분: ForeignKey( to_field='code' ) 사용
    coa_classification = models.ForeignKey(
        COAClassification,
        to_field='code',  # COAClassification의 code 필드로 연결
        db_column='coa_classification',  # DB 컬럼명을 그대로 'coa_classification'로 사용
        on_delete=models.DO_NOTHING,  # 필요에 따라 다른 옵션도 가능
        blank=True,
        null=True,
        related_name='chart_accounts'  # (옵션) 역참조 시 사용: e.g. classification.chart_accounts.all()
    )

    activation           = models.BooleanField(default=True)              # Y/N → True/False

    # 기본(EN) 설명
    desc_long_en         = models.CharField(max_length=255, blank=True)
    desc_short_en        = models.CharField(max_length=100, blank=True)

    # 독어 설명
    desc_long_de         = models.CharField(max_length=255, blank=True)
    desc_short_de        = models.CharField(max_length=100, blank=True)

    class Meta:
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} – {self.desc_long_en or self.desc_long_de}"


# accounting/models/__init__.py
from .coa import ChartOfAccount
__all__ = ["ChartOfAccount"]

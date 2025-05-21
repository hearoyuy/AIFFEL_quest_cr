# accounting/services/coa_cache.py
from accounting.models import CoaClassification, ChartOfAccount
from django.db.models import F

def get_active_cats_and_codes():
    """
    {
      "PL_3_1": {
          "label": "Advertising",
          "group": "Operating Expense",
          "codes": [                        # ← 실제 GL 번호 & 설명
              {"gl_no": "6110", "desc": "Advertising expense"},
              …
          ]
      },
      …
    }
    """
    cats = (CoaClassification.objects
            .values("code", "group", "label")          # code = PL_3_1
            .order_by("code"))

    gl_rows = (ChartOfAccount.objects
               .filter(activation=True)
               .values(
                   gl_no     = F("gl_account_no"),      # 숫자 계정번호
                   cat_code  = F("category"),           # PL_3_1
                   desc      = F("desc_long_en"),
               ))

    by_cat = {c["code"]: {"label": c["label"],
                          "group": c["group"],
                          "codes": []}
              for c in cats}

    for r in gl_rows:
        bucket = by_cat.get(r["cat_code"])
        if bucket is not None:
            bucket["codes"].append(
                {"gl_no": r["gl_no"], "desc": r["desc"]}
            )

    return by_cat

import pandas as pd
from django.contrib import admin, messages
from django.urls import path, reverse
from django.shortcuts import redirect, render
from django.core.management import call_command

from accounting.forms.coa_import import COAImportForm
from accounting.models import ChartOfAccount
from accounting.models import COAClassification


# ──────────────────────────────────────────────
# helper
# ──────────────────────────────────────────────
def clean(val: str | float | int) -> str:
    """NaN/None → 빈 문자열, 나머지는 str + strip"""
    return "" if pd.isna(val) else str(val).strip()


def get_sheet_case_insensitive(xls_dict: dict, key: str):
    """
    시트명을 대소문자·공백 무시하고 찾는다.
    없으면 None.
    """
    key = key.strip().lower()
    for name, df in xls_dict.items():
        if name.strip().lower() == key:
            return df
    return None


# ──────────────────────────────────────────────
# Admin
# ──────────────────────────────────────────────
@admin.register(ChartOfAccount)
class ChartOfAccountAdmin(admin.ModelAdmin):
    """Chart of Account admin + Excel import + FAISS 재빌드"""

    list_display  = [f.name for f in ChartOfAccount._meta.fields]
    list_editable = ("ledger", "coa_classification", "activation")
    search_fields = ("code", "desc_long_en", "desc_long_de")

    # ── extra URL ──────────────────────────────
    def get_urls(self):
        urls = super().get_urls()
        extra = [
            path("import/",         self.admin_site.admin_view(self.import_view),        name="coa_import"),
            path("rebuild-index/",  self.admin_site.admin_view(self.rebuild_index_view), name="coa_rebuild_index"),
        ]
        return extra + urls

    change_list_template = "admin/coa_change_list.html"

    def changelist_view(self, request, extra_context=None):
        extra = extra_context or {}
        extra["import_url"]  = reverse("admin:coa_import")
        extra["rebuild_url"] = reverse("admin:coa_rebuild_index")
        return super().changelist_view(request, extra)

    # ── Excel import ───────────────────────────
    def import_view(self, request):
        """
        Excel 업로드:
        • 시트  “Class” → COAClassification (헤더 없음, code/group/label 순)
        • 시트  “List”  → ChartOfAccount
             ├── 1행  헤더
             └── 2행~ 데이터
        FK: List!B열 “COA Classification” ⇢ COAClassification.code
        """
        if request.method == "POST":
            form = COAImportForm(request.POST, request.FILES)
            if not form.is_valid():
                return render(request, "admin/coa_import.html", {"form": form})

            # wipe option
            if form.cleaned_data.get("clear_existing"):
                ChartOfAccount.objects.all().delete()
                COAClassification.objects.all().delete()

            # ── load excel ───────────────────────
            xls  = form.cleaned_data["file"]
            data = pd.read_excel(xls, sheet_name=None)

            # ── 1) Class 시트 → COAClassification ─
            class_df = get_sheet_case_insensitive(data, "class")
            if class_df is None and len(data) >= 2:  # fallback: 두 번째 시트
                class_df = list(data.values())[1]

            new_class_cnt = 0
            if class_df is not None and not class_df.empty:
                class_df = class_df.iloc[:, :3].copy()
                class_df.columns = ["code", "group", "label"]
                class_df = class_df.dropna(subset=["code"]).fillna("")
                classifications = [
                    COAClassification(
                        code=clean(r.code),
                        group=clean(r.group),
                        label=clean(r.label),
                    )
                    for r in class_df.itertuples(index=False)
                ]
                COAClassification.objects.bulk_create(classifications, ignore_conflicts=True)
                new_class_cnt = len(classifications)

            # ── 2) List 시트 → ChartOfAccount ────
            # ① 먼저 시트를 찾아보고
            list_df = get_sheet_case_insensitive(data, "list")

            # ② 못 찾았을 때만 대체 시트를 지정
            if list_df is None:
                list_df = next(iter(data.values()))
            list_df.columns = list_df.columns.str.strip()
            if len(list_df) > 1:               # 2행부터 데이터
                list_df = list_df.iloc[1:]

            # 필수 컬럼 검증
            required = {"GL Account No.", "COA Classification"}
            missing  = required - set(list_df.columns)
            if missing:
                raise ValueError(f"❌ 엑셀에 누락된 컬럼: {', '.join(missing)}")

            coa_objs = []
            for _, row in list_df.iterrows():
                code = clean(row["COA Classification"])
                coa_class = COAClassification.objects.filter(code=code).first() if code else None

                coa_objs.append(
                    ChartOfAccount(
                        code=clean(row["GL Account No."]),
                        ledger=clean(row.get("Ledger")),
                        statement=clean(row.get("Statement")),
                        coa_classification=coa_class,
                        activation=str(row.get("Activation", "Y")).upper().startswith("Y"),
                        desc_long_en=clean(row.get("Description Long (EN)")),
                        desc_short_en=clean(row.get("Description Short (EN)")),
                        desc_long_de=clean(row.get("Description Long (DE)")),
                        desc_short_de=clean(row.get("Description Short (DE)")),
                    )
                )

            ChartOfAccount.objects.bulk_create(coa_objs, ignore_conflicts=True)

            messages.success(
                request,
                f"✅ COA {len(coa_objs)}건 / Classification {new_class_cnt}건 가져오기 완료"
                + (" (기존 데이터 삭제 후 재삽입)" if form.cleaned_data.get("clear_existing") else "")
            )
            return redirect("..")

        else:
            form = COAImportForm()

        return render(request, "admin/coa_import.html", {"form": form})

    # ── FAISS 재빌드 ───────────────────────────
    actions = ["rebuild_index_action"]

    def rebuild_index_action(self, request, queryset):
        self._rebuild_index()
        self.message_user(request, "FAISS 인덱스가 재생성되었습니다.")
    rebuild_index_action.short_description = "Rebuild FAISS index"

    def rebuild_index_view(self, request):
        self._rebuild_index()
        messages.success(request, "FAISS 인덱스가 재생성되었습니다.")
        return redirect("..")

    @staticmethod
    def _rebuild_index():
        call_command("build_coa_index", dst="media/vector/coa_index")

from django import forms


class COAImportForm(forms.Form):
    file = forms.FileField(
        label="Excel (.xlsx)",
        help_text="list / class 시트가 들어있는 파일"
    )
    clear_existing = forms.BooleanField(
        required=False,
        label="Delete existing data first"
    )

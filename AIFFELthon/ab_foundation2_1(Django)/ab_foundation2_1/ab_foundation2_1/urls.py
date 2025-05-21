from django.contrib import admin
from django.urls import path
from accounting.views.upload_view import upload_view, upload_success_view
from accounting.views import home
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views  # ← 이거 추가
from accounting.views.parser_view import parser_view   # 상단 import
from accounting.views.parser_view import parse_invoice_view
from accounting.views.account_mapping_view import match_account_view
from accounting.views.journal_view import journal_view, journal_entry_form_view, get_document_data_api
from accounting.views.fs.profit_and_loss_view import profit_and_loss_view
from accounting.views.fs.financial_position_view import financial_position_view
from django.conf.urls.static import static # ←★ 새로 추가

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home, name="home"),
    path("upload/", upload_view, name="upload"),
    path("upload/success/", upload_success_view, name="upload_success"),
    path("accounts/login/", auth_views.LoginView.as_view(), name="login"),  # ← 이거 추가
    path("parser/", parser_view, name="parser"),
    path("parser/api/parse/", parse_invoice_view, name="parse_invoice"),
    path('match_account/', match_account_view, name='match_account'),
    path('journal/', journal_view, name='journal'),
    path('profit-and-loss/', profit_and_loss_view, name='profit_and_loss'),
    path('financial-position/', financial_position_view, name='financial_position'),
    path('journal/api/get-data/<int:document_id>/', get_document_data_api, name='get_document_data_api'),
    path('journal/entry/<int:document_id>/', journal_entry_form_view, name='journal_entry_form_view'),
]

# 📦 업로드된 파일 미디어 경로 설정 (개발용)
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.shortcuts import render
from django.contrib.auth.decorators import login_required # 로그인 사용자만 접근하도록
from accounting.models.uploaded_file import UploadedFile # UploadedFile 모델 import

@login_required # 로그인한 사용자만 이 뷰에 접근할 수 있도록 설정 (선택 사항)
def home(request):
    # --- Invoices 데이터 계산 ---
    # 전체 업로드된 인보이스 수
    total_invoices_uploaded = UploadedFile.objects.count()

    # 처리되지 않은 인보이스 수 (to confirm)
    invoices_to_confirm = UploadedFile.objects.filter(is_processed=False).count()

    # 처리된 인보이스 수 (confirmed)
    invoices_confirmed = UploadedFile.objects.filter(is_processed=True).count()
    # 또는 invoices_confirmed = total_invoices_uploaded - invoices_to_confirm

    # --- To-Do Lists 데이터 구성 ---
    todo_items_data = [
        {
            'name': 'Invoices',
            'uploaded': total_invoices_uploaded, # 실제 계산된 값
            'confirmed': invoices_confirmed,    # 실제 계산된 값
            'to_confirm': invoices_to_confirm,  # 실제 계산된 값
            'uploaded_text': None,
            'cleared': None, # 'cleared' 로직은 현재 모델에 없음
            'to_clear': None, # 'to_clear' 로직은 현재 모델에 없음
            'customers_created': None, # Customer 관련 로직은 별도 모델 필요
            'customer_to_check_count': None,
            'masters_created': None, # Master Data 관련 로직은 별도 모델 필요
            'article_to_check_text': None,
            'bookings_created': None, # Manual Booking 관련 로직은 별도 모델 필요
            'booking_approved': None,
            'booking_to_approve_count': None,
        },
        {
            'name': 'Bank Statements',
            # 'uploaded_text': '9 uploaded (till 9th MAR.)', # 이 부분은 실제 데이터 소스 필요
            # 'confirmed': 2,
            # 'to_confirm': 2,
            # 'cleared': 7,
            # 'to_clear': 2,
            # 예시 데이터 또는 실제 데이터 로직 추가 필요
            'uploaded': None, # Bank Statements 관련 모델 및 로직 필요
            'confirmed': None,
            'to_confirm': None,
            'cleared': None,
            'to_clear': None,
            'uploaded_text': "데이터 로딩 필요", # 임시 메시지
            'customers_created': None,
            'customer_to_check_count': None,
            'masters_created': None,
            'article_to_check_text': None,
            'bookings_created': None,
            'booking_approved': None,
            'booking_to_approve_count': None,
        },
        {
            'name': 'Contracts',
            # 'uploaded': 3, # 예시 값
            # 'confirmed': 2,
            # 'to_confirm': 1,
            'uploaded': None, # Contracts 관련 모델 및 로직 필요
            'confirmed': None,
            'to_confirm': None,
            'uploaded_text': "데이터 로딩 필요", # 임시 메시지
            'cleared': None,
            'to_clear': None,
            'customers_created': None,
            'customer_to_check_count': None,
            'masters_created': None,
            'article_to_check_text': None,
            'bookings_created': None,
            'booking_approved': None,
            'booking_to_approve_count': None,
        },
        {
            'name': 'Master Data',
            # 'customers_created': 2,
            # 'customer_to_check_count': 1,
            # 'masters_created': 2,
            # 'article_to_check_text': '1 article number to check, 1 asset number to check',
            'customers_created': None, # Master Data (Customer) 관련 모델 및 로직 필요
            'customer_to_check_count': None,
            'masters_created': None, # Master Data (General) 관련 모델 및 로직 필요
            'article_to_check_text': "데이터 로딩 필요", # 임시 메시지
            'uploaded': None,
            'confirmed': None,
            'to_confirm': None,
            'cleared': None,
            'to_clear': None,
            'uploaded_text': None,
            'bookings_created': None,
            'booking_approved': None,
            'booking_to_approve_count': None,
        },
        {
            'name': 'Manual Booking',
            # 'bookings_created': 3,
            # 'booking_approved': 2,
            # 'booking_to_approve_count': 1,
            'bookings_created': None, # Manual Booking 관련 모델 및 로직 필요
            'booking_approved': None,
            'booking_to_approve_count': None,
            'uploaded': None,
            'confirmed': None,
            'to_confirm': None,
            'cleared': None,
            'to_clear': None,
            'uploaded_text': None,
            'customers_created': None,
            'customer_to_check_count': None,
            'masters_created': None,
            'article_to_check_text': None,
        }
    ]

    # --- Account 정보 데이터 (이 부분은 사용자에 따라 다를 수 있음) ---
    # 예시: 현재 로그인한 사용자의 회사 정보 등을 가져오는 로직
    # 실제로는 request.user를 사용하여 관련 회사 정보를 가져오거나,
    # 다른 방식으로 계정 정보를 설정해야 합니다.
    account_info_data = {
        'company_name': 'Aiffel AI GmbH', # 실제 데이터로 교체 필요
        'client_no': 'DE000001',   # 실제 데이터로 교체 필요
        'user_id': request.user.username if request.user.is_authenticated else 'Guest',
        'service_level': 'Level 1', # 실제 데이터로 교체 필요
        'transactions_month': UploadedFile.objects.filter(uploaded_by=request.user if request.user.is_authenticated else None).count() if request.user.is_authenticated else 0 # 예시: 현재 사용자가 업로드한 파일 수
    }

    context = {
        'todo_items': todo_items_data,
        'account_info': account_info_data,
    }
    return render(request, "accounting/home.html", context)
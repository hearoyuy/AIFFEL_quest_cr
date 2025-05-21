from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
# TransactionDocument 모델의 정확한 경로로 수정해야 합니다.
# 예: from accounting.models import TransactionDocument (프로젝트 구조에 따라 다름)
# 사용자가 제공한 경로: from accounting.models.parsed_invoice_data import TransactionDocument
from accounting.models.parsed_invoice_data import TransactionDocument, Entity, TransactionDetail
from django.db.models import Q
from django.http import JsonResponse
from django.conf import settings # settings 사용을 위해 import
import json
import pathlib
import logging # 로깅을 위해 logging 모듈 import
from decimal import Decimal # Decimal 타입 처리를 위해 import
from django.db import transaction
from django.urls import reverse
from urllib.parse import urlencode
from accounting.models.uploaded_file import UploadedFile # UploadedFile 모델 import
from django.utils import timezone # timezone.now() 사용을 위해
from django.contrib import messages

# 로거 설정 (필요하다면 settings.py에서 더 상세히 설정)
logger = logging.getLogger(__name__)

def journal_view(request):
    # select_related 또는 prefetch_related를 사용하여 성능 최적화
    document_list = TransactionDocument.objects.select_related('uploaded_file').all().order_by('-updated_at')

    # 검색 기능
    search_query = request.GET.get('search_query', None)
    if search_query:
        document_list = document_list.filter(
            Q(invoice_no__icontains=search_query) |
            Q(reference_no__icontains=search_query) |
            Q(tran_doc_id_parsed__icontains=search_query) |
            Q(booking_document_no__icontains=search_query) |
            Q(document_type__icontains=search_query) |
            # UploadedFile 모델의 필드 검색 추가 (TransactionDocument.uploaded_file 관계 사용)
            Q(uploaded_file__original_filename__icontains=search_query) | # Your File Name
            Q(uploaded_file__abf_filename__icontains=search_query)       # ABF File Name
        )

    # 필터링 기능 (상태)
    status_filter = request.GET.get('status', None)
    if status_filter:
        document_list = document_list.filter(status=status_filter)

    # 필터링 기능 (문서 유형)
    doc_type_filter = request.GET.get('doc_type', None)
    if doc_type_filter:
        document_list = document_list.filter(document_type=doc_type_filter)

    # 페이징 처리
    page = request.GET.get('page', 1)
    # 페이지당 항목 수는 필요에 따라 조정 (예: 10)
    items_per_page = request.GET.get('items_per_page', 10)
    try:
        items_per_page = int(items_per_page)
        if items_per_page <= 0 or items_per_page > 100: # 너무 작거나 큰 값 방지
            items_per_page = 10
    except ValueError:
        items_per_page = 10

    paginator = Paginator(document_list, items_per_page)

    try:
        documents = paginator.page(page)
    except PageNotAnInteger:
        documents = paginator.page(1)
    except EmptyPage:
        documents = paginator.page(paginator.num_pages)

    # 문서 유형 선택지를 위한 로직 (필요시 활성화)
    doc_type_choices = TransactionDocument.objects.filter(document_type__isnull=False)\
                                               .values_list('document_type', flat=True)\
                                               .distinct().order_by('document_type')

    context = {
        'documents': documents,
        'status_choices': TransactionDocument.STATUS_CHOICES,
        'doc_type_choices': doc_type_choices, # 문서 유형 선택지 추가
        'current_search_query': search_query or "",
        'current_status_filter': status_filter or "",
        'current_doc_type_filter': doc_type_filter or "",
        'current_items_per_page': items_per_page,
        'uploaded_file_url': None,
    }
    return render(request, 'accounting/journal.html', context)


# @transaction.atomic # 트랜잭션 데코레이터 제거 또는 주석 처리
@transaction.atomic # ★★★ 함수 전체를 하나의 원자적 트랜잭션으로 처리 ★★★
def clear_and_prepare_for_reparse(document_id: int) -> bool:
    """
    특정 TransactionDocument 레코드 자체를 삭제하고,
    연결된 UploadedFile의 상태를 업데이트하여 재분석 준비를 합니다.
    TransactionDetail은 TransactionDocument 삭제 시 on_delete=models.CASCADE에 의해 자동 삭제됩니다.
    모든 작업은 하나의 트랜잭션으로 처리됩니다.
    성공 시 True를 반환하고, 오류 발생 시 예외를 발생시켜 롤백을 유도합니다.
    """
    logger.info(f"--- Starting clear_and_prepare_for_reparse (DELETE TransactionDocument) for document ID: {document_id} ---")
    try:
        # 1. 대상 TransactionDocument 객체 가져오기 (UploadedFile과 함께)
        document_to_delete = get_object_or_404(
            TransactionDocument.objects.select_related('uploaded_file'),
            pk=document_id
        )
        logger.info(f"Retrieved document for deletion: ID={document_to_delete.id}")

        # (선택 사항) 삭제 전, 연결된 UploadedFile 객체를 미리 변수에 할당 (삭제 후 접근 불가)
        uploaded_file_instance = document_to_delete.uploaded_file
        uploaded_file_id_for_log = uploaded_file_instance.id if uploaded_file_instance else None


        # 2. TransactionDocument 레코드 삭제 (DELETE)
        #    TransactionDetail은 on_delete=models.CASCADE에 의해 자동으로 함께 삭제됩니다.
        document_to_delete.delete()
        logger.info(f"TransactionDocument ID {document_id} (and related TransactionDetails via CASCADE) successfully deleted from DB.")

        # (선택 사항) DB에서 실제 삭제되었는지 확인 (테스트/디버깅 목적)
        # if not TransactionDocument.objects.filter(pk=document_id).exists():
        #     logger.info(f"Verified: TransactionDocument ID {document_id} no longer exists in DB.")
        # else:
        #     logger.error(f"Verification FAILED: TransactionDocument ID {document_id} STILL EXISTS in DB after delete call! Rolling back.")
        #     raise Exception(f"Failed to delete TransactionDocument {document_id}.")


        # 3. 연결된 UploadedFile의 관련 필드 업데이트 (UPDATE)
        if uploaded_file_instance: # 위에서 미리 할당한 변수 사용
            logger.info(f"Updating UploadedFile ID {uploaded_file_instance.id}...")
            fields_to_update_uf = []

            # UploadedFile의 parsed_json 필드 초기화
            if hasattr(uploaded_file_instance, 'parsed_json'):
                if uploaded_file_instance.parsed_json is not None:
                    uploaded_file_instance.parsed_json = None
                    fields_to_update_uf.append('parsed_json')
                    logger.info(f"  UploadedFile.parsed_json will be reset to None.")

            # UploadedFile의 is_processed 필드를 False로 설정
            if hasattr(uploaded_file_instance, 'is_processed'):
                if uploaded_file_instance.is_processed is True:
                    uploaded_file_instance.is_processed = False
                    fields_to_update_uf.append('is_processed')
                    logger.info(f"  UploadedFile.is_processed will be set to False.")
            else:
                logger.warning(f"  UploadedFile model does not have an 'is_processed' attribute.")

            if fields_to_update_uf:
                uploaded_file_instance.save(update_fields=fields_to_update_uf)
                logger.info(f"UploadedFile ID {uploaded_file_instance.id} saved with updated fields: {fields_to_update_uf}.")
            else:
                logger.info(f"No fields needed updating in UploadedFile ID {uploaded_file_instance.id}.")
        else:
            logger.warning(f"No UploadedFile was linked to the deleted Document ID {document_id}. Skipping UploadedFile update.")


        logger.info(f"--- Successfully finished clear_and_prepare_for_reparse (deleted Doc ID: {document_id}) ---")
        return True # 모든 작업 성공 시 True 반환

    except TransactionDocument.DoesNotExist:
        logger.error(f"Document with ID {document_id} not found for deletion during clear_and_prepare_for_reparse.")
        raise # 예외를 다시 발생시켜 호출부에서 처리하고, @transaction.atomic이 롤백하도록 함
    except UploadedFile.DoesNotExist: # UploadedFile을 직접 가져오려다 발생할 경우 (가능성 낮음)
        logger.error(f"Associated UploadedFile not found for Document ID {document_id} (this should not happen if it was linked).")
        raise
    except Exception as e: # 다른 모든 예기치 않은 오류
        logger.error(f"An unexpected error occurred in clear_and_prepare_for_reparse for document ID {document_id}: {e}", exc_info=True)
        raise # 예외를 다시 발생시켜 @transaction.atomic이 롤백하도록 함

def generate_booking_doc_no(customer_number, year, doc_type_abbr, current_document_id):
    """
    Booking Document Number를 생성합니다.
    형식: 고객번호_YYYY_DOCABBR_일련번호8자리
    일련번호는 (고객번호, 연도, 문서유형 약어)가 동일한 기존 Booking Doc. No. 중
    가장 큰 번호 + 1로 생성됩니다.
    current_document_id_for_context_only는 현재 로직에서는 직접 사용되지 않으나,
    호출부와의 호환성을 위해 남겨둘 수 있습니다.
    """
    # doc_type_abbr는 TransactionDocument의 accounting_transaction_doc_type에서 축약형을 가져옵니다.
    # 실제 값에 따라 정교한 매핑 또는 변환 로직이 필요할 수 있습니다.
    # 예시: "Standard Invoice" -> "SI", "Credit Note" -> "CN"
    # 여기서는 전달된 값을 그대로 사용하거나, 간단한 처리만 합니다.
    doc_type_cleaned = "".join(filter(str.isalnum, doc_type_abbr or "XX"))[:3].upper()

    prefix = f"{customer_number}_{year}_{doc_type_cleaned}_"
    logger.info(f"Generating Booking Doc. No. with prefix: {prefix}")

    # 해당 prefix로 시작하는 기존 Booking Document Number들 중 가장 큰 일련번호 부분을 찾습니다.
    last_booking_doc = TransactionDocument.objects.filter(
        booking_document_no__startswith=prefix
    ).order_by('-booking_document_no').first() # 접두사로 시작하는 것 중 가장 큰 번호 (문자열 정렬)

    next_serial_number = 1
    if last_booking_doc and last_booking_doc.booking_document_no:
        try:
            # 마지막 부분(_ 이후)을 추출하여 정수로 변환
            last_serial_str = last_booking_doc.booking_document_no.split('_')[-1]
            next_serial_number = int(last_serial_str) + 1
            logger.info(f"Last serial number found: {last_serial_str}, next will be: {next_serial_number}")
        except (ValueError, IndexError) as e:
            logger.warning(f"Could not parse serial number from last Booking Doc. No. '{last_booking_doc.booking_document_no}': {e}. Defaulting to 1.")
            # 파싱 실패 시 1부터 시작 (또는 다른 오류 처리)
            next_serial_number = 1 # 또는 다른 안전한 기본값
    else:
        logger.info(f"No existing Booking Doc. No. found with prefix '{prefix}'. Starting serial from 1.")

    # 8자리로 포맷팅 (0으로 채움)
    serial_number_formatted = str(next_serial_number).zfill(8)

    return f"{prefix}{serial_number_formatted}"


def journal_entry_form_view(request, document_id):
    # document_id는 URL 패턴에 의해 항상 제공된다고 가정합니다.
    # related_name 'uploaded_file'을 함께 가져옵니다.
    document = get_object_or_404(TransactionDocument.objects.select_related('uploaded_file'), pk=document_id)

    # GET 요청 시 폼 필드를 채우기 위한 초기 데이터 준비
    # 이 데이터는 Django Form을 사용하거나 템플릿 JS가 직접 사용할 수 있습니다.
    # 여기서는 기존 코드를 유지하며, 실제 데이터 로딩은 JS의 API 호출에 의존할 가능성 높음.
    uploaded_file_url = None
    # document.uploaded_file이 None이 아니고, original_filepath가 FileField이고 값이 있는지 확인
    if document.uploaded_file and document.uploaded_file.original_filepath:
        uploaded_file_url = document.uploaded_file.original_filepath.url

    # --- form_initial_data 구성 (기존 코드 유지) ---
    # 이 데이터는 템플릿 JS가 get_document_data_api를 호출하여 채우는 데이터와 중복될 수 있으므로 주의
    # GET 요청 시 템플릿이 이 데이터를 사용해 초기 폼을 렌더링한다고 가정합니다.
    form_initial_data = {
        'booking_document_no': document.booking_document_no,
        'transaction_doc_type': document.accounting_transaction_doc_type,
        'internal_request_no': document.internal_order_no,
        'transaction_document_date': document.issuance_date, # 날짜 필드는 ISO format 문자열로 변환하는 것이 일반적
        'service_date': document.service_date, # 날짜 필드 변환 필요
        'booking_date': document.booking_date, # 날짜 필드 변환 필요
        'closing_period': f"{document.created_at.year}-{document.closing_period:02d}" if document.closing_period else None,
        'ledger': document.ledger_standard,
        'transaction_summary': document.transaction_summary,
    }

    # POST 요청 처리
    if request.method == 'POST':
        action = request.POST.get('action') # 제출된 폼의 'action' 값 확인

        if action == 'confirm':
            # --- 'Confirm' 로직 ---
            logger.info(f"'Confirm' action triggered for document ID: {document_id}")
            try:
                with transaction.atomic():
                    # 1. "Booking Doc. No." 생성
                    customer_no = settings.CUSTOMER_NUMBER_FOR_BOOKING_DOC  # settings.py에서 가져오기
                    current_year = timezone.now().year
                    # document.accounting_transaction_doc_type에서 약어 추출 (실제 필드 값에 따라 로직 조정 필요)
                    doc_type_abbr_from_form = request.POST.get('accounting_transaction_doc_type',
                                                               document.accounting_transaction_doc_type or "Unknown")

                    # Booking Doc. No.를 이미 가지고 있다면 재생성하지 않거나, 정책에 따라 다르게 처리
                    if not document.booking_document_no:  # 아직 Booking Doc No가 없을 경우에만 생성
                        generated_booking_doc_no = generate_booking_doc_no(
                            customer_no,
                            current_year,
                            doc_type_abbr_from_form,  # 폼에서 넘어온 값을 사용하거나, 기존 document 값 사용
                            document_id  # 일련번호 생성에 현재 문서 ID 사용 (예시)
                        )
                        document.booking_document_no = generated_booking_doc_no
                        logger.info(
                            f"Generated Booking Doc. No.: {document.booking_document_no} for document ID: {document_id}")
                    else:
                        logger.info(
                            f"Booking Doc. No. already exists: {document.booking_document_no}. Skipping generation.")

                    # 2. TransactionDocument 객체 업데이트
                    document.booking_date = timezone.now().date()
                    document.status = '2_CONFIRMED'
                    document.confirmation_date = timezone.now().date()

                    # 폼에서 제출된 다른 TransactionDocument 필드 업데이트
                    # (Django Form을 사용하는 것이 좋습니다)
                    # 예시:
                    document.transaction_summary = request.POST.get('transaction_summary', document.transaction_summary)
                    document.accounting_transaction_doc_type = request.POST.get('accounting_transaction_doc_type',
                                                                                document.accounting_transaction_doc_type)
                    document.internal_order_no = request.POST.get('internal_request_no', document.internal_order_no)
                    # ... (다른 필드들도 request.POST에서 가져와 업데이트) ...

                    # 3. TransactionDetail (라인 아이템) 처리
                    #    (이 부분은 이전 답변에서 언급된 것처럼, 폼 데이터 구조에 맞춰 상세 구현 필요)
                    #    기존 라인 아이템 삭제 후 새로 생성하는 예시:
                    if hasattr(document, 'details'):
                        document.details.all().delete()
                        logger.info(
                            f"Deleted existing transaction details for document ID: {document_id} before adding new ones for confirm.")

                    # request.POST에서 새로운 라인 아이템 정보 파싱 및 생성 로직
                    # (이 부분은 HTML 폼의 name 속성과 일치해야 하며, Django FormSet 사용 권장)
                    # for i in range(1, int(request.POST.get('line_item_count_from_js', 0)) + 1):
                    #     gl_account = request.POST.get(f'line{i}_gl_account_no')
                    #     amount = request.POST.get(f'line{i}_amount')
                    #     position = request.POST.get(f'line{i}_position') # 'debit' or 'credit'
                    #     # ... (다른 라인 필드) ...
                    #     if gl_account and amount and position:
                    #         TransactionDetail.objects.create(
                    #             transaction_document=document,
                    #             gl_account_no=gl_account,
                    #             amount=Decimal(amount),
                    #             position=position,
                    #             # ...
                    #         )
                    logger.warning(
                        "Confirm action: TransactionDetail creation logic from POST data needs robust implementation.")

                    # 4. TransactionDocument 최종 저장
                    document.save()
                    logger.info(
                        f"Document ID: {document_id} confirmed and all changes saved. Booking Doc. No.: {document.booking_document_no}")

                messages.success(request,
                                 f"문서 (ID: {document_id}, Booking No: {document.booking_document_no})가 성공적으로 확정되었습니다.")
                return redirect('journal')

            except Exception as e:
                logger.error(f"Error during 'Confirm' action for document ID {document_id}: {e}", exc_info=True)
                messages.error(request, f"문서 확정 중 오류가 발생했습니다: {e}")
                # (오류 시 context 구성 및 현재 폼 렌더링 로직 - 이전 답변 참조)
                context = {
                    'transaction_document_id': document_id,
                    'uploaded_file_url': uploaded_file_url,  # 이 변수가 정의되어 있어야 함
                    'document': document,
                    'error_message': f"확정 처리 중 오류: {e}"
                }
                return render(request, 'includes/_accounting_journal_form.html', context)

                # ... (elif action == 'reparse': 등 다른 액션 처리) ...

                # GET 요청 시
                # ... (context 구성 및 렌더링 - 이전 답변 참조) ...
            context = {
                'transaction_document_id': document.id,
                'uploaded_file_url': uploaded_file_url,
                'document': document,
            }
            return render(request, 'includes/_accounting_journal_form.html', context)


        elif action == 'delete':
            # --- 'Delete' 로직 ---
            logger.info(f"'Delete' action triggered for document ID: {document_id}. Deleting document.")
            try:
                 doc.delete() # 문서 객체 삭제
                 logger.info(f"Document ID {document_id} deleted.")
                 # 삭제 후 문서 목록 페이지 등으로 리다이렉트
                 # 'journal_list'는 문서 목록 뷰의 URL 이름이라고 가정합니다.
                 return redirect('journal_list')
            except Exception as e:
                 logger.error(f"Error deleting document ID {document_id}: {e}", exc_info=True)
                 # 삭제 오류 발생 시 사용자에게 알림 또는 오류 페이지 렌더링
                 # 오류 메시지를 context에 담아 현재 폼을 다시 렌더링하거나 다른 페이지로 리다이렉트
                 context = {
                      'document': document, # 삭제 실패한 문서 객체 (필요하다면)
                      'error_message': f"문서 삭제 중 오류 발생: {e}",
                      'transaction_document_id': document_id, # 오류 발생 시 현재 ID 유지
                      'uploaded_file_url': uploaded_file_url,
                       # ... 다른 context 데이터 ...
                 }
                 # 'accounting/journal_entry_form.html' 템플릿을 렌더링한다고 가정
                 # Django Form을 사용한다면 form도 다시 넘겨줘야 함
                 return render(request, 'includes/_accounting_journal_form.html', context)


        elif action == 'reparse':
            # --- 'Reparse' 로직 (새로 추가) ---
            logger.info(f"'Reparse' action triggered for document ID: {document_id}. Clearing parsing data.")

            logger.info(f"'Reparse' action triggered for document ID: {document_id}.")
            reparse_success = False
            try:
                # 분리된 함수 호출
                reparse_success = clear_and_prepare_for_reparse(document_id)
            except Exception as e:  # clear_and_prepare_for_reparse에서 예외가 발생할 경우 대비
                logger.error(f"Exception during reparse process for document ID {document_id}: {e}", exc_info=True)
                reparse_success = False  # 명시적으로 실패 처리

            if reparse_success:
                logger.info(f"Reparse preparation for document ID {document_id} successful. Redirecting to parser.")
                try:
                    # 리디렉션 (GET 파라미터 방식 또는 세션 방식 선택)
                    base_parser_url = reverse('parser')  # name='parser'는 path('parser/', ...)
                    query_string = urlencode({'document_id': document_id})
                    parser_url_with_param = f"{base_parser_url}?{query_string}"
                    return redirect(parser_url_with_param)
                except Exception as e_redirect:
                    logger.error(
                        f"Error redirecting to parser after successful reparse prep for document ID {document_id}: {e_redirect}",
                        exc_info=True)
                    # 리디렉션 실패 시 오류 메시지와 함께 현재 폼 페이지 렌더링
                    document = get_object_or_404(TransactionDocument, pk=document_id)  # document 객체가 필요할 수 있음
                    uploaded_file_url = document.uploaded_file.new_filepath.url if document.uploaded_file and document.uploaded_file.new_filepath else None
                    context = {
                        'transaction_document_id': document_id,
                        'uploaded_file_url': uploaded_file_url,
                        'error_message': f"문서 재분석 준비는 완료되었으나, 파서 페이지로 이동 중 오류 발생: {e_redirect}"
                    }
                    return render(request, 'includes/_accounting_journal_form.html', context)
            else:
                # clear_and_prepare_for_reparse 함수가 False를 반환하거나 예외를 발생시킨 경우
                logger.error(f"Reparse preparation FAILED for document ID: {document_id}.")
                document = get_object_or_404(TransactionDocument, pk=document_id)  # document 객체가 필요할 수 있음
                uploaded_file_url = document.uploaded_file.new_filepath.url if document.uploaded_file and document.uploaded_file.new_filepath else None
                context = {
                    'transaction_document_id': document_id,
                    'uploaded_file_url': uploaded_file_url,
                    'error_message': f"문서 ID {document_id} 재분석 준비 중 오류가 발생했습니다. (데이터가 롤백되었을 수 있습니다)"
                }
                return render(request, 'includes/_accounting_journal_form.html', context)


    # --- GET 요청 로직 ---
    # POST 요청 처리 후 리다이렉트되지 않았다면 (예: Confirm 실패 시)
    # 또는 처음 GET 요청으로 페이지 로드 시 실행됩니다.
    logger.info(f"Processing GET request for journal entry form view for document ID: {document_id}")

    # context 데이터는 POST 처리 후에도 폼을 다시 보여줄 때 재사용될 수 있도록 구성
    # 템플릿 _accounting_journal_form.html은 context에서 필요한 데이터를 가져와 폼을 채웁니다.
    # 여기서는 get_document_data_api가 반환하는 형식의 데이터를 직접 전달하지 않고,
    # 템플릿의 JavaScript가 AJAX로 get_document_data_api를 호출하여 데이터를 가져온다고 가정합니다.
    # 따라서 context에는 get_document_data_api 호출에 필요한 document_id 와
    # 파일 URL 등 템플릿 렌더링에 필요한 최소한의 정보만 담습니다.

    context = {
        'transaction_document_id': document.id, # 현재 문서 ID (템플릿 JS가 get_document_data_api 호출 시 사용)
        'uploaded_file_url': uploaded_file_url, # PDF 뷰어용 URL
        # _accounting_journal_form.html 템플릿이나 include된 다른 템플릿이 필요로 하는 context 변수들을 여기에 추가합니다.
        # 예: 'status_choices': getattr(TransactionDocument, 'STATUS_CHOICES', []),
        # 'doc_type_choices': doc_type_choices, # 필요한 경우 위에서 계산하여 포함
        # GET 요청 시 초기 폼 필드를 채우는 데이터 (get_document_data_api 대신 사용될 경우)
        # 'document_data': form_initial_data, # 템플릿이 이 데이터를 기대한다면 추가
    }
    # '_accounting_journal_form.html' 템플릿을 렌더링합니다.
    # 이 템플릿 안에 <div id="mainContentArea">와 <script> 블록이 포함되어 있습니다.
    return render(request, 'includes/_accounting_journal_form.html', context)

# ───────── helpers.py ─────────
def extract_bank_info(entity: Entity | None,
                      raw_party: dict | None) -> dict[str, str | None]:
    """Entity 값이 없으면 OCR-raw 데이터에서 보충.
       · swift 라는 키만 있을 수도 있으므로 bic_swift 에 합친다
       · bank_iban 만 있을 경우 bank_account_no 로 보여 준다 (Raw 데이터 기준)"""
    logger.debug(f"Entering extract_bank_info.")
    logger.debug(f"  Input - entity: {entity}")
    logger.debug(f"  Input - raw_party keys: {raw_party.keys() if raw_party else 'None'}")
    # 디버그 출력에 'bank_iban' 값도 추가하여 확인
    logger.debug(f"  Input - raw_party values (partial): bank_name={raw_party.get('bank_name') if raw_party else None}, bank_bic={raw_party.get('bank_bic') if raw_party else None}, swift={raw_party.get('swift') if raw_party else None}, bank_account_no={raw_party.get('bank_account_no') if raw_party else None}, iban={raw_party.get('iban') if raw_party else None}, bank_iban={raw_party.get('bank_iban') if raw_party else None}")


    # bank_name 계산 (Entity 우선, Raw fallback)
    bank_name = (
        (entity.bank_name if entity and getattr(entity, 'bank_name', None) else None)
        or (raw_party.get("bank_name") if raw_party else None)
    )
    logger.debug(f"  Calculated bank_name: {bank_name}")


    # bic 계산 (Entity 우선, Raw fallback)
    bic = (
        (entity.bank_bic if entity and getattr(entity, 'bank_bic', None) else None)
        or (raw_party.get("bank_bic") if raw_party else None)
        or (raw_party.get("swift") if raw_party else None)
    )
    logger.debug(f"  Calculated bic: {bic}")

    # account 계산 (Entity 우선, Raw fallback) - 'bank_account_no' -> 'bank_iban' 순서
    account = (
        (entity.bank_account_no if entity and getattr(entity, 'bank_account_no', None) else None) # Priority 1: Entity bank_account_no
        or (raw_party.get("bank_account_no") if raw_party else None) # Priority 2: Raw bank_account_no
        or (raw_party.get("bank_iban") if raw_party else None) # Priority 3: Raw bank_iban (수정된 부분)
    )
    # Note: extract_bank_info는 settings를 보지 않음. settings 우선 로직은 views.py에서 처리
    logger.debug(f"  Calculated account: {account}")

    result = {
        "bank": bank_name,
        "bic_swift": bic,
        "bank_account_no": account,
    }
    logger.debug(f"Exiting extract_bank_info. Result: {result}")
    return result


# ───────── views.py (get_document_data_api) ─────────
def get_document_data_api(request, document_id):
    logger.info(f"Fetching document data for document_id: {document_id}")
    # select_related로 연결된 Entity를 가져와야 getattr 사용 시 DB 쿼리 발생 안함
    doc = get_object_or_404(
        TransactionDocument.objects.select_related("issuer", "receiver", "uploaded_file"),
        pk=document_id,
    )
    logger.info(f"Document fetched: {doc.id}")

    # ---------- RAW JSON 읽기 ----------
    raw_json = {}
    try:
        if getattr(doc.uploaded_file, "parsed_json", None):
            raw_json = doc.uploaded_file.parsed_json           # DB 컬럼
            logger.info("Raw JSON read from parsed_json DB column.")
        elif getattr(doc.uploaded_file, "raw_json_path", None):
            raw_json_path = doc.uploaded_file.raw_json_path
            logger.info(f"Attempting to read raw JSON from file path: {raw_json_path}")
            if raw_json_path and pathlib.Path(raw_json_path).exists():
                 try:
                     with open(raw_json_path, 'r', encoding='utf-8') as f:
                         raw_json = json.load(f)
                     logger.info("Raw JSON successfully read from file.")
                 except Exception as file_read_error:
                     logger.error(f"Error reading raw JSON file {raw_json_path}: {file_read_error}")
                     raw_json = {} # 읽기 실패 시 빈 딕셔너리
            else:
                 logger.warning(f"Raw JSON file path does not exist or is invalid: {raw_json_path}")

    except Exception as general_error:
        logger.error(f"Unexpected error during raw JSON reading: {general_error}")
        pass # 못 읽어도 계속 진행

    raw_issuer   : dict = raw_json.get("issuer"  , {}) or {}
    raw_receiver : dict = raw_json.get("receiver", {}) or {}
    logger.debug(f"Raw Issuer data AFTER creation: {raw_issuer}")
    logger.debug(f"Raw Receiver data AFTER creation: {raw_receiver}")


    # ---------- Payee / Payer 결정 ----------
    role = doc.main_trading_partner_role
    payee_ent: Entity | None = None
    payer_ent: Entity | None = None
    payee_raw: dict = {}
    payer_raw: dict = {}
    logger.info(f"Document Role: {role}")

    # Determine which Entity/Raw data corresponds to Payee/Payer based on role
    if role == "issuer":            # (우리가 구매자 ⇒ 돈을 내야 함)
        # Counterparty issued -> They are Payee; We received -> We are Payer
        payee_ent  = doc.issuer # Counterparty Entity (Seller/Payee)
        payer_ent  = doc.receiver # Our Entity (Buyer/Payer)
        payee_raw  = raw_issuer # Raw data for Counterparty (Issuer)
        payer_raw  = raw_receiver # Raw data for Our side (Receiver)
        logger.info("Role is 'issuer': Payee is doc.issuer (Counterparty), Payer is doc.receiver (Our side).")

    elif role == "receiver":        # (우리가 판매자 ⇒ 돈을 받아야 함)
        # We issued -> We are Payee; Counterparty received -> Counterparty is Payer
        payee_ent  = doc.issuer # Our Entity (Seller/Payee)
        payer_ent  = doc.receiver # Counterparty Entity (Buyer/Payer)
        payee_raw  = raw_issuer # Raw data for Our side (Issuer)
        payer_raw  = raw_receiver # Raw data for Counterparty (Receiver)
        logger.info("Role is 'receiver': Payee is doc.issuer (Our side), Payer is doc.receiver (Counterparty).")

    else:                           # - 미지정 ⇒ 기본값: 우리는 판매자 (우리가 돈을 받아야 함)
        # Default to Sales Invoice scenario
        payee_ent  = doc.issuer # Our Entity (Seller/Payee)
        payer_ent  = doc.receiver # Counterparty Entity (Buyer/Payer)
        payee_raw  = raw_issuer # Raw data for Our side (Issuer)
        payer_raw  = raw_receiver # Raw data for Counterparty (Receiver)
        logger.info("Role is undefined, using default 'receiver': Payee is doc.issuer (Our side), Payer is doc.receiver (Counterparty).")

    # Check if settings.OUR_COMPANY_INFO exists and is a dictionary
    has_our_company_info_in_settings = hasattr(settings, 'OUR_COMPANY_INFO') and isinstance(settings.OUR_COMPANY_INFO, dict)
    logger.info(f"has_our_company_info_in_settings: {has_our_company_info_in_settings}")

    # Determine if Payee is our company based on the determined role
    # Payee is our company when role is 'receiver' or default
    is_our_company_payee = (role != "issuer")
    logger.info(f"Determined is_our_company_payee based on role ('{role}'): {is_our_company_payee}")


    # Determine if Payer is our company based on the determined role
    # Payer is our company when role is 'issuer'
    is_our_company_payer = (role == "issuer")
    logger.info(f"Determined is_our_company_payer based on role ('{role}'): {is_our_company_payer}")


    # ---------- Calculate ALL Payment Field Values ----------
    logger.info("--- Calculating All Payment Field Values ---")

    # Get raw data for payee_raw just before extract_bank_info for debugging disappearance
    logger.debug(f"Before calculating bank info. Checking payee_raw['bank_iban']: {payee_raw.get('bank_iban') if payee_raw else 'N/A'}")


    # Get bank info from Entity/Raw as a fallback source (using extract_bank_info)
    # This is called only once now, the results are used as a potential fallback
    bank_dict_from_entities_raw = extract_bank_info(payee_ent, payee_raw)
    logger.debug(f"Bank Info from Entities/Raw (fallback): {bank_dict_from_entities_raw}")


    # Get settings info for our company if available (for primary source)
    our_company_settings_id = settings.OUR_COMPANY_INFO.get("id") if has_our_company_info_in_settings else None
    our_company_settings_name = settings.OUR_COMPANY_INFO.get("name") if has_our_company_info_in_settings else None
    our_company_settings_bank = settings.OUR_COMPANY_INFO.get("bank") if has_our_company_info_in_settings else None
    our_company_settings_bic_swift = settings.OUR_COMPANY_INFO.get("bic_swift") if has_our_company_info_in_settings else None
    our_company_settings_bank_account_no = settings.OUR_COMPANY_INFO.get("bank_account_no") if has_our_company_info_in_settings else None
    # Assuming settings might also have bank_iban key for account number
    our_company_settings_bank_iban = settings.OUR_COMPANY_INFO.get("bank_iban") if has_our_company_info_in_settings else None

    logger.debug(f"Settings Info (partial): ID={our_company_settings_id}, Name={our_company_settings_name}, Bank={our_company_settings_bank}, BIC={our_company_settings_bic_swift}, AccountNo={our_company_settings_bank_account_no}, IBAN={our_company_settings_bank_iban}")


    # Calculate Payee Entity No.
    # Priority: Settings ID (if our Payee) -> Entity ID -> None
    calculated_payee_entity_no = None
    if is_our_company_payee and our_company_settings_id is not None: # Check against settings ID if our Payee
         calculated_payee_entity_no = our_company_settings_id
         logger.debug("Using settings ID for payment_entity_no (Our Company Payee).")
    elif payee_ent and getattr(payee_ent, 'id', None) is not None: # Otherwise, use Entity ID if exists
         calculated_payee_entity_no = payee_ent.id
         logger.debug("Using payee_ent ID for payment_entity_no.")
    else:
         logger.debug("payment_entity_no is None.")


    # Calculate Payee Name (payment_entity & payment_payee)
    # Priority: Settings Name (if our Payee) -> Entity Name -> None
    calculated_payee_name = None
    if is_our_company_payee and our_company_settings_name: # Check against settings Name if our Payee
        calculated_payee_name = our_company_settings_name
        logger.debug("Using settings Name for payment_entity/payment_payee (Our Company Payee).")
    elif payee_ent and getattr(payee_ent, 'name', None) is not None: # Otherwise, use Entity Name if exists
        calculated_payee_name = payee_ent.name
        logger.debug("Using payee_ent Name for payment_entity/payment_payee.")
    else:
        logger.debug("payment_entity/payment_payee is None.")


    # Calculate Payer Name (payment_payer)
    # Priority: Settings Name (if our Payer) -> Entity Name -> None
    calculated_payer_name = None
    if is_our_company_payer and our_company_settings_name: # Check against settings Name if our Payer
        calculated_payer_name = our_company_settings_name
        logger.debug("Using settings Name for payment_payer (Our Company Payer).")
    elif payer_ent and getattr(payer_ent, 'name', None) is not None: # Otherwise, use Entity Name if exists
        calculated_payer_name = payer_ent.name
        logger.debug("Using payer_ent Name for payment_payer.")
    else:
        logger.debug("payment_payer is None.")


    # Calculate Payee Bank Name
    # Priority: Settings Bank Name (if our Payee) -> extract_bank_info result -> None
    calculated_payee_bank = None
    if is_our_company_payee and our_company_settings_bank: # Check against settings Bank Name if our Payee
        calculated_payee_bank = our_company_settings_bank
        logger.debug("Using settings Bank Name for payment_bank (Our Company Payee).")
    else: # Otherwise, use the result from extract_bank_info
        calculated_payee_bank = bank_dict_from_entities_raw.get("bank")
        logger.debug("Using Entities/Raw Bank Name for payment_bank.")


    # Calculate Payee BIC/SWIFT
    # Priority: Settings BIC/SWIFT (if our Payee) -> extract_bank_info result -> None
    calculated_payee_bic_swift = None
    if is_our_company_payee and our_company_settings_bic_swift: # Check against settings BIC/SWIFT if our Payee
        calculated_payee_bic_swift = our_company_settings_bic_swift
        logger.debug("Using settings BIC/SWIFT for payment_bic_swift (Our Company Payee).")
    else: # Otherwise, use the result from extract_bank_info
        calculated_payee_bic_swift = bank_dict_from_entities_raw.get("bic_swift")
        logger.debug("Using Entities/Raw BIC/SWIFT for payment_bic_swift.")


    # Calculate Payee Bank Account No.
    # Priority: Settings Bank Account No. (if our Payee) -> Settings IBAN (if our Payee) -> extract_bank_info result -> None
    calculated_payee_bank_account_no = None
    if is_our_company_payee and our_company_settings_bank_account_no: # Priority 1: settings bank_account_no if our Payee
        calculated_payee_bank_account_no = our_company_settings_bank_account_no
        logger.debug("Using settings Bank Account No. for payment_bank_account_no (Our Company Payee).")
    elif is_our_company_payee and our_company_settings_bank_iban: # Priority 2: settings bank_iban if our Payee
        calculated_payee_bank_account_no = our_company_settings_bank_iban
        logger.debug("Using settings IBAN for payment_bank_account_no (Our Company Payee).")
    else: # Priority 3: extract_bank_info result (Entity -> Raw bank_account_no -> Raw bank_iban)
        calculated_payee_bank_account_no = bank_dict_from_entities_raw.get("bank_account_no")
        logger.debug("Using Entities/Raw Account No. for payment_bank_account_no.")


    # Debug logs for all calculated values
    logger.info(f"Final Calculated 'payment_entity_no': {calculated_payee_entity_no}")
    logger.info(f"Final Calculated 'payment_entity' (Payee Name): {calculated_payee_name}")
    logger.info(f"Final Calculated 'payment_payee' (Payee Name): {calculated_payee_name}")
    logger.info(f"Final Calculated 'payment_payer' (Payer Name): {calculated_payer_name}")
    logger.info(f"Final Calculated 'payment_bank': {calculated_payee_bank}")
    logger.info(f"Final Calculated 'payment_bic_swift': {calculated_payee_bic_swift}")
    logger.info(f"Final Calculated 'payment_bank_account_no': {calculated_payee_bank_account_no}")
    logger.info("--- End Calculation of All Payment Field Values ---")

    # ---------- 공통 메타 ----------
    data = {
        "booking_document_no": doc.booking_document_no,
        "transaction_doc_type": doc.accounting_transaction_doc_type,
        "internal_request_no": doc.internal_order_no,
        "transaction_document_date": doc.issuance_date.isoformat() if doc.issuance_date else None,
        "service_date": doc.service_date.isoformat() if doc.service_date else None,
        "booking_date": doc.booking_date.isoformat() if doc.booking_date else None,
        "closing_period": f"{doc.created_at.year}-{doc.closing_period:02d}" if doc.closing_period else None,
        "ledger": doc.ledger_standard,
        "transaction_summary": doc.transaction_summary,
        "currency": doc.currency,
        "main_trading_partner_role": role,
        "uploaded_file_url": (
            request.build_absolute_uri(doc.uploaded_file.new_filepath.url)
            if doc.uploaded_file and doc.uploaded_file.new_filepath else None
        ),
        "current_document_id_for_form_action": doc.id,
    }


    # ---------- Entity helper ----------
    # getattr 사용으로 Entity 객체나 필드가 None일 경우 안전하게 접근
    def entity_to_dict(ent: Entity | None):
        if not ent:
            return {}
        return {
            "entity_no":         getattr(ent, 'id', None),
            "entity":            getattr(ent, 'name', None),
            "bank":              getattr(ent, 'bank_name', None),
            "bic_swift":         getattr(ent, 'bank_bic', None),
            "bank_account_no":   getattr(ent, 'bank_account_no', None),
        }

    issuer_dict   = entity_to_dict(doc.issuer) # Issuer Entity 정보
    receiver_dict = entity_to_dict(doc.receiver) # Receiver Entity 정보
    logger.debug(f"Issuer dict: {issuer_dict}")
    logger.debug(f"Receiver dict: {receiver_dict}")

    # Issuer/Receiver 섹션 데이터 채우기 (기존 로직 유지)
    data['issuer'] = issuer_dict
    data['receiver'] = receiver_dict


    # ---------- Payment 채우기 ----------
    data.update({
        # Calculate 단계에서 이미 최종 값이 결정됨. 여기서는 할당만.
        "payment_entity_no": calculated_payee_entity_no,
        "payment_entity": calculated_payee_name,
        "payment_payer": calculated_payer_name,
        "payment_payee": calculated_payee_name,
        "payment_bank": calculated_payee_bank,
        "payment_bic_swift": calculated_payee_bic_swift,
        "payment_bank_account_no": calculated_payee_bank_account_no,

        # ... (나머지 Payment 필드 변경 없음) ...
        "payment_terms":                doc.payment_terms,
        "payment_alternative":          "Yes" if doc.prepayment else "No",
        "payment_date":                 doc.due_date.isoformat() if doc.due_date else None,
        "payment_counterparty_note":    doc.cp_memo,
    })
    logger.debug(f"Final payment data update: {data}")


    # ---------- Transaction Details ----------
    detail_rows = (
        doc.details.order_by("position_no", "id")
        .values(
            "id", "gl_account_no", "gl_account_description",
            "position_no", "position", "currency",
            "amount", "tax_code", "description",
        )
    )
    # Decimal 타입을 float 또는 str로 변환하여 JSON 직렬화 문제 방지
    transaction_details_list = []
    for row in detail_rows:
        row_dict = dict(row)
        if isinstance(row_dict.get('amount'), Decimal):
            row_dict['amount'] = float(row_dict['amount']) # 또는 str()
        transaction_details_list.append(row_dict)

    data["transaction_details"] = transaction_details_list
    logger.debug(f"Transaction details count: {len(data['transaction_details'])}")
    logger.info("Returning JSON response.")

    return JsonResponse(data)
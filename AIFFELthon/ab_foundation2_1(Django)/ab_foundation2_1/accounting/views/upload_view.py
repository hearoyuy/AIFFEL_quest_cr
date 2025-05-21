from django.shortcuts import render, redirect
from django.core.files.storage import FileSystemStorage
from django.http import JsonResponse
from django.urls import reverse
from pdf2image import convert_from_path
import os
import shutil
from django.conf import settings
from accounting.models import UploadedFile  # Make sure your UploadedFile model is imported
from datetime import datetime # datetime은 현재 코드에서 직접 사용되지 않으므로 제거해도 됩니다.
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator

# 경로 설정
POPPLER_PATH = r"C:\poppler\Library\bin"  # Ensure this path is correct for your environment
ORIGINAL_DIR = 'invoices/original_files'
CONVERTED_DIR = 'invoices/converted_files'


@login_required
def upload_view(request):
    if request.method == 'POST':
        user_uploaded_files = request.FILES.getlist('upload_file')
        original_storage = FileSystemStorage(location=os.path.join(settings.MEDIA_ROOT, ORIGINAL_DIR))
        converted_files_path = os.path.join(settings.MEDIA_ROOT, CONVERTED_DIR)
        os.makedirs(converted_files_path, exist_ok=True)

        successfully_uploaded_files_for_session = []
        duplicate_files_info = []

        for f in user_uploaded_files:
            user_filename = f.name

            is_duplicate = UploadedFile.objects.filter(
                original_filename=user_filename,
                uploaded_by=request.user
            ).exists()

            if is_duplicate:
                duplicate_files_info.append({
                    'name': user_filename,
                    'reason': '이미 동일한 이름의 파일이 이전에 등록되었습니다.'
                })
                print(f"중복 파일 감지 (DB 등록 건너뜀): {user_filename} (사용자: {request.user.username})")
            else:
                try:
                    filename_in_original_storage = original_storage.save(user_filename, f)
                    original_file_url = settings.MEDIA_URL + ORIGINAL_DIR + '/' + filename_in_original_storage

                    successfully_uploaded_files_for_session.append({
                        'name': user_filename,
                        'url': original_file_url,
                        'saved_as': filename_in_original_storage
                    })

                    file_extension = os.path.splitext(filename_in_original_storage)[1].lower()
                    original_file_full_path = original_storage.path(filename_in_original_storage)
                    converted_filename_new = ""

                    if file_extension in ['.jpg', '.jpeg', '.png']:
                        converted_filename_new = filename_in_original_storage
                        destination_path = os.path.join(converted_files_path, converted_filename_new)
                        shutil.copyfile(original_file_full_path, destination_path)
                    elif file_extension == '.pdf':
                        try:
                            images = convert_from_path(original_file_full_path, dpi=300, poppler_path=POPPLER_PATH)
                            if images:
                                base_name_from_storage = os.path.splitext(filename_in_original_storage)[0]
                                converted_filename_new = f"{base_name_from_storage}_page_1.jpg"
                                image_path = os.path.join(converted_files_path, converted_filename_new)
                                images[0].save(image_path, "JPEG")
                        except Exception as e:
                            print(f"❌ PDF 변환 실패: {filename_in_original_storage} - {e}")

                    # `transaction_document_type` 인자 제거
                    save_uploaded_file_info(
                        original_filename=user_filename,
                        original_filepath=os.path.join(ORIGINAL_DIR, filename_in_original_storage),
                        new_filename=converted_filename_new if converted_filename_new else None,
                        new_filepath=os.path.join(CONVERTED_DIR,
                                                  converted_filename_new) if converted_filename_new else None,
                        abf_filename="",
                        user=request.user
                    )
                    print(f"파일 정보 저장 완료: {user_filename} (저장된 원본명: {filename_in_original_storage})")

                except Exception as e:
                    print(f"파일 처리 중 오류 발생 ({user_filename}): {e}")
                    duplicate_files_info.append({
                        'name': user_filename,
                        'reason': f'처리 중 오류 발생: {e}'
                    })

        request.session['uploaded_files_success'] = successfully_uploaded_files_for_session
        request.session['duplicate_files_detected'] = duplicate_files_info

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True, 'redirect_url': reverse('upload_success')})

        return redirect('upload_success')

    return render(request, "accounting/upload.html")


@login_required
def upload_success_view(request):
    just_uploaded_successful = request.session.pop('uploaded_files_success', [])
    duplicate_files_detected = request.session.pop('duplicate_files_detected', [])
    recent_qs = (UploadedFile.objects
                 .filter(uploaded_by=request.user)
                 .order_by('-uploaded_at'))
    paginator = Paginator(recent_qs, 10)
    page_number = request.GET.get('page', 1)
    recent_files_page = paginator.get_page(page_number)

    return render(request,
                  "accounting/upload_success.html",
                  {
                      "just_uploaded_files": just_uploaded_successful,
                      "duplicate_files": duplicate_files_detected,
                      "recent_db_files": recent_files_page
                  })


# `transaction_document_type` 파라미터 제거
def save_uploaded_file_info(
        original_filename,
        original_filepath,
        new_filename,
        new_filepath,
        abf_filename,
        user
):
    """
    Saves uploaded file metadata to the UploadedFile model.
    Note: uploaded_at is handled by auto_now_add=True in the model.
    """
    UploadedFile.objects.create(
        original_filename=original_filename,
        original_filepath=original_filepath,
        abf_filename=abf_filename,
        new_filename=new_filename,
        new_filepath=new_filepath,
        uploaded_by=user,
        is_processed=False # is_processed는 모델에 기본값이 있으므로 여기서 명시적으로 False로 설정할 필요는 없을 수 있습니다.
                           # 하지만 명시적으로 두는 것도 괜찮습니다.
    )
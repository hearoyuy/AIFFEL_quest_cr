import base64, json, mimetypes, time
import openai
from django.conf import settings
# from utils.token_counter import count_tokens # 해당 모듈이 없어 주석 처리합니다. 필요시 주석 해제하세요.
from PIL import Image
from io import BytesIO

# utils.token_counter.py 예시 (실제 프로젝트에 맞게 구현 필요)
def count_tokens(text: str) -> int:
    """간단한 토큰 카운터 예시입니다. 실제로는 tiktoken 등을 사용하는 것이 좋습니다."""
    if not text:
        return 0
    return len(text.split()) # 공백 기준 단순 분리, 실제 토큰화와 다름


openai.api_key = settings.OPENAI_API_KEY
DEFAULT_MODEL = "gpt-4o" # Django settings에 OPENAI_DEFAULT_MODEL 등으로 정의하는 것이 좋습니다.
_ASSISTANT_ID = None  # 캐싱


def get_invoice_assistant_id():
    global _ASSISTANT_ID
    if _ASSISTANT_ID:
        return _ASSISTANT_ID
    # 기존 어시스턴트 ID가 있다면 재사용 로직 추가 고려
    # 예: settings에 ASSISTANT_ID를 저장해두거나, 목록 조회 후 이름으로 찾기
    # 현재는 매번 새로 생성하는 코드이므로 주의 필요 (과금 및 어시스턴트 관리 문제)
    print("Creating new assistant...")  # 생성 시 알림
    assistant = openai.beta.assistants.create(
        name="Invoice Extractor",
        instructions="Extract invoice info in the JSON schema below.",
        tools=[{"type": "code_interpreter"}, {"type": "file_search"}],
        model=DEFAULT_MODEL,
    )
    _ASSISTANT_ID = assistant.id
    print(f"New assistant created with ID: {_ASSISTANT_ID}")  # 생성된 ID 출력
    return _ASSISTANT_ID


def call_openai_vision_or_file(
        file_path: str,
        *,
        prompt: str,
        model: str | None = None,
        json_mode: bool = False,
        max_tokens: int = 10000, # gpt-4o 기준, 모델별 max_tokens, max_completion_tokens 확인 필요
        temperature: float = 0.2,
) -> dict:
    """
    이미지(JPG/PNG)는 Vision API, PDF 등 비이미지는 Assistants API로 자동 분기.
    """
    model = model or DEFAULT_MODEL
    mime, _ = mimetypes.guess_type(file_path)

    raw = ""  # raw 변수 초기화

    # ── 이미지 파일 처리 (JPG/PNG 등) ──────────────
    if mime and mime.startswith("image/"):
        print(f"Processing image file: {file_path} with Vision API")
        with Image.open(file_path) as img:
            buffer = BytesIO()
            # 이미지 포맷을 원본으로 유지하되, JPG가 아닌 경우 PNG로 변환하여 호환성 확보
            img_format = img.format if img.format and img.format.lower() in ['jpeg', 'png', 'gif', 'webp'] else 'PNG'
            if img_format.lower() == 'jpeg': # API는 'jpeg'를 요구
                 img_format = 'JPEG'

            img.save(buffer, format=img_format)
            img_b64 = base64.b64encode(buffer.getvalue()).decode()

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{mime};base64,{img_b64}"
                        },
                    },
                ],
            }
        ]
        kwargs = {"model": model, "messages": messages}
        if json_mode:
            kwargs["response_format"] = {"type": "json_object"}

        # OpenAI API 변경에 따라 max_tokens/max_completion_tokens 사용 모델 구분
        # 최신 모델(gpt-4o 등)은 주로 max_tokens 사용
        # "o3"라는 모델명은 공식 OpenAI 모델명이 아닐 수 있으므로, 실제 사용하시는 모델명으로 대체해야 합니다.
        # 여기서는 일반적인 gpt-4o 또는 gpt-4-turbo (vision 포함) 모델 기준으로 작성합니다.
        if model in ["gpt-4o", "gpt-4-turbo", DEFAULT_MODEL]: # DEFAULT_MODEL이 최신 모델을 가리킨다고 가정
            kwargs["max_tokens"] = max_tokens # OpenAI Python SDK v1.x.x부터 max_tokens로 통일 경향
            if temperature is not None: # temperature를 지원하는 경우에만 추가
                 kwargs["temperature"] = temperature
        # vision preview 모델은 max_tokens를 사용했었으나, 최신 모델로 통합되는 추세
        elif "vision-preview" in model: # 예: gpt-4-vision-preview
            kwargs["max_tokens"] = max_tokens
            # kwargs["temperature"] = temperature # Vision API는 temperature를 지원하지 않거나 효과가 제한적일 수 있음
        else:
            # 기타 다른 모델의 경우 API 문서 참조
            kwargs["max_tokens"] = max_tokens
            if temperature is not None:
                kwargs["temperature"] = temperature


        try:
            resp = openai.chat.completions.create(**kwargs)
            if resp.choices and resp.choices[0].message.content:
                raw = resp.choices[0].message.content.strip()
            else:
                raise ValueError("Vision API response is empty.")

        except Exception as e:
            print(f"Vision API Error: {e}")
            raise


    # ── PDF 등 비이미지 파일 처리 (Assistants API 방식) ──────────────
    else:
        print(f"Processing non-image file: {file_path} with Assistants API")
        try:
            # 1. 파일 업로드
            print(f"Uploading file: {file_path}")
            with open(file_path, "rb") as f:
                # 파일 용도 'assistants'로 변경 (이전 코드에서는 vision이었으나 assistants가 맞음)
                file_obj = openai.files.create(file=f, purpose="assistants")
            file_id = file_obj.id
            print(f"File uploaded with ID: {file_id}")

            # 2. 스레드 생성 (또는 기존 스레드 사용)
            print("Creating thread...")
            thread = openai.beta.threads.create()
            thread_id = thread.id
            print(f"Thread created with ID: {thread_id}")

            # 3. 메시지 추가 (파일 포함) - attachments 사용
            print(f"Adding message to thread {thread_id} with file {file_id}...")
            openai.beta.threads.messages.create(
                thread_id=thread_id,
                role="user",
                content=prompt,
                attachments=[  # 수정된 부분: tool_code -> tools, 리스트 안의 객체로 변경
                    {
                        "file_id": file_id,
                        "tools": [{"type": "file_search"}]
                    }
                ]
            )
            print("Message added.")

            # 4. 실행 요청
            assistant_id = get_invoice_assistant_id()
            print(f"Creating run for thread {thread_id} with assistant {assistant_id}...")
            run_params = {
                "thread_id": thread_id,
                "assistant_id": assistant_id,
            }
            # 어시스턴트의 모델을 오버라이드 하거나 추가 지시사항을 넣을 수 있음
            # if model and model != DEFAULT_MODEL: # 어시스턴트 생성 시 모델과 다른 경우
            # run_params["model"] = model
            # if json_mode: # JSON 모드를 위한 추가 지시사항 (어시스턴트 생성 시 instructions에 포함하는 것이 더 일반적)
            # run_params["instructions"] = assistant.instructions + \
            #                             "\nPlease ensure the output is a valid JSON object."
            # 참고: Assistants API에서 JSON 모드를 강제하려면 어시스턴트 생성 시 instructions에 명시하거나,
            #       v2에서는 message 생성 시 response_format을 지정할 수 있게 될 수 있습니다. (현재 MessageRequest에는 없음)
            #       Run 생성 시에는 response_format 직접 지정 옵션은 없습니다.
            #       가장 확실한 방법은 Assistant의 instructions에 JSON 출력 요구를 명시하는 것입니다.

            run = openai.beta.threads.runs.create(**run_params)
            run_id = run.id
            print(f"Run created with ID: {run_id}. Waiting for completion...")

            # 5. 실행 완료 대기 (최대 120초까지 대기, 1초 간격)
            timeout = 120 # PDF 처리 등은 시간이 더 걸릴 수 있으므로 timeout 증가
            start_time = time.time()
            while time.time() - start_time < timeout:
                run_status = openai.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
                print(f"Run status: {run_status.status} (elapsed: {time.time() - start_time:.2f}s)")
                if run_status.status == "completed":
                    print("Run completed.")
                    break
                elif run_status.status == "failed":
                    error_message = "Unknown error"
                    if run_status.last_error:
                        error_message = f"Code: {run_status.last_error.code}, Message: {run_status.last_error.message}"
                    print(f"Run failed. Error: {error_message}")
                    raise RuntimeError(f"OpenAI Assistants run failed: {error_message}")
                elif run_status.status == "requires_action":
                    # Tool call 등이 필요한 경우 이 상태가 될 수 있습니다.
                    # 현재 Invoice Extractor는 file_search만 사용하므로, 이 분기는 복잡한 tool 사용 시 필요합니다.
                    print("Run requires action. This example does not handle tool calls.")
                    # 예시: submit_tool_outputs(...)
                    raise NotImplementedError("Run requires action, but tool call handling is not implemented.")
                elif run_status.status in ["cancelled", "expired", "cancelling"]:
                    print(f"Run status is {run_status.status}.")
                    raise RuntimeError(f"OpenAI Assistants run status is {run_status.status}.")
                time.sleep(1) # 폴링 간격 증가
            else:  # while 루프가 시간 초과로 끝났을 경우
                print(f"Run did not complete within {timeout} seconds. Last status: {run_status.status}")
                # 시간 초과 시 현재 Run을 취소 시도
                try:
                    print(f"Attempting to cancel run {run_id}...")
                    openai.beta.threads.runs.cancel(thread_id=thread_id, run_id=run_id)
                    print(f"Run {run_id} cancellation requested.")
                except Exception as cancel_err:
                    print(f"Failed to cancel run {run_id}: {cancel_err}")
                raise TimeoutError(f"OpenAI Assistants run timed out after {timeout} seconds.")

            # 6. 결과 메시지 추출 (가장 최근 어시스턴트 메시지)
            print(f"Retrieving messages for thread {thread_id}...")
            messages_response = openai.beta.threads.messages.list(thread_id=thread_id, order="desc", limit=10)
            result_text = ""
            for msg in messages_response.data:
                if msg.role == "assistant": # 어시스턴트의 응답만 찾음
                    for content_part in msg.content:
                        if content_part.type == "text":
                            result_text = content_part.text.value
                            print(f"Found assistant message: {result_text[:200]}...")
                            break # 첫 번째 텍스트 내용을 사용
                    if result_text: # 어시스턴트의 텍스트 내용을 찾았으면 종료
                        break
            raw = result_text.strip()

            # 7. (선택) 리소스 정리: 업로드된 파일 및 스레드 삭제
            # 실제 운영 환경에서는 비용 및 데이터 관리 측면에서 필요시 삭제하는 것이 좋습니다.
            # print(f"Attempting to delete file {file_id}...")
            # try:
            #     openai.files.delete(file_id)
            #     print(f"Deleted file {file_id}")
            # except Exception as e:
            #     print(f"Failed to delete file {file_id}: {e}")

            # print(f"Attempting to delete thread {thread_id}...")
            # try:
            #     openai.beta.threads.delete(thread_id)
            #     print(f"Deleted thread {thread_id}")
            # except Exception as e:
            #     print(f"Failed to delete thread {thread_id}: {e}")


        except Exception as e:
            print(f"Assistants API Error: {e}")
            # 에러 발생 시 생성된 리소스(파일, 스레드) 정리 시도
            if 'file_id' in locals() and file_id:
                try:
                    print(f"Cleaning up uploaded file {file_id} due to error...")
                    openai.files.delete(file_id)
                    print(f"File {file_id} deleted.")
                except Exception as cleanup_e:
                    print(f"Failed to delete file {file_id} during cleanup: {cleanup_e}")
            if 'thread_id' in locals() and thread_id:
                try:
                    print(f"Cleaning up thread {thread_id} due to error...")
                    openai.beta.threads.delete(thread_id)
                    print(f"Thread {thread_id} deleted.")
                except Exception as cleanup_e:
                    print(f"Failed to delete thread {thread_id} during cleanup: {cleanup_e}")
            raise

    # ── 코드블록 마커 제거 ──────────────
    print("Removing code block markers...")
    if raw is None:
        raw = ""

    # ```json ... ``` 또는 ``` ... ``` 형식의 마커 제거
    # 시작 마커 제거
    if raw.startswith("```json"):
        raw = raw[len("```json"):].lstrip()
    elif raw.startswith("```"):
        raw = raw[len("```"):].lstrip()

    # 끝 마커 제거
    if raw.endswith("```"):
        raw = raw[:-len("```")].rstrip()
    print(f"Processed raw content (first 300 chars): {raw[:300]}...")


    # ── 토큰 카운트 ──────────────
    tok_in = count_tokens(prompt) # Vision API의 경우 이미지 토큰은 별도 계산 필요
    tok_out_content = raw
    tok_out = count_tokens(tok_out_content)
    print(f"Input tokens (prompt text only): {tok_in}, Output tokens (response text): {tok_out}")


    # ── JSON 파싱 ──────────────
    print("Attempting to parse JSON...")
    try:
        if not raw:
            print("[Warning] Response content is empty, cannot parse JSON.")
            # 빈 응답에 대해 빈 dict를 반환할지, 오류를 발생시킬지 결정
            # raise ValueError("Received empty response from OpenAI, cannot parse JSON.")
            return {} # 또는 적절한 기본값

        parsed_json = json.loads(raw)
        print("JSON parsing successful.")
        return parsed_json
    except json.JSONDecodeError as e:
        print(f"[Error] JSON parsing failed: {e}")
        print(f"String that failed to parse (first 500 chars): {raw[:500]}...")
        raise ValueError(f"Failed to parse JSON from OpenAI response: {e}. Response text: {raw[:200]}") from e
    except Exception as e: # 그 외 예상치 못한 오류
        print(f"[Error] Unexpected error during JSON parsing: {e}")
        print(f"String that failed to parse (first 500 chars): {raw[:500]}...")
        raise

# 다음은 위 코드를 사용하는 예시입니다. (실행 환경에 맞게 수정 필요)
if __name__ == '__main__':
    # Django settings 모킹 또는 실제 설정 로드 필요
    class SettingsMock:
        OPENAI_API_KEY = "sk-your-openai-api-key" # 실제 API 키로 교체하세요.

    settings = SettingsMock() # Django 프로젝트 외부에서 실행 시 settings 모킹

    # 테스트용 파일 생성 (실제 파일 경로 사용)
    dummy_pdf_path = "dummy_invoice.pdf"
    dummy_jpg_path = "dummy_image.jpg"

    try:
        with open(dummy_pdf_path, "w") as f:
            f.write("This is a dummy PDF content for testing invoice extraction.")
        with open(dummy_jpg_path, "w") as f: # 실제 이미지 파일로 대체해야 Vision API 테스트 가능
            f.write("This is dummy image content.") # Pillow는 텍스트 파일 이미지를 열 수 없음

        print("\n--- Testing with PDF (Assistants API) ---")
        # Assistants API는 실제 파일 내용과 프롬프트에 따라 결과가 달라짐
        pdf_prompt = "Extract invoice number and total amount from this document. Return JSON."
        try:
            pdf_result = call_openai_vision_or_file(dummy_pdf_path, prompt=pdf_prompt, json_mode=True)
            print("PDF Extraction Result:", json.dumps(pdf_result, indent=2))
        except Exception as e:
            print(f"Error during PDF test: {e}")

        print("\n--- Testing with JPG (Vision API) ---")
        # Vision API는 실제 이미지와 적절한 프롬프트가 필요
        # 아래는 플레이스홀더 프롬프트이며, 실제 이미지에 맞는 프롬프트로 변경 필요
        # 또한, dummy_jpg_path는 실제 이미지 파일을 가리켜야 합니다.
        jpg_prompt = "What is in this image? If it's an invoice, extract key details. Return JSON."
        # Pillow로 유효한 이미지를 생성하거나 실제 이미지 파일을 사용해야 합니다.
        # 간단한 테스트를 위해 Pillow로 검은색 이미지 생성
        try:
            img = Image.new('RGB', (60, 30), color = 'black')
            img.save(dummy_jpg_path, "JPEG")

            jpg_result = call_openai_vision_or_file(dummy_jpg_path, prompt=jpg_prompt, json_mode=True)
            print("JPG Extraction Result:", json.dumps(jpg_result, indent=2))
        except Exception as e:
            print(f"Error during JPG test: {e}")

    finally:
        # 테스트 파일 삭제
        import os
        if os.path.exists(dummy_pdf_path):
            os.remove(dummy_pdf_path)
        if os.path.exists(dummy_jpg_path):
            os.remove(dummy_jpg_path)

    # 전체 코드 제공
    # (위의 스크립트 전체가 해당됩니다)
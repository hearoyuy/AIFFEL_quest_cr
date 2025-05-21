# accounting/modules/parser_modules/gemini_parser_client.py

import base64
import os
import mimetypes
from PIL import Image
import google.generativeai as genai
from django.conf import settings

genai.configure(api_key=settings.GEMINI_API_KEY)


def preprocess_image(file_path: str) -> str:
    """
    Gemini API 호출 전 이미지 전처리 (리사이즈, JPEG 변환)
    """
    img = Image.open(file_path)
    if img.mode not in ("RGB", "L"):
        img = img.convert("RGB")

    max_size = 1500
    if img.width > max_size or img.height > max_size:
        img.thumbnail((max_size, max_size))

    temp_path = file_path
    if file_path.lower().endswith(".png"):
        temp_path = file_path[:-4] + "_conv.jpg"
        img.save(temp_path, format="JPEG", quality=85)
    else:
        img.save(temp_path)

    return temp_path


def call_gemini_api(file_path: str, prompt: str = "") -> dict:
    print("[GEMINI] Vision 호출")
    try:
        image_path = preprocess_image(file_path)
        with open(image_path, "rb") as img_file:
            image_data = img_file.read()

        mime_type, _ = mimetypes.guess_type(image_path)
        model = genai.GenerativeModel("gemini-pro-vision")

        response = model.generate_content([
            prompt,
            {
                "mime_type": mime_type,
                "data": base64.b64encode(image_data).decode("utf-8")
            }
        ])
        content = response.text.strip()

        for tag in ("```json", "```"):
            if content.startswith(tag):
                content = content[len(tag):]
            if content.endswith("```"):
                content = content[:-3]

        import json
        return json.loads(content)

    except Exception as e:
        print(f"[ERROR] Gemini Vision 실패: {e}")
        return {}
# accounting/modules/parser_modules/classifier.py

from typing import Literal
from accounting.modules.parser_modules.openai_parser_client import call_openai_vision

DocType = Literal["invoice", "debit_note", "unknown"]


def get_doc_type(image_path: str) -> DocType:
    """
    GPT 기반 문서 분류기. 이미지에서 문서 유형을 판별합니다.
    """
    prompt = (
        "You are a document classifier. Determine the document type of the input image.\n"
        "Output exactly one of the following: invoice, debit_note, or unknown.\n"
        "Do not explain. Respond with only the document type keyword."
    )
    try:
        result = call_openai_vision(image_path, prompt=prompt)
        doc_type = result.strip().lower()
        return doc_type if doc_type in ("invoice", "debit_note") else "unknown"
    except Exception as e:
        print(f"[ERROR] GPT 문서 분류 실패: {e}")
        return "unknown"


if __name__ == "__main__":
    import sys
    print(get_doc_type(sys.argv[1]))
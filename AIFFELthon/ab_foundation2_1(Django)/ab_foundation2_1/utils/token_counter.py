# utils/token_counter.py
import tiktoken

__all__ = ["count_tokens", "count_message_tokens"]

_DEFAULT_MODEL = "o3"


def _enc(model: str = _DEFAULT_MODEL):
    return tiktoken.encoding_for_model(model)


def count_tokens(text: str, model: str = _DEFAULT_MODEL) -> int:
    """단일 문자열 토큰 수"""
    return len(_enc(model).encode(text))


def count_message_tokens(messages: list[dict], model: str = _DEFAULT_MODEL) -> int:
    """
    chat-completion messages → 총 토큰 수
    (OpenAI 규격: 메시지마다 +3, assistant 답 시작 +3)
    """
    enc   = _enc(model)
    total = 3  # assistant 시작
    for m in messages:
        total += 3
        total += len(enc.encode(m.get("content", "")))
        if name := m.get("name"):
            total += len(enc.encode(name))
    return total

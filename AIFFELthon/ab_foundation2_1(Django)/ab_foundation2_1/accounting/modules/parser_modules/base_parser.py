# accounting/modules/parser_modules/base_parser.py

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseParser(ABC):
    """
    모든 문서 파서의 공통 인터페이스 및 유틸리티 제공
    """

    @abstractmethod
    def parse(self, image_path: str) -> Dict[str, Any]:
        """해당 문서 타입의 JSON 파싱 결과 리턴"""
        pass

    def validate(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        기본 후처리 및 필드 정규화 예시:
        - 날짜 형식 검사
        - 금액 필드 숫자형 확인
        - 누락 필드 null 삽입 등
        """
        # TODO: 필드 정규화 및 누락 확인 로직 추가 예정
        return parsed

    def merge_results(self, result_gpt: Dict[str, Any], result_gem: Dict[str, Any], required_fields: list) -> Dict[str, Any]:
        """
        GPT와 Gemini 결과 병합:
        - 필드 누락 시 보완
        - 중복 시 GPT 우선
        - 둘 다 없을 경우 null 삽입
        """
        merged = {}
        for key in required_fields:
            gpt_val = result_gpt.get(key)
            gem_val = result_gem.get(key)
            if gpt_val not in [None, ""]:
                merged[key] = gpt_val
            elif gem_val not in [None, ""]:
                merged[key] = gem_val
            else:
                merged[key] = None  # 누락 필드는 null 강제 삽입

        print("[MERGE] 병합 결과:", merged)
        return merged

# accounting/modules/rag_matching/vector_store.py
from typing import List, Dict
from sentence_transformers import SentenceTransformer
import faiss, numpy as np

class VectorStore:
    def __init__(self):
        self.model        = SentenceTransformer("all-MiniLM-L6-v2")
        self.index: faiss.Index = None
        self.account_data: List[Dict] = []

    # ── ① 설명 후보 추출 ─────────────────────────────
    @staticmethod
    def _pick_text(acc: Dict[str, str]) -> str:
        # ① 실제 설명이 있으면 그걸 사용
        for f in ("desc_long_en", "desc_short_en",
                  "desc_long_de", "desc_short_de"):
            val = (acc.get(f) or "").strip()
            if len(val) > 3 and val not in {"0"}:
                return val

        # ② 없으면 classification + category 로 합성
        cls = (acc.get("classification") or "").title()  # Asset / Expense…
        cat = (acc.get("category") or "").title()  # IT, Office Supplies…
        if cls or cat:
            return f"{cls} {cat}".strip()

        # ③ 그래도 없으면 코드라도 반환
        return f"GL {acc['code']}"

    # ───────── 인덱스 빌드 ─────────
    # accounting/modules/rag_matching/vector_store.py
    def build_index(self, accounts: List[Dict]):
        filtered, texts = [], []

        for acc in accounts:
            # 1️⃣ description → desc_long_en → desc_long_de 순으로 채움
            text = self._pick_text(acc)          # ← self. 로 호출
            if not text:
                continue  # 끝까지 비면 인덱스 제외

            acc_copy = acc.copy()
            acc_copy["text"] = text  # 2️⃣ 보강된 값 저장
            filtered.append(acc_copy)
            texts.append(text)

        if not texts:
            raise ValueError("No account descriptions to index.")

        self.account_data = filtered
        embeds = self.model.encode(  # 3️⃣ 반드시 정규화
            texts,
            show_progress_bar=False,
            normalize_embeddings=True
        )
        dim = embeds.shape[1]
        self.index = faiss.IndexFlatIP(dim)  # 코사인 유사도
        self.index.add(embeds.astype("float32"))

    # ───────── 검색 ─────────
    def search(self, keywords, top_k: int = 10) -> List[Dict]:
        """
        keywords : ["laptop","hardware",…]  (3-5개 권장)
        return   : [{"code":"8110","desc":"…","score":87.3}, …]  (내림차순)
        """
        if self.index is None:
            raise RuntimeError("Vector index is not loaded.")

        # ↘ 키워드 타입 호환 (옛 API 지원)
        if isinstance(keywords, str):
            keywords = [keywords]

        # 여러 키워드 임베딩 → 평균 → 정규화
        query_vec = self.model.encode(
            keywords, normalize_embeddings=True
        ).mean(axis=0, keepdims=True)

        sims, idx = self.index.search(query_vec.astype("float32"), top_k)
        sims, idx = sims[0], idx[0]  # ← 여기까지만 1-차원으로 전개

        results = []
        for sim, i in zip(sims, idx):  # ❗ sims, idx 그대로 사용
            if i == -1:
                continue
            acc = self.account_data[i]
            if not acc["text"].strip():  # 빈 설명 필터
                continue
            prob = round(float(sim) * 50 + 50, 1)  # 0-100 스케일
            results.append({
                "code": acc["code"],
                "desc": acc["description"],
                "prob": prob,
            })
        return results

# (파일 맨 아래 추가)  ──────────────────────────────────────────────
# 전역 싱글턴 ─ 다른 모듈에서 바로 import 해서 사용
vector_store = VectorStore()

# 외부 공개 심볼
__all__ = ["VectorStore", "vector_store"]
# accounting/management/commands/build_coa_index.py
from django.core.management.base import BaseCommand
from django.db.models import F, Q, Value, CharField
from django.db.models.functions import Concat
import os

from accounting.models import ChartOfAccount
from accounting.modules.rag_matching.vector_store import VectorStore
from accounting.modules.rag_matching.index_io import save_index


class Command(BaseCommand):
    """
    COA 벡터 인덱스 재생성 – Activation='Y' 계정만
      python manage.py build_coa_index --dst media/vector/coa_index_active
    """
    help = "Build FAISS index from ACTIVE (Activation=Y) GL accounts"

    def add_arguments(self, parser):
        parser.add_argument(
            "--dst",
            default="media/vector/coa_index_active",
            help="*.index / *_meta.pkl save path (without ext)",
        )

    # ──────────────────────────────────
    def handle(self, *args, **opts):
        dst = opts["dst"]

        # ① DB → 활성 계정만 추출
        qs = (
            ChartOfAccount.objects
            .filter(Q(activation=True) | Q(activation__iexact="Y"))
            .annotate(
                description_en = F("desc_long_en"),
                description_de = F("desc_long_de"),
                classification = F("coa_classification"),
            )
            .annotate(                       # 임베딩용 통합 텍스트
                emb_text = Concat(
                    F("coa_classification"), Value(" "),
                    F("description_en"), Value(" "),
                    F("description_de"),
                    output_field=CharField(),
                )
            )
            .values(
                "code",           # GL Account No
                "emb_text",       # 임베딩 대상 텍스트
                "classification",
            )
        )

        rows = list(qs)
        if not rows:
            self.stderr.write(self.style.ERROR("활성(Activation=Y) 계정이 없습니다."))
            return

        self.stdout.write(f"▶︎ 활성 계정 {len(rows)}개 로드")

        # ② 벡터 인덱스 빌드
        store = VectorStore()
        store.build_index(rows)        # rows 안에 'code'·'emb_text' 필수

        # ③ 저장
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        save_index(store.index, dst, store.account_data)
        self.stdout.write(self.style.SUCCESS(f"✓ 인덱스 저장 완료 → {dst}.index"))

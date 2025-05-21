import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ab_foundation2_1.settings")
django.setup()

from accounting.modules.rag_matching.index_io import load_index
from accounting.modules.rag_matching import vector_store as vs

idx, meta = load_index("media/vector/coa_index")
vs.vector_store.index = idx
vs.vector_store.account_data = meta

print(vs.vector_store.search(["desk", "frame"], top_k=10))

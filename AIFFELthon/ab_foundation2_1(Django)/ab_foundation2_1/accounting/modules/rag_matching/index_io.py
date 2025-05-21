import faiss
import pickle
import os

def save_index(index, path: str, metadata: list):
    """
    벡터 인덱스와 함께 account_data(metadata)를 저장합니다.
    - index: FAISS 인덱스 객체
    - path: 저장 경로 (확장자 없음)
    - metadata: account_data 리스트 (List[dict])
    """
    faiss.write_index(index, f"{path}.index")
    with open(f"{path}_meta.pkl", "wb") as f:
        pickle.dump(metadata, f)

def load_index(path: str):
    """
    저장된 인덱스와 metadata를 불러옵니다.
    return: (index 객체, metadata 리스트)
    """
    index = faiss.read_index(f"{path}.index")
    with open(f"{path}_meta.pkl", "rb") as f:
        metadata = pickle.load(f)
    return index, metadata

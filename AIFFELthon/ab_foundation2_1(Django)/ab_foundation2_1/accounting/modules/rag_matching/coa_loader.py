import pandas as pd
from typing import List, Dict

def load_coa_from_excel(file_path: str) -> List[Dict]:
    df = pd.read_excel(file_path)
    df = df[df['Description (EN, Long)'].notnull()]
    account_list = []
    for _, row in df.iterrows():
        account_list.append({
            "account_number": str(row.get("Account No.", "")).zfill(4),
            "description": row.get("Description (EN, Long)", "").strip(),
            "classification": row.get("Classification1", "").strip(),
            "group": row.get("ABF Account No", "").strip(),
            "function": row.get("Function", row.get("Function.1", "")).strip(),
        })
    return account_list

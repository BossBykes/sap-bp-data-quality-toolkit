import pandas as pd
from sap_bp_dq.dedup import find_exact_duplicates

def test_exact_duplicates():
    df = pd.DataFrame([
        {"bp_id": "BP1", "name": "RWE AG", "city": "Essen", "country": "DE"},
        {"bp_id": "BP2", "name": "RWE AG", "city": "Essen", "country": "DE"},
    ])
    dups = find_exact_duplicates(df, keys=["name", "city", "country"])
    assert len(dups) == 2

import pandas as pd
from sap_bp_dq.dedup import find_exact_duplicates, find_fuzzy_duplicates


def test_exact_duplicates():
    df = pd.DataFrame([
        {"bp_id": "BP1", "name": "RWE AG", "city": "Essen", "country": "DE"},
        {"bp_id": "BP2", "name": "RWE AG", "city": "Essen", "country": "DE"},
    ])
    dups = find_exact_duplicates(df, keys=["name", "city", "country"])
    assert len(dups) == 2


def test_fuzzy_duplicates_skip_cross_country_by_default():
    df = pd.DataFrame([
        {"bp_id": "BP1", "name": "RWE AG", "city": "Essen", "country": "DE"},
        {"bp_id": "BP2", "name": "RWE AG", "city": "Essen", "country": "US"},
    ])

    dups = find_fuzzy_duplicates(df, keys=["name", "city"], threshold=90)

    assert dups.empty


def test_fuzzy_duplicates_can_allow_cross_country():
    df = pd.DataFrame([
        {"bp_id": "BP1", "name": "RWE AG", "city": "Essen", "country": "DE"},
        {"bp_id": "BP2", "name": "RWE AG", "city": "Essen", "country": "US"},
    ])

    dups = find_fuzzy_duplicates(
        df, keys=["name", "city"], threshold=90, allow_cross_country=True
    )

    assert len(dups) == 1

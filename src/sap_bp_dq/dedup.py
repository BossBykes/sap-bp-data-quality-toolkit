from __future__ import annotations
import pandas as pd
from rapidfuzz import fuzz

def find_exact_duplicates(df: pd.DataFrame, keys: list[str]) -> pd.DataFrame:
    if not keys:
        return pd.DataFrame(columns=["group_id", "row_index", "bp_id"])

    norm = df.copy()
    for k in keys:
        norm[k] = norm[k].astype(str).str.strip().str.lower()

    dup_mask = norm.duplicated(subset=keys, keep=False)
    dups = df[dup_mask].copy()
    if dups.empty:
        return pd.DataFrame(columns=["group_id", "row_index", "bp_id"])

    # Create group ids based on normalized key tuple
    tuples = norm.loc[dup_mask, keys].apply(lambda r: tuple(r.values), axis=1)
    group_map = {t: i for i, t in enumerate(sorted(set(tuples)), start=1)}
    dups["group_id"] = tuples.map(group_map)
    dups["row_index"] = dups.index
    return dups[["group_id", "row_index", "bp_id"]]

def find_fuzzy_duplicates(df: pd.DataFrame, keys: list[str], threshold: int = 90) -> pd.DataFrame:
    """
    Simple O(n^2) fuzzy match for MVP. Works fine for a few hundred rows.
    Returns pairs that look similar.
    """
    if not keys:
        return pd.DataFrame(
            columns=["row_i", "bp_id_i", "row_j", "bp_id_j", "score", "recommended_action"]
        )

    def row_text(i: int) -> str:
        parts = []
        for k in keys:
            v = df.at[i, k]
            parts.append("" if pd.isna(v) else str(v).strip().lower())
        return " | ".join(parts)

    rows = list(df.index)
    pairs = []
    texts = {i: row_text(i) for i in rows}

    for a in range(len(rows)):
        for b in range(a + 1, len(rows)):
            i, j = rows[a], rows[b]
            score = fuzz.token_sort_ratio(texts[i], texts[j])
            if score >= threshold and texts[i] and texts[j]:
                pairs.append((i, df.at[i, "bp_id"], j, df.at[j, "bp_id"], score))

    df = pd.DataFrame(pairs, columns=["row_i", "bp_id_i", "row_j", "bp_id_j", "score"])

    def _action(score: float) -> str:
        if score >= 97:
            return "merge_candidate"
        if score >= 90:
            return "review"
        return "ignore"

    if not df.empty:
        df["recommended_action"] = df["score"].apply(_action)

    return df

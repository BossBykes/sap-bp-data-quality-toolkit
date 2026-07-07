from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd


def _summary_rows(
    total_rows: int,
    issues: pd.DataFrame,
    exact_dups: pd.DataFrame,
    fuzzy_pairs: pd.DataFrame,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = [
        {"metric": "total_input_rows", "value": total_rows},
        {"metric": "total_issues", "value": len(issues)},
        {"metric": "exact_duplicate_rows", "value": len(exact_dups)},
        {"metric": "fuzzy_duplicate_candidates", "value": len(fuzzy_pairs)},
    ]

    if not issues.empty and "severity" in issues.columns:
        severity_counts = issues["severity"].value_counts().sort_index()
        for severity, count in severity_counts.items():
            rows.append({"metric": f"issue_count_{severity}", "value": int(count)})

    rows.append(
        {
            "metric": "generated_at_utc",
            "value": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
    )
    return rows


def export_excel_report(
    out_path: Path,
    total_rows: int,
    cleaned: pd.DataFrame,
    issues: pd.DataFrame,
    exact_dups: pd.DataFrame,
    fuzzy_pairs: pd.DataFrame,
) -> None:
    summary = pd.DataFrame(
        _summary_rows(
            total_rows=total_rows,
            issues=issues,
            exact_dups=exact_dups,
            fuzzy_pairs=fuzzy_pairs,
        )
    )

    with pd.ExcelWriter(out_path, engine="openpyxl") as writer:
        summary.to_excel(writer, sheet_name="Summary", index=False)
        cleaned.to_excel(writer, sheet_name="Cleaned Records", index=False)
        issues.to_excel(writer, sheet_name="Issues", index=False)
        exact_dups.to_excel(writer, sheet_name="Exact Duplicates", index=False)
        fuzzy_pairs.to_excel(writer, sheet_name="Fuzzy Duplicates", index=False)

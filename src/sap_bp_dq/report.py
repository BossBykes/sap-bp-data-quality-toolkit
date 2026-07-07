from __future__ import annotations
from pathlib import Path
import pandas as pd
from jinja2 import Template

ISSUE_COLUMNS = ["row_index", "bp_id", "field", "issue", "severity"]

TEMPLATE = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8"/>
  <title>SAP BP Data Quality Report</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 24px; }
    h1,h2 { margin-bottom: 8px; }
    table { border-collapse: collapse; width: 100%; margin: 12px 0; }
    th, td { border: 1px solid #ddd; padding: 8px; }
    th { background: #f5f5f5; text-align: left; }
    .kpi { display: inline-block; padding: 10px 14px; border: 1px solid #ddd; margin-right: 10px; }
  </style>
</head>
<body>
  <h1>SAP Business Partner - Data Quality Report</h1>

  <div class="kpi"><b>Total rows:</b> {{ total_rows }}</div>
  <div class="kpi"><b>Total issues:</b> {{ total_issues }}</div>
  <div class="kpi"><b>Exact-dup rows:</b> {{ exact_dup_rows }}</div>
  <div class="kpi"><b>Fuzzy pairs:</b> {{ fuzzy_pairs }}</div>

  <h2>Issues by severity</h2>
  {{ severity_html | safe }}

  <h2>Top issue types</h2>
  {{ top_issues_html | safe }}

  <h2>Sample issues</h2>
  {{ issues_sample_html | safe }}

  <h2>Exact duplicates</h2>
  {{ exact_dups_html | safe }}

  <h2>Fuzzy duplicate pairs (sample)</h2>
  {{ fuzzy_html | safe }}

</body>
</html>
"""


def _ensure_columns(df: pd.DataFrame | None, columns: list[str]) -> pd.DataFrame:
    if df is None:
        return pd.DataFrame(columns=columns)

    out = df.copy()
    for column in columns:
        if column not in out.columns:
            out[column] = pd.Series(dtype="object")
    return out


def _html_table_or_message(
    df: pd.DataFrame,
    message: str,
    *,
    sort_by: str | None = None,
    limit: int = 25,
) -> str:
    if df.empty:
        return f"<p>{message}</p>"

    table = df
    if sort_by and sort_by in table.columns:
        table = table.sort_values(sort_by, ascending=False)
    return table.head(limit).to_html(index=False)


def render_report(
    out_path: Path,
    total_rows: int,
    issues: pd.DataFrame,
    exact_dups: pd.DataFrame,
    fuzzy_pairs: pd.DataFrame,
) -> None:
    issues = _ensure_columns(issues, ISSUE_COLUMNS)
    exact_dups = exact_dups if exact_dups is not None else pd.DataFrame()
    fuzzy_pairs = fuzzy_pairs if fuzzy_pairs is not None else pd.DataFrame()

    if issues.empty:
        severity_summary = pd.DataFrame(columns=["severity", "count"])
        top_issues = pd.DataFrame(columns=["issue", "severity", "count", "example_bp_ids"])
    else:
        top_issues = (
            issues.groupby(["issue", "severity"])
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
            .head(10)
        )
        examples = (
            issues.groupby(["issue", "severity"])["bp_id"]
            .apply(lambda s: ", ".join(s.dropna().astype(str).head(3)))
            .reset_index(name="example_bp_ids")
        )
        top_issues = top_issues.merge(examples, on=["issue", "severity"], how="left")
        severity_summary = (
            issues.groupby("severity")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

    tpl = Template(TEMPLATE)
    html = tpl.render(
        total_rows=total_rows,
        total_issues=len(issues),
        exact_dup_rows=len(exact_dups),
        fuzzy_pairs=len(fuzzy_pairs),
        severity_html=_html_table_or_message(
            severity_summary, "No validation issues found."
        ),
        top_issues_html=_html_table_or_message(top_issues, "No issue types found."),
        issues_sample_html=_html_table_or_message(issues, "No sample issues found."),
        exact_dups_html=_html_table_or_message(
            exact_dups, "No exact duplicate rows found."
        ),
        fuzzy_html=_html_table_or_message(
            fuzzy_pairs, "No fuzzy duplicate pairs found.", sort_by="score"
        ),
    )
    out_path.write_text(html, encoding="utf-8")

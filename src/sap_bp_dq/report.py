from __future__ import annotations
from datetime import datetime, timezone
from pathlib import Path
import pandas as pd
from jinja2 import Template

ISSUE_COLUMNS = ["row_index", "bp_id", "field", "issue", "severity"]

TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <title>SAP BP Data Quality Dashboard</title>
  <style>
    :root {
      color-scheme: light;
      font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
      background: #f4f5f7;
      color: #1f2937;
    }
    * {
      box-sizing: border-box;
    }
    body {
      margin: 0;
      padding: 0;
      min-height: 100vh;
    }
    .page {
      max-width: 1200px;
      margin: 0 auto;
      padding: 24px;
    }
    header.hero {
      padding: 24px 0 12px;
      border-bottom: 1px solid #d1d5db;
    }
    .eyebrow {
      font-size: 0.85rem;
      text-transform: uppercase;
      letter-spacing: 0.12em;
      color: #6b7280;
      margin-bottom: 8px;
    }
    h1 {
      margin: 0;
      font-size: 2rem;
      letter-spacing: -0.03em;
    }
    .hero p {
      margin: 12px 0 0;
      max-width: 68ch;
      color: #4b5563;
    }
    .meta-list {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 12px;
      margin: 20px 0 0;
      padding: 0;
      list-style: none;
    }
    .meta-list div {
      display: flex;
      flex-direction: column;
      gap: 4px;
      font-size: 0.95rem;
      color: #374151;
    }
    .meta-list dt {
      font-weight: 700;
    }
    .section {
      margin-top: 32px;
    }
    .section h2 {
      font-size: 1.25rem;
      margin-bottom: 12px;
      color: #111827;
    }
    .card-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
      gap: 14px;
    }
    .card {
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
      padding: 18px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .card-label {
      font-size: 0.9rem;
      color: #6b7280;
      margin-bottom: 8px;
      text-transform: uppercase;
      letter-spacing: 0.08em;
    }
    .card-value {
      font-size: 1.75rem;
      font-weight: 700;
      color: #111827;
    }
    .table-wrap {
      overflow-x: auto;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      padding: 16px;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }
    .data-table {
      width: 100%;
      border-collapse: collapse;
      min-width: 640px;
    }
    .data-table th,
    .data-table td {
      padding: 12px 14px;
      border: 1px solid #e5e7eb;
      text-align: left;
      vertical-align: top;
    }
    .data-table th {
      background: #f9fafb;
      color: #111827;
      font-weight: 700;
    }
    .data-table tbody tr:nth-child(odd) {
      background: #f8fafc;
    }
    .data-table tbody tr:hover {
      background: #eef2ff;
    }
    .empty-state {
      padding: 18px 16px;
      background: #f9fafb;
      border: 1px solid #e5e7eb;
      border-radius: 10px;
      color: #374151;
    }
    .recommendations {
      display: grid;
      gap: 12px;
      margin-top: 16px;
      padding: 18px 20px;
      background: #ffffff;
      border: 1px solid #e5e7eb;
      border-radius: 12px;
    }
    .recommendations li {
      margin-bottom: 8px;
      line-height: 1.6;
    }
    @media print {
      body {
        background: white;
      }
      .page {
        padding: 0;
      }
      .table-wrap {
        box-shadow: none;
        border: 1px solid #d1d5db;
      }
    }
  </style>
</head>
<body>
  <div class="page">
    <header class="hero">
      <p class="eyebrow">SAP BP Data Quality Dashboard</p>
      <h1>Data Quality Report</h1>
      <p>This report provides an at-a-glance summary of validation findings, duplicate candidates, and next steps for review.</p>
      <div class="meta-list">
        <div><dt>Generated</dt><dd>{{ generated_at }}</dd></div>
        {% if source_input %}<div><dt>Source input</dt><dd>{{ source_input }}</dd></div>{% endif %}
      </div>
    </header>

    <section class="section">
      <h2>Key performance indicators</h2>
      <div class="card-grid">
        {% for card in kpi_cards %}
          <article class="card">
            <div class="card-label">{{ card.label }}</div>
            <div class="card-value">{{ card.value }}</div>
          </article>
        {% endfor %}
      </div>
    </section>

    <section class="section">
      <h2>Issue summary</h2>
      <p>The following section summarizes validation issues and the affected records. Use this information to prioritize corrective actions.</p>
      <div class="card-grid" style="margin-bottom: 18px;">
        <article class="card"><div class="card-label">Validation issues</div><div class="card-value">{{ total_issues }}</div></article>
        <article class="card"><div class="card-label">Exact duplicate rows</div><div class="card-value">{{ exact_dup_rows }}</div></article>
        <article class="card"><div class="card-label">Fuzzy duplicate candidates</div><div class="card-value">{{ fuzzy_pairs }}</div></article>
      </div>
      <div class="section">
        <h3>Issue counts by type</h3>
        <div class="table-wrap">{{ issue_type_html | safe }}</div>
      </div>
      <div class="section">
        <h3>Severity breakdown</h3>
        <div class="table-wrap">{{ severity_html | safe }}</div>
      </div>
    </section>

    <section class="section">
      <h2>Issues table</h2>
      <div class="table-wrap">{{ issues_sample_html | safe }}</div>
    </section>

    <section class="section">
      <h2>Exact duplicates</h2>
      <div class="table-wrap">{{ exact_dups_html | safe }}</div>
    </section>

    <section class="section">
      <h2>Fuzzy duplicate candidates</h2>
      <div class="table-wrap">{{ fuzzy_html | safe }}</div>
    </section>

    <section class="section">
      <h2>Recommended next actions</h2>
      <div class="recommendations">
        <li>Review missing required fields and fill in the missing business partner attributes.</li>
        <li>Correct invalid email, phone, and country values before using the dataset for reporting or integration.</li>
        <li>Investigate exact duplicate groups and resolve duplicates consistently.</li>
        <li>Manually review fuzzy duplicate candidates before merging or updating records.</li>
      </div>
    </section>
  </div>
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
    columns: list[str] | None = None,
) -> str:
    if df.empty:
        return f"<div class=\"empty-state\"><p>{message}</p></div>"

    table = df.copy()
    if columns is not None:
        table = table[[col for col in columns if col in table.columns]]
    if sort_by and sort_by in table.columns:
        table = table.sort_values(sort_by, ascending=False)
    return table.head(limit).to_html(index=False, classes="data-table", border=0)


def render_report(
    out_path: Path,
    total_rows: int,
    issues: pd.DataFrame,
    exact_dups: pd.DataFrame,
    fuzzy_pairs: pd.DataFrame,
    source_input: Path | None = None,
) -> None:
    issues = _ensure_columns(issues, ISSUE_COLUMNS)
    exact_dups = exact_dups if exact_dups is not None else pd.DataFrame()
    fuzzy_pairs = fuzzy_pairs if fuzzy_pairs is not None else pd.DataFrame()

    if issues.empty:
        issue_type_summary = pd.DataFrame(columns=["issue", "count", "example_bp_ids"])
        severity_summary = pd.DataFrame(columns=["severity", "count"])
    else:
        issue_type_summary = (
            issues.groupby("issue")
            .agg(
                count=("issue", "size"),
                example_bp_ids=("bp_id", lambda s: ", ".join(s.dropna().astype(str).head(3))),
            )
            .reset_index()
            .sort_values("count", ascending=False)
        )
        severity_summary = (
            issues.groupby("severity")
            .size()
            .reset_index(name="count")
            .sort_values("count", ascending=False)
        )

    clean_rows = None
    if issues.empty:
        clean_rows = total_rows
    elif "row_index" in issues.columns:
        clean_rows = total_rows - issues["row_index"].dropna().nunique()

    generated_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    kpi_cards = [
        {"label": "Total input rows", "value": total_rows},
        {"label": "Total validation issues", "value": len(issues)},
        {"label": "Exact duplicate rows", "value": len(exact_dups)},
        {"label": "Fuzzy duplicate candidates", "value": len(fuzzy_pairs)},
    ]
    if clean_rows is not None:
        kpi_cards.append({"label": "Clean rows", "value": clean_rows})

    tpl = Template(TEMPLATE)
    html = tpl.render(
        generated_at=generated_at,
        source_input=str(source_input) if source_input is not None else None,
        kpi_cards=kpi_cards,
        total_issues=len(issues),
        total_rows=total_rows,
        exact_dup_rows=len(exact_dups),
        fuzzy_pairs=len(fuzzy_pairs),
        issue_type_html=_html_table_or_message(
            issue_type_summary,
            "No validation issues present.",
            columns=["issue", "count", "example_bp_ids"],
        ),
        severity_html=_html_table_or_message(
            severity_summary,
            "No validation issues present.",
            columns=["severity", "count"],
        ),
        issues_sample_html=_html_table_or_message(
            issues,
            "No sample issues found.",
            columns=["row_index", "bp_id", "field", "issue", "severity"],
        ),
        exact_dups_html=_html_table_or_message(
            exact_dups,
            "No exact duplicate rows found.",
            columns=["group_id", "row_index", "bp_id", "name", "city", "country", "recommended_action"],
        ),
        fuzzy_html=_html_table_or_message(
            fuzzy_pairs,
            "No fuzzy duplicate pairs found.",
            sort_by="score",
            columns=["row_i", "bp_id_i", "row_j", "bp_id_j", "score", "name_i", "city_i", "country_i", "name_j", "city_j", "country_j", "recommended_action"],
        ),
    )
    out_path.write_text(html, encoding="utf-8")

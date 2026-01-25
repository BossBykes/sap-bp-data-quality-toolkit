from __future__ import annotations
from pathlib import Path
import pandas as pd
from jinja2 import Template

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
  <h1>SAP Business Partner – Data Quality Report</h1>

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

def render_report(
    out_path: Path,
    total_rows: int,
    issues: pd.DataFrame,
    exact_dups: pd.DataFrame,
    fuzzy_pairs: pd.DataFrame,
) -> None:
    top_issues = (
        issues.groupby(["issue", "severity"])
        .size()
        .reset_index(name="count")
        .sort_values("count", ascending=False)
        .head(10)
    )
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
        severity_html=severity_summary.to_html(index=False),
        top_issues_html=top_issues.to_html(index=False),
        issues_sample_html=issues.head(25).to_html(index=False),
        exact_dups_html=exact_dups.head(25).to_html(index=False),
        fuzzy_html=fuzzy_pairs.sort_values("score", ascending=False).head(25).to_html(index=False),
    )
    out_path.write_text(html, encoding="utf-8")

from __future__ import annotations
import re
import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def validate_df(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Returns an issues table:
    columns: row_index, bp_id, field, issue, severity
    """
    issues = []

    required = config.get("required_fields", [])
    for field in required:
        missing_mask = df[field].isna() | (df[field].astype(str).str.strip() == "")
        for idx in df[missing_mask].index:
            issues.append((idx, df.at[idx, "bp_id"], field, "missing_required", "HIGH"))

    # bp_type allowed
    allowed_types = set(config.get("allowed_bp_types", []))
    if "bp_type" in df.columns and allowed_types:
        bad = ~df["bp_type"].isin(allowed_types)
        for idx in df[bad].index:
            issues.append((idx, df.at[idx, "bp_id"], "bp_type", "invalid_bp_type", "MEDIUM"))

    # email rule
    if config.get("email_rules", {}).get("enabled", True) and "email" in df.columns:
        non_empty = df["email"].notna() & (df["email"].astype(str).str.strip() != "")
        bad_email = non_empty & (~df["email"].astype(str).str.match(EMAIL_RE))
        for idx in df[bad_email].index:
            issues.append((idx, df.at[idx, "bp_id"], "email", "invalid_email_format", "MEDIUM"))

    # phone rule
    phone_cfg = config.get("phone_rules", {})
    if phone_cfg.get("enabled", True) and "phone" in df.columns:
        min_digits = int(phone_cfg.get("min_digits", 7))
        digits = df["phone"].astype(str).str.replace(r"\D+", "", regex=True)
        bad_phone = df["phone"].notna() & (digits.str.len() < min_digits)
        for idx in df[bad_phone].index:
            issues.append((idx, df.at[idx, "bp_id"], "phone", "phone_too_short", "LOW"))

    return pd.DataFrame(issues, columns=["row_index", "bp_id", "field", "issue", "severity"])
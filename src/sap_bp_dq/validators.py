from __future__ import annotations
import re
import pandas as pd

EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


ISSUE_COLUMNS = ["row_index", "bp_id", "field", "issue", "severity"]


def _bp_id(df: pd.DataFrame, idx) -> object:
    if "bp_id" not in df.columns:
        return None
    return df.at[idx, "bp_id"]


def _missing_mask(series: pd.Series) -> pd.Series:
    return series.isna() | series.map(lambda v: isinstance(v, str) and v.strip() == "")


def validate_df(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    """
    Returns an issues table:
    columns: row_index, bp_id, field, issue, severity
    """
    issues = []

    required = config.get("required_fields", [])
    for field in required:
        if field not in df.columns:
            issues.append((None, None, field, "missing_column", "HIGH"))
            continue

        missing_mask = _missing_mask(df[field])
        for idx in df[missing_mask].index:
            issues.append((idx, _bp_id(df, idx), field, "missing_required", "HIGH"))

    # bp_type allowed
    allowed_types = set(config.get("allowed_bp_types", []))
    if "bp_type" in df.columns and allowed_types:
        bad = ~_missing_mask(df["bp_type"]) & ~df["bp_type"].isin(allowed_types)
        for idx in df[bad].index:
            issues.append((idx, _bp_id(df, idx), "bp_type", "invalid_bp_type", "MEDIUM"))

    # country allowed
    country_cfg = config.get("country_rules", {})
    allowed_countries = set(country_cfg.get("allowed", []))
    if "country" in df.columns and allowed_countries:
        normalized = df["country"].map(
            lambda v: v.strip().upper() if isinstance(v, str) else v
        )
        bad_country = ~_missing_mask(df["country"]) & ~normalized.isin(allowed_countries)
        for idx in df[bad_country].index:
            issues.append((idx, _bp_id(df, idx), "country", "invalid_country", "MEDIUM"))

    # email rule
    if config.get("email_rules", {}).get("enabled", True) and "email" in df.columns:
        non_empty = ~_missing_mask(df["email"])
        bad_email = non_empty & (~df["email"].astype(str).str.match(EMAIL_RE))
        for idx in df[bad_email].index:
            issues.append((idx, _bp_id(df, idx), "email", "invalid_email_format", "MEDIUM"))

    # phone rule
    phone_cfg = config.get("phone_rules", {})
    if phone_cfg.get("enabled", True) and "phone" in df.columns:
        min_digits = int(phone_cfg.get("min_digits", 7))
        digits = df["phone"].astype(str).str.replace(r"\D+", "", regex=True)
        bad_phone = ~_missing_mask(df["phone"]) & (digits.str.len() < min_digits)
        for idx in df[bad_phone].index:
            issues.append((idx, _bp_id(df, idx), "phone", "phone_too_short", "LOW"))

    return pd.DataFrame(issues, columns=ISSUE_COLUMNS)

from __future__ import annotations
from pathlib import Path
import pandas as pd

from sap_bp_dq.utils import load_config, setup_logger
from sap_bp_dq.validators import validate_df
from sap_bp_dq.dedup import find_exact_duplicates, find_fuzzy_duplicates
from sap_bp_dq.excel import export_excel_report
from sap_bp_dq.report import render_report


MISSING_STRINGS = {"", "none", "nan", "null"}


def _clean_string(value):
    if not isinstance(value, str):
        return value

    stripped = value.strip()
    if stripped.lower() in MISSING_STRINGS:
        return pd.NA
    return stripped


def _remove_whitespace(value):
    if not isinstance(value, str):
        return value
    return "".join(value.split())


def basic_cleaning(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    out = df.copy()

    # Trim strings and keep common CSV missing-value artifacts as missing values.
    for col in out.columns:
        out[col] = out[col].apply(_clean_string)

    # normalize some fields
    if "name" in out.columns:
        out["name"] = out["name"].apply(_clean_string)

    if "country" in out.columns and config.get("country_rules", {}).get("uppercase", True):
        out["country"] = out["country"].apply(
            lambda v: v.upper() if isinstance(v, str) else v
        )

    if "phone" in out.columns:
        out["phone"] = out["phone"].apply(_remove_whitespace)

    return out


def _available_preview_columns(df: pd.DataFrame) -> list[str]:
    return [col for col in ["bp_id", "name", "city", "country"] if col in df.columns]


def run_pipeline(input_path: Path, config_path: Path, out_dir: Path) -> dict:
    config = load_config(config_path)
    out_dir.mkdir(parents=True, exist_ok=True)

    log_file = out_dir / "run.log"
    logger = setup_logger(log_file)
    logger.info(f"Loading input: {input_path}")

    df = pd.read_csv(input_path)
    logger.info(f"Rows loaded: {len(df)}")

    logger.info("Basic cleaning...")
    cleaned = basic_cleaning(df, config)

    logger.info("Running validation...")
    issues = validate_df(cleaned, config)
    logger.info(f"Issues found: {len(issues)}")

    logger.info("Finding exact duplicates...")
    exact_keys = config.get("dedup_rules", {}).get("exact_keys", [])
    exact_dups = find_exact_duplicates(cleaned, exact_keys)
    logger.info(f"Exact-duplicate rows: {len(exact_dups)}")

    # Add readable fields to the duplicates table for the report
    preview_cols = _available_preview_columns(cleaned)
    if not exact_dups.empty and "bp_id" in preview_cols:
        exact_dups_preview = exact_dups.merge(
            cleaned[preview_cols],
            on="bp_id",
            how="left",
        )
    else:
        exact_dups_preview = exact_dups.copy()
    if not exact_dups_preview.empty:
        exact_dups_preview["recommended_action"] = "merge_candidate"

    fuzzy_pairs = pd.DataFrame()
    fuzzy_pairs_preview = fuzzy_pairs
    dedup_cfg = config.get("dedup_rules", {})
    if dedup_cfg.get("fuzzy_enabled", True):
        logger.info("Finding fuzzy duplicates...")
        fuzzy_keys = dedup_cfg.get("fuzzy_keys", [])
        threshold = int(dedup_cfg.get("fuzzy_threshold", 90))
        allow_cross_country = bool(dedup_cfg.get("fuzzy_allow_cross_country", False))
        fuzzy_pairs = find_fuzzy_duplicates(
            cleaned,
            fuzzy_keys,
            threshold=threshold,
            allow_cross_country=allow_cross_country,
        )
        logger.info(f"Fuzzy duplicate pairs: {len(fuzzy_pairs)}")
        # Add readable fields for fuzzy pairs (left/right record)
        if not fuzzy_pairs.empty and "bp_id" in preview_cols:
            left = cleaned[preview_cols].rename(
                columns={
                    "bp_id": "bp_id_i",
                    "name": "name_i",
                    "city": "city_i",
                    "country": "country_i",
                }
            )
            right = cleaned[preview_cols].rename(
                columns={
                    "bp_id": "bp_id_j",
                    "name": "name_j",
                    "city": "city_j",
                    "country": "country_j",
                }
            )

            fuzzy_pairs_preview = (
                fuzzy_pairs.merge(left, on="bp_id_i", how="left").merge(
                    right, on="bp_id_j", how="left"
                )
            )
        else:
            fuzzy_pairs_preview = fuzzy_pairs

    cleaned_csv = out_dir / "business_partners_cleaned.csv"
    issues_csv = out_dir / "issues.csv"
    report_html = out_dir / "report.html"
    excel_report = out_dir / "data_quality_report.xlsx"

    logger.info(f"Writing outputs -> {out_dir}")
    cleaned.to_csv(cleaned_csv, index=False)
    issues.to_csv(issues_csv, index=False)

    render_report(
        out_path=report_html,
        total_rows=len(cleaned),
        issues=issues,
        exact_dups=exact_dups_preview,
        fuzzy_pairs=fuzzy_pairs_preview,
        source_input=input_path,
    )
    export_excel_report(
        out_path=excel_report,
        total_rows=len(cleaned),
        cleaned=cleaned,
        issues=issues,
        exact_dups=exact_dups_preview,
        fuzzy_pairs=fuzzy_pairs_preview,
    )

    logger.info("Pipeline complete.")
    return {
        "cleaned_csv": str(cleaned_csv),
        "issues_csv": str(issues_csv),
        "report_html": str(report_html),
        "excel_report": str(excel_report),
        "log_file": str(log_file),
    }

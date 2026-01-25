from __future__ import annotations
from pathlib import Path
import pandas as pd

from sap_bp_dq.utils import load_config, setup_logger
from sap_bp_dq.validators import validate_df
from sap_bp_dq.dedup import find_exact_duplicates, find_fuzzy_duplicates
from sap_bp_dq.report import render_report


def basic_cleaning(df: pd.DataFrame, config: dict) -> pd.DataFrame:
    out = df.copy()

    # trim strings
    for col in out.columns:
        if out[col].dtype == object:
            out[col] = out[col].astype(str).where(out[col].notna(), None)
            out[col] = out[col].astype(object)

    # normalize some fields
    if "name" in out.columns:
        out["name"] = out["name"].astype(str).str.strip()

    if "country" in out.columns and config.get("country_rules", {}).get("uppercase", True):
        out["country"] = out["country"].astype(str).str.strip().str.upper()

    if "phone" in out.columns:
        out["phone"] = out["phone"].astype(str).str.replace(r"\s+", "", regex=True)

    return out


def run_pipeline(input_path: Path, config_path: Path, out_dir: Path) -> dict:
    config = load_config(config_path)

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
    exact_dups_preview = exact_dups.merge(
        cleaned[["bp_id", "name", "city", "country"]],
        on="bp_id",
        how="left",
    )
    if not exact_dups_preview.empty:
        exact_dups_preview["recommended_action"] = "merge_candidate"

    fuzzy_pairs = pd.DataFrame()
    dedup_cfg = config.get("dedup_rules", {})
    if dedup_cfg.get("fuzzy_enabled", True):
        logger.info("Finding fuzzy duplicates...")
        fuzzy_keys = dedup_cfg.get("fuzzy_keys", [])
        threshold = int(dedup_cfg.get("fuzzy_threshold", 90))
        fuzzy_pairs = find_fuzzy_duplicates(cleaned, fuzzy_keys, threshold=threshold)
        logger.info(f"Fuzzy duplicate pairs: {len(fuzzy_pairs)}")
        # Add readable fields for fuzzy pairs (left/right record)
        left = cleaned[["bp_id", "name", "city", "country"]].rename(
            columns={
                "bp_id": "bp_id_i",
                "name": "name_i",
                "city": "city_i",
                "country": "country_i",
            }
        )
        right = cleaned[["bp_id", "name", "city", "country"]].rename(
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

    cleaned_csv = out_dir / "business_partners_cleaned.csv"
    issues_csv = out_dir / "issues.csv"
    report_html = out_dir / "report.html"

    logger.info(f"Writing outputs -> {out_dir}")
    cleaned.to_csv(cleaned_csv, index=False)
    issues.to_csv(issues_csv, index=False)

    render_report(
        out_path=report_html,
        total_rows=len(cleaned),
        issues=issues,
        exact_dups=exact_dups_preview,
        fuzzy_pairs=fuzzy_pairs_preview if not fuzzy_pairs.empty else fuzzy_pairs,
    )

    logger.info("Pipeline complete.")
    return {
        "cleaned_csv": str(cleaned_csv),
        "issues_csv": str(issues_csv),
        "report_html": str(report_html),
        "log_file": str(log_file),
    }

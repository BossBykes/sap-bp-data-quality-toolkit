import pandas as pd
from sap_bp_dq.validators import validate_df
from sap_bp_dq.pipeline import basic_cleaning


def test_required_fields_missing():
    df = pd.DataFrame([
        {"bp_id": "BP00001", "bp_type": "PERSON", "name": "", "country": "DE", "city": "Essen"},
    ])
    config = {
        "required_fields": ["bp_id", "name", "country", "city"],
        "email_rules": {"enabled": False},
    }
    issues = validate_df(df, config)
    assert (issues["issue"] == "missing_required").any()


def test_cleaning_keeps_missing_values_missing():
    df = pd.DataFrame(
        [
            {"bp_id": "BP1", "name": None, "country": "nan", "city": " NULL "},
            {"bp_id": "BP2", "name": float("nan"), "country": " de ", "city": "Essen"},
        ]
    )

    cleaned = basic_cleaning(df, {"country_rules": {"uppercase": True}})

    assert pd.isna(cleaned.at[0, "name"])
    assert pd.isna(cleaned.at[0, "country"])
    assert pd.isna(cleaned.at[0, "city"])
    assert pd.isna(cleaned.at[1, "name"])
    assert cleaned.at[1, "country"] == "DE"


def test_missing_required_column_reports_issue_without_crashing():
    df = pd.DataFrame([{"bp_id": "BP1", "name": "RWE AG"}])
    config = {"required_fields": ["bp_id", "country"]}

    issues = validate_df(df, config)

    missing_column = issues[issues["issue"] == "missing_column"]
    assert len(missing_column) == 1
    assert missing_column.iloc[0]["field"] == "country"


def test_invalid_country_validation():
    df = pd.DataFrame(
        [{"bp_id": "BP1", "bp_type": "COMPANY", "name": "RWE AG", "country": "ZZ"}]
    )
    config = {
        "required_fields": ["bp_id", "country"],
        "country_rules": {"allowed": ["DE", "US"]},
    }

    issues = validate_df(df, config)

    assert (issues["issue"] == "invalid_country").any()

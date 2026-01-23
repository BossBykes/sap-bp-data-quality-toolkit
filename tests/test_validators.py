import pandas as pd
from sap_bp_dq.validators import validate_df

def test_required_fields_missing():
    df = pd.DataFrame([
        {"bp_id": "BP00001", "bp_type": "PERSON", "name": "", "country": "DE", "city": "Essen"},
    ])
    config = {"required_fields": ["bp_id", "name", "country", "city"], "email_rules": {"enabled": False}}
    issues = validate_df(df, config)
    assert (issues["issue"] == "missing_required").any()
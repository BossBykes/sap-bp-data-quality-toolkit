# SAP BP Data Quality Toolkit

A small, practical Python toolkit for validating and cleaning Business Partner-style master data (CSV), detecting duplicates (exact and fuzzy), and generating a simple HTML report. It is designed as a lightweight, configurable pipeline that helps turn messy inputs into clean, reviewable outputs.

## What it does

- Loads Business Partner-style CSV data
- Runs basic cleaning (trim/normalize fields)
- Validates records using configurable rules (YAML)
- Detects duplicates
  - Exact duplicates using configurable key columns
  - Fuzzy duplicates using similarity scoring and a threshold
- Writes outputs to `data/output/`
  - Cleaned CSV
  - Issues CSV
  - HTML report
  - Run log

## Why it exists

Master-data quality problems (missing fields, inconsistent formats, duplicates) create real operational risk and manual rework. This toolkit focuses on a clear workflow: validate, surface issues, propose actions, and provide a report that is easy to review.

## Project structure

```text
SAP-bp_Data-quality-toolkit/
  src/
    sap_bp_dq/
      __init__.py
      __main__.py          # CLI entrypoint: python -m sap_bp_dq
      pipeline.py          # Orchestrates the workflow
      validators.py        # Validation rules
      dedup.py             # Exact + fuzzy duplicate detection
      report.py            # HTML report rendering
      utils.py             # Config + logging helpers
      data_generator.py    # Synthetic data generator for testing/demo
  data/
    raw/
    output/
  config/
    config.yaml
  tests/
  requirements.txt
  pyproject.toml
```

## Requirements

- Python 3.10+ recommended
- Tested on Linux/Ubuntu

## Quick start (local)

1) Create and activate a virtual environment:

```bash
python3 -m venv ~/venvs/sap-bp-dq
source ~/venvs/sap-bp-dq/bin/activate
```

2) Install dependencies:

```bash
pip install -r requirements.txt
```

3) Generate sample data:

```bash
python3 -m sap_bp_dq generate --rows 200
```

4) Run the pipeline:

```bash
python3 -m sap_bp_dq run --input data/raw/business_partners.csv
```

Outputs are written to:

```text
data/output/
  business_partners_cleaned.csv
  issues.csv
  report.html
  run.log
```

Open the report in a browser:

```bash
xdg-open data/output/report.html
```

## CLI usage

Help:

```bash
python3 -m sap_bp_dq -h
```

Generate:

```bash
python3 -m sap_bp_dq generate --rows 500 --seed 42
```

Run:

```bash
python3 -m sap_bp_dq run --input path/to/your.csv --config config/config.yaml --out data/output
```

## Configuration

Rules are configured via YAML (default: `config/config.yaml`). Typical settings include:

- Required fields
- Allowed values (e.g., country codes)
- Email/phone format checks
- Duplicate detection keys and thresholds

Adjust the config to match your data model and quality expectations.

## Testing

Run tests with:

```bash
pytest -q
```

## Notes

- Fuzzy matching is implemented as a simple approach suitable for small-to-medium datasets.
- For very large datasets, you would typically add blocking/indexing strategies to reduce comparisons.

## Author

Chibuike Matthew Ikechukwu  
GitHub: https://github.com/BossBykes

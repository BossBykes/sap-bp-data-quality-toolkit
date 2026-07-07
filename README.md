# SAP BP Data Quality Toolkit

SAP BP Data Quality Toolkit is a portfolio/MVP Python project for validating and reporting on Business Partner-style master data in CSV format. It is not an official SAP product and is not affiliated with SAP.

The toolkit provides a small command-line pipeline that can generate sample data, clean common CSV artifacts, validate configurable data quality rules, identify duplicate candidates, and render review outputs.

## Features

- Generate synthetic Business Partner sample data.
- Clean string fields and normalize selected values.
- Validate required fields, Business Partner type, email format, phone length, and allowed countries.
- Detect exact duplicate groups from configurable keys.
- Detect fuzzy duplicate candidates with configurable match keys and thresholds.
- Write cleaned data, issue records, an HTML report, an Excel workbook, and a run log.

## Project Structure

```text
.
|-- config.yaml
|-- pyproject.toml
|-- requirements.txt
|-- src/
|   `-- sap_bp_dq/
|       |-- __main__.py
|       |-- data_generator.py
|       |-- dedup.py
|       |-- excel.py
|       |-- pipeline.py
|       |-- report.py
|       |-- utils.py
|       `-- validators.py
`-- tests/
    |-- test_dedup.py
    |-- test_pipeline.py
    `-- test_validators.py
```

## Install

From the project root:

```bash
python3 -m venv ~/venvs/sap-bp-dq
source ~/venvs/sap-bp-dq/bin/activate
python -m pip install -e .
```

For development and tests, install the test dependency if it is not already available:

```bash
python -m pip install pytest
```

## Generate Sample Data

```bash
sap-bp-dq generate --rows 200 --out data/raw/business_partners.csv
```

## Run The Pipeline

```bash
sap-bp-dq run --input data/raw/business_partners.csv --config config.yaml --outdir data/output
```

## Output Files

The default run command writes:

```text
data/output/business_partners_cleaned.csv
data/output/issues.csv
data/output/report.html
data/output/data_quality_report.xlsx
data/output/run.log
```

`business_partners_cleaned.csv` contains cleaned input records. `issues.csv` contains validation findings. `report.html` summarizes issues and duplicate candidates for review. `data_quality_report.xlsx` provides a workbook for spreadsheet review. `run.log` records the pipeline steps.

The Excel workbook includes these sheets:

- Summary
- Cleaned Records
- Issues
- Exact Duplicates
- Fuzzy Duplicates

## Configuration

`config.yaml` controls the main data quality rules:

- required fields
- allowed Business Partner types
- country normalization and allowed country codes
- email and phone validation
- exact duplicate keys
- fuzzy duplicate keys and score threshold

Adjust this file to match the expected input schema and review policy for a dataset.

## Tests

```bash
python -m pytest -q
```

## Current Limitations

- The project is an MVP intended for portfolio review and local experimentation.
- Input support is CSV-only.
- Fuzzy matching uses an O(n^2) comparison strategy, so large datasets need blocking or indexing.
- Duplicate recommendations are review aids, not automatic merge decisions.
- The validation rules cover common quality checks but do not model a full SAP Business Partner schema.

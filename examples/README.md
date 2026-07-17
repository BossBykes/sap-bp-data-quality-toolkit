# Example dataset

This example dataset is provided to demonstrate the toolkit with realistic SAP Business Partner-style input.

## Purpose

The sample CSV contains valid and intentionally imperfect records that exercise validation and duplicate detection.

## Included issues

- missing required `city` value
- invalid email address format
- short phone number
- invalid country code outside the allowed list
- exact duplicate records by `name`, `city`, and `country`
- fuzzy duplicate candidate with similar names in the same city

## Run the example

From the project root:

```bash
sap-bp-dq run --input examples/sample_business_partners.csv --config config.yaml --outdir data/output/example_run
```

## Outputs

The command writes the following files to `data/output/example_run`:

- `business_partners_cleaned.csv`
- `issues.csv`
- `report.html`
- `data_quality_report.xlsx`
- `run.log`

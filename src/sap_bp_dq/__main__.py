import argparse
from pathlib import Path
from sap_bp_dq.pipeline import run_pipeline
from sap_bp_dq.data_generator import generate_sample_data

def main():
    parser = argparse.ArgumentParser(prog="sap-bp-dq", description="SAP BP Data Quality Toolkit")
    sub = parser.add_subparsers(dest="cmd", required=True)

    g = sub.add_parser("generate", help="Generate synthetic Business Partner CSV data")
    g.add_argument("--rows", type=int, default=200)
    g.add_argument("--out", type=str, default="data/raw/business_partners.csv")

    r = sub.add_parser("run", help="Run data quality checks + dedup + report")
    r.add_argument("--input", type=str, default="data/raw/business_partners.csv")
    r.add_argument("--config", type=str, default="config.yaml")
    r.add_argument("--outdir", type=str, default="data/output")

    args = parser.parse_args()

    if args.cmd == "generate":
        out_path = Path(args.out)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        generate_sample_data(rows=args.rows, out_path=out_path)
        print(f"Generated sample data -> {out_path}")

    elif args.cmd == "run":
        outdir = Path(args.outdir)
        outdir.mkdir(parents=True, exist_ok=True)
        results = run_pipeline(
            input_path=Path(args.input),
            config_path=Path(args.config),
            out_dir=outdir,
        )
        print("Done.")
        print(f"Cleaned CSV: {results['cleaned_csv']}")
        print(f"Report HTML : {results['report_html']}")
        print(f"Log file    : {results['log_file']}")

if __name__ == "__main__":
    main()

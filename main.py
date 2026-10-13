"""Main CLI entry point for Employee Attendance & Shift Reporting Automation System.

Executes end-to-end data processing, validation, metric calculations,
chart generation, and export of multi-tab Excel, CSV, and text reports.

Usage:
    python main.py
    python main.py --input data/sample_attendance.csv --grace 5
    python main.py --input data/sample_attendance.xlsx --grace 10 --output-dir my_output
"""

import argparse
from pathlib import Path
import sys

from src.data_loader import DataLoaderError, load_attendance_data
from src.validator import validate_attendance_dataframe
from src.attendance_analyzer import analyze_attendance
from src.report_generator import (
    generate_excel_report,
    generate_csv_report,
    generate_validation_csv,
    generate_text_summary,
)
from src.chart_generator import (
    generate_department_chart,
    generate_shift_chart,
    generate_late_arrivals_chart,
    generate_status_donut_chart,
)


def run_pipeline(input_file: Path, grace_period: int = 5, output_dir: Path = Path("output")) -> int:
    """Run the complete attendance automation workflow."""
    print("=" * 72)
    print(" EMPLOYEE ATTENDANCE & SHIFT REPORTING AUTOMATION SYSTEM")
    print("=" * 72)
    print(f"[*] Input File:    {input_file}")
    print(f"[*] Grace Period:  {grace_period} minutes")
    print(f"[*] Output Folder: {output_dir.resolve()}")
    print("-" * 72)

    output_dir.mkdir(parents=True, exist_ok=True)

    # 1. Load Data
    print("[1/5] Loading attendance file...")
    try:
        raw_df = load_attendance_data(input_file)
        print(f"      [OK] Successfully loaded {len(raw_df)} total raw rows.")
    except DataLoaderError as err:
        print(f"      [ERROR] File Load Failure: {err}")
        return 1
    except Exception as err:
        print(f"      [ERROR] Unexpected error loading file: {err}")
        return 1

    # 2. Validation
    print("[2/5] Running schema and data quality validation...")
    val_result = validate_attendance_dataframe(raw_df)

    if not val_result.is_valid_schema:
        print(f"      [ERROR] Fatal Schema Error: {val_result.schema_error}")
        return 1

    print(f"      [OK] Valid Records:    {val_result.valid_count}")
    print(f"      [!] Excluded Records: {val_result.invalid_count}")
    if val_result.issues_summary:
        print("      Validation Issues Found:")
        for issue_name, count in val_result.issues_summary.items():
            print(f"        - {issue_name}: {count} row(s)")

    if val_result.valid_count == 0:
        print("      [WARNING] No valid rows remained after validation. Halting analysis.")
        return 1

    # 3. Attendance Analysis
    print(f"[3/5] Performing shift analysis (Grace threshold = {grace_period} mins)...")
    analysis_result = analyze_attendance(
        df=val_result.valid_df,
        grace_period_minutes=grace_period,
        excluded_records_count=val_result.invalid_count
    )
    metrics = analysis_result.metrics

    print(f"      [OK] Present: {metrics.present_count} | Absent: {metrics.absent_count} | Late: {metrics.late_count}")
    print(f"      [OK] Attendance Rate: {metrics.attendance_percentage}%")
    print(f"      [!] Missing Punches Requiring Review: {metrics.missing_punch_count}")

    # 4. Generate Visual Charts
    print("[4/5] Rendering operations visual charts...")
    try:
        generate_department_chart(analysis_result.dept_summary, output_dir=output_dir)
        generate_shift_chart(analysis_result.shift_summary, output_dir=output_dir)
        generate_late_arrivals_chart(analysis_result.enriched_df, output_dir=output_dir)
        generate_status_donut_chart(analysis_result.metrics, output_dir=output_dir)
        print("      [OK] Charts saved to output folder (PNG format).")
    except Exception as err:
        print(f"      [WARNING] Error generating charts: {err}")

    # 5. Export Reports
    print("[5/5] Generating Excel, CSV, and summary reports...")
    try:
        excel_path = output_dir / "attendance_master_report.xlsx"
        generate_excel_report(analysis_result, invalid_df=val_result.invalid_df, output_path=excel_path)
        print(f"      [OK] Excel Report:    {excel_path.name}")

        csv_clean_path = output_dir / "attendance_cleaned_data.csv"
        generate_csv_report(analysis_result.enriched_df, output_path=csv_clean_path)
        print(f"      [OK] Cleaned CSV:     {csv_clean_path.name}")

        if not val_result.invalid_df.empty:
            csv_val_path = output_dir / "validation_issues_audit.csv"
            generate_validation_csv(val_result.invalid_df, output_path=csv_val_path)
            print(f"      [OK] Validation CSV:  {csv_val_path.name}")

        txt_path = output_dir / "daily_summary_report.txt"
        summary_text = generate_text_summary(analysis_result, output_path=txt_path)
        print(f"      [OK] Summary Text:    {txt_path.name}")
    except Exception as err:
        print(f"      [ERROR] Report export failure: {err}")
        return 1

    print("\n" + summary_text + "\n")
    print("=" * 72)
    print(" PIPELINE COMPLETED SUCCESSFULLY! Output generated in:")
    print(f" -> {output_dir.resolve()}")
    print("=" * 72)
    return 0


def main():
    """Parse command line arguments and execute pipeline."""
    parser = argparse.ArgumentParser(
        description="Employee Attendance & Shift Reporting Automation System"
    )
    parser.add_argument(
        "--input", "-i",
        type=str,
        default="data/sample_attendance.csv",
        help="Path to CSV or Excel attendance file (default: data/sample_attendance.csv)"
    )
    parser.add_argument(
        "--grace", "-g",
        type=int,
        default=5,
        help="Grace period in minutes for late arrival evaluation (default: 5)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        type=str,
        default="output",
        help="Folder to store exported reports and charts (default: output)"
    )

    args = parser.parse_args()
    input_path = Path(args.input)
    output_dir = Path(args.output_dir)

    sys.exit(run_pipeline(input_path, grace_period=args.grace, output_dir=output_dir))


if __name__ == "__main__":
    main()

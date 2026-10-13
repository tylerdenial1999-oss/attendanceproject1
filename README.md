# Employee Attendance & Shift Reporting Automation System

An enterprise-ready, beginner-friendly Python automation system built for manufacturing plants, warehousing facilities, and operations teams to automate daily employee attendance analysis, shift-wise reporting, and punctuality tracking.

---

## 📌 Executive Summary

Manual attendance reconciliation in manufacturing and operations environments is slow, error-prone, and often leads to payroll discrepancies or unaddressed shift shortages. This system automates the ingestion, data quality validation, grace period punctuality analysis, missing punch flagging, and report delivery in under **3 seconds**.

### Key Highlights:
- **Zero Cloud / Paid API Dependencies**: Runs completely locally on open-source Python libraries.
- **Configurable Grace Period**: Evaluate late arrivals against flexible grace thresholds (default: 5 minutes).
- **Human-in-the-Loop Safety**: Flags missing punches and irregular logs for manual supervisor review without making automated punitive decisions.
- **Data Quality Audit Trail**: Never silently discards malformed records; isolates anomalies into a separate audit report.
- **Multi-Format Export**: Generates styled multi-tab Excel workbooks, cleaned CSVs, operational text handover notes, and visual PNG charts.
- **Interactive Web Dashboard**: Streamlit interface with real-time KPI metrics, filters, and 1-click test datasets.

---

## 🏗️ Project Architecture & Directory Structure

```text
employee_attendance_automation/
├── app.py                      # Interactive Streamlit Web Dashboard
├── main.py                     # CLI Pipeline Entry Point
├── requirements.txt            # Project dependencies
├── README.md                   # Complete documentation & interview guide
├── data/
│   ├── sample_attendance.csv       # Realistic dataset with deliberate validation edge cases
│   ├── sample_attendance_clean.csv # 100% clean 20-employee dataset
│   └── sample_attendance.xlsx      # Formatted Excel sample dataset
├── src/
│   ├── __init__.py
│   ├── data_loader.py          # CSV & Excel ingestion with encoding fallbacks
│   ├── validator.py            # Schema, duplicate, date/time, and status validation
│   ├── attendance_analyzer.py  # Late arrival, grace period, missing punch, and KPI logic
│   ├── chart_generator.py      # High-resolution Matplotlib operations charts
│   └── report_generator.py     # OpenPyXL multi-tab workbook, CSV, and text report generator
├── tests/
│   ├── __init__.py
│   ├── test_validator.py       # 11 automated unit tests for validation & ingestion
│   └── test_attendance_analyzer.py # 8 automated tests for grace periods, punches, & KPIs
└── output/                     # Generated reports and visual charts
    ├── attendance_master_report.xlsx
    ├── attendance_cleaned_data.csv
    ├── validation_issues_audit.csv
    ├── daily_summary_report.txt
    ├── department_attendance_chart.png
    ├── shift_attendance_chart.png
    ├── late_arrivals_chart.png
    └── attendance_status_donut.png
```

---

## 🛠️ Technology Stack

| Technology | Purpose |
|---|---|
| **Python 3.10+ / 3.14** | Core programming language |
| **Pandas** | High-performance tabular data manipulation and aggregation |
| **OpenPyXL** | Creation and styling of multi-tab Excel workbooks (`.xlsx`) |
| **Matplotlib** | Headless rendering of corporate operations charts (`.png`) |
| **Streamlit** | Interactive local web dashboard with real-time filtering |
| **pytest** | Automated test suite ensuring pipeline reliability |

---

## 📋 Input Data Format Specification

The system accepts either **CSV** (`.csv`) or **Excel** (`.xlsx`, `.xls`) files containing the following 10 mandatory columns:

| Column Name | Data Type | Example | Description |
|---|---|---|---|
| `employee_id` | String | `E001` | Unique employee badge or roster identifier |
| `employee_name` | String | `Arun Sharma` | Full name of the employee |
| `department` | String | `Production` | Operating unit (Production, Quality, Stores, Maintenance, etc.) |
| `date` | Date (`YYYY-MM-DD`) | `2026-10-12` | Shift date |
| `shift` | String | `Morning` | Scheduled shift name (`Morning`, `Evening`, `Night`) |
| `scheduled_in` | Time (`HH:MM`) | `09:00` | Scheduled shift start time (24-hour clock) |
| `actual_in` | Time (`HH:MM`) | `09:05` | Actual biometric clock-in timestamp (blank if absent) |
| `scheduled_out` | Time (`HH:MM`) | `17:00` | Scheduled shift finish time (24-hour clock) |
| `actual_out` | Time (`HH:MM`) | `17:05` | Actual biometric clock-out timestamp (blank if absent) |
| `status` | String | `Present` | Status: `Present`, `Absent`, `Half Day`, or `On Leave` |

---

## 📐 Formulas & Business Rules

### 1. Attendance Percentage Calculation
$$\text{Attendance Percentage} = \frac{\text{Present Records}}{\text{Expected Attendance Records}} \times 100$$
- **Present Records**: Sum of all employees with status `Present` or `Half Day`.
- **Expected Records**: Total valid records scheduled on the shift roster.
- **Safety Handling**: Excluded malformed records are omitted from the denominator to avoid distorting compliance metrics; zero records yield `0.0%` safely.

### 2. Late Arrival Detection with Grace Period
An employee is flagged as late **if and only if**:
$$\text{Status} \in \{\text{Present}, \text{Half Day}\} \quad \text{AND} \quad \text{Actual In} > \text{Scheduled In} + \text{Grace Period (minutes)}$$
- **Grace Period (Default: 5 Minutes)**: An employee scheduled at `09:00` arriving at `09:04` is classified as **On Time**. An arrival at `09:06` or later is flagged as **Late** by 6 minutes.
- **Absent Employees**: An employee with status `Absent` has empty punches. They are **never** flagged as late.
- **Overnight Shifts**: Safely handles 24-hour clock rollover (e.g., Night shift scheduled at `22:00` and finishing at `06:00`).

### 3. Missing Punch Detection (Human-in-the-Loop)
An entry is marked for manual supervisor verification if:
- $\text{Status} \in \{\text{Present}, \text{Half Day}\}$ and `actual_in` is empty $\rightarrow$ Flagged as `Missing Punch-In`.
- $\text{Status} \in \{\text{Present}, \text{Half Day}\}$ and `actual_out` is empty $\rightarrow$ Flagged as `Missing Punch-Out`.
- $\text{Status} \in \{\text{Present}, \text{Half Day}\}$ and both are empty $\rightarrow$ Flagged as `Missing Both (In & Out)`.

---

## 🚀 Quickstart Guide (Windows Commands)

Open **PowerShell** or **Command Prompt** and follow these exact steps:

### 1. Clone or Navigate to Project
```powershell
cd "c:\project 1"
```

### 2. (Optional) Create and Activate Virtual Environment
```powershell
python -m venv venv
.\venv\Scripts\activate
```

### 3. Install Dependencies
```powershell
python -m pip install -r requirements.txt
```

### 4. Run Automated Tests
```powershell
python -m pytest -v
```
*(Expected: 19 passed tests in ~2 seconds)*

### 5. Run the Automated Batch Pipeline (CLI)
```powershell
# Run with bundled realistic sample dataset (5-minute grace period)
python main.py

# Run with custom parameters:
python main.py --input data/sample_attendance.csv --grace 10 --output-dir output
```

### 6. Launch the Interactive Web Dashboard
```powershell
python -m streamlit run app.py
```
*Your browser will automatically open at `http://localhost:8501`.*

---

## 📊 Sample Input & Pipeline Output

### Input Snippet:
```csv
employee_id,employee_name,department,date,shift,scheduled_in,actual_in,scheduled_out,actual_out,status
E001,Arun Sharma,Production,2026-10-12,Morning,09:00,08:55,17:00,17:05,Present
E002,Kumar Verma,Quality,2026-10-12,Morning,09:00,09:25,17:00,17:00,Present
E003,Ravi Nair,Production,2026-10-12,Evening,14:00,,22:00,,Absent
E005,Manoj Singh,Maintenance,2026-10-12,Morning,09:00,09:02,17:00,,Present
E006,Vikram Joshi,Maintenance,2026-10-12,Morning,09:00,09:04,17:00,17:02,Present
,Vikas Yadav,Production,2026-10-12,Morning,09:00,09:00,17:00,17:00,Present
E022,Harish Salve,Quality,2026-10-12,Morning,25:99,09:00,17:00,17:00,Present
```

### System Execution Results:
```text
[1/5] Loading attendance file...
      [OK] Successfully loaded 24 total raw rows.
[2/5] Running schema and data quality validation...
      [OK] Valid Records:    20
      [!] Excluded Records: 4
      Validation Issues Found:
        - Empty Employee ID: 1 row(s)
        - Duplicate Record: 1 row(s)
        - Invalid Time Format: 1 row(s)
        - Invalid Status: 1 row(s)
[3/5] Performing shift analysis (Grace threshold = 5 mins)...
      [OK] Present: 16 | Absent: 3 | Late: 4
      [OK] Attendance Rate: 80.0%
      [!] Missing Punches Requiring Review: 3
[4/5] Rendering operations visual charts...
      [OK] Charts saved to output folder (PNG format).
[5/5] Generating Excel, CSV, and summary reports...
      [OK] Excel Report:    attendance_master_report.xlsx
      [OK] Cleaned CSV:     attendance_cleaned_data.csv
      [OK] Validation CSV:  validation_issues_audit.csv
      [OK] Summary Text:    daily_summary_report.txt
```

---

## 📑 Excel Report Structure (`attendance_master_report.xlsx`)

The generated workbook uses `openpyxl` with corporate styling:
1. **Executive Summary Tab**:
   - High-contrast banner and generation metadata.
   - Colored KPI metric blocks (Total Scheduled, Present, Absent, Attendance Rate, Late, Missing Punches, Reviews).
   - Department-wise breakdown table with alternating zebra rows and thin borders.
   - Shift-wise performance table.
2. **Attendance Details Tab**:
   - All 20 valid records enriched with computed columns (`is_late`, `late_minutes`, `is_missing_punch`, `review_reason`).
   - Soft amber fill highlights for late personnel; soft red fill highlights for missing punches.
   - Dynamic auto-sized column widths.
3. **Manual Review List Tab**:
   - Filtered view showing only workers with incomplete biometric clock entries.
4. **Validation Exclusions Tab**:
   - Audit trail detailing every excluded row with exact error descriptions (e.g. `Empty Employee ID`, `Invalid time format: scheduled_in '25:99'`).

---

## 🔧 Troubleshooting Common Errors

| Issue | Cause | Fix |
|---|---|---|
| `Fatal Schema Error: Missing required column(s)` | Header name typo or missing column in file | Ensure all 10 required headers match: `employee_id, employee_name, department, date, shift, scheduled_in, actual_in, scheduled_out, actual_out, status`. |
| `UnicodeDecodeError` when loading CSV | Non-UTF8 file encoding | The system automatically falls back to `latin-1` encoding. |
| `The file is empty or contains no readable columns` | Uploading a 0-byte file | The validator rejects empty buffers gracefully without crashing. |
| `Streamlit command not found` | Running in environment without Streamlit | Run `python -m pip install streamlit` or invoke as `python -m streamlit run app.py`. |

---

## 🎓 Interview Presentation Guide

When showcasing this project in technical or operations engineering interviews:

### 1. Architectural Highlights to Explain:
- **Separation of Concerns**: Explain how the project isolates responsibilities: `data_loader.py` (I/O), `validator.py` (data hygiene), `attendance_analyzer.py` (domain logic), `report_generator.py` (presentation layer), and `app.py` (UI).
- **Grace Period Configurability**: Explain why hardcoding a strict minute comparison fails in the real world (traffic, biometric queue delays). Demonstrating a configurable grace parameter highlights understanding of shop-floor realities.

### 2. Key Edge Cases You Handled:
- **Absent vs Late**: Mention that absent employees have empty punch times. A naive comparison might calculate `null` as late or trigger a crash; your code explicitly verifies `status == Present` before comparing timestamps.
- **Overnight Shifts**: Handled clock rollover across midnight (e.g., 22:00 to 06:00 shifts).
- **Defensive Data Handling**: Rejected records are preserved in `validation_issues_audit.csv` rather than being silently dropped, fulfilling enterprise auditing requirements.

### 3. Business Safety:
- Emphasize that the system **flags** anomalies for human supervisor review instead of automatically docking pay or issuing disciplinary actions.

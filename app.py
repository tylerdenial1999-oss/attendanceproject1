"""Streamlit Web Dashboard for Employee Attendance & Shift Reporting Automation System.

Interactive web interface for operations and HR supervisors:
- Upload CSV / Excel attendance logs or 1-click test with sample data
- Dynamic grace period adjustment slider
- Real-time KPI metrics & Matplotlib analytics charts
- Interactive department, shift, date, and status filters
- Flagged manual verification queue
- Validation audit trail for excluded/questionable records
- 1-click downloads for formatted Excel, CSV, and text reports
"""

import io
from pathlib import Path
import pandas as pd
import streamlit as st

from src.data_loader import DataLoaderError, load_attendance_data
from src.validator import validate_attendance_dataframe
from src.attendance_analyzer import analyze_attendance
from src.chart_generator import (
    generate_department_chart,
    generate_shift_chart,
    generate_late_arrivals_chart,
    generate_status_donut_chart,
)
from src.report_generator import (
    generate_excel_report,
    generate_csv_report,
    generate_validation_csv,
    generate_text_summary,
)

# Page configuration
st.set_page_config(
    page_title="Attendance & Shift Automation System",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for polished manufacturing dashboard styling
st.markdown("""
<style>
    .main-title {
        font-size: 2.1rem;
        font-weight: 700;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 1.2rem;
    }
    .metric-card {
        background-color: #F8FAFC;
        border-radius: 8px;
        padding: 12px 16px;
        border: 1px solid #E2E8F0;
        text-align: center;
    }
    .badge-late {
        background-color: #FEF3C7;
        color: #B45309;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
    .badge-missing {
        background-color: #FEE2E2;
        color: #B91C1C;
        padding: 2px 8px;
        border-radius: 4px;
        font-weight: 600;
    }
</style>
""", unsafe_allow_html=True)


def load_file_content(uploaded_file, use_sample: bool, sample_type: str = "raw") -> pd.DataFrame:
    """Helper to load data from user upload or bundled sample."""
    if use_sample:
        sample_path = Path("data/sample_attendance.csv") if sample_type == "raw" else Path("data/sample_attendance_clean.csv")
        if not sample_path.exists():
            raise DataLoaderError(f"Sample file not found at {sample_path}")
        return load_attendance_data(sample_path)
    if uploaded_file is not None:
        return load_attendance_data(uploaded_file)
    return None


def main():
    st.markdown('<div class="main-title">⏱️ Employee Attendance & Shift Reporting System</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="sub-title">Automated attendance verification, punctuality tracking, and shift operations reporting.</div>',
        unsafe_allow_html=True
    )

    # Sidebar Controls
    st.sidebar.header("📁 Data Source & Configuration")

    data_source_mode = st.sidebar.radio(
        "Choose Data Source:",
        ["Use Bundled Sample Data", "Upload CSV / Excel File"],
        index=0
    )

    uploaded_file = None
    use_sample = False
    sample_choice = "raw"

    if data_source_mode == "Use Bundled Sample Data":
        use_sample = True
        sample_choice = st.sidebar.selectbox(
            "Select Sample Dataset:",
            ["Realistic Data with Validation Anomalies (24 rows)", "Clean Standard Data (20 rows)"],
            index=0
        )
        sample_choice_key = "raw" if "Anomalies" in sample_choice else "clean"

        # Download sample template button
        sample_file_path = Path("data/sample_attendance.csv")
        if sample_file_path.exists():
            st.sidebar.download_button(
                label="📥 Download Sample CSV Template",
                data=sample_file_path.read_bytes(),
                file_name="sample_attendance_template.csv",
                mime="text/csv",
                help="Download this template to test formatting or input custom data."
            )
    else:
        uploaded_file = st.sidebar.file_uploader(
            "Upload Attendance Log (CSV or XLSX)",
            type=["csv", "xlsx", "xls"],
            help="Upload an attendance log with scheduled and actual entry/exit timestamps."
        )

    st.sidebar.markdown("---")
    st.sidebar.header("⚙️ Business Rules")
    grace_period = st.sidebar.slider(
        "Grace Period (Minutes):",
        min_value=0,
        max_value=30,
        value=5,
        step=1,
        help="Flag arrival as late only when actual clock-in exceeds scheduled time by more than this period."
    )

    # Load Data
    try:
        raw_df = load_file_content(uploaded_file, use_sample=use_sample, sample_type=sample_choice_key if use_sample else "raw")
    except DataLoaderError as err:
        st.error(f"⚠️ Data Import Error: {err}")
        return
    except Exception as err:
        st.error(f"⚠️ Unexpected reading error: {err}")
        return

    if raw_df is None:
        st.info("👋 Please upload an attendance file from the sidebar or select bundled sample data to begin.")
        return

    # Run Validation
    val_result = validate_attendance_dataframe(raw_df)

    if not val_result.is_valid_schema:
        st.error(f"❌ Schema Validation Failed: {val_result.schema_error}")
        st.warning("Please ensure your uploaded file contains all 10 required columns:")
        st.code("employee_id, employee_name, department, date, shift, scheduled_in, actual_in, scheduled_out, actual_out, status")
        return

    if val_result.valid_count == 0:
        st.error("❌ No valid rows passed data quality checks. Please review the excluded records below.")
        st.dataframe(val_result.invalid_df, use_container_width=True)
        return

    # Run Analysis
    analysis = analyze_attendance(
        df=val_result.valid_df,
        grace_period_minutes=grace_period,
        excluded_records_count=val_result.invalid_count
    )
    metrics = analysis.metrics
    enriched_df = analysis.enriched_df

    # Global Sidebar Filters
    st.sidebar.markdown("---")
    st.sidebar.header("🔍 Filters")

    # Date filter
    available_dates = sorted(enriched_df["date"].unique().tolist())
    selected_dates = st.sidebar.multiselect("Filter by Date:", available_dates, default=available_dates)

    # Department filter
    available_depts = sorted(enriched_df["department"].unique().tolist())
    selected_depts = st.sidebar.multiselect("Filter by Department:", available_depts, default=available_depts)

    # Shift filter
    available_shifts = sorted(enriched_df["shift"].unique().tolist())
    selected_shifts = st.sidebar.multiselect("Filter by Shift:", available_shifts, default=available_shifts)

    # Status filter
    available_statuses = sorted(enriched_df["status"].unique().tolist())
    selected_statuses = st.sidebar.multiselect("Filter by Status:", available_statuses, default=available_statuses)

    # Only Review toggle
    filter_only_review = st.sidebar.checkbox("Show Only Records Requiring Verification", value=False)

    # Apply filters to view dataframe
    filtered_df = enriched_df[
        (enriched_df["date"].isin(selected_dates)) &
        (enriched_df["department"].isin(selected_depts)) &
        (enriched_df["shift"].isin(selected_shifts)) &
        (enriched_df["status"].isin(selected_statuses))
    ]

    if filter_only_review:
        filtered_df = filtered_df[filtered_df["needs_manual_review"]]

    # Top KPI Metrics Row
    kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)
    with kpi1:
        st.metric("Total Records", f"{metrics.total_records}", delta=f"{val_result.invalid_count} excluded" if val_result.invalid_count > 0 else None, delta_color="inverse")
    with kpi2:
        st.metric("Present", f"{metrics.present_count}")
    with kpi3:
        st.metric("Absent", f"{metrics.absent_count}")
    with kpi4:
        st.metric("Attendance %", f"{metrics.attendance_percentage}%")
    with kpi5:
        st.metric("Late Arrivals", f"{metrics.late_count}", help=f"Exceeded scheduled by > {grace_period} mins")
    with kpi6:
        st.metric("Missing Punches", f"{metrics.missing_punch_count}", delta=f"{metrics.manual_review_count} need review" if metrics.manual_review_count > 0 else "0", delta_color="inverse")

    st.markdown("---")

    # Main Tabs
    tab_dash, tab_records, tab_review, tab_quality, tab_export = st.tabs([
        "📊 Visual Dashboard",
        "📋 Attendance Records",
        "⚠️ Manual Review Queue",
        "🛡️ Data Quality & Exclusions",
        "📥 Report Export Center"
    ])

    # TAB 1: Visual Dashboard
    with tab_dash:
        col_c1, col_c2 = st.columns(2)
        with col_c1:
            fig_dept, _ = generate_department_chart(analysis.dept_summary)
            st.pyplot(fig_dept)
        with col_c2:
            fig_shift, _ = generate_shift_chart(analysis.shift_summary)
            st.pyplot(fig_shift)

        col_c3, col_c4 = st.columns(2)
        with col_c3:
            fig_late, _ = generate_late_arrivals_chart(analysis.enriched_df)
            st.pyplot(fig_late)
        with col_c4:
            fig_donut, _ = generate_status_donut_chart(analysis.metrics)
            st.pyplot(fig_donut)

        st.markdown("### 🏢 Department & Shift Breakdown Summaries")
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.caption("Department Performance")
            st.dataframe(analysis.dept_summary, use_container_width=True, hide_index=True)
        with col_t2:
            st.caption("Shift Performance")
            st.dataframe(analysis.shift_summary, use_container_width=True, hide_index=True)

    # TAB 2: Attendance Records
    with tab_records:
        st.markdown(f"### 📋 Filtered Records ({len(filtered_df)} of {len(enriched_df)})")
        display_cols = [
            "employee_id", "employee_name", "department", "date", "shift",
            "scheduled_in", "actual_in", "scheduled_out", "actual_out",
            "status", "is_late", "late_minutes", "is_missing_punch", "review_reason"
        ]
        st.dataframe(
            filtered_df[display_cols],
            use_container_width=True,
            hide_index=True
        )

    # TAB 3: Manual Review Queue
    with tab_review:
        st.markdown("### ⚠️ Records Flagged for Manual Verification")
        st.caption("These records contain punch anomalies (missing punch-in, missing punch-out, or both). Company policies require human verification rather than automatic assumption.")

        if analysis.review_df.empty:
            st.success("✅ All attendance entries are complete. No missing punches or anomalies detected.")
        else:
            st.warning(f"🔔 Found {len(analysis.review_df)} record(s) requiring supervisor verification.")
            review_display = [
                "employee_id", "employee_name", "department", "date", "shift",
                "scheduled_in", "actual_in", "scheduled_out", "actual_out",
                "status", "missing_punch_type", "review_reason"
            ]
            st.dataframe(
                analysis.review_df[review_display],
                use_container_width=True,
                hide_index=True
            )

    # TAB 4: Data Quality & Exclusions
    with tab_quality:
        st.markdown("### 🛡️ Data Quality & Audit Trail")
        st.caption("Original input records are never silently deleted. Questionable or malformed entries are documented here for audit compliance.")

        q1, q2, q3 = st.columns(3)
        with q1:
            st.metric("Total Raw Input Rows", f"{val_result.total_records}")
        with q2:
            st.metric("Valid Rows Processed", f"{val_result.valid_count}")
        with q3:
            st.metric("Excluded Anomaly Rows", f"{val_result.invalid_count}")

        if val_result.invalid_df.empty:
            st.success("✅ Clean dataset: 100% of input rows met schema and data formatting rules.")
        else:
            st.error(f"Found {len(val_result.invalid_df)} row(s) with data quality defects:")
            st.dataframe(val_result.invalid_df, use_container_width=True, hide_index=True)

    # TAB 5: Report Export Center
    with tab_export:
        st.markdown("### 📥 Report Export Center")
        st.write("Generate and download production-ready operational reports in Excel, CSV, and plain-text formats.")

        # In-memory buffer generation for Streamlit direct downloads
        # 1. Excel Workbook
        excel_buffer = io.BytesIO()
        temp_excel_path = Path("output/temp_export.xlsx")
        generate_excel_report(analysis, invalid_df=val_result.invalid_df, output_path=temp_excel_path)
        excel_bytes = temp_excel_path.read_bytes()

        # 2. Clean CSV
        clean_csv_bytes = analysis.enriched_df.to_csv(index=False).encode("utf-8")

        # 3. Validation CSV
        val_csv_bytes = val_result.invalid_df.to_csv(index=False).encode("utf-8") if not val_result.invalid_df.empty else b"No validation errors"

        # 4. Text Summary
        text_summary = generate_text_summary(analysis)

        d_col1, d_col2, d_col3, d_col4 = st.columns(4)

        with d_col1:
            st.download_button(
                label="📊 Download Formatted Excel Report",
                data=excel_bytes,
                file_name="Daily_Attendance_Report.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )

        with d_col2:
            st.download_button(
                label="📄 Download Cleaned CSV",
                data=clean_csv_bytes,
                file_name="Attendance_Cleaned.csv",
                mime="text/csv",
                use_container_width=True
            )

        with d_col3:
            st.download_button(
                label="🛡️ Download Validation Audit CSV",
                data=val_csv_bytes,
                file_name="Validation_Issues_Audit.csv",
                mime="text/csv",
                use_container_width=True,
                disabled=val_result.invalid_df.empty
            )

        with d_col4:
            st.download_button(
                label="📝 Download Text Summary Report",
                data=text_summary.encode("utf-8"),
                file_name="Daily_Shift_Summary.txt",
                mime="text/plain",
                use_container_width=True
            )

        st.markdown("---")
        with st.expander("📄 Preview Plain-Text Shift Handover Report", expanded=True):
            st.code(text_summary, language="text")


if __name__ == "__main__":
    main()

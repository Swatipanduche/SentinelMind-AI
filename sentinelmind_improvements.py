from pathlib import Path
import json
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd
import streamlit as st

BASE = Path(__file__).resolve().parent
THREAT_FILE = BASE / "reports" / "sentinelmind_threat_report.csv"
DEVICE_FILE = BASE / "reports" / "device_risk_assessment.csv"
NODE_FILE = BASE / "data" / "processed" / "network_nodes.csv"
EDGE_FILE = BASE / "data" / "processed" / "network_edges.csv"

# PART 1 + PART 2 — DATABASE AND ROOT CAUSE ANALYSIS
# ============================================================

import json
import sqlite3
from datetime import datetime

import numpy as np
import pandas as pd


INCIDENT_DB = BASE / "reports" / "incident_management.db"


def get_db_connection():
    INCIDENT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(INCIDENT_DB, timeout=30)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS incidents (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                case_id TEXT,
                record_id TEXT UNIQUE,
                investigation_status TEXT DEFAULT 'Open',
                analyst_notes TEXT DEFAULT '',
                created_at TEXT,
                updated_at TEXT
            )
        """)

        columns = {
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(incidents)"
            ).fetchall()
        }

        additions = {
            "incident_summary": "TEXT DEFAULT ''",
            "evidence": "TEXT DEFAULT '{}'",
            "recommended_action": "TEXT DEFAULT ''",
            "analyst": "TEXT DEFAULT ''"
        }

        for name, definition in additions.items():
            if name not in columns:
                conn.execute(
                    f"ALTER TABLE incidents ADD COLUMN {name} {definition}"
                )

        conn.execute("""
            CREATE TABLE IF NOT EXISTS mitigation_comparisons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                comparison_name TEXT,
                before_metrics TEXT,
                after_metrics TEXT,
                analyst_notes TEXT DEFAULT '',
                created_at TEXT
            )
        """)


def save_incident(
    record_id,
    status="Open",
    notes="",
    summary="",
    evidence=None,
    recommended_action="",
    analyst=""
):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    evidence_json = json.dumps(
        evidence if evidence is not None else {},
        default=str
    )

    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT id FROM incidents WHERE record_id = ?",
            (str(record_id),)
        ).fetchone()

        if existing:
            conn.execute("""
                UPDATE incidents
                SET investigation_status = ?,
                    analyst_notes = ?,
                    incident_summary = ?,
                    evidence = ?,
                    recommended_action = ?,
                    analyst = ?,
                    updated_at = ?
                WHERE record_id = ?
            """, (
                status, notes, summary, evidence_json,
                recommended_action, analyst, now, str(record_id)
            ))
        else:
            case_id = (
                f"SM-{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
            )

            conn.execute("""
                INSERT INTO incidents (
                    case_id, record_id, investigation_status,
                    analyst_notes, created_at, updated_at,
                    incident_summary, evidence,
                    recommended_action, analyst
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_id, str(record_id), status, notes,
                now, now, summary, evidence_json,
                recommended_action, analyst
            ))


def get_incident(record_id):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM incidents WHERE record_id = ?",
            (str(record_id),)
        ).fetchone()

    return dict(row) if row else None


def get_all_incidents(status=None):
    with get_db_connection() as conn:
        if status and status != "All":
            rows = conn.execute("""
                SELECT * FROM incidents
                WHERE investigation_status = ?
                ORDER BY updated_at DESC
            """, (status,)).fetchall()
        else:
            rows = conn.execute("""
                SELECT * FROM incidents
                ORDER BY updated_at DESC
            """).fetchall()

    return [dict(row) for row in rows]


def save_mitigation_comparison(
    comparison_name,
    before_metrics,
    after_metrics,
    analyst_notes=""
):
    with get_db_connection() as conn:
        conn.execute("""
            INSERT INTO mitigation_comparisons (
                comparison_name, before_metrics,
                after_metrics, analyst_notes, created_at
            )
            VALUES (?, ?, ?, ?, ?)
        """, (
            comparison_name,
            json.dumps(before_metrics, default=str),
            json.dumps(after_metrics, default=str),
            analyst_notes,
            datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ))


def get_mitigation_comparisons():
    with get_db_connection() as conn:
        rows = conn.execute("""
            SELECT * FROM mitigation_comparisons
            ORDER BY created_at DESC
        """).fetchall()

    return [dict(row) for row in rows]


init_database()


# ============================================================


# PART 4 — BEFORE VS AFTER MITIGATION VERIFICATION
# ============================================================

def summarize_network_capture(df):

    metrics = {
        "Total Flows": int(len(df))
    }

    # --------------------------------------------------------
    # NUMERIC NETWORK METRICS
    # --------------------------------------------------------

    feature_columns = {
        "Flow Duration": [
            "Flow Duration",
            "flow_duration"
        ],
        "Flow Bytes/s": [
            "Flow Bytes/s",
            "Flow_Bytes/s",
            "flow_bytes_per_sec"
        ],
        "Flow Packets/s": [
            "Flow Packets/s",
            "Flow_Packets/s",
            "flow_packets_per_sec"
        ]
    }

    for metric_name, possible_columns in feature_columns.items():

        column = next(
            (
                col for col in possible_columns
                if col in df.columns
            ),
            None
        )

        if column is not None:

            values = pd.to_numeric(
                df[column],
                errors="coerce"
            ).replace(
                [np.inf, -np.inf],
                np.nan
            ).dropna()

            if not values.empty:
                metrics[f"Average {metric_name}"] = round(
                    float(values.mean()), 4
                )

                metrics[f"Median {metric_name}"] = round(
                    float(values.median()), 4
                )

    # --------------------------------------------------------
    # ATTACK RATE / ANOMALY RATE
    # --------------------------------------------------------

    detection_columns = [
        "RF_Prediction",
        "Anomaly_Detected",
        "Predicted_Label",
        "Prediction",
        "Threat_Status"
    ]

    detection_column = next(
        (
            col for col in detection_columns
            if col in df.columns
        ),
        None
    )

    if detection_column is not None:

        values = df[detection_column].dropna()

        if not values.empty:

            if pd.api.types.is_numeric_dtype(values):

                positive_count = int(
                    (pd.to_numeric(values, errors="coerce") > 0).sum()
                )

            else:

                normalized = values.astype(str).str.strip().str.lower()

                benign_values = [
                    "benign",
                    "normal",
                    "0",
                    "false",
                    "no",
                    "safe"
                ]

                positive_count = int(
                    (~normalized.isin(benign_values)).sum()
                )

            metrics["Detected Suspicious Flows"] = positive_count

            metrics["Detected Suspicious Rate (%)"] = round(
                (positive_count / len(values)) * 100,
                2
            )

            metrics["Detection Column"] = detection_column

    return metrics


def display_mitigation_verification():

    st.markdown("## Before vs After Mitigation Verification")

    st.caption(
        "Compare separate network traffic captures to evaluate "
        "changes after a mitigation action."
    )

    st.warning(
        "For a meaningful comparison, use captures collected under "
        "similar network conditions, with comparable time windows "
        "and traffic volumes. A lower suspicious rate alone does "
        "not prove that an attack has been eliminated."
    )

    # --------------------------------------------------------
    # UPLOAD CAPTURES
    # --------------------------------------------------------

    col1, col2 = st.columns(2)

    with col1:

        st.markdown("### Before Mitigation")

        before_file = st.file_uploader(
            "Upload BEFORE CSV",
            type=["csv"],
            key="mitigation_before_upload"
        )

    with col2:

        st.markdown("### After Mitigation")

        after_file = st.file_uploader(
            "Upload AFTER CSV",
            type=["csv"],
            key="mitigation_after_upload"
        )

    if before_file is None or after_file is None:

        st.info(
            "Upload both CSV files to begin the comparison."
        )

    else:

        try:

            before_df = pd.read_csv(before_file)
            after_df = pd.read_csv(after_file)

            if before_df.empty or after_df.empty:

                st.error(
                    "One or both uploaded CSV files contain no records."
                )

                return

            st.success(
                "Both network traffic captures loaded successfully."
            )

            # ------------------------------------------------
            # SUMMARIZE CAPTURES
            # ------------------------------------------------

            before_metrics = summarize_network_capture(
                before_df
            )

            after_metrics = summarize_network_capture(
                after_df
            )

            st.markdown("### Comparison Results")

            comparison_rows = []

            all_metric_names = list(
                dict.fromkeys(
                    list(before_metrics.keys())
                    + list(after_metrics.keys())
                )
            )

            for metric in all_metric_names:

                before_value = before_metrics.get(metric, "Not available")
                after_value = after_metrics.get(metric, "Not available")

                comparison_rows.append({
                    "Metric": metric,
                    "Before": before_value,
                    "After": after_value
                })

            comparison_df = pd.DataFrame(comparison_rows)

            st.dataframe(
                comparison_df,
                use_container_width=True,
                hide_index=True
            )

            # ------------------------------------------------
            # FLOW COUNT COMPARISON
            # ------------------------------------------------

            before_count = before_metrics["Total Flows"]
            after_count = after_metrics["Total Flows"]

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Before Flows",
                f"{before_count:,}"
            )

            c2.metric(
                "After Flows",
                f"{after_count:,}"
            )

            flow_change = (
                ((after_count - before_count) / before_count) * 100
                if before_count > 0
                else 0
            )

            c3.metric(
                "Flow Count Change",
                f"{flow_change:+.2f}%"
            )

            # ------------------------------------------------
            # SAVE COMPARISON
            # ------------------------------------------------

            st.divider()

            st.markdown("### Save Verification Results")

            comparison_name = st.text_input(
                "Comparison Name",
                placeholder="Example: Firewall rule verification"
            )

            analyst_notes = st.text_area(
                "Mitigation Details / Analyst Notes",
                placeholder=(
                    "Describe the mitigation applied and "
                    "any observations from the comparison."
                )
            )

            if st.button(
                "Save Mitigation Comparison",
                use_container_width=True
            ):

                if not comparison_name.strip():

                    st.error(
                        "Please enter a comparison name."
                    )

                else:

                    try:

                        save_mitigation_comparison(
                            comparison_name=comparison_name.strip(),
                            before_metrics=before_metrics,
                            after_metrics=after_metrics,
                            analyst_notes=analyst_notes
                        )

                        st.success(
                            "Mitigation comparison saved successfully."
                        )

                    except Exception as save_error:

                        st.error(
                            f"Could not save comparison: {save_error}"
                        )

        except Exception as error:

            st.error(
                f"Could not process the uploaded CSV files: {error}"
            )

    # --------------------------------------------------------
    # PREVIOUSLY SAVED COMPARISONS
    # --------------------------------------------------------

    st.divider()

    st.markdown("### Saved Mitigation Comparisons")

    try:

        saved_comparisons = get_mitigation_comparisons()

        if saved_comparisons:

            st.json(saved_comparisons)

        else:

            st.info(
                "No mitigation comparisons have been saved yet."
            )

    except Exception as error:

        st.error(
            f"Could not retrieve saved comparisons: {error}"
        )

# ============================================================
# PART 5 — SOURCE IP AND DESTINATION IP INVESTIGATION
# ============================================================

def display_ip_attack_investigation():

    st.markdown("## IP Attack Path Investigation")

    st.caption(
        "Investigate communication patterns between source "
        "and destination IP addresses using the separate "
        "network topology dataset."
    )

    # --------------------------------------------------------
    # LOAD SEPARATE IP DATASET
    # --------------------------------------------------------

    attack_path_file = (
        BASE / "data" / "raw" / "attack_path_sample.csv"
    )

    if not attack_path_file.exists():

        st.error(
            f"IP investigation dataset not found: {attack_path_file}"
        )

        return

    try:

        ip_df = pd.read_csv(attack_path_file)

    except Exception as error:

        st.error(f"Could not load IP dataset: {error}")

        return

    if ip_df.empty:

        st.warning("The IP investigation dataset is empty.")
        return

    # --------------------------------------------------------
    # IDENTIFY IP COLUMNS
    # --------------------------------------------------------

    source_candidates = [
        "Source IP",
        "Src IP",
        "src_ip",
        "source_ip",
        "SourceIP",
        "SrcIP"
    ]

    destination_candidates = [
        "Destination IP",
        "Dst IP",
        "dst_ip",
        "destination_ip",
        "DestinationIP",
        "DstIP"
    ]

    label_candidates = [
        "Label",
        "label",
        "Attack",
        "attack",
        "Threat_Status",
        "Actual_Label"
    ]

    source_column = next(
        (col for col in source_candidates if col in ip_df.columns),
        None
    )

    destination_column = next(
        (
            col for col in destination_candidates
            if col in ip_df.columns
        ),
        None
    )

    label_column = next(
        (col for col in label_candidates if col in ip_df.columns),
        None
    )

    if source_column is None or destination_column is None:

        st.error(
            "Could not identify source and destination IP columns. "
            "Available columns:"
        )

        st.write(list(ip_df.columns))
        return

    # --------------------------------------------------------
    # CLEAN IP DATA
    # --------------------------------------------------------

    ip_df[source_column] = (
        ip_df[source_column].astype(str).str.strip()
    )

    ip_df[destination_column] = (
        ip_df[destination_column].astype(str).str.strip()
    )

    ip_df = ip_df[
        (ip_df[source_column] != "")
        & (ip_df[destination_column] != "")
        & (ip_df[source_column].str.lower() != "nan")
        & (ip_df[destination_column].str.lower() != "nan")
    ].copy()

    if ip_df.empty:

        st.warning("No valid source/destination IP records found.")
        return

    # --------------------------------------------------------
    # DATASET OVERVIEW
    # --------------------------------------------------------

    unique_sources = ip_df[source_column].nunique()
    unique_destinations = ip_df[destination_column].nunique()

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Network Flows", f"{len(ip_df):,}")
    c2.metric("Unique Source IPs", unique_sources)
    c3.metric("Unique Destination IPs", unique_destinations)
    c4.metric(
        "Unique IP Pairs",
        ip_df[[source_column, destination_column]]
        .drop_duplicates()
        .shape[0]
    )

    st.divider()

    # --------------------------------------------------------
    # LABEL SUMMARY
    # --------------------------------------------------------

    if label_column is not None:

        st.markdown("### Traffic Classification")

        label_summary = (
            ip_df[label_column]
            .fillna("Unknown")
            .astype(str)
            .value_counts()
            .reset_index()
        )

        label_summary.columns = [
            "Traffic Classification",
            "Flow Count"
        ]

        st.dataframe(
            label_summary,
            use_container_width=True,
            hide_index=True
        )

    # --------------------------------------------------------
    # SOURCE IP INVESTIGATION
    # --------------------------------------------------------

    st.markdown("### Source IP Investigation")

    source_summary = (
        ip_df.groupby(source_column)
        .size()
        .reset_index(name="Flow Count")
        .sort_values("Flow Count", ascending=False)
    )

    st.dataframe(
        source_summary,
        use_container_width=True,
        hide_index=True
    )

    selected_source = st.selectbox(
        "Select Source IP",
        ["All Sources"] + sorted(
            ip_df[source_column].unique().tolist()
        ),
        key="ip_source_selector"
    )

    # --------------------------------------------------------
    # DESTINATION IP INVESTIGATION
    # --------------------------------------------------------

    st.markdown("### Destination IP Investigation")

    destination_summary = (
        ip_df.groupby(destination_column)
        .size()
        .reset_index(name="Received Flow Count")
        .sort_values("Received Flow Count", ascending=False)
    )

    st.dataframe(
        destination_summary,
        use_container_width=True,
        hide_index=True
    )

    selected_destination = st.selectbox(
        "Select Destination IP",
        ["All Destinations"] + sorted(
            ip_df[destination_column].unique().tolist()
        ),
        key="ip_destination_selector"
    )

    # --------------------------------------------------------
    # FILTER COMMUNICATION RECORDS
    # --------------------------------------------------------

    filtered_df = ip_df.copy()

    if selected_source != "All Sources":

        filtered_df = filtered_df[
            filtered_df[source_column] == selected_source
        ]

    if selected_destination != "All Destinations":

        filtered_df = filtered_df[
            filtered_df[destination_column] == selected_destination
        ]

    st.divider()

    st.markdown("### Source-to-Destination Communication")

    st.write(
        f"Matching network flows: **{len(filtered_df):,}**"
    )

    if filtered_df.empty:

        st.info("No communication records match the selected IP filters.")

    else:

        pair_summary = (
            filtered_df.groupby(
                [source_column, destination_column]
            )
            .size()
            .reset_index(name="Flow Count")
            .sort_values("Flow Count", ascending=False)
        )

        st.dataframe(
            pair_summary,
            use_container_width=True,
            hide_index=True
        )

        st.download_button(
            "Export Filtered IP Investigation CSV",
            data=filtered_df.to_csv(index=False).encode("utf-8"),
            file_name="sentinelmind_ip_investigation.csv",
            mime="text/csv",
            key="ip_investigation_export"
        )

    # --------------------------------------------------------
    # INVESTIGATION LIMITATIONS
    # --------------------------------------------------------

    st.info(
        "Investigation scope: These IP relationships come from "
        "the separate IP attack-path sample. They are not "
        "record-level IP mappings for the CIC-IDS2017 threat report. "
        "Flow counts indicate observed activity in this dataset, "
        "not confirmed device compromise."
    )

# ============================================================


# PART 6 — AUTOMATED DIAGNOSTICS AND SELF-TESTS
# ============================================================

def run_sentinelmind_diagnostics():

    results = []

    def add_result(test_name, status, details):

        results.append({
            "Test": test_name,
            "Status": status,
            "Details": str(details)
        })

    # --------------------------------------------------------
    # 1. PROJECT DATASET FILE CHECKS
    # --------------------------------------------------------

    dataset_paths = {
        "Threat Report": globals().get(
            "THREAT_FILE",
            BASE / "reports" / "sentinelmind_threat_report.csv"
        ),
        "Device Report": globals().get(
            "DEVICE_FILE",
            BASE / "reports" / "sentinelmind_device_report.csv"
        ),
        "Network Node Report": globals().get(
            "NODE_FILE",
            BASE / "reports" / "sentinelmind_node_report.csv"
        ),
        "IP Attack Path Sample": (
            BASE / "data" / "raw" / "attack_path_sample.csv"
        )
    }

    for dataset_name, dataset_path in dataset_paths.items():

        try:

            path = Path(dataset_path)

            if path.exists():

                add_result(
                    f"{dataset_name} File",
                    "PASS",
                    f"Found: {path}"
                )

            else:

                add_result(
                    f"{dataset_name} File",
                    "WARNING",
                    f"File not found: {path}"
                )

        except Exception as error:

            add_result(
                f"{dataset_name} File",
                "FAIL",
                error
            )

    # --------------------------------------------------------
    # 2. CSV READABILITY CHECKS
    # --------------------------------------------------------

    for dataset_name, dataset_path in dataset_paths.items():

        try:

            path = Path(dataset_path)

            if not path.exists():
                continue

            test_df = pd.read_csv(path, nrows=100)

            if test_df.empty:

                add_result(
                    f"{dataset_name} Readability",
                    "WARNING",
                    "CSV contains no data rows."
                )

            else:

                add_result(
                    f"{dataset_name} Readability",
                    "PASS",
                    f"Successfully read {len(test_df.columns)} columns."
                )

        except Exception as error:

            add_result(
                f"{dataset_name} Readability",
                "FAIL",
                error
            )

    # --------------------------------------------------------
    # 3. IP DATASET SCHEMA CHECK
    # --------------------------------------------------------

    ip_path = BASE / "data" / "raw" / "attack_path_sample.csv"

    if ip_path.exists():

        try:

            ip_test_df = pd.read_csv(ip_path, nrows=100)

            source_candidates = [
                "Source IP", "Src IP", "src_ip",
                "source_ip", "SourceIP", "SrcIP"
            ]

            destination_candidates = [
                "Destination IP", "Dst IP", "dst_ip",
                "destination_ip", "DestinationIP", "DstIP"
            ]

            source_found = any(
                col in ip_test_df.columns
                for col in source_candidates
            )

            destination_found = any(
                col in ip_test_df.columns
                for col in destination_candidates
            )

            if source_found and destination_found:

                add_result(
                    "IP Dataset Schema",
                    "PASS",
                    "Source IP and destination IP columns found."
                )

            else:

                add_result(
                    "IP Dataset Schema",
                    "FAIL",
                    f"Available columns: {list(ip_test_df.columns)}"
                )

        except Exception as error:

            add_result(
                "IP Dataset Schema",
                "FAIL",
                error
            )

    # --------------------------------------------------------
    # 4. DATA QUALITY CHECKS
    # --------------------------------------------------------

    for variable_name, display_name in [
        ("threat", "Threat Dataset"),
        ("devices", "Device Dataset"),
        ("nodes", "Network Node Dataset")
    ]:

        loaded_df = globals().get(variable_name)

        if not isinstance(loaded_df, pd.DataFrame):
            continue

        try:

            missing_cells = int(
                loaded_df.isna().sum().sum()
            )

            duplicate_rows = int(
                loaded_df.duplicated().sum()
            )

            add_result(
                f"{display_name} Missing Values",
                "PASS" if missing_cells == 0 else "WARNING",
                f"{missing_cells} missing cells."
            )

            add_result(
                f"{display_name} Duplicate Rows",
                "PASS" if duplicate_rows == 0 else "WARNING",
                f"{duplicate_rows} duplicate rows."
            )

            numeric_columns = loaded_df.select_dtypes(
                include=np.number
            ).columns

            invalid_numeric_count = 0

            for column in numeric_columns:

                values = pd.to_numeric(
                    loaded_df[column],
                    errors="coerce"
                )

                invalid_numeric_count += int(
                    np.isinf(values.dropna()).sum()
                )

            add_result(
                f"{display_name} Numeric Validity",
                "PASS" if invalid_numeric_count == 0 else "WARNING",
                f"{invalid_numeric_count} infinite numeric values."
            )

        except Exception as error:

            add_result(
                f"{display_name} Data Quality",
                "FAIL",
                error
            )

    # --------------------------------------------------------
    # 5. SQLITE DATABASE CONNECTIVITY
    # --------------------------------------------------------

    try:

        conn = get_db_connection()

        test_result = conn.execute(
            "SELECT 1"
        ).fetchone()

        if test_result and test_result[0] == 1:

            add_result(
                "SQLite Database Connection",
                "PASS",
                "Database connection successful."
            )

        else:

            add_result(
                "SQLite Database Connection",
                "FAIL",
                "Database test query returned an unexpected result."
            )

        conn.close()

    except Exception as error:

        add_result(
            "SQLite Database Connection",
            "FAIL",
            error
        )

    # --------------------------------------------------------
    # 6. SQLITE WRITE TEST
    # --------------------------------------------------------

    try:

        conn = get_db_connection()

        conn.execute("SAVEPOINT diagnostics_write_test")

        conn.execute(
            """
            CREATE TEMP TABLE IF NOT EXISTS
            sentinelmind_diagnostics_test (
                test_id INTEGER
            )
            """
        )

        conn.execute(
            """
            INSERT INTO sentinelmind_diagnostics_test
            (test_id)
            VALUES (1)
            """
        )

        test_row = conn.execute(
            """
            SELECT test_id
            FROM sentinelmind_diagnostics_test
            WHERE test_id = 1
            """
        ).fetchone()

        conn.execute(
            "ROLLBACK TO diagnostics_write_test"
        )

        conn.execute(
            "RELEASE diagnostics_write_test"
        )

        conn.close()

        if test_row and test_row[0] == 1:

            add_result(
                "SQLite Write Test",
                "PASS",
                "Temporary database write and read succeeded."
            )

        else:

            add_result(
                "SQLite Write Test",
                "FAIL",
                "Could not verify temporary database write."
            )

    except Exception as error:

        add_result(
            "SQLite Write Test",
            "FAIL",
            error
        )

    # --------------------------------------------------------
    # 7. REQUIRED FUNCTION CHECKS
    # --------------------------------------------------------

    required_functions = [
        "save_incident",
        "get_incident",
        "get_all_incidents",
        "save_mitigation_comparison",
        "get_mitigation_comparisons",
        "display_incident_management",
        "display_mitigation_verification",
        "display_ip_attack_investigation",
        "run_sentinelmind_diagnostics",
        "display_sentinelmind_diagnostics"
    ]

    for function_name in required_functions:

        function_exists = callable(
            globals().get(function_name)
        )

        add_result(
            f"Function: {function_name}",
            "PASS" if function_exists else "FAIL",
            "Function is available."
            if function_exists
            else "Function is missing or not callable."
        )

    return pd.DataFrame(results)


# ============================================================
# PART 6 — DIAGNOSTICS DASHBOARD
# ============================================================

def display_sentinelmind_diagnostics():

    st.markdown("## SentinelMind AI — System Diagnostics")

    st.caption(
        "Automated checks for project datasets, data quality, "
        "database connectivity and required application functions."
    )

    if st.button(
        "Run All System Tests",
        use_container_width=True,
        key="run_sentinelmind_diagnostics"
    ):

        diagnostics_df = run_sentinelmind_diagnostics()

        st.session_state["sentinelmind_diagnostics_results"] = (
            diagnostics_df
        )

    diagnostics_df = st.session_state.get(
        "sentinelmind_diagnostics_results"
    )

    if diagnostics_df is None:

        st.info(
            "Click 'Run All System Tests' to execute the diagnostics."
        )

        return

    # --------------------------------------------------------
    # SUMMARY
    # --------------------------------------------------------

    total_tests = len(diagnostics_df)

    passed = int(
        (diagnostics_df["Status"] == "PASS").sum()
    )

    warnings = int(
        (diagnostics_df["Status"] == "WARNING").sum()
    )

    failed = int(
        (diagnostics_df["Status"] == "FAIL").sum()
    )

    c1, c2, c3, c4 = st.columns(4)

    c1.metric("Total Tests", total_tests)
    c2.metric("Passed", passed)
    c3.metric("Warnings", warnings)
    c4.metric("Failed", failed)

    if failed == 0 and warnings == 0:

        st.success("All executed diagnostics passed.")

    elif failed > 0:

        st.error(
            f"{failed} diagnostic test(s) failed. "
            "Review the report below."
        )

    else:

        st.warning(
            "Diagnostics completed with warnings. "
            "Review the report below."
        )

    # --------------------------------------------------------
    # DETAILED REPORT
    # --------------------------------------------------------

    st.markdown("### Detailed Test Results")

    st.dataframe(
        diagnostics_df,
        use_container_width=True,
        hide_index=True
    )

    # --------------------------------------------------------
    # EXPORT REPORT
    # --------------------------------------------------------

    st.download_button(
        "Download Diagnostics Report",
        data=diagnostics_df.to_csv(index=False).encode("utf-8"),
        file_name="sentinelmind_diagnostics_report.csv",
        mime="text/csv",
        key="download_sentinelmind_diagnostics"
    )


def configure_context(**context):
    """Provide the main application's loaded data to diagnostics."""
    globals().update(context)


# Ensure the shared incident database tables exist.
init_database()

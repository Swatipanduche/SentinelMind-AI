from pathlib import Path
import json
import sqlite3
from datetime import datetime

import pandas as pd
import streamlit as st


BASE = Path(__file__).resolve().parent
INCIDENT_DB = BASE / "reports" / "incident_management.db"


def get_db_connection():
    INCIDENT_DB.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(INCIDENT_DB), timeout=30)
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
                incident_summary TEXT DEFAULT '',
                evidence TEXT DEFAULT '{}',
                recommended_action TEXT DEFAULT '',
                analyst TEXT DEFAULT '',
                created_at TEXT,
                updated_at TEXT
            )
        """)

        existing = {
            row["name"]
            for row in conn.execute("PRAGMA table_info(incidents)").fetchall()
        }

        required_columns = {
            "case_id": "TEXT",
            "record_id": "TEXT",
            "investigation_status": "TEXT DEFAULT 'Open'",
            "analyst_notes": "TEXT DEFAULT ''",
            "incident_summary": "TEXT DEFAULT ''",
            "evidence": "TEXT DEFAULT '{}'",
            "recommended_action": "TEXT DEFAULT ''",
            "analyst": "TEXT DEFAULT ''",
            "created_at": "TEXT",
            "updated_at": "TEXT"
        }

        for column, definition in required_columns.items():
            if column not in existing:
                conn.execute(
                    f"ALTER TABLE incidents ADD COLUMN {column} {definition}"
                )


def save_incident(
    record_id,
    status="Open",
    notes="",
    summary="",
    evidence=None,
    recommended_action="",
    analyst=""
):
    record_id = str(record_id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    evidence_json = json.dumps(evidence or {}, default=str)

    with get_db_connection() as conn:
        existing = conn.execute(
            "SELECT case_id, created_at FROM incidents WHERE record_id = ?",
            (record_id,)
        ).fetchone()

        if existing:
            case_id = existing["case_id"]
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
                recommended_action, analyst, now, record_id
            ))
        else:
            case_id = "SM-" + datetime.now().strftime("%Y%m%d-%H%M%S-%f")
            conn.execute("""
                INSERT INTO incidents (
                    case_id, record_id, investigation_status,
                    analyst_notes, incident_summary, evidence,
                    recommended_action, analyst, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                case_id, record_id, status, notes, summary,
                evidence_json, recommended_action, analyst, now, now
            ))

    return case_id


def get_incident(record_id):
    with get_db_connection() as conn:
        row = conn.execute(
            "SELECT * FROM incidents WHERE record_id = ?",
            (str(record_id),)
        ).fetchone()

    if row is None:
        return None

    result = dict(row)
    try:
        result["evidence"] = json.loads(result.get("evidence") or "{}")
    except (TypeError, json.JSONDecodeError):
        result["evidence"] = {}

    return result


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

    results = []
    for row in rows:
        item = dict(row)
        try:
            item["evidence"] = json.loads(item.get("evidence") or "{}")
        except (TypeError, json.JSONDecodeError):
            item["evidence"] = {}
        results.append(item)

    return results


def display_incident_management():
    st.title("Incident Management")
    st.caption(
        "Persistent investigation register for incidents saved from "
        "the Threat Detection workspace."
    )

    all_incidents = get_all_incidents()

    total = len(all_incidents)
    open_count = sum(
        item["investigation_status"] == "Open"
        for item in all_incidents
    )
    investigating_count = sum(
        item["investigation_status"] == "Investigating"
        for item in all_incidents
    )
    resolved_count = sum(
        item["investigation_status"] == "Resolved"
        for item in all_incidents
    )

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total cases", total)
    c2.metric("Open", open_count)
    c3.metric("Investigating", investigating_count)
    c4.metric("Resolved", resolved_count)

    st.divider()
    st.subheader("Incident register")

    selected_filter = st.selectbox(
        "Filter by status",
        ["All", "Open", "Investigating", "Resolved", "Closed"]
    )

    incidents = get_all_incidents(selected_filter)

    if incidents:
        display_rows = []
        for item in incidents:
            display_rows.append({
                "Case ID": item.get("case_id", ""),
                "Record ID": item.get("record_id", ""),
                "Status": item.get("investigation_status", ""),
                "Summary": item.get("incident_summary", ""),
                "Analyst": item.get("analyst", ""),
                "Created": item.get("created_at", ""),
                "Last Updated": item.get("updated_at", "")
            })

        register_df = pd.DataFrame(display_rows)
        st.dataframe(register_df, use_container_width=True, hide_index=True)

        csv_data = register_df.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Download incident register (CSV)",
            data=csv_data,
            file_name="sentinelmind_incident_register.csv",
            mime="text/csv"
        )

        st.divider()
        st.subheader("Update an incident")

        case_options = {
            f'{item.get("case_id", "No Case ID")} | '
            f'Record {item.get("record_id", "")}': item
            for item in incidents
        }

        selected_label = st.selectbox(
            "Select incident",
            list(case_options.keys())
        )
        incident = case_options[selected_label]

        status_options = [
            "Open", "Investigating", "Resolved", "Closed"
        ]
        current_status = incident.get("investigation_status", "Open")

        with st.form("update_incident_form"):
            updated_status = st.selectbox(
                "Investigation status",
                status_options,
                index=(
                    status_options.index(current_status)
                    if current_status in status_options else 0
                )
            )

            updated_summary = st.text_area(
                "Incident summary",
                value=incident.get("incident_summary", "")
            )

            updated_notes = st.text_area(
                "Analyst notes",
                value=incident.get("analyst_notes", ""),
                height=120
            )

            updated_action = st.text_area(
                "Recommended action",
                value=incident.get("recommended_action", ""),
                height=100
            )

            updated_analyst = st.text_input(
                "Analyst",
                value=incident.get("analyst", "")
            )

            submitted = st.form_submit_button(
                "Update incident",
                use_container_width=True
            )

            if submitted:
                save_incident(
                    record_id=incident["record_id"],
                    status=updated_status,
                    notes=updated_notes,
                    summary=updated_summary,
                    evidence=incident.get("evidence", {}),
                    recommended_action=updated_action,
                    analyst=updated_analyst
                )
                st.success("Incident updated successfully.")
                st.rerun()

    else:
        st.info(
            "No incidents found for this filter. Save a record from "
            "the Threat Detection page to create an incident."
        )


init_database()

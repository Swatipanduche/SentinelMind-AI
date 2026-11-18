from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from incident_management import save_incident, display_incident_management
from incident_management import get_incident, get_all_incidents
import sentinelmind_improvements as improvements


# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="ThreatTrack AI",
    layout="wide",
    initial_sidebar_state="expanded"
)

BASE = Path(__file__).resolve().parent

THREAT_FILE = BASE / "reports" / "sentinelmind_threat_report.csv"
DEVICE_FILE = BASE / "reports" / "device_risk_assessment.csv"
NODE_FILE = BASE / "data" / "processed" / "network_nodes.csv"
EDGE_FILE = BASE / "data" / "processed" / "network_edges.csv"
GRAPH_FILE = BASE / "reports" / "network_topology.html"


# --------------------------------------------------
# DATA LOADING
# --------------------------------------------------

@st.cache_data
def load_data():
    threat = pd.read_csv(THREAT_FILE)
    devices = pd.read_csv(DEVICE_FILE)
    nodes = pd.read_csv(NODE_FILE)
    edges = pd.read_csv(EDGE_FILE)

    return threat, devices, nodes, edges


required_files = [
    THREAT_FILE,
    DEVICE_FILE,
    NODE_FILE,
    EDGE_FILE
]

missing_files = [str(f.relative_to(BASE)) for f in required_files if not f.exists()]

if missing_files:
    st.error("Required project files are missing:")
    for file in missing_files:
        st.write(f"- {file}")
    st.stop()

threat, devices, nodes, edges = load_data()

improvements.configure_context(
    threat=threat,
    devices=devices,
    nodes=nodes,
    THREAT_FILE=THREAT_FILE,
    DEVICE_FILE=DEVICE_FILE,
    NODE_FILE=NODE_FILE,
    EDGE_FILE=EDGE_FILE,
    save_incident=save_incident,
    get_incident=get_incident,
    get_all_incidents=get_all_incidents,
    display_incident_management=display_incident_management
)



# --------------------------------------------------
# HELPER FUNCTIONS
# --------------------------------------------------

def metric_card(label, value, help_text=None):
    st.metric(label=label, value=value, help=help_text)


def is_attack(label):
    return str(label).strip().lower() not in ["benign", "normal"]


def normalize_bool(series):
    return series.astype(str).str.strip().str.lower().isin(
        ["true", "1", "yes"]
    )


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500;600&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap');

:root {
    --ink: #142238;
    --muted: #66758a;
    --navy: #10243a;
    --navy-2: #183650;
    --paper: #f4f7fa;
    --panel: #ffffff;
    --line: #dce4ec;
    --teal: #087f8c;
    --teal-soft: #e4f3f3;
    --amber: #b7791f;
    --red: #c2413b;
    --green: #16805d;
}

html, body, [class*="css"] {
    font-family: 'IBM Plex Sans', sans-serif;
}

.stApp {
    background: var(--paper);
    color: var(--ink);
}

[data-testid="stHeader"] {
    background: rgba(244, 247, 250, 0.92);
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #10243a 0%, #142d45 100%);
    border-right: 1px solid #263f57;
}

[data-testid="stSidebar"] * {
    color: #e8f0f6;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label {
    padding: 0.42rem 0.55rem;
    border-radius: 7px;
    font-size: 0.91rem;
}

[data-testid="stSidebar"] [data-testid="stRadio"] label:hover {
    background: rgba(255,255,255,0.08);
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.15);
}

.block-container {
    max-width: 1560px;
    padding-top: 2.2rem;
    padding-bottom: 3rem;
}

h1, h2, h3, h4 {
    color: var(--ink) !important;
    letter-spacing: -0.025em;
}

h1 {
    font-weight: 700 !important;
    font-size: clamp(2rem, 3vw, 2.8rem) !important;
}

h2, h3 {
    font-weight: 600 !important;
}

p, label, [data-testid="stCaptionContainer"] {
    color: var(--muted);
}

.section-label {
    color: var(--teal);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
}

.subtitle {
    color: var(--muted);
    font-size: 1rem;
    max-width: 850px;
}

div[data-testid="stMetric"] {
    background: var(--panel);
    border: 1px solid var(--line);
    border-top: 3px solid var(--teal);
    border-radius: 10px;
    padding: 1rem 1.1rem;
    box-shadow: 0 4px 14px rgba(16,36,58,0.045);
}

div[data-testid="stMetricLabel"] {
    color: var(--muted);
    font-size: 0.82rem;
    font-weight: 500;
}

div[data-testid="stMetricValue"] {
    color: var(--ink);
    font-family: 'IBM Plex Mono', monospace;
    font-size: 1.65rem;
    font-weight: 600;
}

[data-testid="stDataFrame"], [data-testid="stTable"] {
    border: 1px solid var(--line);
    border-radius: 9px;
    overflow: hidden;
    background: white;
}

[data-testid="stSelectbox"] > div > div,
[data-testid="stTextInput"] > div > div {
    background: white;
    border-color: var(--line);
    border-radius: 7px;
}

[data-testid="stAlert"] {
    border-radius: 9px;
}

.stButton > button {
    border-radius: 7px;
    border: 1px solid var(--line);
    font-weight: 600;
}

hr {
    border-color: var(--line);
}

code, pre, .technical-value {
    font-family: 'IBM Plex Mono', monospace !important;
}

[data-testid="stPlotlyChart"], [data-testid="stVegaLiteChart"] {
    background: white;
    border: 1px solid var(--line);
    border-radius: 10px;
    padding: 0.5rem;
}

@media (max-width: 900px) {
    .block-container {
        padding-left: 1rem;
        padding-right: 1rem;
    }
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown(
        """
        <div style="padding: 0.6rem 0 1.1rem 0;">
          <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                      letter-spacing:0.16em;color:#6dd3d0;">SECURITY RESEARCH / 01</div>
          <div style="font-size:1.55rem;font-weight:700;color:#ffffff;
                      letter-spacing:-0.04em;margin-top:0.45rem;">ThreatTrack AI</div>
          <div style="font-size:0.75rem;color:#a9bdcf;letter-spacing:0.08em;
                      margin-top:0.2rem;">NETWORK INTELLIGENCE</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()

    page_labels = {
        "Dashboard": "Overview",
        "Threat Alerts": "Threat Detection",
        "Network Connections": "Network Intelligence",
        "Device Details": "Device Investigation",
        "How It Works": "Methodology",
        "Incident Management": "Incident Management",
        "Mitigation Verification": "Mitigation Verification",
        "IP Attack Path": "IP Attack Path",
        "System Diagnostics": "System Diagnostics"
    }

    st.markdown(
        '<div style="font-family:\'IBM Plex Mono\',monospace;font-size:0.68rem;'
        'letter-spacing:0.14em;color:#8fa8bc;margin:0.3rem 0 0.5rem 0;">WORKSPACE</div>',
        unsafe_allow_html=True
    )

    selected_page = st.radio(
        "MENU",
        list(page_labels.keys()),
        label_visibility="collapsed"
    )
    page = page_labels[selected_page]

    st.divider()
    st.markdown(
        """
        <div style="font-family:'IBM Plex Mono',monospace;font-size:0.68rem;
                    letter-spacing:0.14em;color:#8fa8bc;margin-bottom:0.55rem;">
          ANALYSIS MODE
        </div>
        <div style="background:#123b35;border:1px solid #216457;border-radius:8px;
                    padding:0.8rem 0.85rem;color:#bce9d9;font-size:0.86rem;">
          <span style="color:#52d3a5;">READY</span>&nbsp; Offline analysis ready
          <div style="font-size:0.72rem;color:#a9cfc4;margin-top:0.35rem;">
            Prepared dataset analysis
          </div>
        </div>
        <div style="font-size:0.7rem;color:#8fa8bc;margin-top:0.8rem;">
          THREATTRACK AI / RESEARCH PROTOTYPE
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# COMMON STATISTICS
# --------------------------------------------------

total_records = len(threat)
total_devices = len(devices)
total_edges = len(edges)

actual_attack = threat["Actual_Label"].apply(is_attack)
predicted_attack = threat["RF_Prediction"].apply(is_attack)

true_positive = int((actual_attack & predicted_attack).sum())
false_positive = int((~actual_attack & predicted_attack).sum())
false_negative = int((actual_attack & ~predicted_attack).sum())
true_negative = int((~actual_attack & ~predicted_attack).sum())

precision = (
    true_positive / (true_positive + false_positive)
    if true_positive + false_positive else 0
)

recall = (
    true_positive / (true_positive + false_negative)
    if true_positive + false_negative else 0
)

f1 = (
    2 * precision * recall / (precision + recall)
    if precision + recall else 0
)

anomaly_flags = normalize_bool(threat["Anomaly_Detected"])
anomaly_count = int(anomaly_flags.sum())

classified_attacks = int(
    (threat["Threat_Status"] == "CLASSIFIED_ATTACK").sum()
)

anomaly_reviews = int(
    (threat["Threat_Status"] == "ANOMALY_REVIEW").sum()
)

normal_records = int(
    (threat["Threat_Status"] == "NORMAL").sum()
)


# --------------------------------------------------
# PAGE 1: OVERVIEW
# --------------------------------------------------

if page == "Overview":

    st.markdown(
        '<p class="section-label">SECURITY OPERATIONS / OVERVIEW</p>',
        unsafe_allow_html=True
    )
    st.title("Network intelligence workspace")
    st.markdown(
        '<p class="subtitle">Review prepared network activity, inspect device '
        'relationships and identify records that may need further investigation.</p>',
        unsafe_allow_html=True
    )

    st.divider()

    # Compact operational summary: these are dataset totals, not live telemetry.
    st.markdown("### Analysis snapshot")
    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Traffic records", f"{total_records:,}",
                    "Records in the prepared threat report.")
    with c2:
        metric_card("Devices represented", f"{total_devices:,}",
                    "Unique devices in the separate network analysis dataset.")
    with c3:
        metric_card("Observed connections", f"{total_edges:,}",
                    "Communication relationships in the network graph dataset.")
    with c4:
        metric_card("Unusual activity flags", f"{anomaly_count:,}",
                    "Records flagged by the Autoencoder.")

    st.divider()

    # The network graph is the visual anchor of the workspace.
    network_col, signal_col = st.columns([1.8, 1], gap="large")

    with network_col:
        st.markdown("### Network topology")
        st.caption(
            "Observed device-to-device relationships from the separate "
            "CSE-CIC-IDS-2018 sample."
        )
        if GRAPH_FILE.exists():
            graph_html = GRAPH_FILE.read_text(encoding="utf-8")
            components.html(graph_html, height=510, scrolling=True)
        else:
            st.warning("Network topology file was not found.")

    with signal_col:
        st.markdown("### Detection signals")
        st.caption("Summary of the prepared threat report.")

        signal_data = pd.DataFrame({
            "Detection outcome": [
                "Classified attack",
                "Anomaly review",
                "Normal"
            ],
            "Records": [
                classified_attacks,
                anomaly_reviews,
                normal_records
            ]
        })
        st.dataframe(
            signal_data,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("### Device review priorities")
        priority_counts = (
            devices["Investigation_Priority"]
            .value_counts()
            .rename_axis("Priority")
            .to_frame("Devices")
        )
        st.bar_chart(priority_counts, height=210)

    st.divider()

    # A concise analyst queue, sorted by the existing heuristic device score.
    st.markdown("### Devices requiring attention")
    st.caption(
        "Highest device-priority scores first. These are investigation aids, "
        "not probabilities that a device is compromised."
    )
    ranked_overview = devices.sort_values(
        "Device_Risk_Score", ascending=False
    ).head(8)

    overview_columns = [
        "IP_Address",
        "Device_Risk_Score",
        "Investigation_Priority",
        "Observed_Role",
        "Incoming_Attack_Flows",
        "Outgoing_Attack_Flows"
    ]
    overview_names = {
        "IP_Address": "Device",
        "Device_Risk_Score": "Priority score",
        "Investigation_Priority": "Review priority",
        "Observed_Role": "Observed role",
        "Incoming_Attack_Flows": "Incoming attack flows",
        "Outgoing_Attack_Flows": "Outgoing attack flows"
    }
    st.dataframe(
        ranked_overview[overview_columns].rename(columns=overview_names),
        use_container_width=True,
        hide_index=True
    )

    st.divider()

    st.markdown("### Model evaluation")
    e1, e2, e3 = st.columns(3)
    with e1:
        metric_card("Precision", f"{precision:.2%}",
                    "Of predicted attacks, the share that were actual attacks in this report.")
    with e2:
        metric_card("Recall", f"{recall:.2%}",
                    "Of actual attacks, the share identified by the model.")
    with e3:
        metric_card("F1 score", f"{f1:.2%}",
                    "Harmonic mean of precision and recall.")

    st.caption(
        "Evaluation is calculated from saved Random Forest predictions and "
        "actual labels in the offline test report. It is not a guarantee of "
        "real-world detection accuracy. The network topology uses a separate "
        "dataset and is not linked record-by-record to this threat report."
    )


# --------------------------------------------------
# PAGE 2: THREAT DETECTION
# --------------------------------------------------

elif page == "Threat Detection":

    st.markdown(
        '<p class="section-label">SECURITY OPERATIONS / DETECTION ENGINE</p>',
        unsafe_allow_html=True
    )
    st.title("Threat detection")
    st.markdown(
        '<p class="subtitle">Explore the model\'s traffic classifications, '
        'review detection performance and inspect individual network records.</p>',
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div style="display:flex;align-items:center;gap:0.6rem;flex-wrap:wrap;margin:1rem 0 1.2rem 0;">
          <span style="background:#e5f2f2;color:#087f8c;padding:0.35rem 0.65rem;border-radius:4px;font:600 0.7rem 'IBM Plex Mono',monospace;">OFFLINE ANALYSIS</span>
          <span style="color:#66758a;font-size:0.78rem;">Prepared network-flow dataset Â· Random Forest + Autoencoder</span>
        </div>
        """,
        unsafe_allow_html=True
    )

    total_predicted_attacks = int(predicted_attack.sum())
    total_actual_attacks = int(actual_attack.sum())
    total_normal_traffic = int((~actual_attack).sum())

    st.markdown("### Traffic overview")
    count_a, count_b, count_c = st.columns(3, gap="medium")
    with count_a:
        metric_card("Records analysed", f"{total_records:,}", "Total records in the prepared threat report.")
    with count_b:
        metric_card("Predicted as attacks", f"{total_predicted_attacks:,}", "Records the Random Forest classified as non-BENIGN.")
    with count_c:
        metric_card("Actual normal records", f"{total_normal_traffic:,}", "Records whose dataset ground-truth label is BENIGN.")

    perf_left, perf_right = st.columns([1.1, 1.5], gap="large")
    with perf_left:
        st.markdown("### Model performance")
        st.caption("Binary evaluation on the saved test predictions.")
        p1, p2, p3 = st.columns(3)
        with p1:
            st.metric("Precision", f"{precision:.2%}")
        with p2:
            st.metric("Recall", f"{recall:.2%}")
        with p3:
            st.metric("F1 score", f"{f1:.2%}")
        st.caption("Precision measures how many predicted attacks were actual attacks. Recall measures how many actual attacks were found. F1 balances both.")

    with perf_right:
        st.markdown("### Detection distribution")
        st.caption("Ground-truth class balance in the report.")
        normal_share = total_normal_traffic / total_records if total_records else 0
        attack_share = total_actual_attacks / total_records if total_records else 0
        st.markdown(
            f"""
            <div style="margin-top:0.55rem;">
              <div style="display:flex;justify-content:space-between;margin-bottom:0.35rem;"><span style="font-size:0.82rem;color:#526277;">BENIGN / normal</span><strong style="font:600 0.82rem 'IBM Plex Mono',monospace;color:#173c42;">{total_normal_traffic:,} Â· {normal_share:.1%}</strong></div>
              <div style="height:11px;background:#e4eaf0;border-radius:3px;overflow:hidden;"><div style="height:100%;width:{normal_share*100:.3f}%;background:#16805d;"></div></div>
              <div style="display:flex;justify-content:space-between;margin:1rem 0 0.35rem 0;"><span style="font-size:0.82rem;color:#526277;">Attack traffic</span><strong style="font:600 0.82rem 'IBM Plex Mono',monospace;color:#9f3935;">{total_actual_attacks:,} Â· {attack_share:.1%}</strong></div>
              <div style="height:11px;background:#e4eaf0;border-radius:3px;overflow:hidden;"><div style="height:100%;width:{attack_share*100:.3f}%;background:#c2413b;"></div></div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.divider()
    st.markdown("### Prediction validation")
    st.caption("Compare the Random Forest prediction against the dataset's actual label. All non-BENIGN labels are grouped as attacks for this binary evaluation.")

    matrix_col, explain_col = st.columns([1.45, 1], gap="large")
    with matrix_col:
        st.markdown(
            f"""
            <div style="border:1px solid #dce4ec;border-radius:9px;overflow:hidden;background:#fff;">
              <div style="display:grid;grid-template-columns:1.15fr 1fr 1fr;background:#edf2f6;color:#526277;font-size:0.72rem;font-weight:600;">
                <div style="padding:0.75rem;border-right:1px solid #dce4ec;">ACTUAL / PREDICTED</div><div style="padding:0.75rem;text-align:center;border-right:1px solid #dce4ec;">NORMAL</div><div style="padding:0.75rem;text-align:center;">ATTACK</div>
              </div>
              <div style="display:grid;grid-template-columns:1.15fr 1fr 1fr;color:#142238;">
                <div style="padding:1rem 0.75rem;background:#f7f9fb;border-right:1px solid #dce4ec;border-top:1px solid #dce4ec;font-weight:600;">Actually normal</div>
                <div style="padding:1rem 0.75rem;text-align:center;border-right:1px solid #dce4ec;border-top:1px solid #dce4ec;background:#e9f4ee;"><div style="font:600 1.25rem 'IBM Plex Mono',monospace;color:#176b4b;">{true_negative:,}</div><div style="font-size:0.68rem;color:#587565;">Correct normal</div></div>
                <div style="padding:1rem 0.75rem;text-align:center;border-top:1px solid #dce4ec;background:#fbefed;"><div style="font:600 1.25rem 'IBM Plex Mono',monospace;color:#a33d38;">{false_positive:,}</div><div style="font-size:0.68rem;color:#96615d;">False alarm</div></div>
                <div style="padding:1rem 0.75rem;background:#f7f9fb;border-right:1px solid #dce4ec;border-top:1px solid #dce4ec;font-weight:600;">Actually attack</div>
                <div style="padding:1rem 0.75rem;text-align:center;border-right:1px solid #dce4ec;border-top:1px solid #dce4ec;background:#fbefed;"><div style="font:600 1.25rem 'IBM Plex Mono',monospace;color:#a33d38;">{false_negative:,}</div><div style="font-size:0.68rem;color:#96615d;">Missed attack</div></div>
                <div style="padding:1rem 0.75rem;text-align:center;border-top:1px solid #dce4ec;background:#e9f4ee;"><div style="font:600 1.25rem 'IBM Plex Mono',monospace;color:#176b4b;">{true_positive:,}</div><div style="font-size:0.68rem;color:#587565;">Correct attack</div></div>
              </div>
            </div>
            """,
            unsafe_allow_html=True
        )
    with explain_col:
        st.markdown("#### How to read this")
        st.markdown("- **Correct normal:** normal traffic correctly left unflagged.\n- **False alarm:** normal traffic incorrectly flagged as an attack.\n- **Missed attack:** attack traffic incorrectly classified as normal.\n- **Correct attack:** attack traffic correctly identified.")
        st.info("These metrics describe performance on the saved test report. They do not guarantee the same performance on unseen or live traffic.")

    st.divider()
    st.markdown("### Traffic investigation")
    st.caption("Filter the saved records and inspect the actual label, model prediction, anomaly signal and heuristic risk score.")

    filter_col, search_col = st.columns([1, 1.35], gap="medium")
    available_statuses = ["All"] + sorted(threat["Threat_Status"].dropna().astype(str).unique().tolist())
    with filter_col:
        selected_status = st.selectbox("Detection result", available_statuses, key="threat_detection_status_filter")
    with search_col:
        search_text = st.text_input("Find traffic type", placeholder="e.g. DoS Hulk, BENIGN, PortScan", key="threat_detection_search").strip()

    filtered = threat.copy()
    if selected_status != "All":
        filtered = filtered[filtered["Threat_Status"] == selected_status]
    if search_text:
        match = (
            filtered["Actual_Label"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
            | filtered["RF_Prediction"].astype(str).str.contains(search_text, case=False, na=False, regex=False)
        )
        filtered = filtered[match]

    result_col, note_col = st.columns([1, 2])
    with result_col:
        st.markdown(f"<div style='font:600 1.25rem IBM Plex Mono,monospace;color:#142238;'>{len(filtered):,}</div><div style='font-size:0.75rem;color:#66758a;'>matching records</div>", unsafe_allow_html=True)
    with note_col:
        st.caption("Showing up to 1,000 matching records.")

    display_columns = ["Actual_Label", "RF_Prediction", "RF_Attack_Confidence", "Anomaly_Score", "Anomaly_Detected", "Threat_Status", "Risk_Score"]
    display_names = {
        "Actual_Label": "Actual traffic",
        "RF_Prediction": "Model prediction",
        "RF_Attack_Confidence": "Attack confidence",
        "Anomaly_Score": "Anomaly score",
        "Anomaly_Detected": "Anomaly flagged",
        "Threat_Status": "Detection result",
        "Risk_Score": "Risk / 100"
    }
    display_data = filtered[display_columns].head(1000).copy().rename(columns=display_names)
    display_data["Anomaly flagged"] = normalize_bool(display_data["Anomaly flagged"])

    st.dataframe(
        display_data,
        use_container_width=True,
        height=430,
        hide_index=True,

        column_config={
            "Attack confidence": st.column_config.NumberColumn("Attack confidence", format="percent"),
            "Anomaly score": st.column_config.NumberColumn("Anomaly score", format="%.5f"),
            "Risk / 100": st.column_config.NumberColumn("Risk / 100", format="%.2f"),
            "Anomaly flagged": st.column_config.CheckboxColumn("Anomaly flagged")
        }
    )

    # --------------------------------------------------
    # THREAT INVESTIGATION WORKSPACE
    # --------------------------------------------------

    st.divider()
    st.markdown("## Threat Investigation Workspace")
    st.caption(
        "Select a saved traffic record to examine its network behaviour, "
        "find similar traffic and review possible security responses."
    )

    if filtered.empty:
        st.info("No records available for investigation with the current filters.")

    else:
        investigation_ids = (
            filtered["Record_ID"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .tolist()
        )

        selected_record_id = st.selectbox(
            "Select a traffic record to investigate",
            investigation_ids,
            key="investigation_record_selector"
        )

        selected_matches = threat[
            threat["Record_ID"].astype(str) == selected_record_id
        ]

        if not selected_matches.empty:

            selected_record = selected_matches.iloc[0]

            prediction = str(selected_record["RF_Prediction"])
            actual_label = str(selected_record["Actual_Label"])

            # -------------------------------
            # A. INCIDENT OVERVIEW
            # -------------------------------

            st.markdown("### 1. Incident overview")

            c1, c2, c3, c4 = st.columns(4)

            c1.metric(
                "AI Prediction",
                prediction
            )

            c2.metric(
                "Attack Confidence",
                f"{float(selected_record['RF_Attack_Confidence']):.2%}"
            )

            c3.metric(
                "Risk Score",
                f"{float(selected_record['Risk_Score']):.2f}/100"
            )

            c4.metric(
                "Anomaly Score",
                f"{float(selected_record['Anomaly_Score']):.5f}"
            )

            st.write(
                f"**Record ID:** {selected_record_id}"
            )

            st.write(
                f"**Detection Result:** {selected_record['Threat_Status']}"
            )

            st.write(
                f"**Anomaly Flagged:** "
                f"{bool(normalize_bool(pd.Series([selected_record['Anomaly_Detected']])).iloc[0])}"
            )

            # -------------------------------
            # B. EVIDENCE ANALYSIS
            # -------------------------------

            st.divider()
            st.markdown("### 2. Network evidence analysis")

            evidence_fields = [
                "Destination Port",
                "Flow Duration",
                "Total Fwd Packets",
                "Total Backward Packets",
                "Total Length of Fwd Packets",
                "Total Length of Bwd Packets",
                "Flow Bytes/s",
                "Flow Packets/s",
                "Fwd Packets/s",
                "Bwd Packets/s",
                "Packet Length Mean",
                "SYN Flag Count",
                "ACK Flag Count",
                "RST Flag Count",
                "FIN Flag Count",
                "PSH Flag Count",
                "Down/Up Ratio",
                "Active Mean",
                "Idle Mean"
            ]

            available_evidence = [
                col for col in evidence_fields
                if col in threat.columns
            ]

            evidence_data = pd.DataFrame({
                "Network feature": available_evidence,
                "Observed value": [
                    selected_record[col]
                    for col in available_evidence
                ]
            })

            st.dataframe(
                evidence_data,
                use_container_width=True,
                hide_index=True,
                height=400
            )

            st.caption(
                "These are observed features from the selected network-flow "
                "record. Their significance depends on comparison with "
                "normal traffic and the relevant attack pattern."
            )


            # -----------------------------------------
            # 3. NORMAL TRAFFIC BASELINE COMPARISON
            # -----------------------------------------

            st.divider()
            st.markdown("### 3. Normal traffic comparison")

            st.caption(
                "Compare the selected record against BENIGN traffic "
                "to identify unusual network behaviour."
            )

            benign_data = threat[
                threat["Actual_Label"]
                .astype(str)
                .str.strip()
                .str.upper() == "BENIGN"
            ].copy()

            benign_data["_port_numeric"] = pd.to_numeric(
                benign_data["Destination Port"],
                errors="coerce"
            )

            selected_port = pd.to_numeric(
                pd.Series([selected_record["Destination Port"]]),
                errors="coerce"
            ).iloc[0]

            same_port_benign = benign_data[
                benign_data["_port_numeric"] == selected_port
            ].copy()

            if len(same_port_benign) >= 20:
                baseline_data = same_port_benign
                baseline_scope = "BENIGN traffic on the same destination port"
            else:
                baseline_data = benign_data
                baseline_scope = "All available BENIGN traffic"

            comparison_features = [
                "Flow Duration",
                "Flow Bytes/s",
                "Flow Packets/s",
                "Total Fwd Packets",
                "Total Backward Packets",
                "Packet Length Mean",
                "SYN Flag Count",
                "RST Flag Count",
                "Down/Up Ratio"
            ]

            comparison_rows = []

            for feature in comparison_features:

                if feature not in threat.columns:
                    continue

                normal_values = pd.to_numeric(
                    baseline_data[feature],
                    errors="coerce"
                ).dropna()

                selected_value = pd.to_numeric(
                    pd.Series([selected_record[feature]]),
                    errors="coerce"
                ).iloc[0]

                if normal_values.empty or pd.isna(selected_value):
                    continue

                comparison_rows.append({
                    "Network feature": feature,
                    "Selected record": selected_value,
                    "Normal median": normal_values.median(),
                    "Normal 95th percentile": normal_values.quantile(0.95),
                    "Above normal 95th percentile": (
                        selected_value > normal_values.quantile(0.95)
                    )
                })

            st.caption(
                f"Baseline: {baseline_scope} "
                f"({len(baseline_data):,} records)"
            )

            if comparison_rows:

                comparison_df = pd.DataFrame(comparison_rows)

                st.dataframe(
                    comparison_df,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "Selected record": st.column_config.NumberColumn(
                            "Selected record",
                            format="%.4f"
                        ),
                        "Normal median": st.column_config.NumberColumn(
                            "Normal median",
                            format="%.4f"
                        ),
                        "Normal 95th percentile": st.column_config.NumberColumn(
                            "Normal 95th percentile",
                            format="%.4f"
                        ),
                        "Above normal 95th percentile":
                            st.column_config.CheckboxColumn(
                                "Above normal 95th percentile"
                            )
                    }
                )

                above_rows = comparison_df[
                    comparison_df["Above normal 95th percentile"]
                ]

                above_count = len(above_rows)

                st.metric(
                    "Features above normal 95th percentile",
                    f"{above_count}/{len(comparison_df)}"
                )

                if above_count > 0:
                    st.warning(
                        "Some measurements exceed the normal "
                        "95th percentile. Review them as investigation evidence."
                    )
                else:
                    st.info(
                        "No compared measurement exceeded the normal "
                        "95th percentile. This does not prove the record is safe."
                    )

                # -----------------------------------------
                # 4. ROOT CAUSE ANALYSIS
                # -----------------------------------------

                st.divider()
                st.markdown("### 4. Evidence-based root cause analysis")

                st.caption(
                    "Examine unusual measurements and understand "
                    "their possible security significance."
                )

                feature_explanations = {
                    "Flow Duration":
                        "Unusually long connection duration. "
                        "Investigate prolonged network sessions.",

                    "Flow Bytes/s":
                        "Unusual data transfer rate. "
                        "Investigate excessive data transmission.",

                    "Flow Packets/s":
                        "Unusual packet transmission rate. "
                        "Investigate repeated network requests.",

                    "Total Fwd Packets":
                        "Unusual outgoing packet count. "
                        "Inspect repeated outbound communication.",

                    "Total Backward Packets":
                        "Unusual incoming packet count. "
                        "Inspect repeated incoming responses.",

                    "Packet Length Mean":
                        "Unusual average packet size. "
                        "Inspect packet size distribution.",

                    "SYN Flag Count":
                        "Unusual SYN activity. "
                        "Investigate repeated connection initiation.",

                    "RST Flag Count":
                        "Unusual reset activity. "
                        "Investigate repeated connection resets.",

                    "Down/Up Ratio":
                        "Unusual incoming-to-outgoing traffic balance."
                }

                st.markdown("#### Investigation findings")

                if above_rows.empty:

                    st.success(
                        "No compared feature exceeded the normal "
                        "95th percentile. Review other indicators "
                        "before deciding that the record is safe."
                    )

                else:

                    for _, evidence in above_rows.iterrows():

                        feature = evidence["Network feature"]
                        observed = evidence["Selected record"]
                        normal_limit = evidence["Normal 95th percentile"]

                        explanation = feature_explanations.get(
                            feature,
                            "This measurement differs from the normal baseline."
                        )

                        with st.expander(
                            f"Unusual feature: {feature}",
                            expanded=True
                        ):

                            st.write(
                                f"**Observed value:** {observed:,.4f}"
                            )

                            st.write(
                                f"**Normal 95th percentile:** "
                                f"{normal_limit:,.4f}"
                            )

                            st.write(
                                f"**Possible interpretation:** {explanation}"
                            )

                # -----------------------------------------
                # 5. OVERALL INVESTIGATION ASSESSMENT
                # -----------------------------------------

                st.markdown("#### Overall investigation assessment")

                prediction = str(
                    selected_record.get("RF_Prediction", "Unknown")
                )

                risk_score = pd.to_numeric(
                    pd.Series([
                        selected_record.get("Risk_Score", 0)
                    ]),
                    errors="coerce"
                ).iloc[0]

                if pd.isna(risk_score):
                    risk_score = 0.0

                anomaly_flag = normalize_bool(
                    pd.Series([
                        selected_record.get("Anomaly_Detected", False)
                    ])
                ).iloc[0]

                ac1, ac2, ac3 = st.columns(3)

                ac1.metric("AI classification", prediction)

                ac2.metric(
                    "Risk score",
                    f"{risk_score:.2f}/100"
                )

                ac3.metric(
                    "Anomaly detected",
                    "Yes" if anomaly_flag else "No"
                )

                st.write(
                    f"**Unusual baseline features:** "
                    f"{above_count} out of {len(comparison_df)}"
                )

                st.info(
                    "Analyst action: Review unusual measurements, "
                    "inspect related records and validate the pattern "
                    "using available network and security logs. "
                    "This assessment does not prove an attack."
                )

            else:

                st.warning(
                    "Insufficient valid numeric data for baseline comparison."
                )


            # -------------------------------
            # SAVE SELECTED RECORD AS AN INCIDENT
            # -------------------------------

            st.divider()
            # -------------------------------
            # C. RELATED TRAFFIC
            # -------------------------------

            st.divider()
            st.markdown("### 3. Related traffic investigation")

            st.caption(
                "Search for other records sharing the selected record's "
                "destination port and model prediction."
            )

            same_port = (
                threat["Destination Port"].astype(str)
                == str(selected_record["Destination Port"])
            )

            same_prediction = (
                threat["RF_Prediction"].astype(str)
                == prediction
            )

            related = threat[
                same_port & same_prediction
            ].copy()

            related = related[
                related["Record_ID"].astype(str)
                != selected_record_id
            ]

            rc1, rc2 = st.columns(2)

            rc1.metric(
                "Similar records found",
                f"{len(related):,}"
            )

            rc2.metric(
                "Same destination port",
                str(selected_record["Destination Port"])
            )

            if related.empty:
                st.info(
                    "No other records matched this port and prediction."
                )

            else:
                related_columns = [
                    "Record_ID",
                    "Actual_Label",
                    "RF_Prediction",
                    "RF_Attack_Confidence",
                    "Anomaly_Score",
                    "Risk_Score"
                ]

                related_display = (
                    related[related_columns]
                    .head(100)
                    .copy()
                )

                related_display["RF_Attack_Confidence"] = (
                    related_display["RF_Attack_Confidence"] * 100
                )

                st.dataframe(
                    related_display,
                    use_container_width=True,
                    hide_index=True,
                    column_config={
                        "RF_Attack_Confidence": st.column_config.NumberColumn(
                            "Attack confidence (%)",
                            format="%.2f%%"
                        ),
                        "Anomaly_Score": st.column_config.NumberColumn(
                            "Anomaly score",
                            format="%.5f"
                        ),
                        "Risk_Score": st.column_config.NumberColumn(
                            "Risk score",
                            format="%.2f"
                        )
                    }
                )

            st.warning(
                "These are records with similar port and prediction values. "
                "They are not confirmed to originate from the same device "
                "or attacker because IP addresses are unavailable."
            )

            # -------------------------------
            # D. RECOMMENDED RESPONSE
            # -------------------------------

            st.divider()
            st.markdown("### 4. Recommended security response")

            attack_name = prediction.strip().lower()

            if "dos hulk" in attack_name:
                recommendations = [
                    "Inspect repeated HTTP request patterns.",
                    "Review web server access and error logs.",
                    "Consider HTTP rate limiting after confirming malicious traffic.",
                    "Monitor server response time and availability."
                ]

            elif "ddos" in attack_name:
                recommendations = [
                    "Examine traffic volume and distribution across sources.",
                    "Review network and server resource utilisation.",
                    "Consider DDoS protection and traffic scrubbing.",
                    "Monitor legitimate traffic during mitigation."
                ]

            elif "portscan" in attack_name:
                recommendations = [
                    "Review repeated connection attempts across destination ports.",
                    "Identify unnecessarily exposed network services.",
                    "Review firewall rules and access restrictions.",
                    "Monitor subsequent connection attempts."
                ]

            elif "goldeneye" in attack_name:
                recommendations = [
                    "Inspect repeated HTTP request activity.",
                    "Review web server resource utilisation.",
                    "Consider request rate limiting.",
                    "Check whether legitimate users experience service disruption."
                ]

            elif "slowhttptest" in attack_name:
                recommendations = [
                    "Inspect HTTP connection duration and request behaviour.",
                    "Review incomplete or unusually long-running connections.",
                    "Consider appropriate connection timeouts and request limits.",
                    "Monitor web server connection utilisation."
                ]

            elif "patator" in attack_name:
                recommendations = [
                    "Review authentication logs for repeated failed attempts.",
                    "Check whether accounts experienced suspicious login activity.",
                    "Consider login rate limiting and multi-factor authentication.",
                    "Review account access history."
                ]

            elif "bot" in attack_name:
                recommendations = [
                    "Review repeated automated request patterns.",
                    "Inspect web server access logs.",
                    "Consider bot detection and request filtering.",
                    "Verify whether automated activity is authorised."
                ]

            elif attack_name == "benign":
                recommendations = [
                    "No attack-specific response is recommended from this prediction alone.",
                    "Review the anomaly score if unusual activity was flagged.",
                    "Compare the record against normal traffic patterns.",
                    "Investigate further if other evidence indicates suspicious behaviour."
                ]

            else:
                recommendations = [
                    "Review the network-flow features associated with this prediction.",
                    "Compare the traffic with known normal behaviour.",
                    "Examine related records and available security logs.",
                    "Confirm the activity before applying security restrictions."
                ]

            st.markdown(
                f"**Detected traffic category:** {prediction}"
            )

            for i, action in enumerate(recommendations, 1):
                st.markdown(f"{i}. {action}")

            st.info(
                "These are rule-based investigation recommendations, "
                "not automatically executed security actions."
            )

            # -------------------------------
            # E. INVESTIGATION CONCLUSION
            # -------------------------------

            st.divider()
            st.markdown("### 5. Analyst investigation conclusion")

            st.caption(
                "Record your own assessment after reviewing the evidence."
            )

            investigation_status = st.selectbox(
                "Investigation status",
                [
                    "Not investigated",
                    "Under investigation",
                    "Resolved",
                    "False positive",
                    "Inconclusive"
                ],
                key="investigation_status"
            )

            analyst_notes = st.text_area(
                "Investigation findings and action taken",
                placeholder=(
                    "Describe what you observed, the evidence reviewed, "
                    "the possible cause and any action taken..."
                ),
                key="investigation_notes"
            )

            st.write(
                "**Dataset ground-truth label:** "
                f"{actual_label}"
            )

            st.caption(
                "The actual label is dataset ground truth for evaluation. "
                "It is not information an analyst would necessarily know "
                "during a live investigation."
            )

            st.markdown("### Save investigation as an incident")

            incident_analyst = st.text_input(
                "Analyst name",
                key="incident_analyst_input"
            )

            incident_summary = st.text_area(
                "Incident summary",
                placeholder="Summarise the observed activity and investigation findings.",
                key="incident_summary_input"
            )

            incident_notes = st.text_area(
                "Analyst notes",
                placeholder="Add investigation notes, validation steps or observations.",
                key="incident_notes_input"
            )

            incident_action = st.text_area(
                "Recommended action",
                placeholder="Describe the recommended response or next steps.",
                key="incident_action_input"
            )

            save_submitted = st.button(
                "Save incident",
                key="save_incident_button",
                type="primary",
                use_container_width=True
            )

            if save_submitted:
                incident_evidence = {
                    "record_id": str(selected_record_id),
                    "prediction": str(
                        selected_record.get("RF_Prediction", "Unknown")
                    ),
                    "risk_score": str(
                        selected_record.get("Risk_Score", "Unavailable")
                    ),
                    "anomaly_detected": str(
                        selected_record.get("Anomaly_Detected", "Unavailable")
                    ),
                    "destination_port": str(
                        selected_record.get("Destination Port", "Unavailable")
                    ),
                    "threat_status": str(
                        selected_record.get("Threat_Status", "Unavailable")
                    )
                }

                case_id = save_incident(
                    record_id=selected_record_id,
                    status="Open",
                    notes=incident_notes,
                    summary=incident_summary,
                    evidence=incident_evidence,
                    recommended_action=incident_action,
                    analyst=incident_analyst
                )

                st.success(
                    f"Incident saved successfully. Case ID: {case_id}"
                )

    st.divider()
    st.markdown("### Unusual activity analysis")
    anomaly_col, note_col = st.columns([1.15, 1], gap="large")
    anomaly_data = threat.copy()
    anomaly_data["Anomaly_Flag"] = anomaly_flags
    anomaly_distribution = (
        anomaly_data["Anomaly_Flag"].value_counts()
        .reindex([False, True], fill_value=0)
        .rename(index={False: "Not flagged", True: "Flagged for review"})
        .rename_axis("Autoencoder result")
        .to_frame("Records")
    )
    with anomaly_col:
        st.bar_chart(anomaly_distribution, height=230)
    with note_col:
        st.markdown("#### What the anomaly signal means")
        st.write("The Autoencoder compares each record with patterns learned from normal traffic. Records that differ strongly from those patterns can receive an anomaly flag.")
        st.info("An anomaly flag is a reason to investigate further. It is not proof that the record is malicious.")


# --------------------------------------------------
# PAGE 3: NETWORK INTELLIGENCE
# --------------------------------------------------

elif page == "Network Intelligence":

    st.markdown(
        '<p class="section-label">DEVICE CONNECTION ANALYSIS</p>',
        unsafe_allow_html=True
    )

    st.title("Network Connections")
    st.caption(
        "Explore how devices communicate with one another and see which "
        "devices have higher investigation-priority scores."
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card(
            "Devices Found",
            f"{total_devices:,}"
        )

    with c2:
        metric_card(
            "Connections Between Devices",
            f"{total_edges:,}"
        )

    with c3:
        metric_card(
            "Connections with Attack Traffic",
            f"{int((edges['Attack_Flows'] > 0).sum()):,}",
            "Connections that contain one or more attack-related flows."
        )

    st.subheader("Network Connection Map")

    if GRAPH_FILE.exists():
        graph_html = GRAPH_FILE.read_text(encoding="utf-8")
        components.html(
            graph_html,
            height=700,
            scrolling=True
        )
    else:
        st.warning("Network connection map file was not found.")

    st.caption(
        "This map was built using a separate CSE-CIC-IDS-2018 sample. "
        "It shows communication relationships observed in that dataset. "
        "It does not confirm that a device is compromised or reconstruct "
        "the path of an attack."
    )

    st.divider()

    st.subheader("Devices That Need Attention")

    ranked = devices.sort_values(
        "Device_Risk_Score",
        ascending=False
    )

    device_display_names = {
        "IP_Address": "Device IP Address",
        "Device_Risk_Score": "Device Priority Score",
        "Investigation_Priority": "Review Priority",
        "Observed_Role": "Observed Device Role",
        "Incoming_Attack_Flows": "Incoming Attack Connections",
        "Outgoing_Attack_Flows": "Outgoing Attack Connections"
    }

    ranked_display = (
        ranked[
            [
                "IP_Address",
                "Device_Risk_Score",
                "Investigation_Priority",
                "Observed_Role",
                "Incoming_Attack_Flows",
                "Outgoing_Attack_Flows"
            ]
        ]
        .rename(columns=device_display_names)
    )

    st.dataframe(
        ranked_display,
        use_container_width=True,
        height=420
    )

    st.caption(
        "The device priority score is a heuristic score used to help decide "
        "which devices may deserve closer investigation. It is not a probability "
        "that a device is compromised."
    )


# --------------------------------------------------
# PAGE 4: DEVICE INVESTIGATION
# --------------------------------------------------

elif page == "Device Investigation":

    st.markdown(
        '<p class="section-label">INDIVIDUAL DEVICE ANALYSIS</p>',
        unsafe_allow_html=True
    )

    st.title("Device Details")
    st.caption(
        "Select a device to explore its observed network activity, "
        "connections and investigation indicators."
    )

    st.divider()

    device_list = sorted(devices["IP_Address"].astype(str).unique())

    selected_device = st.selectbox(
        "Choose a device to explore",
        device_list
    )

    device = devices[
        devices["IP_Address"].astype(str) == selected_device
    ].iloc[0]

    node_matches = nodes[
        nodes["IP_Address"].astype(str) == selected_device
    ]

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card(
            "Device Priority Score",
            f"{device['Device_Risk_Score']:.2f}/100",
            "A heuristic score used to help prioritise device investigation."
        )

    with c2:
        metric_card(
            "Review Priority",
            str(device["Investigation_Priority"]),
            "The investigation-priority category assigned to this device."
        )

    with c3:
        metric_card(
            "Incoming Connections",
            f"{int(device['Incoming_Flows']):,}",
            "Number of observed network flows coming into this device."
        )

    with c4:
        metric_card(
            "Outgoing Connections",
            f"{int(device['Outgoing_Flows']):,}",
            "Number of observed network flows going out from this device."
        )

    st.divider()

    st.subheader("Device Information")

    st.write("**Observed Device Role:**", device["Observed_Role"])
    st.write("**Review Priority:**", device["Investigation_Priority"])

    st.write(
        "**Incoming Attack Connections:**",
        f"{int(device['Incoming_Attack_Flows']):,}"
    )

    st.write(
        "**Outgoing Attack Connections:**",
        f"{int(device['Outgoing_Attack_Flows']):,}"
    )

    st.write(
        "**Incoming Attack Ratio:**",
        f"{device['Incoming_Attack_Ratio']:.4f}"
    )

    st.write(
        "**Outgoing Attack Ratio:**",
        f"{device['Outgoing_Attack_Ratio']:.4f}"
    )

    st.caption(
        "Attack ratios show the share of observed incoming or outgoing flows "
        "that were marked as attack-related in the dataset."
    )

    st.write(
        "**PageRank:**",
        f"{device['PageRank']:.6f}"
    )

    st.caption(
        "PageRank is a graph measure that indicates how connected or influential "
        "a device appears within the communication network."
    )

    st.write(
        "**Betweenness Centrality:**",
        f"{device['Betweenness_Centrality']:.6f}"
    )

    st.caption(
        "Betweenness centrality estimates how often a device sits between "
        "other devices along the shortest paths in the network graph."
    )

    if not node_matches.empty:
        st.divider()
        st.subheader("Additional Device Information")

        node_display_names = {
            "IP_Address": "Device IP Address"
        }

        node_display = node_matches.rename(
            columns=node_display_names
        )

        st.dataframe(
            node_display,
            use_container_width=True
        )

    st.divider()

    st.subheader("Device Connections")

    outgoing = edges[
        edges["Src IP"].astype(str) == selected_device
    ]

    incoming = edges[
        edges["Dst IP"].astype(str) == selected_device
    ]

    left, right = st.columns(2)

    with left:
        st.markdown("#### Devices This Device Connects To")

        if outgoing.empty:
            st.info("No outgoing connections were found in this dataset sample.")
        else:
            outgoing_display = outgoing[
                [
                    "Dst IP",
                    "Protocol",
                    "Dst Port",
                    "Total_Flows",
                    "Attack_Flows"
                ]
            ].rename(
                columns={
                    "Dst IP": "Destination Device",
                    "Protocol": "Protocol",
                    "Dst Port": "Destination Port",
                    "Total_Flows": "Total Connections",
                    "Attack_Flows": "Attack-related Connections"
                }
            )

            st.dataframe(
                outgoing_display,
                use_container_width=True
            )

    with right:
        st.markdown("#### Devices Connecting to This Device")

        if incoming.empty:
            st.info("No incoming connections were found in this dataset sample.")
        else:
            incoming_display = incoming[
                [
                    "Src IP",
                    "Protocol",
                    "Dst Port",
                    "Total_Flows",
                    "Attack_Flows"
                ]
            ].rename(
                columns={
                    "Src IP": "Source Device",
                    "Protocol": "Protocol",
                    "Dst Port": "Destination Port",
                    "Total_Flows": "Total Connections",
                    "Attack_Flows": "Attack-related Connections"
                }
            )

            st.dataframe(
                incoming_display,
                use_container_width=True
            )

    st.caption(
        "These records describe communication observed in the selected "
        "dataset sample. They do not establish who owns a device or prove "
        "that it has been compromised."
    )


# --------------------------------------------------
# PAGE 5: METHODOLOGY
# --------------------------------------------------

elif page == "Methodology":

    st.markdown(
        '<p class="section-label">BEHIND THE ANALYSIS</p>',
        unsafe_allow_html=True
    )

    st.title("How ThreatTrack AI Works")

    st.caption(
        "Learn how the platform analyses network records, identifies unusual "
        "activity and calculates device investigation priorities."
    )

    st.divider()

    st.subheader("1. How Threats Are Identified")

    st.write(
        "A Random Forest machine learning model was trained using selected "
        "CIC-IDS2017 network-flow records. It classifies records as normal "
        "traffic or as one of six attack categories."
    )

    st.write(
        "The first classifier excluded Heartbleed because the selected "
        "records contained too few examples for reliable training."
    )

    st.caption(
        "Technical method: Supervised machine learning using a Random Forest classifier."
    )

    st.divider()

    st.subheader("2. How Unusual Activity Is Found")

    st.write(
        "An Autoencoder was trained using normal network traffic. It learns "
        "patterns found in that traffic and uses reconstruction error to "
        "identify records that look different."
    )

    st.write(
        "These unusual records are highlighted for additional review. "
        "An unusual record is not automatically an attack."
    )

    st.caption(
        "Technical method: Unsupervised anomaly detection using an Autoencoder."
    )

    st.divider()

    st.subheader("3. How Device Connections Are Analysed")

    st.write(
        "A separate CSE-CIC-IDS-2018 sample containing source and destination "
        "IP addresses was used to build a directed communication graph."
    )

    st.write(
        "This graph represents observed communication between devices. "
        "NetworkX calculates graph indicators such as PageRank, "
        "betweenness centrality, connectivity and attack-flow statistics."
    )

    st.caption(
        "Technical method: Network graph analysis using NetworkX."
    )

    st.divider()

    st.subheader("4. How Device Priority Is Calculated")

    st.write(
        "Each device receives a risk score based on a manually weighted "
        "combination of incoming and outgoing attack traffic, PageRank "
        "and connectivity."
    )

    st.write(
        "The score helps organise devices by investigation priority. "
        "It is not a calibrated probability that a device is compromised."
    )

    st.caption(
        "Technical method: Heuristic risk scoring using network-flow and graph indicators."
    )

    st.divider()

    st.subheader("5. What This Analysis Can and Cannot Tell You")

    st.warning(
        """
        - The CIC-IDS2017 model evaluation uses a stratified random split
          of selected Tuesday and Wednesday records.
        - This is not an independent test on a separate network or day.
        - The network graph uses a separate CSE-CIC-IDS-2018 sample.
        - The graph sample is dominated by DDoS traffic and does not
          establish lateral movement or multi-stage attacks.
        - The dashboard analyses prepared datasets. It does not monitor
          a live network.
        - An AI prediction or unusual activity flag is an indicator
          for investigation, not proof of an attack or compromised device.
        """
    )

    st.divider()

    st.subheader("Data Sources")

    st.write(
        "**CIC-IDS2017:** Iman Sharafaldin, Arash Habibi Lashkari, "
        "Ali A. Ghorbani, 2018. "
        "\"Toward Generating a New Intrusion Detection Dataset and "
        "Intrusion Traffic Characterization.\""
    )

    st.write(
        "**CSE-CIC-IDS-2018:** Used as a separate source for network-flow "
        "records containing endpoint IP addresses."
    )


elif page == "Mitigation Verification":
    improvements.display_mitigation_verification()


elif page == "IP Attack Path":
    improvements.display_ip_attack_investigation()


elif page == "System Diagnostics":
    improvements.display_sentinelmind_diagnostics()


elif page == "Incident Management":
    display_incident_management()


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "THREATTRACK AI | Network Threat Detection & Investigation | "
    "Offline Dataset Analysis"
)



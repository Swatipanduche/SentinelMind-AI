
from pathlib import Path
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# --------------------------------------------------
# CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="SentinelMind AI",
    page_icon="🛡️",
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
    .stApp {
        background-color: #080d19;
        color: #e5e7eb;
    }

    [data-testid="stSidebar"] {
        background-color: #101827;
    }

    div[data-testid="stMetric"] {
        background: #121d30;
        border: 1px solid #263750;
        padding: 18px;
        border-radius: 12px;
    }

    div[data-testid="stMetricLabel"],
    div[data-testid="stMetricLabel"] *,
    div[data-testid="stMetricValue"],
    div[data-testid="stMetricValue"] * {
       color: #f1f5f9 !important;
    }

    [data-testid="stSidebar"] * {
       color: #e2e8f0;
}

    h1, h2, h3 {
        color: #f1f5f9;
    }

    .subtitle {
        color: #94a3b8;
        font-size: 14px;
    }

    .section-label {
        color: #38bdf8;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 2px;
    }

    hr {
        border-color: #263750;
    }
    /* Improve dashboard text contrast */
.stApp {
    color: #f1f5f9 !important;
}

div[data-testid="stMetric"] label,
div[data-testid="stMetric"] label *,
div[data-testid="stMetricValue"],
div[data-testid="stMetricValue"] *,
div[data-testid="stMetricLabel"],
div[data-testid="stMetricLabel"] * {
    color: #f1f5f9 !important;
}

[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #e2e8f0 !important;
}
</style>
""", unsafe_allow_html=True)


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.markdown("# 🛡️ SentinelMind")
    st.caption("AI SECURITY INTELLIGENCE PLATFORM")
    st.divider()

    page = st.radio(
        "NAVIGATION",
        [
            "Overview",
            "Threat Detection",
            "Network Intelligence",
            "Device Investigation",
            "Methodology"
        ]
    )

    st.divider()
    st.caption("PROJECT STATUS")
    st.success("Offline analysis ready")
    st.caption("Dataset-based research prototype")


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

    st.markdown('<p class="section-label">SECURITY OPERATIONS CENTER</p>',
                unsafe_allow_html=True)

    st.title("SentinelMind AI")
    st.markdown(
        '<p class="subtitle">Network threat detection, anomaly analysis '
        'and device-level intelligence.</p>',
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("Network Overview")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        metric_card("Analyzed Records", f"{total_records:,}")

    with c2:
        metric_card("Network Devices", f"{total_devices:,}")

    with c3:
        metric_card("Communication Links", f"{total_edges:,}")

    with c4:
        metric_card("Anomaly Flags", f"{anomaly_count:,}")

    st.divider()

    st.subheader("Threat Triage")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Classified Attacks", f"{classified_attacks:,}")

    with c2:
        metric_card("Anomaly Review", f"{anomaly_reviews:,}")

    with c3:
        metric_card("Normal Traffic", f"{normal_records:,}")

    left, right = st.columns(2)

    with left:
        st.markdown("### Threat Status Distribution")

        status_counts = (
            threat["Threat_Status"]
            .value_counts()
            .rename_axis("Status")
            .to_frame("Records")
        )

        st.bar_chart(status_counts,horizontal=True)

    with right:
        st.markdown("### Device Investigation Priorities")

        priority_counts = (
            devices["Investigation_Priority"]
            .value_counts()
            .rename_axis("Priority")
            .to_frame("Devices")
        )

        st.bar_chart(priority_counts,horizontal=True)

    st.divider()

    st.subheader("Model Performance")

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Precision", f"{precision:.4f}")

    with c2:
        metric_card("Recall", f"{recall:.4f}")

    with c3:
        metric_card("F1 Score", f"{f1:.4f}")

    st.caption(
        "Metrics are calculated from the saved Random Forest predictions "
        "and actual labels in the offline test report."
    )


# --------------------------------------------------
# PAGE 2: THREAT DETECTION
# --------------------------------------------------

elif page == "Threat Detection":

    st.markdown('<p class="section-label">MACHINE LEARNING ENGINE</p>',
                unsafe_allow_html=True)

    st.title("Threat Detection")
    st.caption(
        "Inspect supervised attack classifications and unsupervised "
        "anomaly detection results."
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Precision", f"{precision:.4%}")

    with c2:
        metric_card("Recall", f"{recall:.4%}")

    with c3:
        metric_card("F1 Score", f"{f1:.4%}")

    st.subheader("Random Forest Evaluation")

    confusion = pd.DataFrame(
        [
            [true_negative, false_positive],
            [false_negative, true_positive]
        ],
        index=["Actual Benign", "Actual Attack"],
        columns=["Predicted Benign", "Predicted Attack"]
    )

    st.dataframe(confusion, use_container_width=True)

    st.caption(
        "Binary evaluation: all non-BENIGN classes are treated as attacks."
    )

    st.divider()

    st.subheader("Threat Records")

    available_statuses = ["All"] + sorted(
        threat["Threat_Status"].dropna().unique().tolist()
    )

    selected_status = st.selectbox(
        "Filter by threat status",
        available_statuses
    )

    filtered = threat.copy()

    if selected_status != "All":
        filtered = filtered[
            filtered["Threat_Status"] == selected_status
        ]

    st.write(f"Showing {len(filtered):,} records")

    display_columns = [
        "Actual_Label",
        "RF_Prediction",
        "RF_Attack_Confidence",
        "Anomaly_Score",
        "Anomaly_Detected",
        "Threat_Status",
        "Risk_Score"
    ]

    st.dataframe(
        filtered[display_columns].head(1000),
        use_container_width=True,
        height=420
    )

    st.caption("Showing up to 1,000 matching records.")

    st.divider()

    st.subheader("Anomaly Detection")

    anomaly_data = threat.copy()
    anomaly_data["Anomaly_Flag"] = anomaly_flags

    anomaly_distribution = (
        anomaly_data.groupby("Anomaly_Flag")
        .size()
        .rename_axis("Anomaly Detected")
        .to_frame("Records")
    )

    st.bar_chart(anomaly_distribution)

    st.info(
        "The autoencoder is a complementary anomaly detector. "
        "An anomaly flag means a record deserves review; it does not "
        "automatically prove malicious activity."
    )


# --------------------------------------------------
# PAGE 3: NETWORK INTELLIGENCE
# --------------------------------------------------

elif page == "Network Intelligence":

    st.markdown('<p class="section-label">NETWORK GRAPH ANALYTICS</p>',
                unsafe_allow_html=True)

    st.title("Network Intelligence")
    st.caption(
        "Explore communication relationships and device-level risk indicators."
    )

    st.divider()

    c1, c2, c3 = st.columns(3)

    with c1:
        metric_card("Devices", f"{total_devices}")

    with c2:
        metric_card("Communication Links", f"{total_edges}")

    with c3:
        metric_card(
            "Attack-related Links",
            f"{int((edges['Attack_Flows'] > 0).sum())}"
        )

    st.subheader("Interactive Network Topology")

    if GRAPH_FILE.exists():
        graph_html = GRAPH_FILE.read_text(encoding="utf-8")
        components.html(
            graph_html,
            height=700,
            scrolling=True
        )
    else:
        st.warning("Network graph HTML file was not found.")

    st.caption(
        "Graph built from the separate CSE-CIC-IDS-2018 sample. "
        "It represents observed communication relationships, not confirmed "
        "compromised devices or reconstructed attack paths."
    )

    st.divider()

    st.subheader("Device Risk Ranking")

    ranked = devices.sort_values(
        "Device_Risk_Score",
        ascending=False
    )

    st.dataframe(
        ranked[
            [
                "IP_Address",
                "Device_Risk_Score",
                "Investigation_Priority",
                "Observed_Role",
                "Incoming_Attack_Flows",
                "Outgoing_Attack_Flows"
            ]
        ],
        use_container_width=True,
        height=420
    )

    st.caption(
        "Device risk scores are heuristic investigation-priority scores, "
        "not probabilities of compromise."
    )


# --------------------------------------------------
# PAGE 4: DEVICE INVESTIGATION
# --------------------------------------------------

elif page == "Device Investigation":

    st.markdown('<p class="section-label">DEVICE-LEVEL INVESTIGATION</p>',
                unsafe_allow_html=True)

    st.title("Device Investigation")
    st.caption(
        "Inspect observed traffic, graph relationships and risk indicators."
    )

    st.divider()

    device_list = sorted(devices["IP_Address"].astype(str).unique())

    selected_device = st.selectbox(
        "Select a device",
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
            "Risk Score",
            f"{device['Device_Risk_Score']:.2f}/100"
        )

    with c2:
        metric_card(
            "Priority",
            str(device["Investigation_Priority"])
        )

    with c3:
        metric_card(
            "Incoming Flows",
            f"{int(device['Incoming_Flows']):,}"
        )

    with c4:
        metric_card(
            "Outgoing Flows",
            f"{int(device['Outgoing_Flows']):,}"
        )

    st.divider()

    st.subheader("Device Intelligence")

    st.write("**Observed Role:**", device["Observed_Role"])
    st.write("**Investigation Priority:**", device["Investigation_Priority"])

    st.write(
        "**Incoming Attack Flows:**",
        f"{int(device['Incoming_Attack_Flows']):,}"
    )

    st.write(
        "**Outgoing Attack Flows:**",
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

    st.write(
        "**PageRank:**",
        f"{device['PageRank']:.6f}"
    )

    st.write(
        "**Betweenness Centrality:**",
        f"{device['Betweenness_Centrality']:.6f}"
    )

    if not node_matches.empty:
        st.divider()
        st.subheader("Observed Node Statistics")
        st.dataframe(node_matches, use_container_width=True)

    st.divider()

    st.subheader("Communication Relationships")

    outgoing = edges[
        edges["Src IP"].astype(str) == selected_device
    ]

    incoming = edges[
        edges["Dst IP"].astype(str) == selected_device
    ]

    left, right = st.columns(2)

    with left:
        st.markdown("#### Outgoing Connections")
        if outgoing.empty:
            st.info("No outgoing connections in this sample.")
        else:
            st.dataframe(
                outgoing[
                    [
                        "Dst IP",
                        "Protocol",
                        "Dst Port",
                        "Total_Flows",
                        "Attack_Flows"
                    ]
                ],
                use_container_width=True
            )

    with right:
        st.markdown("#### Incoming Connections")
        if incoming.empty:
            st.info("No incoming connections in this sample.")
        else:
            st.dataframe(
                incoming[
                    [
                        "Src IP",
                        "Protocol",
                        "Dst Port",
                        "Total_Flows",
                        "Attack_Flows"
                    ]
                ],
                use_container_width=True
            )

    st.caption(
        "These records describe observed communication in the selected "
        "dataset sample. They do not establish device ownership or compromise."
    )


# --------------------------------------------------
# PAGE 5: METHODOLOGY
# --------------------------------------------------

elif page == "Methodology":

    st.markdown('<p class="section-label">SYSTEM DOCUMENTATION</p>',
                unsafe_allow_html=True)

    st.title("Methodology & Data Sources")

    st.subheader("1. Supervised Attack Classification")

    st.write(
        "A Random Forest classifier was trained on selected CIC-IDS2017 "
        "flow records to classify benign traffic and six attack categories."
    )

    st.write(
        "The first classifier excluded Heartbleed because the selected "
        "records contained too few examples for reliable training."
    )

    st.subheader("2. Unsupervised Anomaly Detection")

    st.write(
        "The SentinelMind autoencoder was trained using benign Tuesday "
        "CIC-IDS2017 traffic. Input features are clipped using training-derived "
        "limits, scaled using a fitted StandardScaler, and reconstructed by "
        "the neural network. Reconstruction error is compared with a threshold "
        "calibrated on Tuesday benign validation traffic."
    )

    st.write(
        "A separate cross-day experiment evaluated the Tuesday-trained "
        "autoencoder on Wednesday traffic. This experiment measures how well "
        "the model identifies unusual patterns across different capture days; "
        "an anomaly flag is an investigation signal, not proof of an attack."
    )

    st.subheader("3. Network Intelligence")

    st.write(
        "A separate CSE-CIC-IDS-2018 sample containing source and destination "
        "IP addresses was used to build a directed communication graph."
    )

    st.write(
        "NetworkX calculates graph indicators such as PageRank, "
        "betweenness centrality, connectivity and attack-flow statistics."
    )

    st.subheader("4. Risk Scoring")

    st.write(
        "The device risk score is a manually weighted heuristic based on "
        "incoming and outgoing attack traffic, PageRank and connectivity. "
        "It is an investigation-priority indicator, not a calibrated "
        "probability that a device is compromised."
    )

    st.subheader("5. Important Evaluation Limitations")

    st.warning(
        """
        - The dashboard Random Forest metrics are based on a held-out
          test dataset derived from selected CIC-IDS2017 Tuesday and
          Wednesday records using a stratified random split.
        - The autoencoder was trained on Tuesday benign traffic, with its
          anomaly threshold calibrated using Tuesday benign validation data.
        - A separate cross-day experiment evaluated this autoencoder on
          Wednesday traffic. This is not validation on a separate network,
          a different dataset, or live traffic.
        - The dashboard report and the separate cross-day experiment are
          distinct evaluation outputs and should not be treated as the same
          test.
        - The network graph uses a separate CSE-CIC-IDS-2018 sample.
        - The graph sample is dominated by DDoS traffic and does not
          establish lateral movement or multi-stage attacks.
        - The dashboard displays offline dataset analysis, not live
          network monitoring.
        """
    )

    st.subheader("Dataset Attribution")

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


# --------------------------------------------------
# FOOTER
# --------------------------------------------------

st.divider()

st.caption(
    "SENTINELMIND AI | Defensive Cybersecurity Research Prototype | "
    "Offline Dataset Analysis"
)

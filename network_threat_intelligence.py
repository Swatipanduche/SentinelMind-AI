
import pandas as pd
import networkx as nx
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

NODES_FILE = BASE_DIR / "data/processed/network_nodes.csv"
EDGES_FILE = BASE_DIR / "data/processed/network_edges.csv"
OUTPUT_FILE = BASE_DIR / "reports/device_risk_assessment.csv"

# Load data
nodes_df = pd.read_csv(NODES_FILE)
edges_df = pd.read_csv(EDGES_FILE)

G = nx.DiGraph()

# Add all observed devices
for _, row in nodes_df.iterrows():
    G.add_node(str(row["IP_Address"]))

# Add communication relationships
for _, row in edges_df.iterrows():
    source = str(row["Src IP"])
    target = str(row["Dst IP"])

    G.add_edge(
        source,
        target,
        total_flows=int(row["Total_Flows"]),
        attack_flows=int(row["Attack_Flows"])
    )

# Centrality calculations
pagerank = nx.pagerank(G, weight="total_flows")
betweenness = nx.betweenness_centrality(G, normalized=True)
in_degree = dict(G.in_degree())
out_degree = dict(G.out_degree())

# Calculate traffic statistics for each device
records = []

for device in G.nodes():

    incoming_edges = list(G.in_edges(device, data=True))
    outgoing_edges = list(G.out_edges(device, data=True))

    incoming_flows = sum(
        data["total_flows"] for _, _, data in incoming_edges
    )
    outgoing_flows = sum(
        data["total_flows"] for _, _, data in outgoing_edges
    )

    incoming_attacks = sum(
        data["attack_flows"] for _, _, data in incoming_edges
    )
    outgoing_attacks = sum(
        data["attack_flows"] for _, _, data in outgoing_edges
    )

    incoming_ratio = (
        incoming_attacks / incoming_flows
        if incoming_flows else 0
    )

    outgoing_ratio = (
        outgoing_attacks / outgoing_flows
        if outgoing_flows else 0
    )

    records.append({
        "IP_Address": device,
        "In_Degree": in_degree[device],
        "Out_Degree": out_degree[device],
        "Incoming_Flows": incoming_flows,
        "Outgoing_Flows": outgoing_flows,
        "Incoming_Attack_Flows": incoming_attacks,
        "Outgoing_Attack_Flows": outgoing_attacks,
        "Incoming_Attack_Ratio": incoming_ratio,
        "Outgoing_Attack_Ratio": outgoing_ratio,
        "PageRank": pagerank[device],
        "Betweenness_Centrality": betweenness[device]
    })

risk_df = pd.DataFrame(records)

# Normalize numerical features for a transparent heuristic score
def normalize(series):
    maximum = series.max()
    if maximum == 0:
        return series * 0
    return series / maximum

risk_df["Incoming_Attack_Score"] = normalize(
    risk_df["Incoming_Attack_Flows"]
)

risk_df["Outgoing_Attack_Score"] = normalize(
    risk_df["Outgoing_Attack_Flows"]
)

risk_df["PageRank_Score"] = normalize(risk_df["PageRank"])

risk_df["Connectivity_Score"] = normalize(
    risk_df["In_Degree"] + risk_df["Out_Degree"]
)

# Heuristic prioritization score, not a calibrated probability
risk_df["Device_Risk_Score"] = (
    0.45 * risk_df["Incoming_Attack_Score"] +
    0.45 * risk_df["Outgoing_Attack_Score"] +
    0.05 * risk_df["PageRank_Score"] +
    0.05 * risk_df["Connectivity_Score"]
) * 100

# Describe observed traffic roles
def classify_role(row):
    incoming = row["Incoming_Attack_Flows"] > 0
    outgoing = row["Outgoing_Attack_Flows"] > 0

    if incoming and outgoing:
        return "Attack Source and Target"
    elif outgoing:
        return "Attack Traffic Source"
    elif incoming:
        return "Attack Traffic Target"
    return "No Attack Traffic Observed"

risk_df["Observed_Role"] = risk_df.apply(classify_role, axis=1)

# Assign investigation priority
def risk_level(score):
    if score >= 70:
        return "HIGH"
    elif score >= 35:
        return "MEDIUM"
    return "LOW"

risk_df["Investigation_Priority"] = (
    risk_df["Device_Risk_Score"].apply(risk_level)
)

# Sort highest priority first
risk_df = risk_df.sort_values(
    "Device_Risk_Score",
    ascending=False
)

# Save results
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
risk_df.to_csv(OUTPUT_FILE, index=False)

# Display intelligence report
print("\n========== SENTINELMIND NETWORK INTELLIGENCE ==========")

print("\nNetwork overview")
print("Devices:", G.number_of_nodes())
print("Communication links:", G.number_of_edges())

print("\nTop 10 devices by heuristic risk score")

columns = [
    "IP_Address",
    "Device_Risk_Score",
    "Investigation_Priority",
    "Observed_Role",
    "Incoming_Attack_Flows",
    "Outgoing_Attack_Flows"
]

print(risk_df[columns].head(10).to_string(index=False))

print("\nObserved traffic roles:")
print(risk_df["Observed_Role"].value_counts().to_string())

print("\nInvestigation priorities:")
print(risk_df["Investigation_Priority"].value_counts().to_string())

print("\nRisk assessment saved to:")
print(OUTPUT_FILE)

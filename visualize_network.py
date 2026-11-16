
import pandas as pd
from pyvis.network import Network
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

NODES_FILE = BASE_DIR / "data/processed/network_nodes.csv"
EDGES_FILE = BASE_DIR / "data/processed/network_edges.csv"
RISK_FILE = BASE_DIR / "reports/device_risk_assessment.csv"
OUTPUT_FILE = BASE_DIR / "reports/network_topology.html"

nodes_df = pd.read_csv(NODES_FILE)
edges_df = pd.read_csv(EDGES_FILE)
risk_df = pd.read_csv(RISK_FILE)

risk_lookup = risk_df.set_index("IP_Address").to_dict("index")

net = Network(
    height="800px",
    width="100%",
    directed=True,
    bgcolor="#0b1020",
    font_color="white"
)

net.barnes_hut(
    gravity=-3000,
    central_gravity=0.25,
    spring_length=180,
    spring_strength=0.04,
    damping=0.09
)

# Add devices
for _, row in nodes_df.iterrows():

    ip = str(row["IP_Address"])
    risk = risk_lookup.get(ip, {})

    score = float(risk.get("Device_Risk_Score", 0))
    priority = risk.get("Investigation_Priority", "LOW")
    role = str(risk.get("Observed_Role", "Unknown")).strip()
    attacks = int(row["Attack_Flows"])

    colors = {
        "HIGH": "#ff3b5c",
        "MEDIUM": "#ffad33",
        "LOW": "#36cfc9"
    }

    # Highlight the attack target
    if role == "Attack Traffic Target":
       color = "#a855f7"
       node_label = "TARGET"
       node_size = 45
    else:
       color = colors.get(priority, "#36cfc9")
       node_label = " "
       node_size = 18 + min(score / 3, 25)

    title = (
        f"IP Address: {ip}<br>"
        f"Risk Score: {score:.2f}/100<br>"
        f"Priority: {priority}<br>"
        f"Observed Role: {role}<br>"
        f"Attack Flows: {attacks}<br>"
        f"Incoming Flows: {int(row['Incoming_Flows'])}<br>"
        f"Outgoing Flows: {int(row['Outgoing_Flows'])}"
    )

    net.add_node(
    ip,
    label=node_label,
    title=title,
    color=color,
    size=node_size,
    borderWidth=2
)

# Add communication links
for _, row in edges_df.iterrows():

    source = str(row["Src IP"])
    target = str(row["Dst IP"])

    total = int(row["Total_Flows"])
    attacks = int(row["Attack_Flows"])

    net.add_edge(
        source,
        target,
        title=(
            f"Source: {source}<br>"
            f"Destination: {target}<br>"
            f"Total Flows: {total}<br>"
            f"Attack Flows: {attacks}<br>"
            f"Attack Ratio: {float(row['Attack_Ratio']):.2%}"
        ),
        color="#ff4d6d" if attacks > 0 else "#36cfc9",
        width=1 + min(total / 1000, 7),
        arrows="to"
    )

# Graph interaction settings
net.set_options("""
{
  "interaction": {
    "hover": true,
    "navigationButtons": true,
    "keyboard": true
  },
  "physics": {
    "enabled": true,
    "stabilization": {
      "iterations": 200
    }
  },
  "edges": {
    "smooth": {
      "type": "dynamic"
    }
  }
}
""")

# Export visualization
OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
net.write_html(str(OUTPUT_FILE), open_browser=False)

print("\\n========== SENTINELMIND INTELLIGENCE GRAPH ==========")
print("Devices:", len(nodes_df))
print("Communication links:", len(edges_df))
print("Risk intelligence integrated:", len(risk_df))
print("Saved:", OUTPUT_FILE)
print("Visualization updated successfully!")

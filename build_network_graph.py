
import pandas as pd
from pathlib import Path

INPUT = Path("data/raw/attack_path_sample.csv")
OUTPUT = Path("data/processed")

OUTPUT.mkdir(parents=True, exist_ok=True)

print("Loading network records...")
df = pd.read_csv(INPUT, low_memory=False)

# Clean endpoint and label fields
for col in ["Src IP", "Dst IP", "Label"]:
    df[col] = df[col].astype(str).str.strip()

df["Timestamp"] = pd.to_datetime(
    df["Timestamp"],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)

df["Is_Attack"] = df["Label"].str.lower() != "benign"

# Build directed communication edges
edges = (
    df.groupby(["Src IP", "Dst IP", "Protocol", "Dst Port"])
    .agg(
        Total_Flows=("Label", "size"),
        Attack_Flows=("Is_Attack", "sum"),
        First_Seen=("Timestamp", "min"),
        Last_Seen=("Timestamp", "max")
    )
    .reset_index()
)

edges["Benign_Flows"] = (
    edges["Total_Flows"] - edges["Attack_Flows"]
)

edges["Attack_Ratio"] = (
    edges["Attack_Flows"] / edges["Total_Flows"]
)

edges.to_csv(OUTPUT / "network_edges.csv", index=False)

# Build device-level statistics
source_stats = df.groupby("Src IP").agg(
    Outgoing_Flows=("Dst IP", "size"),
    Attack_Flows=("Is_Attack", "sum")
)

destination_stats = df.groupby("Dst IP").agg(
    Incoming_Flows=("Src IP", "size")
)

nodes = source_stats.join(
    destination_stats, how="outer"
).fillna(0)

nodes.index.name = "IP_Address"

nodes["Attack_Ratio"] = (
    nodes["Attack_Flows"] /
    nodes["Outgoing_Flows"].replace(0, 1)
)

nodes.to_csv(OUTPUT / "network_nodes.csv")

print("\n========== NETWORK GRAPH DATA ==========")
print("Unique devices:", len(nodes))
print("Communication edges:", len(edges))
print("Attack-related edges:", (edges["Attack_Flows"] > 0).sum())

print("\nTop communication sources:")
print(nodes.sort_values(
    "Outgoing_Flows", ascending=False
).head(10))

print("\nTop communication targets:")
print(destination_stats.sort_values(
    "Incoming_Flows", ascending=False
).head(10))

print("\nSaved:")
print("data/processed/network_edges.csv")
print("data/processed/network_nodes.csv")

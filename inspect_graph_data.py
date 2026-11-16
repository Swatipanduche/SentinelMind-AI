
import pandas as pd
from pathlib import Path

FILE = Path("data/raw/attack_path_sample.csv")

print("Loading network-flow sample...")

df = pd.read_csv(FILE, low_memory=False)

print("\n========== DATASET OVERVIEW ==========")
print("Total records:", len(df))
print("Total columns:", len(df.columns))

print("\n========== NETWORK IDENTITIES ==========")
print("Unique source IPs:", df["Src IP"].nunique())
print("Unique destination IPs:", df["Dst IP"].nunique())
print("Unique devices overall:",
      len(set(df["Src IP"].dropna()) | set(df["Dst IP"].dropna())))

print("\n========== PROTOCOL DISTRIBUTION ==========")
print(df["Protocol"].value_counts().head(10))

print("\n========== ATTACK DISTRIBUTION ==========")
print(df["Label"].value_counts())

print("\n========== TIMESTAMP CHECK ==========")
timestamps = pd.to_datetime(df["Timestamp"], errors="coerce")
print("Valid timestamps:", timestamps.notna().sum())
print("Invalid timestamps:", timestamps.isna().sum())

print("\n========== DATA QUALITY ==========")
print("Missing source IPs:", df["Src IP"].isna().sum())
print("Missing destination IPs:", df["Dst IP"].isna().sum())

print("\n========== SAMPLE RECORDS ==========")
print(df[[
    "Src IP", "Dst IP", "Dst Port",
    "Protocol", "Timestamp", "Label"
]].head(10).to_string(index=False))

print("\nInspection completed.")

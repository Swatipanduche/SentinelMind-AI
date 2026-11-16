
import pandas as pd

FILE = "data/raw/attack_path_sample_2.csv"

print("Loading second network sample...")
df = pd.read_csv(FILE, low_memory=False)

print("\n========== DATASET OVERVIEW ==========")
print("Records:", len(df))
print("Columns:", len(df.columns))

print("\n========== NETWORK IDENTITIES ==========")
print("Unique source IPs:", df["Src IP"].nunique())
print("Unique destination IPs:", df["Dst IP"].nunique())
print(
    "Unique devices:",
    len(set(df["Src IP"].dropna()) | set(df["Dst IP"].dropna()))
)

print("\n========== ATTACK DISTRIBUTION ==========")
print(df["Label"].value_counts())

print("\n========== TIMESTAMP RANGE ==========")
timestamps = pd.to_datetime(
    df["Timestamp"],
    format="%d/%m/%Y %H:%M:%S",
    errors="coerce"
)
print("Start:", timestamps.min())
print("End:", timestamps.max())
print("Invalid timestamps:", timestamps.isna().sum())

print("\n========== TOP SOURCE IPs ==========")
print(df["Src IP"].value_counts().head(10))

print("\n========== TOP DESTINATION IPs ==========")
print(df["Dst IP"].value_counts().head(10))

print("\nInspection completed.")

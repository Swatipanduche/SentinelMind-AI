
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/processed")

files = [
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv"
]

frames = []

for filename in files:
    print("Loading:", filename)

    df = pd.read_csv(DATA_DIR / filename)
    df.columns = df.columns.str.strip()
    frames.append(df)

data = pd.concat(frames, ignore_index=True)

print("\n========== FINAL DATASET ==========")
print("Total records:", f"{len(data):,}")
print("Total features:", len(data.columns) - 1)

print("\nAttack distribution:")
print(data["Label"].value_counts())

print("\nMissing values:", data.isna().sum().sum())

print("\nInfinite values:",
      data.select_dtypes(include="number")
      .isin([float("inf"), float("-inf")])
      .sum().sum())

output_path = Path("data/processed/sentinelmind_dataset.csv")
data.to_csv(output_path, index=False)

print("\nCombined dataset saved:", output_path)

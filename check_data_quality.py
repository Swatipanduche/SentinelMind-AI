
import pandas as pd
import numpy as np
from pathlib import Path

DATA_DIR = Path("data/raw")

files = [
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv"
]

for filename in files:
    print("\n" + "=" * 60)
    print("CHECKING:", filename)

    missing_counts = {}
    infinite_counts = {}
    total_rows = 0

    for chunk in pd.read_csv(
        DATA_DIR / filename,
        chunksize=100_000
    ):
        chunk.columns = chunk.columns.str.strip()
        total_rows += len(chunk)

        missing = chunk.isna().sum()
        for col, count in missing.items():
            missing_counts[col] = missing_counts.get(col, 0) + count

        numeric = chunk.select_dtypes(include="number")
        infinite = np.isinf(numeric).sum()

        for col, count in infinite.items():
            infinite_counts[col] = infinite_counts.get(col, 0) + count

    print("Total records:", f"{total_rows:,}")

    print("\nColumns with missing values:")
    print({k: v for k, v in missing_counts.items() if v > 0})

    print("\nColumns with infinite values:")
    print({k: v for k, v in infinite_counts.items() if v > 0})

    print("\nData quality scan completed.")

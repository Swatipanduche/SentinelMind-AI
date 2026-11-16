
import pandas as pd
import numpy as np
from pathlib import Path

RAW_DIR = Path("data/raw")
CLEAN_DIR = Path("data/processed")

CLEAN_DIR.mkdir(parents=True, exist_ok=True)

files = [
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv"
]

for filename in files:
    print("\nProcessing:", filename)

    input_path = RAW_DIR / filename
    output_path = CLEAN_DIR / filename

    total_rows = 0
    removed_rows = 0
    kept_rows = 0

    first_chunk = True

    for chunk in pd.read_csv(input_path, chunksize=100_000):

        # Standardize column names and labels
        chunk.columns = chunk.columns.str.strip()
        chunk["Label"] = chunk["Label"].astype(str).str.strip()

        # Convert infinite values into missing values
        chunk.replace([np.inf, -np.inf], np.nan, inplace=True)

        # Identify numeric feature columns
        numeric_cols = chunk.select_dtypes(
            include="number"
        ).columns

        # Remove rows with missing numeric features
        before = len(chunk)
        chunk.dropna(subset=numeric_cols, inplace=True)

        removed_rows += before - len(chunk)
        kept_rows += len(chunk)
        total_rows += before

        # Save cleaned data
        chunk.to_csv(
            output_path,
            mode="w" if first_chunk else "a",
            header=first_chunk,
            index=False
        )

        first_chunk = False

    print("Original records:", f"{total_rows:,}")
    print("Removed records:", f"{removed_rows:,}")
    print("Remaining records:", f"{kept_rows:,}")
    print("Saved to:", output_path)

print("\nDataset cleaning completed!")

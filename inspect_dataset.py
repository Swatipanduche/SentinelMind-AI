
import pandas as pd
from pathlib import Path

DATA_DIR = Path("data/raw")

files = [
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv"
]

for filename in files:
    print("\n" + "=" * 60)
    print("FILE:", filename)

    file_path = DATA_DIR / filename

    # Read only 5 rows initially
    df = pd.read_csv(file_path, nrows=5)

    print("\nColumns:")
    print(df.columns.tolist())

    print("\nFirst 5 rows:")
    print(df.head())

    print("\nDataset dimensions (sample):", df.shape)

    label_columns = [
        col for col in df.columns
        if col.strip().lower() == "label"
    ]

    if label_columns:
        print("\nSample labels:")
        print(df[label_columns[0]].value_counts())

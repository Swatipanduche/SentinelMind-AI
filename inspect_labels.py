
import pandas as pd
from pathlib import Path
from collections import Counter

DATA_DIR = Path("data/raw")

files = [
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv"
]

for filename in files:
    print("\n" + "=" * 55)
    print("ANALYSING:", filename)

    counts = Counter()

    for chunk in pd.read_csv(
        DATA_DIR / filename,
        chunksize=200_000
    ):
        chunk.columns = chunk.columns.str.strip()

        labels = chunk["Label"].astype(str).str.strip()
        counts.update(labels.value_counts().to_dict())

    print("\nAttack distribution:")
    for label, count in counts.most_common():
        print(f"{label}: {count:,}")

    print("\nTotal records:", sum(counts.values()))

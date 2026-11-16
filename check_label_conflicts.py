
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/sentinelmind_dataset.csv")

df = pd.read_csv(DATA_PATH)

features = df.drop(columns=["Label"]).columns

# Find feature combinations associated with multiple labels
label_counts = (
    df.groupby(list(features), dropna=False)["Label"]
    .nunique()
)

conflicting_groups = label_counts[label_counts > 1]

# Extract all records belonging to conflicting groups
indexed = df.set_index(list(features))

conflicts = indexed.loc[
    indexed.index.isin(conflicting_groups.index)
].reset_index()

print("\n========== CONFLICTING LABEL DISTRIBUTION ==========")
print(conflicts["Label"].value_counts())

print("\n========== CONFLICTING LABEL COMBINATIONS ==========")

combinations = (
    conflicts.groupby(list(features), dropna=False)["Label"]
    .agg(lambda x: sorted(set(x)))
)

for labels in combinations.head(15):
    print(labels)

print("\nTotal conflicting groups:", len(conflicting_groups))
print("Total conflicting records:", len(conflicts))

# Save the records for further inspection
conflicts.to_csv(
    "data/processed/conflicting_records.csv",
    index=False
)

print("\nSaved: data/processed/conflicting_records.csv")


import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/sentinelmind_dataset.csv")

print("Loading dataset...")
df = pd.read_csv(DATA_PATH)

# 1. Exact duplicate records
duplicate_mask = df.duplicated(keep="first")

print("\n========== DUPLICATE ANALYSIS ==========")
print("Total rows:", f"{len(df):,}")
print("Exact duplicate rows:", f"{duplicate_mask.sum():,}")
print("Unique rows:", f"{len(df) - duplicate_mask.sum():,}")

print("\nDuplicate records by class:")
print(df.loc[duplicate_mask, "Label"].value_counts())

# 2. Check whether identical features have different labels
feature_columns = df.drop(columns=["Label"]).columns

feature_duplicate_mask = df.duplicated(
    subset=list(feature_columns),
    keep=False
)

print("\n========== FEATURE DUPLICATES ==========")
print("Rows with repeated feature values:",
      f"{feature_duplicate_mask.sum():,}")

# 3. Identify zero-variance features
X = df[feature_columns]

zero_variance = X.columns[X.nunique(dropna=False) <= 1].tolist()

print("\n========== ZERO-VARIANCE FEATURES ==========")
print("Count:", len(zero_variance))

for feature in zero_variance:
    print("-", feature)

print("\nInspection completed.")

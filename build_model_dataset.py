
import pandas as pd
from pathlib import Path

INPUT_PATH = Path("data/processed/sentinelmind_dataset.csv")
OUTPUT_PATH = Path("data/processed/model_dataset.csv")

print("Loading dataset...")
df = pd.read_csv(INPUT_PATH)

original_count = len(df)

# Identify feature columns
feature_columns = df.drop(columns=["Label"]).columns.tolist()

# Remove groups with conflicting labels
label_counts = (
    df.groupby(feature_columns, dropna=False)["Label"]
    .transform("nunique")
)

df = df.loc[label_counts == 1].copy()

conflicts_removed = original_count - len(df)

# Remove exact duplicate rows
before_deduplication = len(df)
df = df.drop_duplicates()
duplicates_removed = before_deduplication - len(df)

# Remove zero-variance features
feature_columns = df.drop(columns=["Label"]).columns

zero_variance = [
    col for col in feature_columns
    if df[col].nunique(dropna=False) <= 1
]

df = df.drop(columns=zero_variance)

# Save the model dataset
df.to_csv(OUTPUT_PATH, index=False)

print("\n========== MODEL DATASET REPORT ==========")
print("Original records:", f"{original_count:,}")
print("Conflicting records removed:", f"{conflicts_removed:,}")
print("Duplicate records removed:", f"{duplicates_removed:,}")
print("Zero-variance features removed:", len(zero_variance))
print("Final records:", f"{len(df):,}")
print("Final features:", len(df.columns) - 1)

print("\nFinal class distribution:")
print(df["Label"].value_counts())

print("\nMissing values:", df.isna().sum().sum())
print("\nSaved:", OUTPUT_PATH)

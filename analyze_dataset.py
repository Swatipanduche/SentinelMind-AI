
import pandas as pd
from pathlib import Path

DATA_PATH = Path("data/processed/sentinelmind_dataset.csv")

print("Loading SentinelMind dataset...")
df = pd.read_csv(DATA_PATH)

print("\n========== DATASET OVERVIEW ==========")
print("Shape:", df.shape)
print("Duplicate rows:", df.duplicated().sum())

print("\n========== CLASS DISTRIBUTION ==========")
counts = df["Label"].value_counts()
percentages = df["Label"].value_counts(normalize=True) * 100

distribution = pd.DataFrame({
    "Records": counts,
    "Percentage": percentages.round(3)
})

print(distribution)

print("\n========== FEATURE ANALYSIS ==========")
X = df.drop(columns=["Label"])

print("Numeric features:", len(X.select_dtypes(include="number").columns))
print("Non-numeric features:", len(X.select_dtypes(exclude="number").columns))

print("\n========== FEATURE VARIANCE ==========")
variances = X.var(numeric_only=True).sort_values()

print("Lowest 10 variance features:")
print(variances.head(10))

print("\nAnalysis completed.")

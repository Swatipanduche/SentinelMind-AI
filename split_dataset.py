
import pandas as pd
from pathlib import Path
from sklearn.model_selection import train_test_split

INPUT_PATH = Path("data/processed/model_dataset.csv")
OUTPUT_DIR = Path("data/processed")

print("Loading modelling dataset...")
df = pd.read_csv(INPUT_PATH)

# Exclude Heartbleed from this first classifier
# Only 11 examples are available, which is insufficient
# for reliable training and testing.
df = df[df["Label"] != "Heartbleed"].copy()

print("\nDataset after excluding Heartbleed:")
print("Records:", f"{len(df):,}")
print("Classes:", df["Label"].nunique())

X = df.drop(columns=["Label"])
y = df["Label"]

# Stratified 80:20 split
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)

# Save training and testing datasets
train_df = X_train.copy()
train_df["Label"] = y_train

test_df = X_test.copy()
test_df["Label"] = y_test

train_df.to_csv(OUTPUT_DIR / "train_dataset.csv", index=False)
test_df.to_csv(OUTPUT_DIR / "test_dataset.csv", index=False)

print("\n========== DATA SPLIT REPORT ==========")
print("Training records:", f"{len(train_df):,}")
print("Testing records:", f"{len(test_df):,}")

print("\nTraining class distribution:")
print(y_train.value_counts())

print("\nTesting class distribution:")
print(y_test.value_counts())

print("\nSaved:")
print("data/processed/train_dataset.csv")
print("data/processed/test_dataset.csv")

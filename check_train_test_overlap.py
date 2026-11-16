
import pandas as pd

print("Loading train and test datasets...")

train = pd.read_csv("data/processed/train_dataset.csv")
test = pd.read_csv("data/processed/test_dataset.csv")

X_train = train.drop(columns=["Label"])
X_test = test.drop(columns=["Label"])

print("\nChecking exact feature-row overlap...")

train_hashes = set(
    pd.util.hash_pandas_object(X_train, index=False)
)

test_hashes = pd.util.hash_pandas_object(X_test, index=False)

overlap = train_hashes.intersection(test_hashes)

print("\n========== OVERLAP ANALYSIS ==========")
print("Training records:", len(X_train))
print("Testing records:", len(X_test))
print("Matching feature rows:", len(overlap))
print(
    "Overlap percentage:",
    round(len(overlap) / len(X_test) * 100, 4),
    "%"
)

print("\nAnalysis completed.")

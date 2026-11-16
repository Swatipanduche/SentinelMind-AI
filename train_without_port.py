
import pandas as pd
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report
)

DATA_DIR = Path("data/processed")

print("Loading datasets...")

train_df = pd.read_csv(DATA_DIR / "train_dataset.csv")
test_df = pd.read_csv(DATA_DIR / "test_dataset.csv")

X_train = train_df.drop(columns=["Label", "Destination Port"])
y_train = train_df["Label"]

X_test = test_df.drop(columns=["Label", "Destination Port"])
y_test = test_df["Label"]

# Use the same training sample size and random seed
train_sample = train_df.sample(
    n=200000,
    random_state=42,
    replace=False
)

X_train_sample = train_sample.drop(
    columns=["Label", "Destination Port"]
)
y_train_sample = train_sample["Label"]

X_train_sample = X_train_sample.astype("float32")
X_test = X_test.astype("float32")

print("\nTraining Random Forest without Destination Port...")

model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

model.fit(X_train_sample, y_train_sample)

print("\nEvaluating model...")

predictions = model.predict(X_test)

print("\n========== RESULTS WITHOUT DESTINATION PORT ==========")
print("Accuracy:", accuracy_score(y_test, predictions))
print("Balanced Accuracy:", balanced_accuracy_score(y_test, predictions))

print("\nClassification Report:")
print(classification_report(y_test, predictions, zero_division=0))

Path("models").mkdir(exist_ok=True)
joblib.dump(model, "models/random_forest_without_port.pkl")

print("\nModel saved: models/random_forest_without_port.pkl")

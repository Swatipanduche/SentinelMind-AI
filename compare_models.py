
import pandas as pd
import joblib

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score
)

print("Loading test dataset and models...")

df = pd.read_csv("data/processed/test_dataset.csv")

y_test = df["Label"]
X_test = df.drop(columns=["Label"])

original_model = joblib.load("models/random_forest_model.pkl")
without_port_model = joblib.load("models/random_forest_without_port.pkl")

print("\nGenerating predictions...")

pred_original = original_model.predict(X_test)

pred_without_port = without_port_model.predict(
    X_test.drop(columns=["Destination Port"])
)

results = []

for name, predictions in [
    ("Original Model", pred_original),
    ("Without Destination Port", pred_without_port)
]:
    results.append({
        "Model": name,
        "Accuracy": accuracy_score(y_test, predictions),
        "Balanced Accuracy": balanced_accuracy_score(y_test, predictions),
        "Precision": precision_score(y_test, predictions, average="macro"),
        "Recall": recall_score(y_test, predictions, average="macro"),
        "Macro F1": f1_score(y_test, predictions, average="macro")
    })

comparison = pd.DataFrame(results)

print("\n========== MODEL COMPARISON ==========")
print(comparison.to_string(index=False))

comparison.to_csv("reports/model_comparison.csv", index=False)

print("\nSaved: reports/model_comparison.csv")

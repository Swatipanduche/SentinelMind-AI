import pandas as pd
import joblib

from pathlib import Path
from sklearn.metrics import classification_report, accuracy_score, balanced_accuracy_score

print("Loading model and test dataset...")

model = joblib.load("models/random_forest_model.pkl")
df = pd.read_csv("data/processed/test_dataset.csv")

X = df.drop(columns=["Label"])
y = df["Label"]

print("\nTesting without Destination Port...")

X_without_port = X.drop(columns=["Destination Port"])

predictions = model.predict(X_without_port)

print("\n========== RESULTS WITHOUT DESTINATION PORT ==========")
print("Accuracy:", accuracy_score(y, predictions))
print("Balanced Accuracy:", balanced_accuracy_score(y, predictions))

print("\nClassification Report:")
print(classification_report(y, predictions, zero_division=0))
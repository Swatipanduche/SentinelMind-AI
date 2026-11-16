
import pandas as pd
import numpy as np
import joblib
import time

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    accuracy_score,
    balanced_accuracy_score
)

DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")
MODEL_DIR.mkdir(exist_ok=True)

print("Loading training and testing datasets...")

train_df = pd.read_csv(DATA_DIR / "train_dataset.csv")
test_df = pd.read_csv(DATA_DIR / "test_dataset.csv")

X_train = train_df.drop(columns=["Label"])
y_train = train_df["Label"]

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]

# Use a stratified 200,000-record training sample
X_sample, _, y_sample, _ = train_test_split(
    X_train,
    y_train,
    train_size=200000,
    random_state=42,
    stratify=y_train
)

# Reduce memory usage
X_sample = X_sample.astype(np.float32)
X_test = X_test.astype(np.float32)

print("\n========== TRAINING INFORMATION ==========")
print("Training sample:", f"{len(X_sample):,}")
print("Testing records:", f"{len(X_test):,}")
print("Features:", X_sample.shape[1])
print("Classes:", y_sample.nunique())

# Initialize Random Forest
model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

print("\nTraining Random Forest...")
start_time = time.time()

model.fit(X_sample, y_sample)

training_time = time.time() - start_time

print(f"Training completed in {training_time:.2f} seconds.")

# Predictions
print("\nEvaluating model...")
y_pred = model.predict(X_test)

# Evaluation metrics
print("\n========== MODEL PERFORMANCE ==========")

print("Accuracy:", round(accuracy_score(y_test, y_pred), 4))
print("Balanced Accuracy:", round(
    balanced_accuracy_score(y_test, y_pred), 4
))

print("\nClassification Report:")
report = classification_report(
    y_test,
    y_pred,
    zero_division=0
)
print(report)

print("\nConfusion Matrix:")
labels = model.classes_

cm = confusion_matrix(y_test, y_pred, labels=labels)

print(pd.DataFrame(
    cm,
    index=labels,
    columns=labels
))

# Save model
joblib.dump(model, MODEL_DIR / "random_forest_model.pkl")

print("\nModel saved: models/random_forest_model.pkl")

# Save feature importance
importance = pd.DataFrame({
    "Feature": X_sample.columns,
    "Importance": model.feature_importances_
}).sort_values(by="Importance", ascending=False)

importance.to_csv(
    MODEL_DIR / "feature_importance.csv",
    index=False
)

print("Feature importance saved: models/feature_importance.csv")
print("\nExperiment completed.")

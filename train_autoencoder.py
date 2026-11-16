
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.neural_network import MLPRegressor
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")
REPORT_DIR = Path("reports")

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(exist_ok=True)

print("Loading datasets...")

train_df = pd.read_csv(DATA_DIR / "train_dataset.csv")
test_df = pd.read_csv(DATA_DIR / "test_dataset.csv")

# Learn exclusively from benign traffic
benign_df = train_df[
    train_df["Label"] == "BENIGN"
].sample(n=50000, random_state=42)

X_benign = benign_df.drop(columns=["Label"])

X_train, X_val = train_test_split(
    X_benign,
    test_size=0.20,
    random_state=42
)

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]

print("Training records:", len(X_train))
print("Validation records:", len(X_val))
print("Testing records:", len(X_test))

# Learn clipping limits from benign training records only
print("\nCalculating feature clipping limits...")

lower_limits = X_train.quantile(0.001)
upper_limits = X_train.quantile(0.999)

def clip_features(data):
    return data.clip(
        lower=lower_limits,
        upper=upper_limits,
        axis=1
    )

X_train_clip = clip_features(X_train)
X_val_clip = clip_features(X_val)
X_test_clip = clip_features(X_test)

# Robust scaling reduces sensitivity to extreme values
print("\nScaling features using RobustScaler...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train_clip)
X_val_scaled = scaler.transform(X_val_clip)
X_test_scaled = scaler.transform(X_test_clip)

# Build neural reconstruction model
print("\nBuilding improved Autoencoder...")

autoencoder = MLPRegressor(
    hidden_layer_sizes=(48, 24, 12, 24, 48),
    activation="relu",
    solver="adam",
    learning_rate_init=0.0005,
    batch_size=256,
    max_iter=250,
    early_stopping=True,
    validation_fraction=0.1,
    n_iter_no_change=12,
    random_state=42,
    verbose=True
)

print("\nTraining Autoencoder...")

autoencoder.fit(
    X_train_scaled,
    X_train_scaled
)

# Calculate benign validation reconstruction errors
print("\nCalculating validation errors...")

val_reconstructed = autoencoder.predict(X_val_scaled)

val_errors = np.mean(
    (X_val_scaled - val_reconstructed) ** 2,
    axis=1
)

threshold = np.percentile(val_errors, 99)

print("\n99th percentile anomaly threshold:", threshold)

# Evaluate on held-out labelled test data
print("\nEvaluating Autoencoder...")

test_reconstructed = autoencoder.predict(X_test_scaled)

test_errors = np.mean(
    (X_test_scaled - test_reconstructed) ** 2,
    axis=1
)

predictions = (test_errors > threshold).astype(int)
actual = (y_test != "BENIGN").astype(int)

print("\n========== IMPROVED AUTOENCODER RESULTS ==========")

print("Precision:", precision_score(actual, predictions, zero_division=0))
print("Recall:", recall_score(actual, predictions, zero_division=0))
print("F1 Score:", f1_score(actual, predictions, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(actual, predictions))

print("\nClassification Report:")
print(
    classification_report(
        actual,
        predictions,
        target_names=["BENIGN", "ATTACK"],
        zero_division=0
    )
)

# Per-class attack detection
evaluation = pd.DataFrame({
    "Label": y_test.values,
    "Anomaly": predictions,
    "Reconstruction_Error": test_errors
})

print("\nDetection rate by traffic class:")

print(
    evaluation.groupby("Label")["Anomaly"]
    .agg(["count", "mean"])
    .to_string()
)

# Save evaluation report
evaluation.to_csv(
    REPORT_DIR / "autoencoder_predictions_improved.csv",
    index=False
)

# Save model and preprocessing configuration
joblib.dump(
    {
        "model": autoencoder,
        "scaler": scaler,
        "threshold": threshold,
        "features": list(X_train.columns),
        "lower_limits": lower_limits,
        "upper_limits": upper_limits
    },
    MODEL_DIR / "sentinelmind_autoencoder_improved.pkl"
)

print("\nImproved Autoencoder saved successfully.")
print("Model: models/sentinelmind_autoencoder_improved.pkl")
print("Report: reports/autoencoder_predictions_improved.csv")

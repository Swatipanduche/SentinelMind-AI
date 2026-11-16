
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
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

print("Loading test dataset...")

test_df = pd.read_csv(DATA_DIR / "test_dataset.csv")

X_test = test_df.drop(columns=["Label"])
y_test = test_df["Label"]

actual = (y_test != "BENIGN").astype(int)

# -----------------------------------
# 1. RANDOM FOREST CLASSIFIER
# -----------------------------------

print("\nLoading Random Forest...")

rf_model = joblib.load(
    MODEL_DIR / "random_forest_model.pkl"
)

rf_features = list(rf_model.feature_names_in_)

rf_input = X_test[rf_features]

rf_predictions = rf_model.predict(rf_input)
rf_probabilities = rf_model.predict_proba(rf_input)

benign_index = list(rf_model.classes_).index("BENIGN")

rf_attack_confidence = 1 - rf_probabilities[:, benign_index]

rf_attack = (rf_predictions != "BENIGN")

print("Random Forest predictions completed.")

# -----------------------------------
# 2. AUTOENCODER ANOMALY DETECTION
# -----------------------------------

print("\nLoading Autoencoder...")

ae_bundle = joblib.load(
    MODEL_DIR / "sentinelmind_tuesday_autoencoder.pkl"
)

autoencoder = ae_bundle["model"]
scaler = ae_bundle["scaler"]
threshold = ae_bundle["threshold"]

features = ae_bundle["features"]
lower_limits = ae_bundle["lower_limits"]
upper_limits = ae_bundle["upper_limits"]

ae_input = X_test[features].clip(
    lower=lower_limits,
    upper=upper_limits,
    axis=1
)

scaled_input = scaler.transform(ae_input)

reconstructed = autoencoder.predict(scaled_input)

reconstruction_errors = np.mean(
    (scaled_input - reconstructed) ** 2,
    axis=1
)

ae_anomaly = reconstruction_errors > threshold

print("Autoencoder predictions completed.")


# -----------------------------------
# 3. INTELLIGENT THREAT DECISION
# -----------------------------------

print("\nGenerating threat decisions...")

# Three distinct security outcomes
threat_status = np.select(
    [
        rf_attack,
        (~rf_attack) & ae_anomaly
    ],
    [
        "CLASSIFIED_ATTACK",
        "ANOMALY_REVIEW"
    ],
    default="NORMAL"
)

# Retain the combined alert for evaluation
combined_alert = threat_status != "NORMAL"

# Heuristic risk score (not a calibrated probability)
normalized_anomaly = np.clip(
    reconstruction_errors / (2 * threshold),
    0,
    1
)

risk_score = (
    0.70 * rf_attack_confidence +
    0.30 * normalized_anomaly
) * 100

# -----------------------------------
# 4. EVALUATION
# -----------------------------------


print("\n========== SENTINELMIND RESULTS ==========")

# Primary classifier evaluation
print("\n1. RANDOM FOREST - PRIMARY ATTACK CLASSIFIER")

print("Precision:", precision_score(actual, rf_attack, zero_division=0))
print("Recall:", recall_score(actual, rf_attack, zero_division=0))
print("F1 Score:", f1_score(actual, rf_attack, zero_division=0))

print("\nConfusion Matrix:")
print(confusion_matrix(actual, rf_attack))

# Independent anomaly detection evaluation
print("\n2. AUTOENCODER - ANOMALY DETECTION")

print("Precision:", precision_score(actual, ae_anomaly, zero_division=0))
print("Recall:", recall_score(actual, ae_anomaly, zero_division=0))
print("F1 Score:", f1_score(actual, ae_anomaly, zero_division=0))

# Decision engine distribution
print("\n3. SENTINELMIND THREAT TRIAGE")

print(pd.Series(threat_status).value_counts())

review_count = np.sum(
    (~rf_attack) & ae_anomaly
)

print("\nAnomaly-only review records:", review_count)
print("These records require investigation, not automatic attack confirmation.")



# -----------------------------------
# 5. GENERATE THREAT INTELLIGENCE REPORT
# -----------------------------------

results = pd.DataFrame({
    "Actual_Label": y_test.values,
    "RF_Prediction": rf_predictions,
    "RF_Attack_Confidence": rf_attack_confidence,
    "Anomaly_Score": reconstruction_errors,
    "Anomaly_Detected": ae_anomaly,
    "Threat_Status": threat_status,
    "Risk_Score": risk_score
})

results.to_csv(
    REPORT_DIR / "sentinelmind_threat_report.csv",
    index=False
)

print("\nThreat report saved:")
print("reports/sentinelmind_threat_report.csv")

print("\nSentinelMind Threat Decision Engine completed.")


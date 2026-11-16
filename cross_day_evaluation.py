
import pandas as pd
import numpy as np
import joblib

from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

DATA_DIR = Path("data/processed")
MODEL_DIR = Path("models")
REPORT_DIR = Path("reports/cross_day")

MODEL_DIR.mkdir(exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)

TUESDAY_FILE = "Tuesday-WorkingHours.pcap_ISCX.csv"
WEDNESDAY_FILE = "Wednesday-workingHours.pcap_ISCX.csv"

MODEL_PATH = MODEL_DIR / "random_forest_tuesday_cross_day.pkl"

print("\n========== SENTINELMIND CROSS-DAY EVALUATION ==========")

# --------------------------------------------------
# 1. Load source datasets independently
# --------------------------------------------------

print("\nLoading Tuesday and Wednesday datasets...")

tuesday = pd.read_csv(DATA_DIR / TUESDAY_FILE)
wednesday = pd.read_csv(DATA_DIR / WEDNESDAY_FILE)

tuesday.columns = tuesday.columns.str.strip()
wednesday.columns = wednesday.columns.str.strip()

tuesday["Label"] = tuesday["Label"].str.strip()
wednesday["Label"] = wednesday["Label"].str.strip()

features = [c for c in tuesday.columns if c != "Label"]

assert features == [
    c for c in wednesday.columns if c != "Label"
], "Feature columns do not match!"

print("Tuesday records:", len(tuesday))
print("Wednesday records:", len(wednesday))
print("Features:", len(features))

# --------------------------------------------------
# 2. Clean Tuesday training data independently
# --------------------------------------------------

print("\nPreparing Tuesday training data...")

# Remove conflicting feature groups within Tuesday only
tuesday_conflicts = (
    tuesday.groupby(features, dropna=False)["Label"]
    .transform("nunique") > 1
)

print("Tuesday conflicting records:", tuesday_conflicts.sum())

train_df = tuesday.loc[~tuesday_conflicts].copy()

# Remove exact duplicate records
before = len(train_df)
train_df = train_df.drop_duplicates()
print("Tuesday duplicate records removed:", before - len(train_df))

# Remove invalid numerical records, if any
X_raw = train_df[features].replace([np.inf, -np.inf], np.nan)
valid_rows = X_raw.notna().all(axis=1)

print("Invalid Tuesday records removed:", (~valid_rows).sum())

train_df = train_df.loc[valid_rows].copy()

# Determine zero-variance features using Tuesday only
zero_variance = [
    col for col in features
    if train_df[col].nunique(dropna=False) <= 1
]

model_features = [c for c in features if c not in zero_variance]

print("Zero-variance features removed:", len(zero_variance))
print("Final training features:", len(model_features))

# --------------------------------------------------
# 3. Train binary Random Forest using Tuesday only
# --------------------------------------------------

print("\nPreparing binary labels...")

X_train = train_df[model_features].astype(np.float32)
y_train = (train_df["Label"] != "BENIGN").astype(int)

print("Training records:", len(X_train))
print("Benign records:", int((y_train == 0).sum()))
print("Attack records:", int((y_train == 1).sum()))

print("\nTraining Tuesday-only Random Forest...")

rf_model = RandomForestClassifier(
    n_estimators=100,
    max_depth=20,
    min_samples_leaf=2,
    class_weight="balanced_subsample",
    random_state=42,
    n_jobs=-1
)

rf_model.fit(X_train, y_train)

print("Random Forest training completed.")

# --------------------------------------------------
# 4. Identify Wednesday ambiguous records
# --------------------------------------------------

print("\nPreparing Wednesday evaluation data...")

wednesday_conflicts = (
    wednesday.groupby(features, dropna=False)["Label"]
    .transform("nunique") > 1
)

print("Wednesday ambiguous records:", wednesday_conflicts.sum())

test_df = wednesday.loc[~wednesday_conflicts].copy()

# Preserve repeated Wednesday records for record-level evaluation
X_test_raw = test_df[model_features].replace(
    [np.inf, -np.inf], np.nan
)

valid_test = X_test_raw.notna().all(axis=1)

print("Invalid Wednesday records removed:", (~valid_test).sum())

test_df = test_df.loc[valid_test].copy()

X_test = test_df[model_features].astype(np.float32)

y_test = (test_df["Label"] != "BENIGN").astype(int)

# --------------------------------------------------
# 5. Identify shared and Wednesday-only patterns
# --------------------------------------------------

print("\nAnalyzing cross-day feature patterns...")

tuesday_hashes = pd.util.hash_pandas_object(
    train_df[features],
    index=False
)

wednesday_hashes = pd.util.hash_pandas_object(
    test_df[features],
    index=False
)

# Tuesday has no conflicting feature groups.
# Map each Tuesday pattern to its binary label.
tuesday_pattern_labels = pd.DataFrame({
    "pattern": tuesday_hashes.values,
    "tuesday_attack": y_train.values
}).drop_duplicates("pattern").set_index("pattern")["tuesday_attack"]

test_df = test_df.copy()
test_df["Pattern_Hash"] = wednesday_hashes.values

test_df["Tuesday_Attack_Label"] = (
    test_df["Pattern_Hash"].map(tuesday_pattern_labels)
)

shared = test_df["Tuesday_Attack_Label"].notna()

same_binary_label = (
    test_df["Tuesday_Attack_Label"].eq(
        (test_df["Label"] != "BENIGN").astype(int)
    )
)

test_df["Pattern_Group"] = np.select(
    [
        ~shared,
        shared & same_binary_label
    ],
    [
        "WEDNESDAY_ONLY",
        "SHARED_LABEL_AGREEMENT"
    ],
    default="SHARED_LABEL_DISAGREEMENT"
)

print("\nPattern distribution:")
print(test_df["Pattern_Group"].value_counts().to_string())

# --------------------------------------------------
# 6. Predict Wednesday traffic
# --------------------------------------------------

print("\nEvaluating Wednesday traffic...")

predictions = rf_model.predict(X_test)
probabilities = rf_model.predict_proba(X_test)[:, 1]

test_df["Actual_Attack"] = y_test.values
test_df["Predicted_Attack"] = predictions
test_df["Attack_Probability"] = probabilities

# --------------------------------------------------
# 7. Evaluation metrics
# --------------------------------------------------

def calculate_metrics(name, frame):

    if len(frame) == 0:
        print("\n", name, "- No records available")
        return None

    actual = frame["Actual_Attack"].astype(int)
    predicted = frame["Predicted_Attack"].astype(int)

    cm = confusion_matrix(actual, predicted, labels=[0, 1])

    tn, fp, fn, tp = cm.ravel()

    fpr = fp / (fp + tn) if (fp + tn) else 0
    specificity = tn / (tn + fp) if (tn + fp) else 0

    result = {
        "Evaluation": name,
        "Records": len(frame),
        "Accuracy": accuracy_score(actual, predicted),
        "Precision": precision_score(
            actual, predicted, zero_division=0
        ),
        "Recall": recall_score(
            actual, predicted, zero_division=0
        ),
        "F1": f1_score(
            actual, predicted, zero_division=0
        ),
        "False_Positive_Rate": fpr,
        "Specificity": specificity,
        "True_Negatives": tn,
        "False_Positives": fp,
        "False_Negatives": fn,
        "True_Positives": tp
    }

    print("\n==========", name, "==========")
    print("Records:", len(frame))
    print("Accuracy:", round(result["Accuracy"], 5))
    print("Precision:", round(result["Precision"], 5))
    print("Recall:", round(result["Recall"], 5))
    print("F1:", round(result["F1"], 5))
    print("False Positive Rate:", round(fpr, 5))
    print("Confusion Matrix:")
    print(cm)

    return result


results = []

# All unambiguous Wednesday records
results.append(
    calculate_metrics("ALL_WEDNESDAY", test_df)
)

# Evaluate each pattern group separately
for group in [
    "WEDNESDAY_ONLY",
    "SHARED_LABEL_AGREEMENT",
    "SHARED_LABEL_DISAGREEMENT"
]:
    subset = test_df[test_df["Pattern_Group"] == group]

    result = calculate_metrics(group, subset)

    if result is not None:
        results.append(result)

# --------------------------------------------------
# 8. Unique feature-pattern evaluation
# --------------------------------------------------

print("\nEvaluating unique Wednesday feature patterns...")

unique_test = test_df.drop_duplicates(subset=features)

unique_result = calculate_metrics(
    "UNIQUE_WEDNESDAY_PATTERNS",
    unique_test
)

if unique_result is not None:
    results.append(unique_result)

# --------------------------------------------------
# 9. Per-attack detection rates
# --------------------------------------------------

print("\n========== PER-CLASS DETECTION ==========")

class_report = (
    test_df.groupby("Label")
    .agg(
        Records=("Actual_Attack", "size"),
        Detected_Attacks=("Predicted_Attack", "sum"),
        Mean_Attack_Probability=("Attack_Probability", "mean")
    )
)

class_report["Detection_Rate"] = (
    class_report["Detected_Attacks"] /
    class_report["Records"]
)

print(class_report.to_string())

class_report.to_csv(
    REPORT_DIR / "per_attack_detection.csv"
)

# --------------------------------------------------
# 10. Save reports and model
# --------------------------------------------------

metrics_df = pd.DataFrame(results)

metrics_df.to_csv(
    REPORT_DIR / "cross_day_metrics.csv",
    index=False
)

test_df[
    [
        "Label",
        "Actual_Attack",
        "Predicted_Attack",
        "Attack_Probability",
        "Pattern_Group"
    ]
].to_csv(
    REPORT_DIR / "wednesday_predictions.csv",
    index=False
)

joblib.dump(
    {
        "model": rf_model,
        "features": model_features,
        "zero_variance_features": zero_variance,
        "training_day": "Tuesday",
        "evaluation_day": "Wednesday",
        "label_mapping": {
            "BENIGN": 0,
            "ATTACK": 1
        }
    },
    MODEL_PATH
)

print("\n========== EXPERIMENT COMPLETED ==========")
print("Model saved:", MODEL_PATH)
print("Metrics saved:", REPORT_DIR / "cross_day_metrics.csv")
print("Predictions saved:", REPORT_DIR / "wednesday_predictions.csv")
print("Per-attack report saved:", REPORT_DIR / "per_attack_detection.csv")

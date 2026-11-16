
import pandas as pd
import joblib

from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.inspection import permutation_importance

DATA_DIR = Path("data/processed")
MODEL_PATH = Path("models/random_forest_model.pkl")

print("Loading trained model and test dataset...")

model = joblib.load(MODEL_PATH)
df = pd.read_csv(DATA_DIR / "test_dataset.csv")

X = df.drop(columns=["Label"])
y = df["Label"]

# Use a stratified sample to keep computation manageable
X_sample, _, y_sample, _ = train_test_split(
    X,
    y,
    train_size=10000,
    random_state=42,
    stratify=y
)

print("\nCalculating permutation importance...")
print("Evaluation records:", len(X_sample))

result = permutation_importance(
    model,
    X_sample,
    y_sample,
    scoring="f1_macro",
    n_repeats=3,
    random_state=42,
    n_jobs=-1
)

importance_df = pd.DataFrame({
    "Feature": X.columns,
    "Importance": result.importances_mean,
    "Std": result.importances_std
}).sort_values(
    by="Importance",
    ascending=False
)

print("\n========== PERMUTATION IMPORTANCE ==========")
print(importance_df.head(20).to_string(index=False))

Path("reports").mkdir(exist_ok=True)

importance_df.to_csv(
    "reports/permutation_importance.csv",
    index=False
)

print("\nSaved: reports/permutation_importance.csv")

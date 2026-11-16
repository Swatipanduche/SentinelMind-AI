
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

print("Loading datasets...")

train = pd.read_csv("data/processed/train_dataset.csv")
test = pd.read_csv("data/processed/test_dataset.csv")

# Sample records
train_sample = train.sample(n=5000, random_state=42)
test_sample = test.sample(n=5000, random_state=42)

X_train = train_sample.drop(columns=["Label"])
y_train = train_sample["Label"]

X_test = test_sample.drop(columns=["Label"])
y_test = test_sample["Label"]

print("\nScaling features...")

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

print("\nFinding nearest training records...")

nn = NearestNeighbors(
    n_neighbors=1,
    metric="euclidean",
    n_jobs=-1
)

nn.fit(X_train_scaled)

distances, indices = nn.kneighbors(X_test_scaled)

nearest_labels = y_train.iloc[indices.flatten()].reset_index(drop=True)
actual_labels = y_test.reset_index(drop=True)

comparison = pd.DataFrame({
    "Actual_Label": actual_labels,
    "Nearest_Train_Label": nearest_labels,
    "Distance": distances.flatten()
})

comparison["Label_Match"] = (
    comparison["Actual_Label"] == comparison["Nearest_Train_Label"]
)

print("\n========== NEAREST LABEL ANALYSIS ==========")

print(
    "Same nearest-neighbour label:",
    comparison["Label_Match"].mean() * 100,
    "%"
)

print("\nLabel match by distance:")

for threshold in [0.01, 0.1, 1.0]:
    subset = comparison[comparison["Distance"] <= threshold]

    if len(subset) > 0:
        print(
            f"Distance <= {threshold}: "
            f"{subset['Label_Match'].mean() * 100:.2f}% "
            f"matching labels ({len(subset)} records)"
        )

print("\nDetailed results by actual class:")
print(
    comparison.groupby("Actual_Label")["Label_Match"]
    .agg(["count", "mean"])
    .to_string()
)

comparison.to_csv(
    "reports/nearest_label_analysis.csv",
    index=False
)

print("\nSaved: reports/nearest_label_analysis.csv")

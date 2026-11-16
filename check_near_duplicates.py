
import pandas as pd
import numpy as np

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

print("Loading datasets...")

train = pd.read_csv("data/processed/train_dataset.csv")
test = pd.read_csv("data/processed/test_dataset.csv")

X_train = train.drop(columns=["Label"])
X_test = test.drop(columns=["Label"])

# Use manageable samples
train_sample = X_train.sample(n=5000, random_state=42)
test_sample = X_test.sample(n=5000, random_state=42)

print("\nScaling features...")

scaler = StandardScaler()

train_scaled = scaler.fit_transform(train_sample)
test_scaled = scaler.transform(test_sample)

print("\nFinding nearest training records...")

neighbors = NearestNeighbors(
    n_neighbors=1,
    metric="euclidean",
    n_jobs=-1
)

neighbors.fit(train_scaled)

distances, indices = neighbors.kneighbors(test_scaled)

nearest_distances = distances.flatten()

print("\n========== NEAR-DUPLICATE ANALYSIS ==========")
print("Test samples:", len(test_sample))
print("Minimum distance:", np.min(nearest_distances))
print("Median distance:", np.median(nearest_distances))
print("Mean distance:", np.mean(nearest_distances))
print("Maximum distance:", np.max(nearest_distances))

for threshold in [0.01, 0.1, 1.0]:
    count = np.sum(nearest_distances <= threshold)
    print(
        f"Records with distance <= {threshold}: "
        f"{count} ({count / len(nearest_distances) * 100:.2f}%)"
    )

print("\nAnalysis completed.")

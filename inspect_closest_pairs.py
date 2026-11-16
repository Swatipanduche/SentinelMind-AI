
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.neighbors import NearestNeighbors

train = pd.read_csv("data/processed/train_dataset.csv")
test = pd.read_csv("data/processed/test_dataset.csv")

train_sample = train.sample(n=5000, random_state=42)
test_sample = test.sample(n=5000, random_state=42)

X_train = train_sample.drop(columns=["Label"])
X_test = test_sample.drop(columns=["Label"])

scaler = StandardScaler()

X_train_scaled = scaler.fit_transform(X_train)
X_test_scaled = scaler.transform(X_test)

nn = NearestNeighbors(n_neighbors=1, metric="euclidean")
nn.fit(X_train_scaled)

distances, indices = nn.kneighbors(X_test_scaled)

nearest_train = train_sample.iloc[indices.flatten()].reset_index(drop=True)
test_reset = test_sample.reset_index(drop=True)

results = pd.DataFrame({
    "Test_Label": test_reset["Label"],
    "Nearest_Train_Label": nearest_train["Label"],
    "Distance": distances.flatten()
})

results["Label_Match"] = (
    results["Test_Label"] == results["Nearest_Train_Label"]
)

results = results.sort_values("Distance")

print("\n========== 20 CLOSEST TRAIN-TEST PAIRS ==========")
print(results.head(20).to_string(index=False))

results.head(20).to_csv(
    "reports/closest_train_test_pairs.csv",
    index=False
)

print("\nSaved: reports/closest_train_test_pairs.csv")

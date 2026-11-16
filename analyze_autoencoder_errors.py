
import pandas as pd
import numpy as np

df = pd.read_csv("reports/autoencoder_predictions.csv")

print("\n========== RECONSTRUCTION ERROR ANALYSIS ==========")

print("\nStatistics by traffic class:")

stats = df.groupby("Label")["Reconstruction_Error"].agg(
    ["count", "mean", "median", "std", "min", "max"]
)

print(stats.to_string())

print("\nPercentiles by traffic class:")

for label, group in df.groupby("Label"):
    print(f"\n{label}")

    print(
        group["Reconstruction_Error"]
        .quantile([0.50, 0.75, 0.90, 0.95, 0.99])
        .to_string()
    )

print("\nAnalysis completed.")

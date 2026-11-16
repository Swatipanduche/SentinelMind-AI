
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

PATH = Path("models/feature_importance.csv")

df = pd.read_csv(PATH)

top_features = df.head(20)

print("\n========== TOP 20 IMPORTANT FEATURES ==========")
print(top_features.to_string(index=False))

plt.figure(figsize=(12, 8))

plt.barh(
    top_features["Feature"][::-1],
    top_features["Importance"][::-1]
)

plt.xlabel("Feature Importance")
plt.ylabel("Network Traffic Feature")
plt.title("SentinelMind AI - Random Forest Feature Importance")
plt.tight_layout()

Path("reports").mkdir(exist_ok=True)

plt.savefig(
    "reports/feature_importance.png",
    dpi=300
)

plt.show()

print("\nChart saved: reports/feature_importance.png")

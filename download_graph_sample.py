
import requests
from pathlib import Path

URL = (
    "https://huggingface.co/datasets/"
    "pcy12345BSU/CSE-CIC-IDS-2018/resolve/main/"
    "data/Thuesday-20-02-2018_TrafficForML_CICFlowMeter.csv"
)

OUTPUT = Path("data/raw/attack_path_sample.csv")
MAX_RECORDS = 20000

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

print("Connecting to dataset...")

response = requests.get(URL, stream=True, timeout=(20, 120))
response.raise_for_status()

print("Extracting first 20,000 records...")

count = 0

with open(OUTPUT, "w", encoding="utf-8", newline="") as file:
    for line in response.iter_lines():
        if not line:
            continue

        file.write(line.decode("utf-8-sig") + "\n")
        count += 1

        if count >= MAX_RECORDS + 1:  # Include header
            break

response.close()

print("\nExtraction completed!")
print("Records extracted:", count - 1)
print("Saved to:", OUTPUT)


import requests
from pathlib import Path

URL = (
    "https://huggingface.co/datasets/"
    "pcy12345BSU/CSE-CIC-IDS-2018/resolve/main/"
    "data/Thursday-22-02-2018_TrafficForML_CICFlowMeter.csv"
)

OUTPUT = Path("data/raw/attack_path_sample_2.csv")
MAX_RECORDS = 20000

OUTPUT.parent.mkdir(parents=True, exist_ok=True)

print("Connecting to Thursday dataset...")

response = requests.get(URL, stream=True, timeout=(20, 120))
response.raise_for_status()

count = 0

with open(OUTPUT, "w", encoding="utf-8", newline="") as file:
    for line in response.iter_lines():
        if not line:
            continue

        file.write(line.decode("utf-8-sig") + "\n")
        count += 1

        if count >= MAX_RECORDS + 1:
            break

response.close()

print("Extraction completed!")
print("Records:", count - 1)
print("Saved:", OUTPUT)

# SentinelMind AI
### AI-Assisted Network Threat Detection and Security Operations Dashboard

SentinelMind AI is a cybersecurity research project that combines machine learning, anomaly detection, and network graph analysis to support network threat investigation.

It analyzes network traffic datasets, classifies known attack patterns, identifies unusual traffic for analyst review, and presents the results through an interactive Streamlit dashboard.

> **Project type:** Offline cybersecurity research prototype. It is not a live network monitoring or production security system.

## Features

The dashboard contains five sections:

1. **Overview** – Threat summary, traffic statistics, and detection results.
2. **Threat Detection** – Supervised attack classification and anomaly review.
3. **Network Intelligence** – Network topology and communication analysis.
4. **Device Investigation** – Device-level traffic information, centrality metrics, and heuristic risk prioritization.
5. **Methodology** – Dataset, model, evaluation, and project limitations.

## Technology Stack

- Python
- Streamlit
- Pandas and NumPy
- Scikit-learn
- NetworkX
- PyVis
- Matplotlib
- Joblib

## Detection Approach

### 1. Random Forest Classification

A Random Forest classifier is used to distinguish benign traffic from known attack patterns represented in the training data.

### 2. Autoencoder-Based Anomaly Detection

An autoencoder is trained using benign network traffic. Traffic with unusual reconstruction behaviour is flagged for further analyst review.

An anomaly is not automatically considered a confirmed attack.

### 3. Hybrid Threat Triage

The project combines classification and anomaly results into three dashboard categories:

- `NORMAL` – No attack classification or anomaly flag.
- `CLASSIFIED_ATTACK` – Classified as an attack by the supervised model.
- `ANOMALY_REVIEW` – Unusual traffic requiring further investigation.

### 4. Network Intelligence

NetworkX is used to analyze a separate network topology sample, including:

- PageRank
- Betweenness centrality
- Network connectivity
- Communication relationships

### 5. Device Investigation

A heuristic risk score helps prioritize devices for investigation. It is an analytical score, not a calibrated probability that a device is compromised.

## Datasets

The project uses:

- **CIC-IDS2017** – Network traffic data for supervised classification and anomaly detection.
- **CSE-CIC-IDS-2018** – A separate sample used for network topology analysis.

The network topology sample is separate from the CIC-IDS2017 model evaluation.

Full datasets are not included in this repository because of their size and should be obtained from their original research sources.

## Evaluation Results

### Dashboard classification evaluation

The Random Forest results below are from a held-out test split of selected Tuesday and Wednesday CIC-IDS2017 records.

| Metric | Random Forest |
|---|---:|
| Precision | 99.83% |
| Recall | 99.85% |
| F1-score | 99.84% |

The autoencoder evaluation on the dashboard report produced:

| Metric | Autoencoder |
|---|---:|
| Precision | 90.05% |
| Recall | 76.55% |
| F1-score | 82.75% |

These results describe the evaluated dataset and split. They should not be interpreted as guaranteed performance on other networks.

### Separate cross-day experiment

A separate experiment trained models using Tuesday traffic and evaluated them on Wednesday traffic.

The Tuesday-trained Random Forest did not detect the Wednesday attack families at its evaluated default threshold. The Tuesday-trained autoencoder achieved approximately:

- Precision: 92.5%
- Recall: 62.2%
- F1-score: 74.4%
- ROC-AUC: 0.89

This experiment demonstrates the challenges of changing traffic distributions and previously unseen attack families within the same CIC-IDS2017 capture environment. It does not establish zero-day detection capability or generalization to independent networks.

## Project Structure

```text
SentinelMind-AI/
├── app.py
├── requirements.txt
├── .gitignore
├── .streamlit/
│   └── config.toml
├── backend/
├── data/
│   └── processed/
│       ├── network_nodes.csv
│       └── network_edges.csv
├── docs/
├── frontend/
├── lib/
├── models/
│   └── feature_importance.csv
├── notebooks/
├── reports/
│   ├── sentinelmind_threat_report.csv
│   ├── device_risk_assessment.csv
│   └── network_topology.html
└── *.py
## Installation and Setup

1. Clone the repository.
2. Create a virtual environment: python -m venv venv
3. Activate it: .\venv\Scripts\Activate.ps1
4. Install dependencies: pip install -r requirements.txt
5. Run: python -m streamlit run app.py --server.port 8503

## Dashboard Data Requirements

The dashboard requires:
- eports/sentinelmind_threat_report.csv
- eports/device_risk_assessment.csv
- eports/network_topology.html
- data/processed/network_nodes.csv
- data/processed/network_edges.csv

These pre-generated files are included in the repository. Full datasets and trained model binaries are excluded.

## Limitations

- Offline dataset-analysis prototype, not live network monitoring.
- Anomalies indicate unusual behaviour, not confirmed attacks.
- Device risk scores are heuristic indicators, not compromise probabilities.
- Network topology does not prove lateral movement.
- No claim of guaranteed zero-day detection.

## Future Improvements

- Live network traffic ingestion.
- Analyst feedback and alert investigation.
- Evaluation on independent datasets.
- Improved false-positive analysis.
- Model explainability enhancements.

---
**SentinelMind AI** | AI-Assisted Network Threat Detection and Security Analytics

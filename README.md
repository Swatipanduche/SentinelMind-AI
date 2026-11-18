# SentinelMind AI

**Network Intelligence and Cybersecurity Research Platform**

SentinelMind AI is a Streamlit-based research prototype for analysing prepared network-traffic datasets, identifying suspicious patterns, reviewing investigation evidence, and managing security incidents.

## Features

1. **Threat Detection** – Review prepared traffic records and model predictions.
2. **Network Intelligence** – Explore network nodes, connections, and topology.
3. **Device Investigation** – Review device-level risk information.
4. **Root Cause Analysis** – Examine supporting evidence and possible explanations.
5. **Incident Management** – Save, review, and update investigation records.
6. **Mitigation Verification** – Compare before-and-after network traffic captures.
7. **IP Attack Path** – Investigate source and destination IP relationships.
8. **System Diagnostics** – Run application, dataset, and database checks.
9. **Methodology** – Review the analytical approach and project limitations.

## Technology

- Python
- Streamlit
- Pandas and NumPy
- Scikit-learn
- NetworkX
- PyVis
- SQLite
- Matplotlib

See `requirements.txt` for the installed Python dependencies.

## Project Structure

```text
Stai/
├── app_redesigned_v2.py
├── incident_management.py
├── sentinelmind_improvements.py
├── requirements.txt
├── README.md
├── DEPLOYMENT.md
├── .gitignore
├── data/
│   ├── raw/
│   │   ├── attack_path_sample.csv
│   │   ├── attack_path_sample_2.csv
│   │   └── original dataset files and license
│   └── processed/
│       ├── sentinelmind_dataset.csv
│       ├── network_nodes.csv
│       ├── network_edges.csv
│       └── other processed datasets
├── reports/
│   ├── sentinelmind_threat_report.csv
│   ├── device_risk_assessment.csv
│   ├── network_topology.html
│   ├── incident_management.db
│   └── analysis and experiment outputs
└── venv/
```

## Installation

### 1. Clone or copy the project

Keep the project directory structure intact.

### 2. Create a virtual environment

```bash
python -m venv venv
```

### 3. Activate it

Windows PowerShell:

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 5. Run the application

```bash
python -m streamlit run app_redesigned_v2.py
```

Open the local URL displayed in the terminal.

## Data Requirements

The application uses prepared CSV datasets under `data/processed/`, raw samples under `data/raw/`, and generated reports under `reports/`.

Keep the expected filenames and directory structure unchanged. The System Diagnostics page can help identify missing or unreadable files.

The original dataset license and attribution information should be retained when redistributing dataset files.

## Important Limitations

- This is a prepared-dataset analysis platform, not a live network monitoring system.
- Model predictions and risk indicators are investigation aids, not proof of malicious activity.
- Network graph datasets may be separate from the datasets used for model evaluation.
- Results depend on the quality, coverage, and representativeness of the supplied data.
- Mitigation comparisons depend on comparable before-and-after traffic captures.
- IP investigation results depend on the available endpoint data.

## Persistent Incident Records

Incident records are stored in a local SQLite database under `reports/incident_management.db`.

Back up this database regularly if investigation history must be retained.

## Project Status

SentinelMind AI is a cybersecurity research prototype intended for educational, analytical, and demonstration purposes.

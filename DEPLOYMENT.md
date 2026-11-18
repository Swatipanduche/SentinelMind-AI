# SentinelMind AI – Deployment Guide

## A. Local Windows Deployment

1. Install a compatible Python version.
2. Open PowerShell in the project directory.
3. Activate the virtual environment:

```powershell
.\venv\Scripts\Activate.ps1
```

4. Install the dependencies:

```powershell
python -m pip install -r requirements.txt
```

5. Check Python syntax:

```powershell
python -m py_compile app_redesigned_v2.py
python -m py_compile incident_management.py
python -m py_compile sentinelmind_improvements.py
```

6. Launch Streamlit:

```powershell
python -m streamlit run app_redesigned_v2.py
```

## B. Before Deployment

Verify that the following files and folders are included:

- app_redesigned_v2.py
- incident_management.py
- sentinelmind_improvements.py
- requirements.txt
- data/processed/
- data/raw/
- reports/ files required by the application

Run the System Diagnostics page and resolve relevant failures.

Test the following pages:

- Overview
- Threat Detection
- Network Intelligence
- Device Investigation
- Methodology
- Incident Management
- Mitigation Verification
- IP Attack Path
- System Diagnostics

## C. Streamlit Community Cloud

For a cloud deployment:

1. Create a Git repository for the project.
2. Include the application modules, requirements file, and required datasets.
3. Push the repository to GitHub.
4. Open Streamlit Community Cloud.
5. Create a new app using the repository.
6. Set the main application file to:

   app_redesigned_v2.py

7. Deploy and review the application logs.

### Cloud deployment considerations

- Large CSV files may exceed repository or hosting limits.
- Keep sensitive files and credentials out of Git.
- Verify that every required dataset is available in the deployed environment.
- Cloud application filesystems may not provide durable SQLite storage across restarts or redeployments.
- A persistent database service or durable storage solution may be required for long-term incident records.
- Test file uploads and downloads in the deployed environment.

## D. Security Checklist

- Never commit passwords, API keys, or private credentials.
- Do not expose confidential investigation records.
- Restrict access to the application where necessary.
- Keep Python dependencies updated and review security advisories.
- Back up the incident database.
- Validate uploaded CSV files before processing.

## E. Final Verification

Deployment should be considered successful only after:

- The application starts without errors.
- All required datasets load.
- Every sidebar page opens.
- Diagnostics complete.
- Incident records can be saved and retrieved.
- Mitigation comparison uploads work.
- IP investigation loads the expected sample.
- The deployed environment retains any data that must persist.

## F. Project Limitation

SentinelMind AI analyses prepared datasets. Deployment does not turn it into a live packet-capture or real-time intrusion detection service.

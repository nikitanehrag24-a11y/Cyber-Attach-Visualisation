"""
Central config for all 5 datasets: where they come from, and what filename
they should land at in data/raw/ once downloaded. Keeping this in one place
means if a Kaggle slug changes, you fix it here instead of hunting through
every notebook/script.
"""

from pathlib import Path

# --- Paths ---
ROOT_DIR = Path(__file__).resolve().parents[2]  # repo root
RAW_DIR = ROOT_DIR / "data" / "raw"
INTERIM_DIR = ROOT_DIR / "data" / "interim"
PROCESSED_DIR = ROOT_DIR / "data" / "processed"

# --- Dataset registry ---
# kaggle_slug is the "owner/dataset-name" you'd pass to `kaggle datasets download -d`
DATASETS = {
    "global_threats": {
        "description": "Global Cybersecurity Threats (2015-2024)",
        "kaggle_slug": "atharvasoundankar/global-cybersecurity-threats-2015-2024",
        "raw_filename": "Global_Cybersecurity_Threats_2015-2024.csv",
        "source": "kaggle",
    },
    "cfr_incidents": {
        "description": "Cyber Incidents 2005-2020 (Council on Foreign Relations)",
        "kaggle_slug": "fireballbyedimyrnmom/cyber-incidents-up-to-2020",
        "raw_filename": "cyber-operations-incidents.csv",
        "source": "kaggle",
    },
    "vulnerabilities": {
        "description": "Security Vulnerabilities Dataset",
        "kaggle_slug": "ighoshsubho/security-vulnerabilities-dataset",
        "raw_filename": "security_vulnerabilities.csv",
        "source": "kaggle",
    },
    "attack_signatures": {
        "description": "Cyber Security Attacks (~40k records, 25 metrics)",
        "kaggle_slug": "teamincribo/cyber-security-attacks",
        "raw_filename": "cybersecurity_attacks.csv",
        "source": "kaggle",
    },
    "malmem_2022": {
        "description": "CIC-MalMem-2022 malware memory dataset",
        "kaggle_slug": None,
        "raw_filename": "cic_malmem_2022.csv",
        "source": "manual",
        "manual_url": "https://www.unb.ca/cic/datasets/malmem-2022.html",
    },
}

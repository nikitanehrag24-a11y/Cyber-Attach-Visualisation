"""
Checks for Kaggle API credentials and attempts to download and process the real datasets.
If authentication fails or is missing, it automatically falls back to generating high-quality
synthetic datasets in the `data/processed/` folder so the application can run immediately.
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path

# Add project root to python path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from src.preprocessing.config import DATASETS, RAW_DIR, PROCESSED_DIR
import src.preprocessing.run_all as run_all
import src.preprocessing.download_data as download_data

def generate_mock_global_threats(out_path):
    print("Generating mock Global Cybersecurity Threats dataset...")
    countries = ["China", "India", "Uk", "Germany", "Japan", "France", "Australia", "Russia", "Usa", "Brazil"]
    attack_types = ["Phishing", "Ransomware", "Man-In-The-Middle", "Ddos", "Sql Injection", "Malware"]
    industries = ["Education", "Retail", "It", "Telecommunications", "Government", "Banking", "Healthcare"]
    sources = ["Hacker Group", "Insider", "Nation-State", "Unknown"]
    vulnerabilities = ["Unpatched Software", "Weak Passwords", "Social Engineering", "Zero-Day"]
    defense = ["Vpn", "Firewall", "Ai-Based Detection", "Antivirus", "Encryption"]
    
    np.random.seed(42)
    rows = 3000
    data = {
        "country": np.random.choice(countries, rows),
        "year": np.random.randint(2015, 2025, rows),
        "attack_type": np.random.choice(attack_types, rows),
        "target_industry": np.random.choice(industries, rows),
        "financial_loss_in_million_": np.round(np.random.uniform(0.5, 99.99, rows), 2),
        "number_of_affected_users": np.random.randint(100, 1000000, rows),
        "attack_source": np.random.choice(sources, rows),
        "security_vulnerability_type": np.random.choice(vulnerabilities, rows),
        "defense_mechanism_used": np.random.choice(defense, rows),
        "incident_resolution_time_in_hours": np.random.randint(1, 73, rows)
    }
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df)} rows)")

def generate_mock_cfr_incidents(out_path):
    print("Generating mock CFR Incidents dataset...")
    sponsors = ["China", "Russia", "Iran", "North Korea", "Unknown", "United States", "Syria"]
    types = ["Espionage", "Sabotage", "Theft", "Defacement", "Denial of Service"]
    categories = ["Government", "Military", "Financial", "Infrastructure", "Civil Society", "Unknown"]
    
    np.random.seed(43)
    rows = 478
    start_date = datetime(2005, 1, 1)
    dates = [start_date + timedelta(days=int(np.random.randint(0, 365*15))) for _ in range(rows)]
    
    data = {
        "title": [f"Cyber operation targeting {np.random.choice(categories)} sector" for _ in range(rows)],
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "year": [d.year for d in dates],
        "sponsor": np.random.choice(sponsors, rows),
        "affiliations": np.random.choice(["State-Sponsored", "APT Group", "Independent", "Unknown"], rows),
        "type": np.random.choice(types, rows),
        "category": np.random.choice(categories, rows),
        "response": np.random.choice(["Public condemnation", "Sanctions", "Indictment", "None", "Counter-operation"], rows),
        "victims": [f"Organizations in {np.random.choice(['Usa', 'Europe', 'Asia', 'Global'])}" for _ in range(rows)],
        "description": ["Details of cyber operational activity classified by CFR researchers." for _ in range(rows)],
        "sources_1": ["https://www.cfr.org/" for _ in range(rows)],
        "sources_2": ["" for _ in range(rows)],
        "sources_3": ["" for _ in range(rows)]
    }
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df)} rows)")

def generate_mock_vulnerabilities(out_path):
    print("Generating mock Security Vulnerabilities dataset...")
    severities = ["Low", "Medium", "High", "Critical", "Unrated"]
    keywords = ["Buffer Overflow", "XSS", "Remote Code Execution", "SQL Injection", "Privilege Escalation", "Directory Traversal"]
    
    np.random.seed(44)
    rows = 1200
    start_date = datetime(2015, 1, 1)
    dates = [start_date + timedelta(days=int(np.random.randint(0, 365*9))) for _ in range(rows)]
    
    data = {
        "title": [f"CVE-{d.year}-{np.random.randint(1000, 9999)}: {np.random.choice(keywords)}" for d in dates],
        "date": [d.strftime("%Y-%m-%d") for d in dates],
        "year": [d.year for d in dates],
        "severity": np.random.choice(severities, rows, p=[0.1, 0.4, 0.3, 0.15, 0.05]),
        "summary": ["A vulnerability was discovered in software, allowing unauthorized access or service disruption." for _ in range(rows)],
        "link": ["https://nvd.nist.gov/" for _ in range(rows)]
    }
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df)} rows)")

def generate_mock_attack_signatures(out_path):
    print("Generating mock Cybersecurity Attacks (signatures) dataset...")
    protocols = ["TCP", "UDP", "ICMP"]
    packet_types = ["Data", "Control", "Management"]
    traffic_types = ["HTTP", "HTTPS", "FTP", "DNS", "SSH", "Unknown"]
    attack_types = ["DDoS", "Malware", "Phishing", "Intrusion", "SQL Injection"]
    severities = ["Low", "Medium", "High", "Critical"]
    action_taken = ["Blocked", "Allowed", "Logged", "Mitigated"]
    
    np.random.seed(45)
    rows = 5000
    start_date = datetime(2023, 1, 1)
    timestamps = [start_date + timedelta(minutes=int(np.random.randint(0, 60*24*365))) for _ in range(rows)]
    
    data = {
        "timestamp": [t.strftime("%Y-%m-%d %H:%M:%S") for t in timestamps],
        "source_ip_address": [f"192.168.1.{np.random.randint(1, 255)}" for _ in range(rows)],
        "destination_ip_address": [f"10.0.0.{np.random.randint(1, 255)}" for _ in range(rows)],
        "source_port": np.random.randint(1024, 65535, rows),
        "destination_port": np.random.choice([80, 443, 22, 53, 8080], rows),
        "protocol": np.random.choice(protocols, rows),
        "packet_length": np.random.randint(40, 1500, rows),
        "packet_type": np.random.choice(packet_types, rows),
        "traffic_type": np.random.choice(traffic_types, rows),
        "payload_data": ["RAW PAYLOAD IN HEXADECIMAL REPRESENTATION" for _ in range(rows)],
        "malware_indicators": np.random.choice(["None", "IoC Detected", "Suspicious Domain"], rows, p=[0.8, 0.15, 0.05]),
        "anomaly_scores": np.round(np.random.uniform(0.0, 1.0, rows), 4),
        "alertswarnings": np.random.choice(["None", "Alert Triggered"], rows, p=[0.7, 0.3]),
        "attack_type": np.random.choice(attack_types, rows),
        "attack_signature": [f"SigRule-{np.random.randint(100, 999)}" for _ in range(rows)],
        "action_taken": np.random.choice(action_taken, rows),
        "severity_level": np.random.choice(severities, rows, p=[0.4, 0.3, 0.2, 0.1]),
        "user_information": [f"User-{np.random.randint(10, 99)}" for _ in range(rows)],
        "device_information": np.random.choice(["Workstation", "Server", "Mobile", "IoT"], rows),
        "network_segment": np.random.choice(["DMZ", "Corporate", "Finance", "Guest"], rows),
        "geolocation_data": np.random.choice(["US", "CN", "RU", "DE", "IN", "BR", "JP"], rows),
        "proxy_information": ["Direct" for _ in range(rows)],
        "firewall_logs": ["Firewall Pass" for _ in range(rows)],
        "idsips_alerts": np.random.choice(["None", "IDS Alert"], rows, p=[0.85, 0.15]),
        "log_source": np.random.choice(["IDS", "Firewall", "ActiveDirectory", "Syslog"], rows)
    }
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df)} rows)")

def generate_mock_malmem(out_path):
    print("Generating mock CIC-MalMem-2022 dataset...")
    categories = ["Benign", "Spyware", "Ransomware", "Trojan"]
    families = ["Tibs", "Zeus", "Gator", "180Solutions", "Cidox", "Conti", "Locky", "Pysa"]
    
    np.random.seed(46)
    rows = 1500
    
    data = {
        "category": np.random.choice(categories, rows, p=[0.4, 0.2, 0.2, 0.2]),
        "family": np.random.choice(families, rows),
        "pslistnproc": np.random.randint(30, 60, rows),
        "handlesnhandles": np.random.randint(500, 3000, rows),
        "dlllistndlls": np.random.randint(15, 120, rows),
        "malfindninjections": np.random.randint(0, 15, rows)
    }
    df = pd.DataFrame(data)
    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path} ({len(df)} rows)")

def main():
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    
    print("Checking for Kaggle API credentials...")
    # Check if env credentials or ~/.kaggle/kaggle.json are present
    has_credentials = (
        "KAGGLE_USERNAME" in os.environ and "KAGGLE_KEY" in os.environ
    ) or Path("~/.kaggle/kaggle.json").expanduser().exists() or Path("~/.kaggle/access_token").expanduser().exists()
    
    if has_credentials:
        print("Kaggle credentials found. Attempting real download & cleaning...")
        try:
            download_data.main()
            run_all.main()
            print("\nReal datasets successfully downloaded and processed!")
            return
        except Exception as e:
            print(f"\nReal dataset download or preprocessing failed: {e}")
            print("Falling back to generating synthetic datasets...")
    else:
        print("Kaggle credentials not configured in environment or ~/.kaggle/")
        print("Generating mock datasets in data/processed/ to enable dashboard execution...")
        
    generate_mock_global_threats(PROCESSED_DIR / "global_threats_clean.csv")
    generate_mock_cfr_incidents(PROCESSED_DIR / "cfr_incidents_clean.csv")
    generate_mock_vulnerabilities(PROCESSED_DIR / "vulnerabilities_clean.csv")
    generate_mock_attack_signatures(PROCESSED_DIR / "attack_signatures_clean.csv")
    generate_mock_malmem(PROCESSED_DIR / "malmem_clean.csv")
    
    print("\nFallback dataset generation completed successfully. App is ready to run!")

if __name__ == "__main__":
    main()

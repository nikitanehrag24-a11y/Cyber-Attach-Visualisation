"""
Standardizes schemas and handles data alignment between the five datasets.
Maps country names, geo codes, and attack types to a common standard.
"""

import pandas as pd
from typing import Dict

# Standard mapping of various country strings/codes to standard capitalized names
COUNTRY_MAPPING: Dict[str, str] = {
    "us": "Usa",
    "usa": "Usa",
    "united states": "Usa",
    "united states of america": "Usa",
    "uk": "Uk",
    "united kingdom": "Uk",
    "gb": "Uk",
    "cn": "China",
    "china": "China",
    "ru": "Russia",
    "russia": "Russia",
    "de": "Germany",
    "germany": "Germany",
    "in": "India",
    "india": "India",
    "br": "Brazil",
    "brazil": "Brazil",
    "jp": "Japan",
    "japan": "Japan",
    "fr": "France",
    "france": "France",
    "au": "Australia",
    "australia": "Australia",
    "ca": "Canada",
    "canada": "Canada",
    "ir": "Iran",
    "iran": "Iran",
    "kp": "North Korea",
    "north korea": "North Korea",
    "sy": "Syria",
    "syria": "Syria",
}

# Standard mapping of attack types to unify terminology
ATTACK_TYPE_MAPPING: Dict[str, str] = {
    "ddos": "Ddos",
    "denial of service": "Ddos",
    "dos": "Ddos",
    "phishing": "Phishing",
    "social engineering": "Phishing",
    "ransomware": "Ransomware",
    "malware": "Malware",
    "intrusion": "Intrusion",
    "unauthorized access": "Intrusion",
    "sql injection": "Sql Injection",
    "man-in-the-middle": "Man-In-The-Middle",
    "mitm": "Man-In-The-Middle",
    "espionage": "Espionage",
    "sabotage": "Sabotage",
    "theft": "Theft",
}

def standardize_country(val: str) -> str:
    """Standardizes a country name or code using the mapping dictionary."""
    if not isinstance(val, str):
        return "Unknown"
    cleaned = val.strip().lower()
    return COUNTRY_MAPPING.get(cleaned, val.strip().title())

def standardize_attack_type(val: str) -> str:
    """Standardizes attack types into a unified set of labels."""
    if not isinstance(val, str):
        return "Unknown"
    cleaned = val.strip().lower()
    return ATTACK_TYPE_MAPPING.get(cleaned, val.strip().title())

def get_integrated_global_threats(df: pd.DataFrame) -> pd.DataFrame:
    """Applies standardization to the global threats dataset."""
    if df.empty:
        return df
    res = df.copy()
    if "country" in res.columns:
        res["standard_country"] = res["country"].apply(standardize_country)
    else:
        res["standard_country"] = "Unknown"
        
    if "attack_type" in res.columns:
        res["standard_attack_type"] = res["attack_type"].apply(standardize_attack_type)
    else:
        res["standard_attack_type"] = "Unknown"
        
    return res

def get_integrated_cfr_incidents(df: pd.DataFrame) -> pd.DataFrame:
    """Applies standardization to the CFR incidents dataset."""
    if df.empty:
        return df
    res = df.copy()
    
    # Standarize sponsor (attacker country) and victim country if needed
    if "sponsor" in res.columns:
        res["standard_country"] = res["sponsor"].apply(standardize_country)
    else:
        res["standard_country"] = "Unknown"
        
    if "type" in res.columns:
        res["standard_attack_type"] = res["type"].apply(standardize_attack_type)
    else:
        res["standard_attack_type"] = "Unknown"
        
    if "date" in res.columns and "year" not in res.columns:
        res["year"] = pd.to_datetime(res["date"], errors="coerce").dt.year
        
    return res

def get_integrated_attack_signatures(df: pd.DataFrame) -> pd.DataFrame:
    """Applies standardization to the network attack signatures dataset."""
    if df.empty:
        return df
    res = df.copy()
    
    if "geolocation_data" in res.columns:
        res["standard_country"] = res["geolocation_data"].apply(standardize_country)
    else:
        res["standard_country"] = "Unknown"
        
    if "attack_type" in res.columns:
        res["standard_attack_type"] = res["attack_type"].apply(standardize_attack_type)
    else:
        res["standard_attack_type"] = "Unknown"
        
    if "timestamp" in res.columns:
        res["year"] = pd.to_datetime(res["timestamp"], errors="coerce").dt.year
    else:
        res["year"] = 2023  # Fallback year based on mock data range if timestamp unavailable
        
    return res

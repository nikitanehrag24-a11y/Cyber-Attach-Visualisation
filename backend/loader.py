"""
Loads the cleaned datasets from the data/processed directory and caches them.
Provides helper functions to retrieve individual dataframes.
"""

from pathlib import Path
import pandas as pd
import streamlit as st

# Setup base paths relative to this file
PROJECT_ROOT = Path(__file__).resolve().parents[1]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

@st.cache_data
def load_global_threats() -> pd.DataFrame:
    """Loads the cleaned Global Cybersecurity Threats dataset."""
    file_path = PROCESSED_DIR / "global_threats_clean.csv"
    if not file_path.exists():
        st.warning(f"Global threats file not found at {file_path}. Using empty dataframe.")
        return pd.DataFrame()
    return pd.read_csv(file_path)

@st.cache_data
def load_cfr_incidents() -> pd.DataFrame:
    """Loads the cleaned Council on Foreign Relations incidents dataset."""
    file_path = PROCESSED_DIR / "cfr_incidents_clean.csv"
    if not file_path.exists():
        st.warning(f"CFR incidents file not found at {file_path}. Using empty dataframe.")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

@st.cache_data
def load_vulnerabilities() -> pd.DataFrame:
    """Loads the cleaned Security Vulnerabilities dataset."""
    file_path = PROCESSED_DIR / "vulnerabilities_clean.csv"
    if not file_path.exists():
        st.warning(f"Vulnerabilities file not found at {file_path}. Using empty dataframe.")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
    return df

@st.cache_data
def load_attack_signatures() -> pd.DataFrame:
    """Loads the cleaned Cybersecurity Attacks (signatures) dataset."""
    file_path = PROCESSED_DIR / "attack_signatures_clean.csv"
    if not file_path.exists():
        st.warning(f"Attack signatures file not found at {file_path}. Using empty dataframe.")
        return pd.DataFrame()
    df = pd.read_csv(file_path)
    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    return df

@st.cache_data
def load_malmem() -> pd.DataFrame:
    """Loads the cleaned CIC-MalMem-2022 dataset."""
    file_path = PROCESSED_DIR / "malmem_clean.csv"
    if not file_path.exists():
        st.warning(f"MalMem file not found at {file_path}. Using empty dataframe.")
        return pd.DataFrame()
    return pd.read_csv(file_path)

def load_all_datasets() -> dict[str, pd.DataFrame]:
    """Loads all five datasets and returns them in a dictionary."""
    return {
        "global_threats": load_global_threats(),
        "cfr_incidents": load_cfr_incidents(),
        "vulnerabilities": load_vulnerabilities(),
        "attack_signatures": load_attack_signatures(),
        "malmem": load_malmem(),
    }

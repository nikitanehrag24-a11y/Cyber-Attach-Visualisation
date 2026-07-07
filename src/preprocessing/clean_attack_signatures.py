"""
Cleaning pipeline for the Cyber Security Attacks dataset (~40k records,
25 metrics -- network-traffic-level attack records).

Usage:
    python -m src.preprocessing.clean_attack_signatures
"""

import pandas as pd

from src.preprocessing.base_cleaning import (
    standardize_column_names,
    report_missing,
    fill_missing,
    remove_duplicates,
    standardize_categorical,
)
from src.preprocessing.config import DATASETS, RAW_DIR, PROCESSED_DIR


def load_raw() -> pd.DataFrame:
    raw_path = RAW_DIR / DATASETS["attack_signatures"]["raw_filename"]
    if not raw_path.exists():
        raise FileNotFoundError(f"{raw_path} not found.")
    return pd.read_csv(raw_path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_column_names(df)
    # Expected columns after standardization include:
    # timestamp, source_ip_address, destination_ip_address, source_port,
    # destination_port, protocol, packet_length, packet_type, traffic_type,
    # payload_data, malware_indicators, anomaly_scores, alertswarnings,
    # attack_type, attack_signature, action_taken, severity_level,
    # user_information, device_information, network_segment,
    # geolocation_data, proxy_information, firewall_logs, idsips_alerts,
    # log_source

    print("Missing values before cleaning:")
    print(report_missing(df))

    df = remove_duplicates(df)

    if "timestamp" in df.columns:
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")

    categorical_cols = [c for c in [
        "protocol", "packet_type", "traffic_type", "attack_type",
        "attack_signature", "action_taken", "severity_level",
        "network_segment", "log_source",
    ] if c in df.columns]
    df = standardize_categorical(df, categorical_cols)
    df = fill_missing(df, {c: "Unknown" for c in categorical_cols})

    # Numeric network fields -- median fill so a handful of missing port/length
    # values don't distort the distribution the way a 0 or mean would with
    # this kind of skewed network data
    numeric_cols = [c for c in [
        "source_port", "destination_port", "packet_length", "anomaly_scores",
    ] if c in df.columns]
    df = fill_missing(df, {c: "median" for c in numeric_cols})

    # High-cardinality / free-text / log fields: fill blank rather than 'Unknown'
    # since these aren't categories to group by, just descriptive log content
    freetext_cols = [c for c in [
        "payload_data", "malware_indicators", "alertswarnings",
        "user_information", "device_information", "geolocation_data",
        "proxy_information", "firewall_logs", "idsips_alerts",
        "source_ip_address", "destination_ip_address",
    ] if c in df.columns]
    df = fill_missing(df, {c: "" for c in freetext_cols})

    print("\nMissing values after cleaning:")
    print(report_missing(df))

    return df


def main():
    df_raw = load_raw()
    df_clean = clean(df_raw)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "attack_signatures_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"\nSaved cleaned dataset -> {out_path} ({len(df_clean)} rows)")


if __name__ == "__main__":
    main()

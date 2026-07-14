"""
Data Integration pipeline for CyberVision.
Integrates the cleaned datasets (Global Cybersecurity Threats, CFR Incidents, Attack Signatures, etc.)
along temporal and spatial dimensions, calculating custom risk scores for countries and industries.

Usage:
    python -m src.preprocessing.integrate_data
"""

import pandas as pd
import numpy as np
from src.preprocessing.config import PROCESSED_DIR


def integrate_spatial() -> pd.DataFrame:
    """Aggregates threat data by country and computes custom risk scores."""
    threats_path = PROCESSED_DIR / "global_threats_clean.csv"
    if not threats_path.exists():
        print(f"[SKIP] {threats_path} not found. Clean global threats first.")
        return pd.DataFrame()

    df = pd.read_csv(threats_path)
    
    # Group by country
    spatial_df = df.groupby("country").agg(
        attack_count=("country", "count"),
        total_financial_loss=("financial_loss_in_million_", "sum"),
        avg_financial_loss=("financial_loss_in_million_", "mean"),
        avg_resolution_time=("incident_resolution_time_in_hours", "mean"),
        total_affected_users=("number_of_affected_users", "sum"),
    ).reset_index()

    # Normalize values for risk scoring
    def min_max_normalize(series: pd.Series) -> pd.Series:
        if series.max() == series.min():
            return pd.Series(0.0, index=series.index)
        return (series - series.min()) / (series.max() - series.min())

    norm_count = min_max_normalize(spatial_df["attack_count"])
    norm_loss = min_max_normalize(spatial_df["avg_financial_loss"])
    norm_time = min_max_normalize(spatial_df["avg_resolution_time"])

    # Risk score: weighted sum (0-100 scale)
    spatial_df["risk_score"] = (norm_count * 0.4 + norm_loss * 0.4 + norm_time * 0.2) * 100
    spatial_df["risk_score"] = spatial_df["risk_score"].round(1)

    # Round other floats
    spatial_df["total_financial_loss"] = spatial_df["total_financial_loss"].round(2)
    spatial_df["avg_financial_loss"] = spatial_df["avg_financial_loss"].round(2)
    spatial_df["avg_resolution_time"] = spatial_df["avg_resolution_time"].round(1)

    print(f"Spatial integration complete: {len(spatial_df)} countries mapped.")
    return spatial_df


def integrate_temporal() -> pd.DataFrame:
    """Aligns threats, CFR incidents, and vulnerabilities by year."""
    threats_path = PROCESSED_DIR / "global_threats_clean.csv"
    cfr_path = PROCESSED_DIR / "cfr_incidents_clean.csv"
    vuln_path = PROCESSED_DIR / "vulnerabilities_clean.csv"

    # Aggregated threat trends
    threat_summary = pd.DataFrame()
    if threats_path.exists():
        df_threats = pd.read_csv(threats_path)
        if "year" in df_threats.columns:
            threat_summary = df_threats.groupby("year").agg(
                global_incidents=("year", "count"),
                avg_financial_loss=("financial_loss_in_million_", "mean"),
                total_affected_users=("number_of_affected_users", "sum")
            ).reset_index()

    # Aggregated CFR incidents
    cfr_summary = pd.DataFrame()
    if cfr_path.exists():
        df_cfr = pd.read_csv(cfr_path)
        if "year" in df_cfr.columns:
            cfr_summary = df_cfr.groupby("year").agg(
                cfr_incidents=("year", "count")
            ).reset_index()

    # Aggregated Vulnerabilities
    vuln_summary = pd.DataFrame()
    if vuln_path.exists():
        df_vuln = pd.read_csv(vuln_path)
        if "year" in df_vuln.columns:
            vuln_summary = df_vuln.groupby("year").agg(
                vulnerabilities_disclosed=("year", "count")
            ).reset_index()

    # Merge all available summaries on year
    all_years = set()
    for summary in [threat_summary, cfr_summary, vuln_summary]:
        if not summary.empty and "year" in summary.columns:
            all_years.update(summary["year"].dropna().astype(int).unique())
            
    if not all_years:
        print("[SKIP] No datasets available for temporal integration.")
        return pd.DataFrame()
        
    temporal_df = pd.DataFrame({"year": sorted(list(all_years))})
    
    if not threat_summary.empty:
        temporal_df = pd.merge(temporal_df, threat_summary, on="year", how="left")
    if not cfr_summary.empty:
        temporal_df = pd.merge(temporal_df, cfr_summary, on="year", how="left")
    if not vuln_summary.empty:
        temporal_df = pd.merge(temporal_df, vuln_summary, on="year", how="left")

    # Clean temporal fields
    temporal_df = temporal_df.fillna(0)
    temporal_df["year"] = temporal_df["year"].astype(int)
    
    for col in ["cfr_incidents", "global_incidents", "total_affected_users", "vulnerabilities_disclosed"]:
        if col in temporal_df.columns:
            temporal_df[col] = temporal_df[col].astype(int)
            
    if "avg_financial_loss" in temporal_df.columns:
        temporal_df["avg_financial_loss"] = temporal_df["avg_financial_loss"].round(2)

    print(f"Temporal integration complete: {len(temporal_df)} years mapped.")
    return temporal_df


def main():
    spatial_df = integrate_spatial()
    temporal_df = integrate_temporal()

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    if not spatial_df.empty:
        spatial_path = PROCESSED_DIR / "integrated_spatial.csv"
        spatial_df.to_csv(spatial_path, index=False)
        print(f"Saved -> {spatial_path}")

    if not temporal_df.empty:
        temporal_path = PROCESSED_DIR / "integrated_temporal.csv"
        temporal_df.to_csv(temporal_path, index=False)
        print(f"Saved -> {temporal_path}")


if __name__ == "__main__":
    main()

"""
Calculates analytics, summaries, and KPIs for the dashboards.
Generates metrics for charts, cards, and tables.
"""

import pandas as pd
from typing import Dict, Any, List

def get_kpis(global_threats_df: pd.DataFrame, cfr_df: pd.DataFrame, vulnerabilities_df: pd.DataFrame) -> Dict[str, Any]:
    """Computes high-level KPI metrics for the Home/Dashboard views."""
    total_attacks = len(global_threats_df)
    
    if not global_threats_df.empty:
        total_loss = global_threats_df["financial_loss_in_million_"].sum()
        avg_loss = global_threats_df["financial_loss_in_million_"].mean()
        avg_resolution = global_threats_df["incident_resolution_time_in_hours"].mean()
        affected_users = global_threats_df["number_of_affected_users"].sum()
    else:
        total_loss = 0.0
        avg_loss = 0.0
        avg_resolution = 0.0
        affected_users = 0
        
    cfr_count = len(cfr_df)
    vuln_count = len(vulnerabilities_df)
    
    return {
        "total_attacks": total_attacks,
        "total_loss_million": total_loss,
        "avg_loss_million": avg_loss,
        "avg_resolution_hours": avg_resolution,
        "affected_users": affected_users,
        "cfr_incidents_count": cfr_count,
        "vulnerabilities_count": vuln_count,
    }

def get_yearly_trends(df: pd.DataFrame) -> pd.DataFrame:
    """Groups incidents by year and returns a dataframe of yearly trends."""
    if df.empty or "year" not in df.columns:
        return pd.DataFrame(columns=["year", "Count"])
    return df.groupby("year").size().reset_index(name="Count").sort_values("year")

def get_country_impacts(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes counts and average financial loss per country."""
    if df.empty or "standard_country" not in df.columns:
        return pd.DataFrame(columns=["standard_country", "Count", "avg_loss"])
    
    grouped = df.groupby("standard_country")
    counts = grouped.size().reset_index(name="Count")
    
    if "financial_loss_in_million_" in df.columns:
        losses = grouped["financial_loss_in_million_"].mean().reset_index(name="avg_loss")
        result = pd.merge(counts, losses, on="standard_country")
    else:
        result = counts
        result["avg_loss"] = 0.0
        
    return result.sort_values(by="Count", ascending=False)

def get_industry_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes incident counts, average loss, and average severity index per industry."""
    if df.empty or "target_industry" not in df.columns:
        return pd.DataFrame(columns=["target_industry", "Count", "total_loss", "avg_loss"])
        
    grouped = df.groupby("target_industry")
    counts = grouped.size().reset_index(name="Count")
    
    if "financial_loss_in_million_" in df.columns:
        total_losses = grouped["financial_loss_in_million_"].sum().reset_index(name="total_loss")
        avg_losses = grouped["financial_loss_in_million_"].mean().reset_index(name="avg_loss")
        result = pd.merge(counts, total_losses, on="target_industry")
        result = pd.merge(result, avg_losses, on="target_industry")
    else:
        result = counts
        result["total_loss"] = 0.0
        result["avg_loss"] = 0.0
        
    return result.sort_values(by="total_loss", ascending=False)

def get_attack_type_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Summarizes incident counts by attack type."""
    if df.empty or "standard_attack_type" not in df.columns:
        return pd.DataFrame(columns=["standard_attack_type", "Count"])
    return df.groupby("standard_attack_type").size().reset_index(name="Count").sort_values(by="Count", ascending=False)

def get_top_vulnerabilities(df: pd.DataFrame, limit: int = 10) -> pd.DataFrame:
    """Retrieves top vulnerabilities sorted by severity level."""
    if df.empty:
        return df
    
    # Custom sort order for severity
    severity_order = {"Critical": 0, "High": 1, "Medium": 2, "Low": 3, "Unrated": 4}
    res = df.copy()
    if "severity" in res.columns:
        res["severity_rank"] = res["severity"].map(severity_order).fillna(5)
        res = res.sort_values(by=["severity_rank", "year"], ascending=[True, False])
        res = res.drop(columns=["severity_rank"])
        
    return res.head(limit)

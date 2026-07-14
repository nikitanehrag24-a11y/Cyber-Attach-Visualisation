"""
Calculates customized risk scores (from 0.0 to 10.0) for countries and industries
based on incident density, financial loss, and resolution time.
"""

import pandas as pd
import numpy as np

def calculate_normalized_scores(
    df: pd.DataFrame,
    group_col: str,
    weight_count: float = 0.3,
    weight_loss: float = 0.4,
    weight_time: float = 0.3
) -> pd.DataFrame:
    """
    Computes a risk score from 0.0 to 10.0 for a grouped column (e.g., country or industry)
    using MinMax scaling on count, average loss, and average resolution time.
    """
    if df.empty or group_col not in df.columns:
        return pd.DataFrame(columns=[group_col, "incident_count", "avg_loss", "avg_resolution_time", "risk_score"])
        
    # Group by standard dimension
    grouped = df.groupby(group_col)
    
    # 1. Incident Count
    counts = grouped.size().reset_index(name="incident_count")
    
    # 2. Avg Financial Loss
    loss_col = "financial_loss_in_million_"
    if loss_col in df.columns:
        losses = grouped[loss_col].mean().reset_index(name="avg_loss")
    else:
        losses = pd.DataFrame({group_col: counts[group_col], "avg_loss": 0.0})
        
    # 3. Avg Resolution Time
    time_col = "incident_resolution_time_in_hours"
    if time_col in df.columns:
        times = grouped[time_col].mean().reset_index(name="avg_resolution_time")
    else:
        times = pd.DataFrame({group_col: counts[group_col], "avg_resolution_time": 0.0})
        
    # Merge aggregations
    metrics = pd.merge(counts, losses, on=group_col)
    metrics = pd.merge(metrics, times, on=group_col)
    
    # MinMax helper function
    def minmax_scale(series: pd.Series) -> pd.Series:
        min_val = series.min()
        max_val = series.max()
        if max_val == min_val:
            return pd.Series(0.5, index=series.index)
        return (series - min_val) / (max_val - min_val)
        
    # Normalize features between 0.0 and 1.0
    norm_count = minmax_scale(metrics["incident_count"])
    norm_loss = minmax_scale(metrics["avg_loss"])
    norm_time = minmax_scale(metrics["avg_resolution_time"])
    
    # Compute weighted score out of 10.0
    weighted_score = (
        weight_count * norm_count +
        weight_loss * norm_loss +
        weight_time * norm_time
    ) * 10.0
    
    metrics["risk_score"] = np.round(weighted_score, 2)
    return metrics.sort_values(by="risk_score", ascending=False)

def get_country_risk_scores(
    df: pd.DataFrame,
    w_count: float = 0.3,
    w_loss: float = 0.4,
    w_time: float = 0.3
) -> pd.DataFrame:
    """Calculates risk scores for each country."""
    return calculate_normalized_scores(df, "standard_country", w_count, w_loss, w_time)

def get_industry_risk_scores(
    df: pd.DataFrame,
    w_count: float = 0.3,
    w_loss: float = 0.4,
    w_time: float = 0.3
) -> pd.DataFrame:
    """Calculates risk scores for each industry."""
    return calculate_normalized_scores(df, "target_industry", w_count, w_loss, w_time)

"""
Applies dynamic filters (Country, Year Range, Attack Type, Industry, Severity, and Search Query)
to the standard datasets loaded into memory.
"""

import pandas as pd
from typing import List, Union, Tuple, Optional

def filter_global_threats(
    df: pd.DataFrame,
    countries: List[str],
    years: Tuple[int, int],
    attack_types: List[str],
    industries: List[str]
) -> pd.DataFrame:
    """Filters the Global Cybersecurity Threats dataset based on parameters."""
    if df.empty:
        return df
    
    res = df.copy()
    
    # Filter by Country
    if countries and "All" not in countries:
        res = res[res["standard_country"].isin(countries)]
        
    # Filter by Year Range
    if years:
        res = res[(res["year"] >= years[0]) & (res["year"] <= years[1])]
        
    # Filter by Attack Type
    if attack_types and "All" not in attack_types:
        res = res[res["standard_attack_type"].isin(attack_types)]
        
    # Filter by Industry
    if industries and "All" not in industries:
        if "target_industry" in res.columns:
            res = res[res["target_industry"].isin(industries)]
            
    return res

def filter_cfr_incidents(
    df: pd.DataFrame,
    countries: List[str],
    years: Tuple[int, int],
    attack_types: List[str],
    search_query: str = ""
) -> pd.DataFrame:
    """Filters the CFR incidents dataset based on parameters."""
    if df.empty:
        return df
    
    res = df.copy()
    
    # Filter by Country (Sponsor)
    if countries and "All" not in countries:
        res = res[res["standard_country"].isin(countries)]
        
    # Filter by Year Range
    if years:
        # Fill missing years to avoid dropping them incorrectly if they can't be parsed
        res = res[(res["year"] >= years[0]) & (res["year"] <= years[1])]
        
    # Filter by Attack Type
    if attack_types and "All" not in attack_types:
        res = res[res["standard_attack_type"].isin(attack_types)]
        
    # Search Query (Title/Description/Sponsor)
    if search_query:
        query = search_query.lower()
        title_mask = res["title"].str.lower().str.contains(query, na=False)
        desc_mask = res["description"].str.lower().str.contains(query, na=False)
        res = res[title_mask | desc_mask]
        
    return res

def filter_vulnerabilities(
    df: pd.DataFrame,
    years: Tuple[int, int],
    severities: List[str],
    search_query: str = ""
) -> pd.DataFrame:
    """Filters the Security Vulnerabilities dataset based on parameters."""
    if df.empty:
        return df
    
    res = df.copy()
    
    # Filter by Year Range
    if years and "year" in res.columns:
        res = res[(res["year"] >= years[0]) & (res["year"] <= years[1])]
        
    # Filter by Severity
    if severities and "All" not in severities:
        if "severity" in res.columns:
            res = res[res["severity"].isin(severities)]
            
    # Search Query (Title/Summary)
    if search_query:
        query = search_query.lower()
        title_mask = res["title"].str.lower().str.contains(query, na=False)
        sum_mask = res["summary"].str.lower().str.contains(query, na=False)
        res = res[title_mask | sum_mask]
        
    return res

def filter_attack_signatures(
    df: pd.DataFrame,
    countries: List[str],
    years: Tuple[int, int],
    attack_types: List[str],
    severities: List[str]
) -> pd.DataFrame:
    """Filters the network attack signatures dataset based on parameters."""
    if df.empty:
        return df
    
    res = df.copy()
    
    # Filter by Country
    if countries and "All" not in countries:
        res = res[res["standard_country"].isin(countries)]
        
    # Filter by Year Range
    if years and "year" in res.columns:
        res = res[(res["year"] >= years[0]) & (res["year"] <= years[1])]
        
    # Filter by Attack Type
    if attack_types and "All" not in attack_types:
        res = res[res["standard_attack_type"].isin(attack_types)]
        
    # Filter by Severity
    if severities and "All" not in severities:
        if "severity_level" in res.columns:
            res = res[res["severity_level"].isin(severities)]
            
    return res

def filter_malmem(df: pd.DataFrame, search_query: str = "") -> pd.DataFrame:
    """Filters the MalMem dataset based on search query (family or category)."""
    if df.empty:
        return df
    
    res = df.copy()
    
    if search_query:
        query = search_query.lower()
        cat_mask = res["category"].str.lower().str.contains(query, na=False)
        fam_mask = res["family"].str.lower().str.contains(query, na=False)
        res = res[cat_mask | fam_mask]
        
    return res

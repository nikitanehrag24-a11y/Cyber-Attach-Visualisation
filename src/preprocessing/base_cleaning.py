"""
Generic, dataset-agnostic cleaning utilities. Dataset-specific cleaning
scripts (clean_global_threats.py, clean_malmem.py, etc.) should import and
compose these rather than reimplementing cleaning logic each time.
"""

import pandas as pd


def standardize_column_names(df: pd.DataFrame) -> pd.DataFrame:
    """lowercase, strip whitespace, replace spaces with underscores."""
    df = df.copy()
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(r"\s+", "_", regex=True)
        .str.replace(r"[^\w]", "", regex=True)
    )
    return df


def report_missing(df: pd.DataFrame) -> pd.Series:
    """Returns count of missing values per column, descending. Use this
    BEFORE deciding how to handle missing values -- don't blindly dropna."""
    missing = df.isna().sum()
    return missing[missing > 0].sort_values(ascending=False)


def drop_high_missing_columns(df: pd.DataFrame, threshold: float = 0.5) -> pd.DataFrame:
    """Drops columns where more than `threshold` fraction of values are missing."""
    frac_missing = df.isna().mean()
    cols_to_drop = frac_missing[frac_missing > threshold].index.tolist()
    if cols_to_drop:
        print(f"Dropping columns with >{threshold*100:.0f}% missing: {cols_to_drop}")
    return df.drop(columns=cols_to_drop)


def fill_missing(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """
    strategy: dict mapping column_name -> 'mean' | 'median' | 'mode' | <literal value>
    Example: {"financial_loss": "median", "attack_source": "Unknown"}
    """
    df = df.copy()
    for col, method in strategy.items():
        if col not in df.columns:
            continue
        if method == "mean":
            df[col] = df[col].fillna(df[col].mean())
        elif method == "median":
            df[col] = df[col].fillna(df[col].median())
        elif method == "mode":
            df[col] = df[col].fillna(df[col].mode().iloc[0])
        else:
            df[col] = df[col].fillna(method)
    return df


def remove_duplicates(df: pd.DataFrame, subset: list = None) -> pd.DataFrame:
    before = len(df)
    df = df.drop_duplicates(subset=subset)
    after = len(df)
    if before != after:
        print(f"Removed {before - after} duplicate rows.")
    return df


def standardize_categorical(df: pd.DataFrame, columns: list) -> pd.DataFrame:
    """Trims whitespace and title-cases categorical text columns
    (e.g. 'usa ', 'USA', 'Usa' -> 'Usa') so groupby/plots don't fragment."""
    df = df.copy()
    for col in columns:
        if col in df.columns and df[col].dtype == object:
            df[col] = df[col].astype(str).str.strip().str.title()
    return df


def standardize_year_column(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Coerces a year column to nullable integer, dropping obviously invalid years."""
    df = df.copy()
    df[col] = pd.to_numeric(df[col], errors="coerce").astype("Int64")
    df = df[(df[col].isna()) | ((df[col] >= 1990) & (df[col] <= 2030))]
    return df


def flag_outliers_iqr(df: pd.DataFrame, col: str, factor: float = 1.5) -> pd.Series:
    """Returns a boolean mask of rows flagged as outliers via the IQR method.
    Use for review, not automatic deletion -- a $50M loss might be real, not junk."""
    q1, q3 = df[col].quantile([0.25, 0.75])
    iqr = q3 - q1
    lower, upper = q1 - factor * iqr, q3 + factor * iqr
    return (df[col] < lower) | (df[col] > upper)

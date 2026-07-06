"""
Cleaning pipeline for the Global Cybersecurity Threats (2015-2024) dataset.
This is the worked example -- copy this pattern for the other 4 datasets
(clean_cfr_incidents.py, clean_vulnerabilities.py, clean_attack_signatures.py,
clean_malmem.py).

Usage:
    python -m src.preprocessing.clean_global_threats
"""

import pandas as pd

from src.preprocessing.base_cleaning import (
    standardize_column_names,
    report_missing,
    fill_missing,
    remove_duplicates,
    standardize_categorical,
    standardize_year_column,
)
from src.preprocessing.config import DATASETS, RAW_DIR, PROCESSED_DIR


def load_raw() -> pd.DataFrame:
    raw_path = RAW_DIR / DATASETS["global_threats"]["raw_filename"]
    if not raw_path.exists():
        raise FileNotFoundError(
            f"{raw_path} not found. Run `python -m src.preprocessing.download_data` first."
        )
    return pd.read_csv(raw_path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_column_names(df)

    print("Missing values before cleaning:")
    print(report_missing(df))

    # NOTE: adjust these column names once you've confirmed the actual
    # header names after downloading (standardize_column_names will have
    # lowercased/underscored them, e.g. "Financial Loss (in Million $)"
    # -> "financial_loss_in_million"). Print df.columns after step 1 to check.

    df = remove_duplicates(df)

    if "year" in df.columns:
        df = standardize_year_column(df, "year")

    categorical_cols = [c for c in ["country", "attack_type", "target_industry",
                                     "attack_source", "vulnerability_type",
                                     "defense_mechanism_used"] if c in df.columns]
    df = standardize_categorical(df, categorical_cols)

    # Fill missing numeric fields with median, categorical with 'Unknown'
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    fill_strategy = {col: "median" for col in numeric_cols}
    fill_strategy.update({col: "Unknown" for col in categorical_cols})
    df = fill_missing(df, fill_strategy)

    print("\nMissing values after cleaning:")
    print(report_missing(df))

    return df


def main():
    df_raw = load_raw()
    df_clean = clean(df_raw)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "global_threats_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"\nSaved cleaned dataset -> {out_path} ({len(df_clean)} rows)")


if __name__ == "__main__":
    main()

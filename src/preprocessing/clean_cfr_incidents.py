"""
Cleaning pipeline for the Cyber Incidents 2005-2020 (Council on Foreign
Relations) dataset.

Usage:
    python -m src.preprocessing.clean_cfr_incidents
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
    raw_path = RAW_DIR / DATASETS["cfr_incidents"]["raw_filename"]
    if not raw_path.exists():
        raise FileNotFoundError(f"{raw_path} not found.")
    return pd.read_csv(raw_path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_column_names(df)
    # Expected columns after standardization:
    # title, date, affiliations, description, response, victims, sponsor,
    # type, category, sources_1, sources_2, sources_3

    print("Missing values before cleaning:")
    print(report_missing(df))

    df = remove_duplicates(df, subset=["title", "date"] if {"title", "date"}.issubset(df.columns) else None)

    # Parse date -> year (date formats in CFR-style datasets are often messy strings,
    # so errors="coerce" turns unparseable ones into NaT rather than crashing)
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year

    categorical_cols = [c for c in ["type", "category", "sponsor", "affiliations"] if c in df.columns]
    df = standardize_categorical(df, categorical_cols)

    # Text/categorical fields: fill missing with 'Unknown' rather than dropping rows --
    # an incident with an unknown sponsor is still a valid incident record.
    text_fill_cols = [c for c in ["sponsor", "affiliations", "type", "category",
                                   "response", "victims", "description"] if c in df.columns]
    df = fill_missing(df, {c: "Unknown" for c in text_fill_cols})

    # Source columns are reference links, not analytical fields -- keep as-is,
    # just fill blanks so downstream code doesn't choke on NaN
    source_cols = [c for c in ["sources_1", "sources_2", "sources_3"] if c in df.columns]
    df = fill_missing(df, {c: "" for c in source_cols})

    print("\nMissing values after cleaning:")
    print(report_missing(df))

    return df


def main():
    df_raw = load_raw()
    df_clean = clean(df_raw)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "cfr_incidents_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"\nSaved cleaned dataset -> {out_path} ({len(df_clean)} rows)")


if __name__ == "__main__":
    main()

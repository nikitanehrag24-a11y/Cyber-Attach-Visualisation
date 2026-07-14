"""
Cleaning pipeline for the Security Vulnerabilities Dataset.

Usage:
    python -m src.preprocessing.clean_vulnerabilities
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
    raw_path = RAW_DIR / DATASETS["vulnerabilities"]["raw_filename"]
    if not raw_path.exists():
        raise FileNotFoundError(f"{raw_path} not found.")
    return pd.read_csv(raw_path)


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_column_names(df)
    # Expected columns after standardization: title, date, severity, summary, link

    print("Missing values before cleaning:")
    print(report_missing(df))

    df = remove_duplicates(df, subset=["title"] if "title" in df.columns else None)

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df["year"] = df["date"].dt.year

    if "severity" in df.columns:
        df = standardize_categorical(df, ["severity"])
        # severity is core to the "Vulnerability Explorer" viz (severity/exploit trends),
        # so missing severity gets its own explicit bucket rather than being dropped or
        # silently merged into "Unknown" alongside genuinely-unknown-cause records
        df = fill_missing(df, {"severity": "Unrated"})

    text_fill_cols = [c for c in ["summary", "link"] if c in df.columns]
    df = fill_missing(df, {c: "" for c in text_fill_cols})

    print("\nMissing values after cleaning:")
    print(report_missing(df))

    return df


def main():
    df_raw = load_raw()
    df_clean = clean(df_raw)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "vulnerabilities_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"\nSaved cleaned dataset -> {out_path} ({len(df_clean)} rows)")


if __name__ == "__main__":
    main()

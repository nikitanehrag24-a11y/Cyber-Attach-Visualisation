"""
Cleaning pipeline for the CIC-MalMem-2022 malware memory dataset.

NOTE: this script auto-detects the label column and its structure since we
haven't confirmed the exact schema of your downloaded file yet. Run this,
check the printed label breakdown near the top of the output, and tell
Claude what it prints if anything looks off (e.g. if it's binary-only
Benign/Malicious rather than family-level Spyware/Ransomware/Trojan/Benign).

Usage:
    python -m src.preprocessing.clean_malmem
"""

import pandas as pd

from src.preprocessing.base_cleaning import (
    standardize_column_names,
    report_missing,
    remove_duplicates,
)
from src.preprocessing.config import DATASETS, RAW_DIR, PROCESSED_DIR


def load_raw() -> pd.DataFrame:
    raw_path = RAW_DIR / DATASETS["malmem_2022"]["raw_filename"]
    if not raw_path.exists():
        raise FileNotFoundError(
            f"{raw_path} not found. Download manually from "
            f"{DATASETS['malmem_2022']['manual_url']}"
        )
    return pd.read_csv(raw_path)


def find_label_column(df: pd.DataFrame) -> str | None:
    """Looks for the most likely label/category column by name."""
    candidates = ["category", "class", "label", "filename"]
    for col in candidates:
        if col in df.columns:
            return col
    return None


def clean(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_column_names(df)

    print("Missing values before cleaning:")
    print(report_missing(df))

    df = remove_duplicates(df)

    label_col = find_label_column(df)
    if label_col is None:
        print("\nWARNING: no obvious label column found (checked category/class/"
              "label/filename). Print df.columns and tell Claude what you see.")
        print(df.columns.tolist())
        return df

    print(f"\nUsing '{label_col}' as the label column. Unique values (first 20):")
    print(df[label_col].unique()[:20])

    # If the label is composite like "Spyware-TIBS-<hash>-6.raw", split out the
    # top-level category (Benign/Spyware/Ransomware/Trojan) and the specific
    # family (TIBS, Zeus, etc.) as separate columns -- this is the feature
    # engineering the proposal's section 4.5 (Malware Family Analytics) needs.
    df["category"] = df[label_col].astype(str)
    df["family"] = "Benign"
    is_composite = df[label_col].astype(str).str.contains("-")
    if is_composite.any():
        split_cols = df.loc[is_composite, label_col].astype(str).str.split("-", expand=True)
        df.loc[is_composite, "category"] = split_cols[0]
        if split_cols.shape[1] > 1:
            df.loc[is_composite, "family"] = split_cols[1]

    df["category"] = df["category"].astype(str).str.strip().str.title()
    if "family" in df.columns:
        df["family"] = df["family"].astype(str).str.strip().str.title()

    print("\nFinal category breakdown:")
    print(df["category"].value_counts())
    if "family" in df.columns:
        print("\nFinal family breakdown (top 20):")
        print(df["family"].value_counts().head(20))

    print("\nMissing values after cleaning:")
    print(report_missing(df))

    return df


def main():
    df_raw = load_raw()
    df_clean = clean(df_raw)

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    out_path = PROCESSED_DIR / "malmem_clean.csv"
    df_clean.to_csv(out_path, index=False)
    print(f"\nSaved cleaned dataset -> {out_path} ({len(df_clean)} rows)")


if __name__ == "__main__":
    main()

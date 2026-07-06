"""
Pulls all Kaggle-hosted datasets into data/raw/ using the Kaggle CLI.
Run once after cloning the repo (requires ~/.kaggle/kaggle.json to be set up
- see docs/data_setup.md for the one-time credential steps).

Usage:
    python -m src.preprocessing.download_data
"""

import subprocess
import zipfile
from pathlib import Path

from src.preprocessing.config import DATASETS, RAW_DIR


def download_kaggle_dataset(slug: str, dest_dir: Path):
    """Downloads and unzips a Kaggle dataset into dest_dir."""
    dest_dir.mkdir(parents=True, exist_ok=True)
    print(f"Downloading {slug} ...")
    subprocess.run(
        ["kaggle", "datasets", "download", "-d", slug, "-p", str(dest_dir)],
        check=True,
    )
    # unzip whatever landed here
    for zip_path in dest_dir.glob("*.zip"):
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(dest_dir)
        zip_path.unlink()  # remove the zip once extracted
    print(f"Done: {slug}\n")


def main():
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for key, meta in DATASETS.items():
        if meta["source"] != "kaggle":
            print(f"[SKIP] {key}: not a Kaggle dataset. {meta.get('manual_url', '')}")
            continue
        if not meta["kaggle_slug"]:
            print(f"[SKIP] {key}: no kaggle_slug set yet in config.py — add it first.")
            continue
        download_kaggle_dataset(meta["kaggle_slug"], RAW_DIR)


if __name__ == "__main__":
    main()

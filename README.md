# CyberVision — Group 14

Interactive web-based data visualization and analytics platform integrating
global cyber-incident, vulnerability, and malware datasets.

## Team

| Domain | Members |
|---|---|
| Data Processing, Cleaning & Preprocessing | Pranjali Deshpande (240336), Khushi Sharma (240544) |
| Data Integration & Exploratory Analytics | Mayank Pattnaik (230641), Vishesh Thepadia (231165) |
| Geospatial & Network Visualization | Namrata Chavhan (240301), Vivekananda Kumbhar (241188) |
| Frontend Layout & Framework | Nikita Nehra (240698) |
| Backend Logic Integration | Haryashva Gupta (240445) |

## Project structure

```
cybervision/
├── data/
│   ├── raw/          # original downloaded files, never edited (gitignored)
│   ├── interim/       # partially-cleaned checkpoints (gitignored)
│   └── processed/     # final clean datasets used by EDA/dashboards (gitignored)
├── src/
│   ├── preprocessing/  # cleaning, merging, feature engineering
│   ├── visualization/  # chart-building helper functions
│   └── utils/          # shared helpers
├── notebooks/          # exploratory Jupyter notebooks
├── dashboards/         # Streamlit app
├── tests/
└── docs/
```

Note: raw/interim/processed data folders are gitignored (too large + reproducible
from source). Anyone cloning the repo needs to run the download step below.

## Setup

```bash
git clone <repo-url>
cd cybervision
python3 -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Data setup

1. Set up Kaggle API credentials — see `docs/data_setup.md`.
2. Fill in the missing `kaggle_slug` values in `src/preprocessing/config.py`
   (3 of 5 datasets still need their exact Kaggle slugs confirmed).
3. Download all Kaggle-hosted datasets:
   ```bash
   python -m src.preprocessing.download_data
   ```
4. Manually download CIC-MalMem-2022 from
   https://www.unb.ca/cic/datasets/malmem-2022.html and place it at
   `data/raw/cic_malmem_2022.csv`.

## Running the cleaning pipeline

```bash
python -m src.preprocessing.clean_global_threats
```

This is the worked example. Copy the same pattern for the other 4 datasets
(clean_cfr_incidents.py, clean_vulnerabilities.py, clean_attack_signatures.py,
clean_malmem.py), all living in `src/preprocessing/`.

## Git workflow

- `main` — stable, always runnable
- `dev` — integration branch
- feature branches: `feature/<your-name>-<short-description>`, e.g.
  `feature/pranjali-clean-global-threats`

```bash
git checkout -b feature/pranjali-clean-global-threats
# ... work, commit ...
git push origin feature/pranjali-clean-global-threats
# open a PR into dev
```

Commit message convention: `[preprocessing] short description`,
`[eda] short description`, `[viz] short description`, etc. — makes it easy
to scan `git log` by domain later.

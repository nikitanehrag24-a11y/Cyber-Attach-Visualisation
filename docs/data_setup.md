# Data setup (one-time, per team member)

## 1. Kaggle API credentials

1. Log in to kaggle.com -> click your profile picture -> **Settings**.
2. Scroll to **API** -> click **Create New Token**. This downloads `kaggle.json`.
3. Move it to the right location:
   ```bash
   mkdir -p ~/.kaggle
   mv ~/Downloads/kaggle.json ~/.kaggle/
   chmod 600 ~/.kaggle/kaggle.json
   ```
   Windows (PowerShell):
   ```powershell
   mkdir $env:USERPROFILE\.kaggle
   move $env:USERPROFILE\Downloads\kaggle.json $env:USERPROFILE\.kaggle\
   ```
4. Test it:
   ```bash
   kaggle datasets list -s cybersecurity
   ```
   If this prints a list of datasets, you're set up correctly.

**Never commit `kaggle.json` to git** — it's already covered by `.gitignore`.

## 2. Confirming the remaining dataset slugs

Only `global_threats` has a confirmed Kaggle slug in `config.py` right now.
For the other 3 Kaggle datasets, search kaggle.com for the exact name from
the proposal ("Cyber Incidents 2005-2020", "Security Vulnerabilities Dataset",
"Cyber Security Attacks"), open the dataset page, and copy the slug from the
URL: `kaggle.com/datasets/<owner>/<dataset-name>` -> slug is `<owner>/<dataset-name>`.

Paste each into `src/preprocessing/config.py`.

## 3. CIC-MalMem-2022 (manual download)

This one isn't on Kaggle — it's hosted directly by the University of New
Brunswick's Canadian Institute for Cybersecurity:
https://www.unb.ca/cic/datasets/malmem-2022.html

Download the CSV and place it at `data/raw/cic_malmem_2022.csv`.

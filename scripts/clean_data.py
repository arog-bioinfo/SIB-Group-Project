import pandas as pd
from pathlib import Path

def clean_tsv_to_csv(tsv_path, csv_path):
    df = pd.read_csv(tsv_path, sep="\t")
    # Standardize column names
    df.columns = (
        df.columns.str.strip()
        .str.lower()
        .str.replace(" ", "_")
    )
    # Drop rows without collection date
    df = df.dropna(subset=["isolate_collection_date"])
    df.to_csv(csv_path, index=False)

base = Path("data")

variants = {
    "b1": "b1_meta",
    "xbb15": "xbb15_meta",
    "beta": "beta_meta",
    "delta": "delta_meta",
    "omicron_ba1": "omicron_meta",
    "ba2": "ba2_meta",
}

for v, stem in variants.items():
    tsv = base / v / f"{stem}.tsv"
    csv = base / v / f"{stem}_clean.csv"
    clean_tsv_to_csv(tsv, csv)

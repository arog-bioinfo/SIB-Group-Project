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

clean_tsv_to_csv(base / "delta"   / "delta_meta.tsv",
                 base / "delta"   / "delta_meta_clean.csv")
clean_tsv_to_csv(base / "omicron" / "omicron_meta.tsv",
                 base / "omicron" / "omicron_meta_clean.csv")

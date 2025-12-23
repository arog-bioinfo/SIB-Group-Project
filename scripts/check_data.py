import pandas as pd
from pathlib import Path

base = Path("data")

# Map variant folder → clean metadata file stem
variants = {
    "b1": "b1_meta_clean",
    "alpha": "alpha_meta_clean",
    "beta": "beta_meta_clean",
    "delta": "delta_meta_clean",
    "omicron_ba1": "omicron_meta_clean",
    "ba2": "ba2_meta_clean",
}

# 1) Load and basic checks
dfs = {}
for v, stem in variants.items():
    df = pd.read_csv(base / v / f"{stem}.csv")
    dfs[v] = df
    print(f"{v} rows:", len(df))

for v, df in dfs.items():
    print(f"\n{v} collection date range:")
    print("  min:", df["isolate_collection_date"].min())
    print("  max:", df["isolate_collection_date"].max())
    print(f"{v} example locations:",
          df["geographic_location"].dropna().unique()[:5])
    

# 2) Check accessions vs FASTA

def load_fasta_accessions(fasta_path, n=None):
    accs = set()
    with open(fasta_path) as fh:
        for line in fh:
            if line.startswith(">"):
                header = line[1:].strip()
                first_token = header.split()[0]
                accs.add(first_token)
            if n is not None and len(accs) >= n:
                break
    return accs

for v in variants.keys():
    fasta_path = base / v / "ncbi_dataset" / "data" / "genomic.fna"
    fasta_accs = load_fasta_accessions(fasta_path, n=10000)
    df = dfs[v]
    some_acc = df["accession"].iloc[0]
    print(f"\n{v} example accession from metadata: {some_acc}")
    print("In FASTA?", some_acc in fasta_accs)

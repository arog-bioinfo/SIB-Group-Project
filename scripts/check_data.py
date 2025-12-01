import pandas as pd
from pathlib import Path

base = Path("data")

delta = pd.read_csv(base / "delta" / "delta_meta_clean.csv")
omicron = pd.read_csv(base / "omicron" / "omicron_meta_clean.csv")

print("Delta rows:", len(delta))
print("Omicron rows:", len(omicron))

for df, name in [(delta, "Delta"), (omicron, "Omicron")]:
    print(f"\n{name} collection date range:")
    print("  min:", df["isolate_collection_date"].min())
    print("  max:", df["isolate_collection_date"].max())
    print(f"{name} example locations:", df["geographic_location"].dropna().unique()[:5])




#check acessions and FASTA mapping

def load_fasta_accessions(fasta_path, n=None):
    accs = set()
    with open(fasta_path) as fh:
        for line in fh:
            if line.startswith(">"):
                header = line[1:].strip()
                first_token = header.split()[0]  # e.g. "PQ169688.1"
                accs.add(first_token)
            if n is not None and len(accs) >= n:
                break
    return accs

delta_accs_fasta = load_fasta_accessions(
    base / "delta" / "ncbi_dataset" / "data" / "genomic.fna", n=10000
)
omicron_accs_fasta = load_fasta_accessions(
    base / "omicron" / "ncbi_dataset" / "data" / "genomic.fna", n=10000
)

for df, fasta_accs, name in [
    (delta, delta_accs_fasta, "Delta"),
    (omicron, omicron_accs_fasta, "Omicron"),
]:
    some_acc = df["accession"].iloc[0]
    print(f"\n{name} example accession from metadata: {some_acc}")
    print("In FASTA?", some_acc in fasta_accs)

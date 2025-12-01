from pathlib import Path
import pandas as pd

ext = Path("external") / "SARS2-spike-predictor-phenos" / "results"

clade_pheno = pd.read_csv(ext / "clade_phenotypes.csv")
mut_pheno   = pd.read_csv(ext / "mutation_phenotypes.csv")



print("Clade phenotypes columns:", clade_pheno.columns[:10].tolist())
print("Mutation phenotypes columns:", mut_pheno.columns[:10].tolist())
print("Clade rows:", len(clade_pheno), "Mutation rows:", len(mut_pheno))


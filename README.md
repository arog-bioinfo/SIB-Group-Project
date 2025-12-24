# SIB Group Project: Molecular Fitness Prediction & Population Simulation of Viral Variants

## Overview
This project aims to predict the molecular fitness of viral variants and simulate population-level spread using machine learning and agent-based modeling. The project is divided into two modules:
1. **Molecular Fitness Prediction:** Use genomic and drug interaction data to predict viral fitness.
2. **Population Simulation:** Integrate fitness scores into an agent-based model to simulate interventions.

## Objectives
- Develop ML models for viral fitness prediction.
- Simulate population-level spread and test public health interventions.
- Innovate with advanced techniques (e.g., Transformers, Topological Data Analysis).

## Team Members
- [Artur Gomes (AROG)](https://github.com/arog-bioinfo)
- [Bárbara Freitas](https://github.com/barbarafreitas22)
- [Catarina Gomes](https://github.com/cgomes03)
- [André Dias](https://github.com/Diasf333)
- [Maria Portela](https://github.com/mariaportela4)

## Folder Structure
```bash
project-root/
│
├── /data/
│   ├── processed/     # Cleaned/integrated data
│   └──raw/           # Original datasets
│
├── /docs/
│   ├── articles/      # Research articles
│   ├── guideline.pdf  # Work Guidelines
│   ├── sota.pdf       # State of the Art review
│   └── notebook.pdf   # Final Notebook
│
└── /scripts/
    ├── module1/       # Molecular fitness prediction
    └── module2/       # Population simulation
```

## Key Python Packages

| Package       | Purpose                   |
|---------------|---------------------------|
| numpy         | Numerical operations      |
| pandas        | Data manipulation         |
| scikit-learn  | Machine learning          |
| matplotlib    | Plotting                  |
| seaborn       | Visualizations            |
| biopython     | Genomic data processing   |
| rdkit         | Cheminformatics           |
| torch         | Deep learning             |
| transformers  | Sequence modeling         |
| mesa          | Agent-based simulation    |
| networkx      | Network analysis          |
| scipy         | Scientific computing      |
| tqdm          | Progress bars             |

## Setup

### Clone the repository

```bash
git clone [repo-url]
cd [repo-folder]
```
### Prepare Environment

```bash
# Create the environment with environment.yml
conda env create -f environment.yml

# Activate it
conda activate sib_viralmodel
```



### Automatic download of NCBI Virus data

The script `scripts/make_data.sh` uses the NCBI Datasets CLI to download SARS-CoV-2 genomes (Delta and Omicron) and their metadata from NCBI Virus.

```bash
./scripts/make_data.sh
```


The downloaded `.zip` files are stored in `data/raw/` with the following names:

- `b1.zip`
- `xbb15.zip`
- `beta.zip`
- `delta.zip`
- `omicron_ba1.zip`
- `ba2.zip`


```bash
unzip data/raw/delta.zip -d data/delta
ls data/delta/ncbi_dataset/data
```



## Extract and clean metadata

To extract the metadata tables from the NCBI packages and convert them into clean CSV files used in our analyses:

```bash
./scripts/extract_metadata.sh
python scripts/clean_data.py
```


These scripts:

- unzip the NCBI data packages in `data/raw/` into variant-specific folders (e.g. `data/b1/`, `data/beta/`, `data/delta/`, `data/omicron_ba1/`, `data/ba2/`, `data/xbb15/`);
- use `dataformat tsv virus-genome` to create metadata tables (`*_meta.tsv`) for each variant with accession, virus name, geographic location, and collection date;
- convert and clean them into `*_meta_clean.csv` (standardized column names, removal of entries without collection date).

The final files used for the molecular model (Module 1) are, for each variant:

- `data/<variant>/ncbi_dataset/data/genomic.fna` :  full genome sequences
- `data/<variant>/<variant>_meta_clean.csv` : cleaned metadata aligned to those sequences

Each row in the metadata files corresponds to a genome in the FASTA file, linked by the `accession` identifier.

### External spike phenotype data (Bloom lab)

We include the Bloom lab repository `SARS2-spike-predictor-phenos` as a git submodule under `external/SARS2-spike-predictor-phenos`.

To fetch it:

```bash
git submodule update --init --recursive
```

Once the submodule is fetched, we can access the pre-computed phenotype tables:

- `external/SARS2-spike-predictor-phenos/results/clade_phenotypes.csv`
- `external/SARS2-spike-predictor-phenos/results/mutation_phenotypes.csv`


We use these external tables to:
- obtain clade-level spike phenotypes and growth rates for SARS-CoV-2 variants;
- obtain mutation-level spike phenotypes (e.g., ACE2 binding, antibody escape) that can be linked to mutations observed in our NCBI sequences.

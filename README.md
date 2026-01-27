# SIB Group Project: Molecular Fitness Prediction & Population Simulation of Viral Variants

## TL;DR
We build a multi-scale pipeline that:
1. Predicts SARS-CoV-2 molecular fitness from spike protein sequences using protein language models (ESM-2).
2. Injects these fitness estimates into an agent-based epidemiological model to simulate population-level spread under different public health interventions.

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
├── data/
│   ├── raw/                     # Original NCBI datasets (ZIP) and intermediate unpacked folders
│   └── processed/               # Integrated and cleaned data used by notebooks
│       ├── final_dataset.csv
│       ├── ml_splits_scaled.pkl
│       ├── ncbi_genomes.csv
│       └── spike_mutations_predictor.pkl
│
├── docs/
│   ├── articles/
│   │   ├── module1/             # Papers for molecular fitness modeling
│   │   └── module2/             # Papers for ABMs and epidemiological simulation
│   ├── sota/LaTeX_files/        # State-of-the-art write-up (LaTeX + references)
│   ├── guideline.pdf            # Course project guidelines
│   └── notebook.pdf             # Final compiled notebook / report (if exported)
│
├── external/
│   └── SARS2-spike-predictor-phenos/   # Bloom lab submodule with spike phenotypes
│
├── notebooks/
│   ├── 01_GenData_preparation.ipynb    # Data download + integration (Module 1)
│   ├── 01_data_epi_exploration.ipynb   # Early EDA on epi data (optional)
│   ├── 02_Genomic_EDA.ipynb            # Genomic + phenotype EDA (Module 1)
│   ├── 03_ML_FeatureEng.ipynb          # Baseline ML on tabular features
│   ├── 05_ESM2_Embeddings.ipynb        # ESM-2 embeddings + XGBoost
│   └── 02_module.ipynb                 # ABM simulations (Module 2)
│
├── results/
│   ├── figures/
│   │   ├── 01_target_distribution.png
│   │   ├── 01_sequences_per_variant.png
│   │   ├── 02_variant_timeline.png
│   │   ├── 03_fitness_distribution.png
│   │   └── 04_data_summary_table.png
│   └── data_summary.csv
│
├── scripts/
│   ├── agents.py                       # Agent states and local infection logic
│   ├── model.py                        # Core ABM and policy variants
│   ├── borderedspace.py                # Continuous space with country borders
│   ├── 04_Extract_Spike_Sequences.py   # Extract & align spike sequences
│   ├── check_data.py                   # Data sanity checks
│   ├── clean_data.py                   # Cleaning metadata tables
│   ├── load_external_phenos.py         # Integrate Bloom lab phenotypes
│   ├── extract_metadata.sh             # Metadata extraction from NCBI packages
│   └── make_data.sh                    # Automated NCBI download pipeline
│
├── environment.yml
├── LICENSE
└── README.md
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

# Module 1 – Molecular Fitness Prediction (SARS-CoV-2)

## Data Preparation – `01_GenData_preparation.ipynb`

This notebook builds the core genomic–phenotype dataset used downstream:

- Loads **271,386 SARS-CoV-2 sequences** from **7 variants** from NCBI.
- Integrates experimental fitness measurements from the **Bloom Lab dataset** (phenotype).
- Extracts temporal features:
  - year  
  - month  
  - days since the beginning of the pandemic
- Applies **stratified downsampling** to obtain **500 sequences per variant** (**3,500 total**).
- Produces `final_dataset.csv`, the main tabular input for later notebooks.

**Output:** `final_dataset.csv`  
- **3,500 sequences** (500 per variant)

**Columns:**
- `accession` – NCBI accession ID  
- `location` – sampling location  
- `date` – collection date  
- `variant` – SARS-CoV-2 variant label  
- `phenotype` – experimental fitness / phenotype score  
- `spike_mutations` – spike mutations relative to Wuhan-Hu-1  

---

## Exploratory Data Analysis – `02_Genomic_EDA.ipynb`

This notebook validates and explores the curated dataset:

- Checks data quality:
  - missing values  
  - duplicates  
  - consistency of key columns
- Explores temporal, geographical, and variant-wise distributions.
- Computes correlations between mutations and fitness, focusing on spike-related changes.

**Conclusion:**  
Models trained directly on tabular temporal/categorical features tend to learn time trends rather than genuine sequence biology, revealing **temporal leakage** and motivating **sequence-based representations**.

---

## Spike Extraction – `04_Extract_Spike_Sequences.py`

Due to the need for explicit amino acid-level modeling, this script:

- Extracts **Spike gene sequences** from raw NCBI genome ZIP files.
- Translates DNA to protein for each genome (**1,273 amino acids per spike sequence**).
- Aligns spike sequences with `final_dataset.csv` via the `accession` field.

**Output:** `final_dataset_with_spike.csv`  
- Extends `final_dataset.csv` with a column containing **full spike protein sequences** for each accession.

---

## Baseline ML on Tabular Features – `03_ML_FeatureEng.ipynb`

This notebook evaluates whether simple tabular features are sufficient to predict phenotype:

- Uses `final_dataset_with_spike.csv` as input (tabular features only).
- Implements a **temporal train/test split** (80/20) to respect time ordering.
- Normalizes numerical features and encodes categorical variables.
- Trains baseline models:
  - XGBoost  
  - Random Forest  
  - Ridge Regression  

**Conclusion:**  
Models primarily exploit temporal drift rather than biological content, confirming leakage and motivating **protein language model (PLM) embeddings**.

---

## ESM-2 Embeddings & Enriched ML – `05_ESM2_Embeddings.ipynb`

To capture biologically meaningful sequence patterns, this notebook:

- Reads `final_dataset_with_spike.csv`.
- Applies **ESM-2 (Protein Language Model)** to each spike sequence, producing **1,280-dimensional embeddings** per sequence.
- Applies **PCA** to reduce embedding dimensionality while retaining most variance.
- Combines reduced embeddings with categorical metadata (e.g., variant, location).
- Trains **XGBoost** on these enriched representations to predict phenotype.

This stage implements the **advanced sequence modeling component** required in the project (PLM-based deep representation learning).

# Module 2 – Agent-Based Epidemiological Simulation

## Overview – `02_module.ipynb`

This notebook implements **Module 2**, a multi-scale **agent-based model (ABM)** in Python using **Mesa**, where macro-level policy/control parameters modulate infection dynamics among moving agents in continuous space.

### Core objectives

- Represent individual agents that move in continuous 2D space.
- Simulate infection, recovery, and resistance dynamics.
- Integrate a macro-level intervention index (or explicit measures) that controls virus transmission probability.
- Compare public health scenarios (e.g., baseline vs masks vs confinement vs vaccination).

Although the notebooks can conceptually take **Module 1 fitness outputs** as inputs (governing transmissibility or disease duration), the code is structured so that this coupling can be done via `base_virus_spread_chance` or measure parameters.

---

## Agents – `abm/agents.py`

Defines the agent state machine and per-step behavior.

### Agent states

- `Enum State` with:
  - `SUSCEPTIBLE`
  - `INFECTED`
  - `RESISTANT`

### `VirusAgentContinuous` (Mesa Agent)

- Holds agent state and 2D position `pos`.

**Methods:**

- `move()`  
  Random movement in continuous space, scaled by `model.movement_speed`.

- `try_to_infect_nearby()`  
  For `INFECTED` agents:
  - Finds neighbors within `model.infection_radius`.
  - Infects susceptible neighbors with probability `model.virus_spread_chance`.
  - If the space is a `BorderedContinuousSpace`, infections can be restricted to same-country neighbors.

- `try_gain_resistance()`  
  With probability `model.gain_resistance_chance`, transitions to `RESISTANT`.

- `try_remove_infection()`  
  Infected agents recover with probability `model.recovery_chance`; upon recovery, they may become `RESISTANT`.

- `step()`  
  Executes:
  1. Movement  
  2. Infection attempt (if infected)  
  3. Recovery / resistance checks  

---

## Model & Policy Logic – `abm/model.py`

Implements the base ABM and two policy variants.

### Common helpers

- `number_infected`
- `number_susceptible`
- `number_resistant`
- `resistant_susceptible_ratio()` – summarizes acquired resistance relative to susceptibles.

---

## Base Model – `VirusModelContinuousBase`

### Core ABM parameters

**Population**
- `N` agents on a continuous grid of size `width × height`.

**Infection dynamics**
- `base_virus_spread_chance` – baseline transmissibility.
- `infection_radius` – distance threshold for transmission.
- `virus_check_frequency` – probability of evaluating recovery per step.
- `recovery_chance` – chance to leave `INFECTED` state given a check.
- `gain_resistance_chance` – chance to become `RESISTANT` upon recovery.

**Movement**
- `movement_speed` – step size in random walk.

**Space options**
- Standard Mesa `ContinuousSpace` (possibly toroidal).
- Custom `BorderedContinuousSpace` with explicit country regions, border blocking, and probabilistic border crossing.

### Model behavior

- Instantiates `N` susceptible agents and places them in space.
- Randomly seeds an initial outbreak (`initial_outbreak_size` agents infected).
- Uses a `DataCollector` to track:
  - Infected  
  - Susceptible  
  - Resistant  
  - R / S ratio over time
- Delegates policy-specific configuration to `_configure_measures_impact()` (abstract).

---

## Measures Index Model – `VirusModelContinuousMeasuresIndex`

Implements a scalar policy index:

\[
m \in [0, 1]
\]

- `measures_index` is validated in `[0, 1]`.

### Configuration

- `virus_spread_chance = base_virus_spread_chance * (1 - measures_index)`

### Interpretation

- `measures_index = 0` → no measures, full transmissibility.
- `measures_index = 1` → maximal measures, zero transmission under this mapping.

This model is ideal for directly plugging in **Module 1 fitness estimates** or scenario-dependent control values to modulate effective transmissibility.

---

## Specific Measures Model – `VirusModelContinuousSpecificMeasures`

Implements explicit policy switches.

### Inputs (booleans)

- `masks`
- `confinement`
- `vaccination`

### Policy mapping (`_configure_measures_impact()`)

- **Masks**
  - `virus_spread_chance = base_virus_spread_chance * 0.25`
  - Strong reduction in transmissibility.

- **Confinement**
  - `movement_speed -= 0.3`
  - Reduced mobility and fewer contacts.

- **Vaccination**
  - `gain_resistance_chance += 0.3`
  - Higher chance of developing resistance after infection.

These settings enable scenario comparisons such as:
- baseline  
- masks-only  
- confinement-only  
- combined interventions  

---

## Geography & Borders – `abm/borderedspace.py`

`BorderedContinuousSpace` extends Mesa `ContinuousSpace` with spatial structure:

- Named rectangular regions (e.g., countries), each defined by:
  - `name`
  - `x_min`, `x_max`
  - `y_min`, `y_max`
- Optional blocking of out-of-bounds moves (`block_out_of_bounds`).
- Optional blocking or probabilistic cross-border movement:
  - `block_cross_border`
  - `border_cross_prob`
- Ability to query neighbors within a radius but restrict to same region:
  - `same_country_only=True`

This enables simulation of **spatially structured populations** with heterogeneous connectivity and mobility between regions.


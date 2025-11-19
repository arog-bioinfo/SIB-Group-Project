# SIB Group Project: Molecular Fitness Prediction & Population Simulation for Influenza H5N1

## Overview
This project aims to predict the molecular fitness of Influenza H5N1 variants and simulate population-level spread using machine learning and agent-based modeling. The project is divided into two modules:
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
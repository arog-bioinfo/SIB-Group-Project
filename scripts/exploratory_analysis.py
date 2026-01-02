#!/usr/bin/env python3
"""
Exploratory Data Analysis Pipeline - Molecular Data
Module 1: Viral Fitness Prediction

Usage:
    python scripts/exploratory_analysis.py
    
Output:
    results/figures/
    ├── 01_sequences_per_variant.png
    ├── 02_variant_timeline.png
    ├── 03_fitness_distribution.png
    ├── 04_data_summary_table.png
    └── data_summary.csv

Description:
    This script loads SARS-CoV-2 genomic sequences and phenotype data,
    performs exploratory data analysis, and generates publication-quality
    visualizations for the Module 1 (Viral Fitness Prediction) presentation.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from datetime import datetime


# ============================================================================
# CONFIGURATION
# ============================================================================

# Directory paths
DATA_DIR = Path("data")
RESULTS_DIR = Path("results/figures")
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

# SARS-CoV-2 variants mapping (key: directory name, value: display name)
VARIANTS = {
    "b1": "B.1",
    "beta": "Beta",
    "delta": "Delta",
    "omicron_ba1": "Omicron BA.1",
    "ba2": "BA.2",
    "xbb15": "XBB.1.5"
}

# Path to phenotype data (SARS2-spike-predictor-phenos)
PHENO_DIR = Path("external/SARS2-spike-predictor-phenos/results")

# Matplotlib style configuration
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# ============================================================================
# FUNCTION 1: Load NCBI Metadata
# ============================================================================

def load_ncbi_metadata():
    """
    Load genomic sequence metadata from NCBI.
    
    Returns:
        tuple: (all_data dict, summary_df) or (None, None) on error
            all_data: Dictionary with metadata for each variant
            summary_df: DataFrame with summary statistics per variant
    """
    print("\n" + "="*80)
    print("LOADING NCBI GENOMIC SEQUENCES")
    print("="*80)
    
    all_data = {}
    summary_list = []
    
    for var_key, var_name in VARIANTS.items():
        meta_file = DATA_DIR / var_key / f"{var_key}_meta.tsv"
        
        try:
            # Load metadata TSV
            meta = pd.read_csv(meta_file, sep="\t")
            
            # Parse collection date to datetime
            meta['Isolate Collection date'] = pd.to_datetime(
                meta['Isolate Collection date'], 
                errors='coerce'
            )
            
            all_data[var_key] = meta
            
            # Extract summary statistics
            n_seqs = len(meta)
            date_min = meta['Isolate Collection date'].min()
            date_max = meta['Isolate Collection date'].max()
            date_range = f"{date_min.strftime('%Y-%m')}/{date_max.strftime('%Y-%m')}"
            n_countries = meta['Geographic Location'].nunique()
            
            summary_list.append({
                'Variant': var_name,
                'Sequences': n_seqs,
                'Period': date_range,
                'Countries': n_countries
            })
            
            print(f"✓ {var_name:20s} {n_seqs:8,d} sequences ({date_range})")
            
        except FileNotFoundError:
            print(f"✗ {var_name:20s} FILE NOT FOUND: {meta_file}")
            return None, None
    
    summary_df = pd.DataFrame(summary_list)
    total_seqs = summary_df['Sequences'].sum()
    
    print(f"\n{'─'*80}")
    print(f"TOTAL: {total_seqs:,} sequences")
    print(f"{'─'*80}")
    
    return all_data, summary_df

# ============================================================================
# FUNCTION 2: Load Phenotype Data
# ============================================================================

def load_phenotypes():
    """
    Load viral fitness phenotype data from SARS2-spike-predictor-phenos.
    
    Returns:
        pd.DataFrame: Phenotype data with 3913 clades and 19 features,
                     or None on error
    """
    print("\n" + "="*80)
    print("LOADING PHENOTYPE DATA")
    print("="*80)
    
    pheno_file = PHENO_DIR / "clade_phenotypes.csv"
    
    try:
        clade_pheno = pd.read_csv(pheno_file)
        print(f"\n✓ Clade phenotypes: {len(clade_pheno)} rows")
        print(f"  Features: {len(clade_pheno.columns)}")
        
        # Analyze primary target variable
        target_col = 'clade growth'
        n_valid = clade_pheno[target_col].notna().sum()
        print(f"\n  Target variable '{target_col}':")
        print(f"    Valid values: {n_valid}/{len(clade_pheno)}")
        print(f"    Mean:  {clade_pheno[target_col].mean():.3f}")
        print(f"    Std:   {clade_pheno[target_col].std():.3f}")
        print(f"    Min:   {clade_pheno[target_col].min():.3f}")
        print(f"    Max:   {clade_pheno[target_col].max():.3f}")
        
        return clade_pheno
        
    except FileNotFoundError:
        print(f"\n FILE NOT FOUND: {pheno_file}")
        return None

# ============================================================================
# FUNCTION 3: Plot 1 - Sequences per Variant
# ============================================================================

def plot_sequences_per_variant(summary_df):
    """
    Create bar chart of sequence counts per variant.
    
    Args:
        summary_df (pd.DataFrame): Summary statistics from load_ncbi_metadata()
    """
    print("\n→ Creating Figure 1: Sequences per Variant...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Create bars with color gradient
    colors = plt.cm.Set2(np.linspace(0, 1, len(summary_df)))
    bars = ax.bar(summary_df['Variant'], summary_df['Sequences'], 
                  color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    # Labels and title
    ax.set_xlabel('COVID-19 Variant', fontsize=12, fontweight='bold')
    ax.set_ylabel('Number of Sequences', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of NCBI Genomic Sequences\nPer SARS-CoV-2 Variant', 
                 fontsize=14, fontweight='bold', pad=20)
    
    # Formatting
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{int(x/1000)}K' if x >= 1000 else f'{int(x)}'))
    ax.grid(axis='y', alpha=0.3)
    plt.xticks(rotation=45, ha='right')
    
    # Add total annotation
    total = summary_df['Sequences'].sum()
    ax.text(0.98, 0.97, f'Total: {total:,} sequences', 
            transform=ax.transAxes, fontsize=11,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))
    
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / '01_sequences_per_variant.png', dpi=300, bbox_inches='tight')
    print(f"  Saved: {RESULTS_DIR / '01_sequences_per_variant.png'}")
    plt.close()

# ============================================================================
# FUNCTION 4: Plot 2 - Variant Timeline
# ============================================================================

def plot_variant_timeline(all_data):
    """
    Create timeline showing emergence and dominance periods of variants.
    
    Args:
        all_data (dict): Metadata for each variant from load_ncbi_metadata()
    """
    print("\n→ Creating Figure 2: Variant Timeline...")
    
    fig, ax = plt.subplots(figsize=(14, 7))
    
    y_pos = 0
    colors = plt.cm.Set2(np.linspace(0, 1, len(VARIANTS)))
    
    for (var_key, var_name), color in zip(VARIANTS.items(), colors):
        meta = all_data[var_key]
        dates = meta['Isolate Collection date'].dropna()
        
        if len(dates) > 0:
            date_min = dates.min()
            date_max = dates.max()
            
            # Plot horizontal bar for each variant
            ax.barh(y_pos, (date_max - date_min).days, left=date_min, 
                   height=0.6, color=color, alpha=0.8, edgecolor='black', linewidth=1.5)
            
            # Add variant name centered on bar
            mid_date = date_min + (date_max - date_min) / 2
            ax.text(mid_date, y_pos, f'{var_name}', 
                   ha='center', va='center', fontweight='bold', fontsize=10)
            
            y_pos += 1
    
    ax.set_yticks(range(len(VARIANTS)))
    ax.set_yticklabels([])
    ax.set_xlabel('Date', fontsize=12, fontweight='bold')
    ax.set_title('Timeline of COVID-19 Variant Emergence and Dominance\n2020-2023', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Format date axis
    fig.autofmt_xdate(rotation=45, ha='right')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / '02_variant_timeline.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {RESULTS_DIR / '02_variant_timeline.png'}")
    plt.close()

# ============================================================================
# FUNCTION 5: Plot 3 - Fitness Distribution
# ============================================================================

def plot_fitness_distribution(clade_pheno):
    """
    Create histogram of clade growth (fitness) values.
    
    Args:
        clade_pheno (pd.DataFrame): Phenotype data from load_phenotypes()
    """
    print("\n→ Creating Figure 3: Fitness Distribution...")
    
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Extract target variable
    fitness = clade_pheno['clade growth'].dropna()
    
    # Create histogram with gradient coloring
    n, bins, patches = ax.hist(fitness, bins=25, color='skyblue', alpha=0.7, 
                               edgecolor='black', linewidth=1.2)
    
    # Apply gradient color to bars
    for i, patch in enumerate(patches):
        patch.set_facecolor(plt.cm.viridis(i/len(patches)))
    
    # Add statistical reference lines
    mean = fitness.mean()
    median = fitness.median()
    
    ax.axvline(mean, color='red', linestyle='--', linewidth=2.5, label=f'Mean: {mean:.3f}')
    ax.axvline(median, color='orange', linestyle='--', linewidth=2.5, label=f'Median: {median:.3f}')
    
    # Labels and title
    ax.set_xlabel('Relative Fitness (Clade Growth)', fontsize=12, fontweight='bold')
    ax.set_ylabel('Frequency (# Clades)', fontsize=12, fontweight='bold')
    ax.set_title('Distribution of Viral Fitness (Clade Growth)\nModule 1 Target Variable', 
                fontsize=14, fontweight='bold', pad=20)
    
    # Add statistics box
    stats_text = f"""Statistics:
    N: {len(fitness)}
    Mean: {mean:.3f}
    Std: {fitness.std():.3f}
    Min: {fitness.min():.3f}
    Q1: {fitness.quantile(0.25):.3f}
    Median: {median:.3f}
    Q3: {fitness.quantile(0.75):.3f}
    Max: {fitness.max():.3f}"""
    
    ax.text(0.98, 0.97, stats_text, transform=ax.transAxes, fontsize=10,
            verticalalignment='top', horizontalalignment='right',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.9),
            family='monospace')
    
    ax.legend(loc='upper left', fontsize=11)
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / '03_fitness_distribution.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {RESULTS_DIR / '03_fitness_distribution.png'}")
    plt.close()

# ============================================================================
# FUNCTION 6: Save Summary Table
# ============================================================================

def save_summary_table(summary_df, clade_pheno):
    """
    Export summary statistics and create visualization as PNG.
    
    Args:
        summary_df (pd.DataFrame): Summary from load_ncbi_metadata()
        clade_pheno (pd.DataFrame): Phenotype data from load_phenotypes()
    """
    print("\n→ Saving Summary Table...")
    
    # Add phenotype information
    summary_df['Phenotypes'] = 3913
    summary_df['Target'] = 'clade growth'
    
    # Save to CSV
    summary_df.to_csv(RESULTS_DIR / 'data_summary.csv', index=False)
    print(f"   Saved: {RESULTS_DIR / 'data_summary.csv'}")
    
    # Create table visualization
    fig, ax = plt.subplots(figsize=(14, 6))
    ax.axis('tight')
    ax.axis('off')
    
    # Prepare table data
    table_data = []
    table_data.append(['Variant', 'Sequences', 'Period', 'Countries', 'Phenotypes Available'])
    
    for idx, row in summary_df.iterrows():
        table_data.append([
            row['Variant'],
            f"{row['Sequences']:,}",
            row['Period'],
            str(row['Countries']),
            '3,913 clades'
        ])
    
    # Add total row
    total_seqs = summary_df['Sequences'].sum()
    table_data.append(['TOTAL', f'{total_seqs:,}', '2020-2023', '-', '3,913 clades'])
    
    # Create table
    table = ax.table(cellText=table_data, cellLoc='center', loc='center',
                    colWidths=[0.15, 0.15, 0.15, 0.15, 0.25])
    
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.5)
    
    # Style header row
    for i in range(5):
        table[(0, i)].set_facecolor('#4CAF50')
        table[(0, i)].set_text_props(weight='bold', color='white')
    
    # Style total row
    for i in range(5):
        table[(len(table_data)-1, i)].set_facecolor('#FFC107')
        table[(len(table_data)-1, i)].set_text_props(weight='bold')
    
    # Alternate row colors
    for i in range(1, len(table_data)-1):
        for j in range(5):
            if i % 2 == 0:
                table[(i, j)].set_facecolor('#E3F2FD')
            else:
                table[(i, j)].set_facecolor('#FFFFFF')
    
    plt.title('Summary of Molecular Data - Module 1\nNCBI Sequences + Phenotypes', 
             fontsize=14, fontweight='bold', pad=20)
    
    plt.savefig(RESULTS_DIR / '04_data_summary_table.png', dpi=300, bbox_inches='tight')
    print(f"   Saved: {RESULTS_DIR / '04_data_summary_table.png'}")
    plt.close()

# ============================================================================
# MAIN PIPELINE
# ============================================================================

def main():
    """
    Main pipeline orchestration.
    
    Workflow:
        1. Load NCBI genomic sequences metadata
        2. Load phenotype data
        3. Generate exploratory data analysis visualizations
        4. Export summary statistics
    
    Returns:
        bool: True if successful, False otherwise
    """
    print("\n" + "="*80)
    print("= PIPELINE: EXPLORATORY DATA ANALYSIS - MOLECULAR DATA")
    print("="*80)
    print(f"   Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   Output directory: {RESULTS_DIR}")
    print("="*80)
    
    # Step 1: Load NCBI metadata
    all_data, summary_df = load_ncbi_metadata()
    if all_data is None:
        print("\n Error loading NCBI metadata. Aborting.")
        return False
    
    # Step 2: Load phenotypes
    clade_pheno = load_phenotypes()
    if clade_pheno is None:
        print("\n Error loading phenotype data. Aborting.")
        return False
    
    # Step 3: Generate visualizations
    print("\n" + "="*80)
    print("GENERATING VISUALIZATIONS")
    print("="*80)
    
    plot_sequences_per_variant(summary_df)
    plot_variant_timeline(all_data)
    plot_fitness_distribution(clade_pheno)
    save_summary_table(summary_df, clade_pheno)
    
    # Step 4: Print summary
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    print(summary_df.to_string(index=False))
    print(f"\nTotal sequences: {summary_df['Sequences'].sum():,}")
    print(f"Total clades with phenotypes: {len(clade_pheno):,}")
    print(f"Clades with fitness labels: {clade_pheno['clade growth'].notna().sum()}")
    

    return True

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
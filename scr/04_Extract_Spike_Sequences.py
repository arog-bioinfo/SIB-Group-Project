#!/usr/bin/env python3
"""
Extract spike protein sequences from NCBI SARS-CoV-2 genomic datasets.

Input: NCBI ZIP files containing genomic FASTA (data/raw/*.zip)
Output: spike_sequences_by_accession.csv (accession → spike protein sequence)
        final_dataset_with_spike.csv (merged metadata + spike sequences)

Spike extraction:
- Gene coordinates: 21563-25384 (nucleotides, 1-based indexing)
- Translation: DNA → protein using standard genetic code
- Output: FASTA headers parsed to accession, spike protein (1273 amino acids)

Usage:
    python3 extract_spike_sequences.py
"""

import pandas as pd
import zipfile
import re
from pathlib import Path
from typing import Dict

# SARS-CoV-2 spike gene coordinates (nucleotides, 1-based)
SPIKE_START = 21563
SPIKE_END = 25384

# Variant ZIP filenames (must exist in data/raw/)
VARIANTS = ['b1', 'beta', 'delta', 'omicron_ba1', 'ba2', 'xbb15']

# Standard genetic code (DNA → amino acid)
CODON_TABLE = {
    'TTT': 'F', 'TTC': 'F', 'TTA': 'L', 'TTG': 'L',
    'TCT': 'S', 'TCC': 'S', 'TCA': 'S', 'TCG': 'S',
    'TAT': 'Y', 'TAC': 'Y', 'TAA': '*', 'TAG': '*',
    'TGT': 'C', 'TGC': 'C', 'TGA': '*', 'TGG': 'W',
    'CTT': 'L', 'CTC': 'L', 'CTA': 'L', 'CTG': 'L',
    'CCT': 'P', 'CCC': 'P', 'CCA': 'P', 'CCG': 'P',
    'CAT': 'H', 'CAC': 'H', 'CAA': 'Q', 'CAG': 'Q',
    'CGT': 'R', 'CGC': 'R', 'CGA': 'R', 'CGG': 'R',
    'ATT': 'I', 'ATC': 'I', 'ATA': 'I', 'ATG': 'M',
    'ACT': 'T', 'ACC': 'T', 'ACA': 'T', 'ACG': 'T',
    'AAT': 'N', 'AAC': 'N', 'AAA': 'K', 'AAG': 'K',
    'AGT': 'S', 'AGC': 'S', 'AGA': 'R', 'AGG': 'R',
    'GTT': 'V', 'GTC': 'V', 'GTA': 'V', 'GTG': 'V',
    'GCT': 'A', 'GCC': 'A', 'GCA': 'A', 'GCG': 'A',
    'GAT': 'D', 'GAC': 'D', 'GAA': 'E', 'GAG': 'E',
    'GGT': 'G', 'GGC': 'G', 'GGA': 'G', 'GGG': 'G',
}

def translate_dna_to_protein(dna_seq: str) -> str:
    """
    Translate DNA sequence to protein using standard genetic code.
    
    Args:
        dna_seq: DNA sequence (nucleotide string)
    
    Returns:
        Protein sequence (amino acid string)
    """
    # Convert to uppercase and clean invalid characters
    dna_seq = re.sub(r'[^ATGC]', 'X', dna_seq.upper())
    
    protein = []
    for i in range(0, len(dna_seq) - 2, 3):
        codon = dna_seq[i:i+3]
        aa = CODON_TABLE.get(codon, 'X')  # 'X' for invalid codons
        protein.append(aa)
    
    return ''.join(protein)

def extract_spike_from_zip(zip_path: Path, variant_name: str) -> Dict[str, str]:
    """
    Extract spike protein sequences from NCBI genomic ZIP file.
    
    Args:
        zip_path: Path to NCBI dataset ZIP
        variant_name: Variant identifier for logging
    
    Returns:
        Dictionary mapping accession to spike protein sequence
    """
    spike_sequences = {}
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            # Find genomic FASTA file
            fasta_files = [f for f in zf.namelist() if f.endswith('genomic.fna')]
            
            if not fasta_files:
                print(f"WARNING: {variant_name}: genomic.fna not found in {zip_path}")
                return spike_sequences
            
            fasta_file = fasta_files[0]
            print(f"  Processing {variant_name}: {fasta_file}")
            
            # Parse FASTA from ZIP
            with zf.open(fasta_file) as f:
                current_accession = None
                current_seq = []
                count = 0
                
                for line in f:
                    line = line.decode('utf-8').strip()
                    
                    if line.startswith('>'):
                        # Save previous sequence
                        if current_accession and current_seq:
                            full_seq = ''.join(current_seq)
                            
                            # Extract spike region (0-based indexing)
                            if len(full_seq) >= SPIKE_END:
                                spike_dna = full_seq[SPIKE_START-1:SPIKE_END]
                                spike_protein = translate_dna_to_protein(spike_dna)
                                spike_sequences[current_accession] = spike_protein
                                count += 1
                        
                        # Parse FASTA header for accession
                        header = line[1:].strip()
                        current_accession = header.split()[0]  # First token = accession
                        current_seq = []
                    else:
                        current_seq.append(line)
                
                # Save last sequence
                if current_accession and current_seq:
                    full_seq = ''.join(current_seq)
                    if len(full_seq) >= SPIKE_END:
                        spike_dna = full_seq[SPIKE_START-1:SPIKE_END]
                        spike_protein = translate_dna_to_protein(spike_dna)
                        spike_sequences[current_accession] = spike_protein
                        count += 1
            
            print(f"  SUCCESS: {variant_name}: extracted {count} spike sequences")
    
    except Exception as e:
        print(f"ERROR: {variant_name}: {e}")
    
    return spike_sequences

def main():
    """
    Main extraction pipeline.
    """
    print("SARS-CoV-2 Spike Protein Sequence Extraction Pipeline\n")
    
    base_dir = Path('.')
    raw_dir = base_dir / 'data' / 'raw'
    
    # Extract spike sequences from all variant ZIPs
    all_spikes = {}
    
    for variant in VARIANTS:
        zip_path = raw_dir / f'{variant}.zip'
        
        if not zip_path.exists():
            print(f"WARNING: {variant}: {zip_path} not found, skipping...")
            continue
        
        print(f"\nProcessing {variant.upper()}")
        spikes = extract_spike_from_zip(zip_path, variant)
        all_spikes.update(spikes)
    
    print(f"\n{'='*60}")
    print(f"SUCCESS: TOTAL {len(all_spikes)} spike sequences extracted")
    print(f"{'='*60}\n")
    
    # Save spike sequences
    output_df = pd.DataFrame(list(all_spikes.items()), 
                           columns=['accession', 'spike_protein_sequence'])
    output_path = base_dir / 'data' / 'processed' / 'spike_sequences_by_accession.csv'
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    output_df.to_csv(output_path, index=False)
    print(f"Saved: {output_path}\n")
    
    # Verify alignment with final_dataset.csv
    print("DATASET ALIGNMENT VERIFICATION\n")
    
    final_dataset_path = base_dir / 'data' / 'processed' / 'final_dataset.csv'
    if final_dataset_path.exists():
        df_final = pd.read_csv(final_dataset_path)
        
        # Compute alignment statistics
        accessions_in_final = set(df_final['accession'])
        accessions_with_spike = set(all_spikes.keys())
        
        match = accessions_in_final & accessions_with_spike
        missing = accessions_in_final - accessions_with_spike
        
        print(f"Accessions in final_dataset.csv: {len(accessions_in_final)}")
        print(f"Accessions with spike extracted: {len(accessions_with_spike)}")
        print(f"Match rate: {len(match)} ({100*len(match)/len(accessions_in_final):.1f}%)")
        print(f"Missing spike sequences: {len(missing)}")
        
        # Merge datasets
        df_with_spike = df_final.merge(
            output_df, 
            on='accession', 
            how='left'
        )
        
        output_merged = base_dir / 'data' / 'processed' / 'final_dataset_with_spike.csv'
        df_with_spike.to_csv(output_merged, index=False)
        
        print(f"\nSUCCESS: Merged dataset saved: {output_merged}")
        print(f"  Columns: {df_with_spike.columns.tolist()}")
        print(f"  Spike sequences populated: {df_with_spike['spike_protein_sequence'].notna().sum()}")
    else:
        print(f"WARNING: {final_dataset_path} not found")
    
    print("\nPipeline completed successfully.")

if __name__ == "__main__":
    main()

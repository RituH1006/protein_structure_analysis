"""
EXPANDED PROTEIN DATASET BUILDER - ROBUST
- Fetches verified Archaea and Bacteria sequences from UniProt
- Computes all physicochemical features using Biopython with error handling
- Saves features AND the raw (cleaned) sequence to 'data/processed/proteins_100plus_metadata.csv'
"""

import requests
import pandas as pd
import numpy as np
from pathlib import Path
from Bio.SeqUtils.ProtParam import ProteinAnalysis
import re
import sys
import time

# ============================================================================
# CONFIGURATION
# ============================================================================
OUTPUT_CSV = Path("data/processed/proteins_100plus_metadata.csv")
Path("data/processed").mkdir(parents=True, exist_ok=True)

ARCHAE_TAXON = "2157"
BACTERIA_TAXON = "2"
MIN_SEQ_LEN = 100
MAX_SEQ_LEN = 1000
MAX_PROTEINS_PER_GROUP = 200
REQUEST_DELAY = 0.3

# ============================================================================
# CLEAN SEQUENCE – remove non‑standard amino acids
# ============================================================================
def clean_sequence(seq):
    """Keep only standard 20 amino acids (ACDEFGHIKLMNPQRSTVWY)."""
    seq = seq.upper().replace(' ', '').replace('\n', '').replace('\r', '')
    seq = re.sub(r'[^ACDEFGHIKLMNPQRSTVWY]', '', seq)
    return seq

# ============================================================================
# FEATURE EXTRACTION (all via ProteinAnalysis, no external calls)
# ============================================================================
def compute_aa_composition(seq):
    aa_list = 'ACDEFGHIKLMNPQRSTVWY'
    length = len(seq)
    if length == 0:
        return {f'aa_{aa}': 0.0 for aa in aa_list}
    comp = {}
    for aa in aa_list:
        comp[f'aa_{aa}'] = (seq.count(aa) / length) * 100
    return comp

def compute_protein_params(seq):
    """
    Compute all numeric features using ProteinAnalysis.
    Returns a dictionary; on failure returns sensible defaults.
    """
    try:
        analysis = ProteinAnalysis(seq)
        helix, turn, sheet = analysis.secondary_structure_fraction()
        instab = analysis.instability_index()
        gravy = analysis.gravy()
        aromaticity = analysis.aromaticity()
        mw = analysis.molecular_weight() / 1000.0  # kDa
        charge = analysis.charge_at_pH(7)
        charge_density = charge / len(seq)
        try:
            iep = analysis.isoelectric_point()
        except:
            if charge > 0:
                iep = 7.0 + charge / len(seq) * 5
            else:
                iep = 7.0 - abs(charge) / len(seq) * 5
            iep = max(3.0, min(12.0, iep))
        cys_pairs = seq.count('C') // 2
    except Exception as e:
        print(f"      [Warning] Feature extraction failed: {e}")
        helix = turn = sheet = 0.0
        instab = 40.0
        gravy = 0.0
        aromaticity = 0.0
        mw = len(seq) * 110.0 / 1000.0
        charge_density = 0.0
        iep = 7.0
        cys_pairs = 0
    return {
        'mw': mw,
        'pi': iep,
        'aromaticity': aromaticity,
        'instability': instab,
        'gravy': gravy,
        'charge_density': charge_density,
        'cys_pairs': cys_pairs,
        'helix_%': helix * 100,
        'sheet_%': sheet * 100,
        'turn_%': turn * 100
    }

# ============================================================================
# FETCH FROM UNIPROT (TSV endpoint, more robust)
# ============================================================================
def fetch_uniprot_sequences(taxonomy_id, group_name, max_results=200):
    """Fetch sequences using TSV format (avoids JSON parsing issues)."""
    base_url = "https://rest.uniprot.org/uniprotkb/stream"
    query = f"taxonomy_id:{taxonomy_id} AND reviewed:true AND length:[{MIN_SEQ_LEN} TO {MAX_SEQ_LEN}]"
    params = {
        "query": query,
        "format": "tsv",
        "fields": "accession,sequence,organism_name,protein_name",
        "size": max_results,
    }
    print(f"  Fetching up to {max_results} {group_name} sequences...")
    try:
        response = requests.get(base_url, params=params, timeout=60)
        response.raise_for_status()
        lines = response.text.strip().split('\n')
        if len(lines) < 2:
            print(f"    No data returned.")
            return []
        header = lines[0].split('\t')
        acc_idx = header.index('Entry')
        seq_idx = header.index('Sequence')
        org_idx = header.index('Organism')
        name_idx = header.index('Protein names')
        all_data = []
        for line in lines[1:]:
            cols = line.split('\t')
            if len(cols) <= max(acc_idx, seq_idx, org_idx, name_idx):
                continue
            uniprot_id = cols[acc_idx]
            sequence = cols[seq_idx]
            organism = cols[org_idx]
            protein_name = cols[name_idx]
            sequence = clean_sequence(sequence)
            if len(sequence) < MIN_SEQ_LEN:
                continue
            all_data.append({
                'uniprot_id': uniprot_id,
                'sequence': sequence,
                'organism': organism,
                'protein_name': protein_name
            })
            if len(all_data) >= max_results:
                break
        print(f"    Retrieved {len(all_data)} sequences")
        return all_data
    except Exception as e:
        print(f"    ERROR: {e}")
        return []

# ============================================================================
# MAIN
# ============================================================================
def main():
    print("="*80)
    print("BUILDING EXPANDED PROTEIN DATASET FOR THERMOSTABILITY ANALYSIS")
    print("="*80)
    
    print("\n[1] FETCHING ARCHAEA (THERMOPHILES) FROM UNIPROT")
    archaea_list = fetch_uniprot_sequences(ARCHAE_TAXON, "Archaea", MAX_PROTEINS_PER_GROUP)
    
    print("\n[2] FETCHING BACTERIA (MESOPHILES) FROM UNIPROT")
    bacteria_list = fetch_uniprot_sequences(BACTERIA_TAXON, "Bacteria", MAX_PROTEINS_PER_GROUP)
    
    if not archaea_list and not bacteria_list:
        print("\n✗ No sequences retrieved. Exiting.")
        sys.exit(1)
    
    all_records = []
    
    for rec in archaea_list:
        row = extract_all_features(
            seq=rec['sequence'],
            uniprot_id=rec['uniprot_id'],
            organism=rec['organism'],
            protein_name=rec['protein_name'][:200],
            protein_class=1,
            growth_temp_str="80°C"
        )
        all_records.append(row)
    
    for rec in bacteria_list:
        row = extract_all_features(
            seq=rec['sequence'],
            uniprot_id=rec['uniprot_id'],
            organism=rec['organism'],
            protein_name=rec['protein_name'][:200],
            protein_class=0,
            growth_temp_str="37°C"
        )
        all_records.append(row)
    
    df = pd.DataFrame(all_records)
    df = df.drop_duplicates(subset=['uniprot_id'], keep='first').reset_index(drop=True)
    
    print("\n" + "="*80)
    print("DATASET SUMMARY")
    print("="*80)
    print(f"Total proteins: {len(df)}")
    print(f"  Archaea (thermophiles): {(df['protein_class']==1).sum()}")
    print(f"  Bacteria (mesophiles):  {(df['protein_class']==0).sum()}")
    print(f"Sequence length range: {df['seq_len'].min()} – {df['seq_len'].max()} aa")
    
    # Define column order: include 'sequence' after 'protein_name'
    column_order = ['uniprot_id', 'organism', 'protein_name', 'sequence', 'protein_class', 'type', 'temperature',
                    'seq_len', 'mw', 'pi', 'aromaticity', 'instability', 'gravy', 'charge_density',
                    'cys_pairs', 'helix_%', 'sheet_%', 'turn_%'] + [f'aa_{aa}' for aa in 'ACDEFGHIKLMNPQRSTVWY']
    for col in column_order:
        if col not in df.columns:
            df[col] = 0
    df = df[column_order]
    
    df.to_csv(OUTPUT_CSV, index=False)
    print(f"\n✓ Saved to: {OUTPUT_CSV}")
    print("\n" + "="*80)
    print("✓ DATASET CREATED (includes raw sequence column).")
    print("  Now you can run: python extract_features_complete.py (if needed)")
    print("  Or directly: python train_models.py")
    print("="*80)

def extract_all_features(seq, uniprot_id, organism, protein_name, protein_class, growth_temp_str):
    seq = clean_sequence(seq)
    seq_len = len(seq)
    aa_comp = compute_aa_composition(seq)
    prot_params = compute_protein_params(seq)
    row = {
        'uniprot_id': uniprot_id,
        'organism': organism,
        'protein_name': protein_name,
        'sequence': seq,                     # <-- ADDED: raw cleaned sequence
        'protein_class': protein_class,
        'type': 'Thermophile' if protein_class == 1 else 'Mesophile',
        'temperature': growth_temp_str,
        'seq_len': seq_len,
        **prot_params,
        **aa_comp
    }
    return row

if __name__ == "__main__":
    main()
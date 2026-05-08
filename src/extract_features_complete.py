"""
EXTRACT FEATURES FROM 100+ PROTEINS (MODIFIED)
Converts raw sequences to numerical feature vectors for ML training.
Handles non‑standard amino acids, missing data, and uses ProteinAnalyzer.
"""

import pandas as pd
import numpy as np
import sys
import re
from pathlib import Path

sys.path.insert(0, '.')
from src.structure_analyzer import ProteinAnalyzer

print("="*80)
print("FEATURE EXTRACTION: 100+ PROTEINS (MODIFIED)")
print("="*80)

# ============================================================================
# CONFIGURATION
# ============================================================================
INPUT_PATHS = [
    'data/raw/proteins_100plus_metadata.csv'
]
OUTPUT_PATH = 'data/processed/protein_features_100.csv'
MIN_SEQ_LEN = 50

# ============================================================================
# HELPER: CLEAN SEQUENCE
# ============================================================================
def clean_sequence(seq):
    """Keep only standard 20 amino acids (ACDEFGHIKLMNPQRSTVWY)."""
    if not isinstance(seq, str):
        return ""
    seq = seq.upper().replace(' ', '').replace('\n', '').replace('\r', '')
    seq = re.sub(r'[^ACDEFGHIKLMNPQRSTVWY]', '', seq)
    return seq

# ============================================================================
# LOAD RAW DATA
# ============================================================================
print("\n[STEP 1] Load raw protein sequences")
print("-" * 80)

df_raw = None
for path in INPUT_PATHS:
    if Path(path).exists():
        df_raw = pd.read_csv(path)
        print(f"✓ Loaded from: {path}")
        print(f"  Rows: {len(df_raw)}")
        print(f"  Columns: {list(df_raw.columns)}")
        break

if df_raw is None:
    raise FileNotFoundError(f"Could not find input CSV. Tried: {INPUT_PATHS}")

# Ensure required columns
required = ['uniprot_id', 'sequence']
for col in required:
    if col not in df_raw.columns:
        raise ValueError(f"Missing required column: {col}")

# If 'type' column is present, use it; otherwise infer from protein_class
if 'type' not in df_raw.columns:
    if 'protein_class' in df_raw.columns:
        df_raw['type'] = df_raw['protein_class'].map({1: 'Archaea (Thermophile)', 0: 'Bacteria (Mesophile)'})
    else:
        print("⚠ Warning: 'type' column missing, will set all to 'Unknown'")
        df_raw['type'] = 'Unknown'

# Clean sequences
print("\nCleaning sequences (removing non‑standard amino acids)...")
df_raw['original_length'] = df_raw['sequence'].str.len()
df_raw['sequence'] = df_raw['sequence'].apply(clean_sequence)
df_raw['seq_len_cleaned'] = df_raw['sequence'].str.len()
removed = (df_raw['original_length'] - df_raw['seq_len_cleaned']).sum()
print(f"  Removed {removed} non‑standard characters total")
df_raw = df_raw[df_raw['seq_len_cleaned'] >= MIN_SEQ_LEN].reset_index(drop=True)
print(f"  After cleaning: {len(df_raw)} proteins (min length {MIN_SEQ_LEN})")

# ============================================================================
# FEATURE EXTRACTION
# ============================================================================
print("\n[STEP 2] Extract features using ProteinAnalyzer")
print("-" * 80)

def extract_features_for_row(row):
    seq = row['sequence']
    uniprot = row['uniprot_id']
    organism = row.get('organism', 'Unknown')
    protein_name = row.get('protein_name', 'Unknown')
    type_str = row.get('type', 'Unknown')
    
    if 'Archaea' in str(type_str):
        protein_class = 1
        temp = "80°C"
    elif 'Bacteria' in str(type_str):
        protein_class = 0
        temp = "37°C"
    else:
        protein_class = -1
        temp = "Unknown"
    
    try:
        analyzer = ProteinAnalyzer(seq)
    except Exception as e:
        print(f"  Warning: ProteinAnalyzer failed for {uniprot}: {e}")
        return None
    
    try:
        ss = analyzer.get_secondary_structure()
        aa_comp = analyzer.get_amino_acid_composition()
        mw = analyzer.get_molecular_weight()
        pi = analyzer.get_isoelectric_point()
        aromaticity = analyzer.get_aromaticity()
        instability = analyzer.get_instability_index()
        gravy = analyzer.get_gravy()
        charge_density = analyzer.calculate_charge_density()
    except Exception as e:
        print(f"  Warning: Property calc failed for {uniprot}: {e}")
        ss = {'helix': 0.0, 'sheet': 0.0, 'turn': 0.0}
        aa_comp = {aa: 0.0 for aa in 'ACDEFGHIKLMNPQRSTVWY'}
        mw = len(seq) * 110.0 / 1000.0
        pi = 7.0
        aromaticity = 0.0
        instability = 40.0
        gravy = 0.0
        charge_density = 0.0
    
    feat = {
        'uniprot_id': uniprot,
        'organism': organism,
        'protein_name': protein_name,
        'protein_class': protein_class,
        'type': type_str,
        'temperature': temp,
        'seq_len': len(seq),
        'mw': float(mw),
        'pi': float(pi),
        'aromaticity': float(aromaticity),
        'instability': float(instability),
        'gravy': float(gravy),
        'charge_density': float(charge_density),
        'cys_pairs': int(seq.count('C') // 2),
        'helix_%': float(ss.get('helix', 0)),
        'sheet_%': float(ss.get('sheet', 0)),
        'turn_%': float(ss.get('turn', 0)),
    }
    for aa in 'ACDEFGHIKLMNPQRSTVWY':
        feat[f'aa_{aa}'] = float(aa_comp.get(aa, 0.0))
    return feat

all_features = []
skipped = 0
for idx, row in df_raw.iterrows():
    feat = extract_features_for_row(row)
    if feat is None:
        skipped += 1
    else:
        all_features.append(feat)
    if (idx + 1) % 50 == 0:
        print(f"  Processed {idx+1}/{len(df_raw)} proteins...")

print(f"\n✓ Extracted features for {len(all_features)} proteins")
print(f"⚠ Skipped {skipped} proteins")
if len(all_features) == 0:
    raise ValueError("No features extracted – check your ProteinAnalyzer or sequences.")

df_features = pd.DataFrame(all_features)

# ============================================================================
# VALIDATE FEATURES
# ============================================================================
print("\n[STEP 3] Validate features")
print("-" * 80)

feature_cols = [c for c in df_features.columns if c not in 
                ['uniprot_id', 'organism', 'protein_name', 'protein_class', 'type', 'temperature']]
print(f"Total features: {len(feature_cols)}")
nan_counts = df_features[feature_cols].isna().sum()
if nan_counts.sum() > 0:
    print(f"\n⚠ Filling {nan_counts.sum()} missing values with 0")
    df_features[feature_cols] = df_features[feature_cols].fillna(0)

# ============================================================================
# SAVE
# ============================================================================
print("\n[STEP 4] Save to CSV")
print("-" * 80)
Path('data/processed').mkdir(parents=True, exist_ok=True)
df_features.to_csv(OUTPUT_PATH, index=False)
print(f"✓ Saved: {OUTPUT_PATH}")
print(f"  Shape: {df_features.shape}")

# ============================================================================
# SUMMARY
# ============================================================================
print("\n" + "="*80)
print("SUMMARY")
print("="*80)
print(f"Total proteins: {len(df_features)}")
print(f"  Archaea: {(df_features['protein_class']==1).sum()}")
print(f"  Bacteria: {(df_features['protein_class']==0).sum()}")
print(f"Sequence length: {df_features['seq_len'].min()} – {df_features['seq_len'].max()} aa")
print("\nSample values:")
sample_cols = ['uniprot_id', 'mw', 'pi', 'instability', 'gravy', 'helix_%']
print(df_features[sample_cols].head(5).to_string(index=False))
print("\n" + "="*80)
print("✓ READY FOR TRAINING: python train_models.py")
print("="*80)
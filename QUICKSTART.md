# Quick Start Guide

Get up and running with the Protein Structure/Function Analysis project in 5 minutes!

## Prerequisites

- Python 3.8+
- Git
- pip or conda

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/protein-structure-analysis.git
cd protein-structure-analysis
```

### 2. Create Virtual Environment

Using venv:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

Or using conda:
```bash
conda create -n protein-analysis python=3.9
conda activate protein-analysis
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Verify Installation

```bash
python -c "import src; print('✓ Installation successful!')"
```

## First Steps

#### Use Python Scripts

```python
from src.structure_analyzer import ProteinAnalyzer

# Analyze a protein
sequence = "MKTAYIAKQRQISFVKSHFSRQLEERLGLIEVQAPILSRVGDGTQDNLSGAEKAVQVKVKALPDAQFEVVHSLAKWKRQTLGQHDFSAGEGLYTHMKALRPDEDRLSPLHSVYVDQWDWERVMGDGERQFSTLKSTVEAIWAGIKATEAAVSEEFGLAPFLPDQIHFVHSQELLSRYPDLDAKGRERAIAKDLGAVFLVGIGGKLSDGHRHDVRAPDYDDWSTPSELGHAGLNGDILVWNPVLEDAFELSSMGIRVDADTLKHQLALTGDEDRLELEWHQALLRGEMPQTIGGGIGQSRLTMLLLQLPHIGQVQAGVWPAAVRESVPSLL"

analyzer = ProteinAnalyzer(sequence)
features = analyzer.extract_all_features()

print(f"Molecular Weight: {features['molecular_weight']:.2f} Da")
print(f"Isoelectric Point: {features['isoelectric_point']:.2f}")
print(f"GRAVY: {features['gravy']:.3f}")
```

### Option C: Download Real Data

```python
from src.data_fetcher import PDBFetcher

# Search for protein structures
pdb = PDBFetcher()
results = pdb.search_structures("insulin", limit=5)
print(f"Found {len(results)} structures")

# Download a structure
pdb.download_structure("1MSO")
```

## Common Tasks

### Extract Features from Multiple Proteins

```python
from src.structure_analyzer import ProteinAnalyzer
import pandas as pd

proteins = {
    'Protein1': 'MKTAYIA...',
    'Protein2': 'MVLSPAD...',
}

results = []
for name, seq in proteins.items():
    analyzer = ProteinAnalyzer(seq)
    features = analyzer.extract_all_features()
    features['Protein'] = name
    results.append(features)

df = pd.DataFrame(results)
df.to_csv('protein_features.csv', index=False)
```

### Train a Machine Learning Model

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import pandas as pd

# Load feature data
df = pd.read_csv('protein_features.csv')

# Prepare data
X = df.drop(['Protein', 'function'], axis=1)
y = df['function']

# Split data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# Train model
model = RandomForestClassifier(n_estimators=100)
model.fit(X_train, y_train)

# Evaluate
score = model.score(X_test, y_test)
print(f"Accuracy: {score:.3f}")
```

### Visualize Results

```python
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

df = pd.read_csv('protein_features.csv')

# Create visualization
fig, axes = plt.subplots(2, 2, figsize=(12, 10))

# Molecular weight distribution
axes[0, 0].hist(df['molecular_weight'], bins=20)
axes[0, 0].set_xlabel('Molecular Weight (Da)')
axes[0, 0].set_title('MW Distribution')

# Isoelectric point
axes[0, 1].scatter(df['molecular_weight'], df['isoelectric_point'])
axes[0, 1].set_xlabel('Molecular Weight (Da)')
axes[0, 1].set_ylabel('Isoelectric Point')

# GRAVY
axes[1, 0].hist(df['gravy'], bins=20)
axes[1, 0].set_xlabel('GRAVY')
axes[1, 0].set_title('GRAVY Distribution')

# Aromaticity
axes[1, 1].hist(df['aromaticity'], bins=20)
axes[1, 1].set_xlabel('Aromaticity')
axes[1, 1].set_title('Aromaticity Distribution')

plt.tight_layout()
plt.savefig('protein_analysis.png')
plt.show()
```

## Configuration

Edit `config/config.yaml` to customize:

```yaml
# PDB settings
pdb:
  resolution_limit: 2.5
  max_structures: 100

# Feature extraction
features:
  normalize: true
  calculate_properties:
    molecular_weight: true
    isoelectric_point: true

# Model settings
models:
  random_forest:
    n_estimators: 100
    max_depth: 10
```

## File Organization

```
project/
├── data/
│   ├── raw/           ← Download data here
│   └── processed/     ← Processed data
├── notebooks/         ← Jupyter notebooks
├── src/              ← Source code modules
├── results/
│   ├── figures/      ← Generated plots
│   ├── models/       ← Trained models
│   └── tables/       ← Output tables
└── config.yaml       ← Configuration
```

## Tips & Tricks

### 1. Use Jupyter Lab Instead of Notebook

```bash
pip install jupyterlab
jupyter lab notebooks/
```

### 2. Monitor Memory Usage

```bash
pip install memory-profiler
python -m memory_profiler script.py
```

### 3. Speed Up Processing

```python
# Use parallel processing
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier(n_jobs=-1)  # Use all cores
```

### 4. Save Intermediate Results

```python
import pickle
import json

# Save model
with open('model.pkl', 'wb') as f:
    pickle.dump(model, f)

# Save results
with open('results.json', 'w') as f:
    json.dump(results, f)
```

## Troubleshooting

### Issue: Import errors

**Solution:**
```bash
pip install -r requirements.txt --upgrade
```

### Issue: Memory error on large datasets

**Solution:**
```python
# Process in chunks
chunk_size = 1000
for i in range(0, len(proteins), chunk_size):
    chunk = proteins[i:i+chunk_size]
    # Process chunk
```

### Issue: Slow download speeds from PDB

**Solution:**
```python
# Use local mirror or batch downloads with delays
from time import sleep
pdb.batch_download(pdb_ids, delay=1.0)  # 1 second between requests
```

## Next Steps

1. **Read the Documentation**: Check `docs/methodology.md` for detailed methods
2. **Explore Notebooks**: Run all notebooks in order (01, 02, 03, 04)
3. **Customize for Your Research**: Modify for your specific protein functions
4. **Check Results**: Review output in `results/` directory
5. **Share Your Work**: Push to GitHub and create a pull request

## Resources

- **BioPython Docs**: https://biopython.org/wiki/Documentation
- **Scikit-learn**: https://scikit-learn.org/stable/
- **PDB Help**: https://www.rcsb.org/help/
- **UniProt Help**: https://www.uniprot.org/help/

## Need Help?

- Check `docs/troubleshooting.md`
- Open an issue on GitHub
- Contact: your.email@example.com

---

**Happy analyzing! 🧬**

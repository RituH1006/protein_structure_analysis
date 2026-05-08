# Methodology

## Research Overview

This project investigates the relationship between protein structural features and their biological functions using computational analysis and machine learning. The study combines structural bioinformatics with statistical learning to develop predictive models.

---

## 1. Data Collection and Preparation

### 1.1 Data Sources

#### Protein Data Bank (PDB)
- **Source**: https://www.rcsb.org/
- **Content**: 3D structures from X-ray crystallography, NMR, and cryo-EM
- **Selection Criteria**:
  - Resolution ≤ 3.0 Å (adjustable)
  - Experimental method: X-ray diffraction (primarily)
  - Only human proteins or model organisms
  - Minimum sequence length: 50 amino acids

#### UniProt Database
- **Source**: https://www.uniprot.org/
- **Content**: Protein sequences and functional annotations
- **Information Used**:
  - Amino acid sequences
  - Functional annotations (Gene Ontology)
  - Protein families and domains
  - Evolutionary information

#### InterPro Database
- **Source**: https://www.ebi.ac.uk/interpro/
- **Content**: Protein families, domains, and functional sites
- **Use**: Identifying conserved motifs and domains

### 1.2 Data Preprocessing

1. **Sequence Validation**: Remove sequences with non-standard amino acids
2. **Structure Quality Check**: Filter by resolution and R-factor
3. **Redundancy Reduction**: Remove highly similar sequences (>90% identity)
4. **Missing Value Handling**: Imputation using mean/median or removal
5. **Normalization**: Scale features to unit variance

---

## 2. Structural Analysis

### 2.1 Physicochemical Properties

Properties calculated from amino acid sequences:

#### Basic Properties
- **Molecular Weight**: Sum of amino acid masses
- **Isoelectric Point (pI)**: pH at which protein has zero net charge
- **Aromaticity**: Fraction of aromatic amino acids (F, W, Y)
- **Instability Index**: Measure of protein stability in vitro

#### Hydropathy Indices
- **GRAVY** (Grand Average of Hydropathy): Kyte-Doolittle scale
  - Positive values: hydrophobic proteins
  - Negative values: hydrophilic proteins

#### Charge Properties
- **Net Charge**: Sum of charged residues at pH 7
- **Charge Density**: Charge per residue

### 2.2 Sequence Composition

#### Amino Acid Composition
- Percentage of each amino acid
- Grouped compositions (hydrophobic, hydrophilic, charged)

#### Dipeptide Frequency
- Frequency of two-residue patterns
- Total of 400 possible dipeptides

#### k-mer Analysis
- Frequency of k-length subsequences
- Default k=3 (tripeptides)

### 2.3 Secondary Structure

Predicted using DSSP-like algorithms:
- **Helix**: α-helix percentage
- **Sheet**: β-sheet percentage
- **Turn**: Turn/coil percentage

### 2.4 Structural Motifs

Identification of:
- Transmembrane domains
- Signal peptides
- Functional sites
- Protein-protein interaction regions

---

## 3. Feature Engineering

### 3.1 Feature Categories

#### Structural Features
1. Radius of gyration (Rg)
2. Contact order
3. Secondary structure content
4. Domain composition
5. Disulfide bond presence

#### Sequence Features
1. Amino acid composition (20 features)
2. Dipeptide frequency (400 features - optional)
3. k-mer composition
4. Sequence length
5. Charge distribution

#### Physicochemical Features
1. Molecular weight
2. Isoelectric point
3. GRAVY
4. Aromaticity
5. Instability index
6. Charge density

#### Conservation Features
1. Sequence entropy
2. Conservation score
3. Rate of evolution

### 3.2 Feature Selection

Methods used:
- **Univariate Analysis**: Statistical tests (ANOVA, correlation)
- **Recursive Feature Elimination** (RFE)
- **Feature Importance**: Tree-based methods
- **Variance Threshold**: Remove low-variance features

### 3.3 Feature Normalization

```python
# Standard scaling
X_scaled = (X - mean) / std_dev

# Min-Max normalization
X_normalized = (X - min) / (max - min)
```

---

## 4. Machine Learning Models

### 4.1 Model Selection

#### 1. Random Forest
- **Rationale**: Robust to high-dimensional data, non-linear relationships
- **Hyperparameters**:
  - n_estimators: 100
  - max_depth: 10
  - min_samples_split: 5

#### 2. Support Vector Machine (SVM)
- **Rationale**: Effective in high-dimensional spaces
- **Hyperparameters**:
  - kernel: RBF (Radial Basis Function)
  - C: 1.0
  - gamma: 'scale'

#### 3. Logistic Regression
- **Rationale**: Interpretable baseline model
- **Hyperparameters**:
  - solver: 'lbfgs'
  - max_iter: 1000

#### 4. XGBoost (optional)
- **Rationale**: Gradient boosting for improved performance
- **Hyperparameters**:
  - n_estimators: 100
  - max_depth: 6
  - learning_rate: 0.1

### 4.2 Training Strategy

```
Data
  ↓
80% Training Set → 5-Fold Cross-Validation → Hyperparameter Tuning
  ↓                                            ↓
Model Selection → Train Final Model → 20% Test Set → Evaluate
```

### 4.3 Cross-Validation

- **Method**: Stratified K-Fold (k=5)
- **Rationale**: Maintains class distribution in imbalanced datasets
- **Metrics**: Accuracy, Precision, Recall, F1-Score, AUC-ROC

### 4.4 Hyperparameter Optimization

- **Method**: GridSearchCV with cross-validation
- **Parameters**: Learning rate, tree depth, regularization
- **Objective**: Maximize F1-score or AUC-ROC

---

## 5. Model Evaluation

### 5.1 Performance Metrics

#### Classification Metrics
- **Accuracy**: (TP + TN) / (TP + TN + FP + FN)
- **Precision**: TP / (TP + FP)
- **Recall**: TP / (TP + FN)
- **F1-Score**: 2 × (Precision × Recall) / (Precision + Recall)

#### Probabilistic Metrics
- **AUC-ROC**: Area under Receiver Operating Characteristic curve
- **PR-AUC**: Precision-Recall curve area

#### Confusion Matrix
- True Positives, False Positives
- True Negatives, False Negatives

### 5.2 Statistical Testing

- **Significance Testing**: p-value < 0.05
- **95% Confidence Intervals**: For performance metrics
- **Statistical Power Analysis**: Sample size sufficiency

### 5.3 Model Comparison

- **Paired t-tests**: Compare model performances
- **Effect Size**: Cohen's d
- **Model Selection**: Best performing model on test set

---

## 6. Validation and Interpretability

### 6.1 External Validation

- **Independent test set**: 20% of data
- **Cross-dataset validation**: Test on different protein sources
- **Literature comparison**: Compare with published benchmarks

### 6.2 Feature Importance Analysis

#### Methods
1. **Tree-based Importance**: MDI (Mean Decrease in Impurity)
2. **Permutation Importance**: Impact on model when feature shuffled
3. **SHAP Values**: Shapley values for fair feature attribution
4. **Partial Dependence Plots**: Feature-target relationships

### 6.3 Model Interpretability

- **LIME**: Local Interpretable Model-agnostic Explanations
- **Feature Interaction Analysis**: Which features work together?
- **Prediction Confidence**: Uncertainty estimation

---

## 7. Data Visualization

### 7.1 Exploratory Visualizations

- Distribution plots: Histogram, KDE
- Correlation matrix: Heatmap
- Scatter plots: Feature relationships
- Box plots: Property distributions by protein class

### 7.2 Results Visualizations

- ROC curves: Model performance
- Precision-Recall curves: Class imbalance handling
- Confusion matrices: Detailed error analysis
- Feature importance plots: Top contributing features
- SHAP plots: Model explanations

### 7.3 Structural Visualizations

- 3D protein structures: Visualization of spatial arrangement
- Domain architecture: Protein composition
- Sequence alignments: Comparative analysis

---

## 8. Reproducibility

### 8.1 Version Control

- Git repository with complete history
- Clear commit messages
- Documentation of all changes

### 8.2 Computational Environment

- Python 3.8+
- All dependencies listed in requirements.txt
- Docker container specification (optional)

### 8.3 Random Seeds

```python
RANDOM_SEED = 42
np.random.seed(RANDOM_SEED)
random.seed(RANDOM_SEED)
```

### 8.4 Data Versioning

- All datasets downloaded from public repositories
- Download date and version recorded
- Scripts for re-downloading if needed

---

## 9. Statistical Rigor

### 9.1 Sample Size

- Minimum 100 proteins per function class
- Power analysis for statistical tests
- Effect size reporting

### 9.2 Multiple Comparisons

- Bonferroni correction for multiple tests
- False Discovery Rate (FDR) control

### 9.3 Assumptions Testing

- Normality: Shapiro-Wilk test
- Equal variances: Levene's test
- Linearity: Scatter plot inspection

---

## 10. Computational Details

### 10.1 Hardware Requirements

- RAM: 8 GB minimum (16 GB recommended)
- Storage: 10 GB for databases
- CPU: Multi-core preferred for parallel processing

### 10.2 Runtime Estimates

- Data download: 1-2 hours
- Feature extraction: 30-60 minutes
- Model training: 10-30 minutes
- Total pipeline: 2-3 hours

### 10.3 Parallel Processing

- n_jobs = -1: Uses all available cores
- Batch processing: Data divided into chunks
- Memory-efficient: Streaming where possible

---

## References

1. UniProt Consortium. (2019). UniProt: A worldwide hub of protein knowledge.
2. Burley, S. K., et al. (2023). RCSB Protein Data Bank.
3. Pedregosa, F., et al. (2011). Scikit-learn: ML in Python. JMLR.
4. BioPython: http://biopython.org/
5. Cramer, J. S. (2005). Logistic Regression for Economics.

---

**Last Updated**: May 2024
**Status**: Active Research

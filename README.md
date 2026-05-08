##### Thermostability Classification: Machine Learning Pipeline

Complete ML workflow for classifying thermophilic Archaea vs mesophilic Bacteria proteins from sequence features. Features zero‑overlap validation, overfitting detection, and publication‑ready visualisations.

##### 

##### Overview

Goal – Robust classifiers to distinguish thermostable proteins (Archaea, 65–113 °C) from mesophilic ones (Bacteria, 30–42 °C)



Dataset – 400 real, verified proteins from UniProt (200 Archaea, 200 Bacteria)



Features – 31 numerical properties per protein:

8 physicochemical (MW, pI, instability, GRAVY, …) + 3 secondary structure + 20 amino‑acid composition



Models – Random Forest, SVM, Logistic Regression (with L2 regularisation)



Key innovation – 6‑check zero‑overlap validation guaranteeing complete train/test isolation



##### Quick Start (5 steps)

Download proteins

python download\_proteins\_100plus.py

→ data/processed/proteins\_100plus\_metadata.csv



Extract features

python extract\_features\_100.py

→ data/processed/protein\_features\_100.csv



Train models

python train\_models\_fixed.py

→ results/models/ + results/tables/model\_results\_corrected.csv



Validate (overfitting detection)

python validate\_models.py

→ results/tables/validation\_results.csv



Visualise

python visualize\_models.py

→ 5 figures in results/visualizations/



##### Workflow 

##### 

Raw sequences (UniProt)

&#x20;       ↓

DOWNLOAD → metadata CSV

&#x20;       ↓

EXTRACT → 31 features

&#x20;       ↓

SPLIT FIRST (train/test) + 6‑check zero‑overlap

&#x20;       ↓

SCALE (fit on train only)

&#x20;       ↓

TRAIN (RF, SVM, LR)

&#x20;       ↓

VALIDATE (train vs test, overfitting, calibration)

&#x20;       ↓

VISUALISE (5 publication‑ready plots)

Key guarantees

Split first – no preprocessing before splitting



Zero overlap – 6 independent checks



Honest scaling – scaler fitted only on training set



Overfitting detection – train‑test gap >10 % flagged



Reproducible – fixed random\_state=42





##### Project Structure

Protein\_Structure\_Analysis/

├── data/processed/

│   ├── proteins\_100plus\_metadata.csv      # raw metadata (sequences)

│   └── protein\_features\_100.csv           # 31 numerical features

├── results/

│   ├── models/                            # trained models + scaler + indices

│   ├── tables/                            # performance \& validation CSVs

│   └── visualizations/                    # 5 PNG figures

├── src/

│   └── structure\_analyzer.py              # feature extraction logic

├── get\_protein\_data.py

├── extract\_features\_100.py

├── train\_models\_fixed.py

├── validate\_models.py

├── visualize\_models.py

└── README.md



##### Scripts in Detail

Script	Purpose	Output	Runtime

download\_proteins\_100plus.py	Fetch 400 verified sequences (Archaea + Bacteria) via UniProt API	proteins\_100plus\_metadata.csv	2‑3 min

extract\_features\_100.py	Compute 31 features per protein	protein\_features\_100.csv	30‑60 s

train\_models\_fixed.py	Train RF, SVM, LR with zero‑overlap validation; 5‑fold CV on training set	models + model\_results\_corrected.csv	30‑45 s

validate\_models.py	Detect overfitting, calibration, sensitivity/specificity	validation\_results.csv, feature importance	10 s

visualize\_models.py	Generate 5 publication‑ready figures (PNG)	5 PNGs in visualizations/	15 s

Data Leakage Prevention – 6‑Check Validation

Check	What it verifies

1	No index overlap between train and test

2	All proteins assigned (complete coverage)

3	No duplicate UniProt IDs across sets

4	No identical sequences across sets

5	Class balance preserved (stratification)

6	No duplicates within each set

All six must pass before training.



##### Example output:

✓ \[PASS] Zero overlap in indices

✓ \[PASS] Zero duplicate UniProt IDs between sets

✓ \[PASS] Zero duplicate sequences between sets

✓ \[PASS] Stratification maintained

✓ \[PASS] All proteins unique within sets





##### Expected Results (Typical Performance)

Model	Accuracy	F1‑Score	ROC‑AUC	Overfitting Gap

Random Forest	84‑88%	0.84‑0.88	0.90‑0.94	usually <10%

SVM	80‑85%	0.80‑0.85	0.88‑0.92	often lower

Logistic Regression	75‑80%	0.75‑0.80	0.85‑0.90	lowest (most regularised)

Best model typically Random Forest or Logistic Regression (depending on dataset size).



##### Interpretation of Validation Metrics

Metric	Meaning

Sensitivity (Recall)	How well the model catches true Archaea (thermophiles)

Specificity	How well it correctly identifies Bacteria (mesophiles)

Precision	Among predicted Archaea, how many are correct

F1‑Score	Harmonic mean of precision and recall

Overfitting Score	Train Accuracy – Test Accuracy; >10 % suggests overfitting

Calibration	Difference between mean predicted probability and actual class frequency; <5 % is well‑calibrated





##### Troubleshooting

KeyError: 'sequence'	Script automatically falls back to pre‑computed features – safe to ignore.

FileNotFoundError: protein\_features\_100.csv	Run extract\_features\_100.py first.

Duplicate UniProt ID errors	Use train\_models\_fixed.py – it deduplicates automatically.

Low accuracy (<70%)	Check class balance; use feature selection; increase training data.

Overfitting detected	Increase regularisation (C smaller for LR), reduce tree depth (RF), or use fewer features.

Performance Optimisation

Speed – reduce n\_estimators (RF), use 3‑fold CV, parallelise (n\_jobs=-1)



Memory – use sparse matrices if needed



Better results – feature engineering, ensemble stacking, or hyperparameter tuning (GridSearchCV)



##### Future Enhancements

Deep learning (e.g., 1D‑CNN on sequences)



SHAP for model interpretability



REST API deployment



Bayesian hyperparameter optimisation



License \& Disclaimer

For educational/research use only. Predictions are based solely on sequence features; actual thermostability depends on 3D structure and experimental conditions.



Version: 1.0




**Thermostability Classification: Machine Learning Pipeline**

Complete ML workflow for classifying thermophilic Archaea vs mesophilic Bacteria proteins from sequence features. Features zero‑overlap validation, overfitting detection, and visualizations.

**Overview**

Goal – Robust classifiers to distinguish thermostable proteins (Archaea, 65–113 °C) from mesophilic ones (Bacteria, 30–42 °C)

Dataset – 400 real, verified proteins from UniProt (200 Archaea, 200 Bacteria)



Features – 31 numerical properties per protein:

8 physicochemical (MW, pI, instability, GRAVY, …) + 3 secondary structure + 20 amino‑acid composition



Models – Random Forest, SVM, Logistic Regression (with L2 regularisation)


**Quick Start (5 steps)**

1. Download proteins

python download\_proteins\_100plus.py

→ data/processed/proteins\_100plus\_metadata.csv


2. Extract features

python extract\_features\_100.py

→ data/processed/protein\_features\_100.csv

3.Train models

python train\_models\_fixed.py

→ results/models/ + results/tables/model\_results\_corrected.csv

4. Validate (overfitting detection)

python validate\_models.py

→ results/tables/validation\_results.csv

5. Visualise

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




"""
CORRECTED ML TRAINING - NO DATA LEAKAGE (IMPROVED)
Nested Cross-Validation with Zero-Overlap Validation
Feature Selection + Hyperparameter Tuning + Honest Evaluation
"""

import pandas as pd
import numpy as np
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split, cross_validate, StratifiedKFold, GridSearchCV
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score
from sklearn.pipeline import Pipeline
from sklearn.feature_selection import SelectKBest, mutual_info_classif
import sys
from collections import Counter

sys.path.insert(0, '.')

print("="*80)
print("CORRECTED ML TRAINING - NESTED CV WITH ZERO OVERLAP")
print("="*80)

# ============================================================================
# STEP 0: LOAD RAW DATA
# ============================================================================

print("\nSTEP 0: LOAD RAW PROTEIN DATA")
print("-"*80)

# Try multiple possible file paths
possible_paths = [
    'data/processed/protein_features_100.csv',
    'data/processed/protein_features.csv',
    'protein_features_100.csv',
]

df_raw = None
loaded_path = None

for path in possible_paths:
    if Path(path).exists():
        try:
            df_test = pd.read_csv(path)
            # Check if this file has features (not just metadata)
            exclude_cols = ['uniprot_id', 'organism', 'protein_class', 'type', 'sequence', 'protein_name', 'temperature']
            feature_cols_check = [c for c in df_test.columns if c not in exclude_cols]
            
            if len(feature_cols_check) > 20:  # Has features
                df_raw = df_test
                loaded_path = path
                print(f"✓ Loaded from: {path}")
                print(f"  Rows: {len(df_raw)}")
                print(f"  Columns: {len(df_raw.columns)}")
                print(f"  Feature columns: {len(feature_cols_check)}")
                break
        except Exception as e:
            print(f"  Warning: Could not load {path}: {e}")
            continue

if df_raw is None:
    raise FileNotFoundError("No feature CSV found. Run extract_features_100_FIXED.py first.")

print(f"\nLoaded {len(df_raw)} proteins")

# ============================================================================
# STEP 1: VALIDATION AND CLEANING
# ============================================================================

print("\n" + "="*80)
print("STEP 1: DATA VALIDATION AND CLEANING")
print("="*80)

# Verify required columns
required_cols = ['uniprot_id', 'organism', 'protein_class']
for col in required_cols:
    if col not in df_raw.columns:
        raise ValueError(f"Missing required column: {col}")

print(f"\n✓ Required columns present")

# Check protein_class values
print(f"\nProtein class values:")
class_values = df_raw['protein_class'].unique()
print(f"  Unique values: {sorted(class_values)}")
print(f"  Value counts:\n{df_raw['protein_class'].value_counts()}")

# If all values are -1 (or any other invalid sentinel), re-create from 'type' column
if not df_raw['protein_class'].isin([0, 1]).any():
    print("\n⚠ Invalid protein_class values detected (no 0 or 1). Re‑creating from 'type' column.")
    if 'type' in df_raw.columns:
        # Map: 'Thermophile' → 1, 'Mesophile' → 0
        type_to_class = {'Thermophile': 1, 'Mesophile': 0}
        df_raw['protein_class'] = df_raw['type'].map(type_to_class)
        # Drop rows where type didn't match (should be none)
        df_raw = df_raw.dropna(subset=['protein_class']).reset_index(drop=True)
        print(f"✓ Re‑created protein_class: {(df_raw['protein_class']==1).sum()} Archaea, {(df_raw['protein_class']==0).sum()} Bacteria")
    else:
        raise ValueError("Cannot fix protein_class: 'type' column missing.")

# Now filter only valid classes (0 and 1) – should already be fine
df_raw = df_raw[df_raw['protein_class'].isin([0, 1])].reset_index(drop=True)
df_raw = df_raw.dropna(subset=['protein_class']).reset_index(drop=True)

print(f"\n✓ Data cleaned")
print(f"  Remaining samples: {len(df_raw)}")
print(f"  Archaea (1): {(df_raw['protein_class']==1).sum()}")
print(f"  Bacteria (0): {(df_raw['protein_class']==0).sum()}")
# ============================================================================
# STEP 2: HANDLE DUPLICATES
# ============================================================================

print("\n" + "="*80)
print("STEP 2: HANDLE DUPLICATE UNIPROT IDs")
print("="*80)

duplicate_ids = df_raw[df_raw.duplicated(subset=['uniprot_id'], keep=False)]['uniprot_id'].unique()

if len(duplicate_ids) > 0:
    print(f"\n⚠ Found {len(duplicate_ids)} duplicate UniProt IDs")
    
    df_raw_dedup = df_raw.drop_duplicates(subset=['uniprot_id'], keep='first')
    
    print(f"  Original: {len(df_raw)} proteins")
    print(f"  After dedup: {len(df_raw_dedup)} proteins")
    print(f"  Removed: {len(df_raw) - len(df_raw_dedup)} duplicates")
    
    df_raw = df_raw_dedup.reset_index(drop=True)
    
    print(f"\n✓ Duplicates removed")
else:
    print(f"\n✓ No duplicate UniProt IDs found")

# ============================================================================
# STEP 3: EXTRACT FEATURES
# ============================================================================

print("\n" + "="*80)
print("STEP 3: PREPARE FEATURE DATA")
print("="*80)

# Get feature columns
exclude = ['uniprot_id', 'organism', 'protein_name', 'protein_class', 'type', 'temperature', 'sequence']
feature_cols = [c for c in df_raw.columns if c not in exclude]

print(f"\nFeature columns found: {len(feature_cols)}")
print(f"  {', '.join(feature_cols[:5])}...")

# Extract features and targets
X = df_raw[feature_cols].values.astype(float)  # IMPORTANT: Convert to float
y = df_raw['protein_class'].values.astype(int)   # IMPORTANT: Convert to int

print(f"\nData shape: X = {X.shape}, y = {y.shape}")
print(f"X dtype: {X.dtype}, y dtype: {y.dtype}")
print(f"Y values: {np.unique(y)} (should be [0, 1])")

# Verify no NaN or Inf
if np.isnan(X).any():
    print("⚠ NaN values in X - filling with 0")
    X = np.nan_to_num(X, nan=0.0)

if np.isinf(X).any():
    print("⚠ Inf values in X - replacing with large numbers")
    X = np.nan_to_num(X, posinf=1e6, neginf=-1e6)

print(f"✓ Feature matrix validated")

# ============================================================================
# STEP 4: NESTED CROSS-VALIDATION
# ============================================================================

print("\n" + "="*80)
print("STEP 4: NESTED CROSS-VALIDATION")
print("="*80)

# Outer CV for honest evaluation
outer_cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Inner CV for hyperparameter tuning
inner_cv = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)

# Simple pipeline: scaling + logistic regression
# (Feature selection can be too aggressive with small k values)
pipe = Pipeline([
    ('scale', StandardScaler()),
    ('lr', LogisticRegression(max_iter=2000, random_state=42))
])

# Simpler hyperparameter grid
param_grid = {
    'lr__C': [0.01, 0.1, 1.0, 10.0],
}

print(f"\nOuter CV: {outer_cv.get_n_splits()} folds")
print(f"Inner CV: {inner_cv.get_n_splits()} folds")
print(f"Parameter grid size: {len(param_grid['lr__C'])}")
print(f"Total fits: {5 * 3 * 4} = {5 * 3 * 4}")

# Store results
outer_scores = []
outer_y_true = []
outer_y_pred = []
best_params_list = []

print(f"\nRunning nested cross-validation...")

fold_num = 0
for train_idx, test_idx in outer_cv.split(X, y):
    fold_num += 1
    
    # Get train and test data for this outer fold
    X_train_outer, X_test_outer = X[train_idx], X[test_idx]
    y_train_outer, y_test_outer = y[train_idx], y[test_idx]
    
    print(f"\nOuter fold {fold_num}:")
    print(f"  Train: {len(y_train_outer)} samples (Archaea: {(y_train_outer==1).sum()}, Bacteria: {(y_train_outer==0).sum()})")
    print(f"  Test:  {len(y_test_outer)} samples (Archaea: {(y_test_outer==1).sum()}, Bacteria: {(y_test_outer==0).sum()})")
    
    # Inner CV: tune hyperparameters
    try:
        gs = GridSearchCV(pipe, param_grid, cv=inner_cv, scoring='accuracy', n_jobs=-1)
        gs.fit(X_train_outer, y_train_outer)
        
        print(f"  Best params: {gs.best_params_}")
        print(f"  Best inner CV score: {gs.best_score_:.4f}")
        
    except Exception as e:
        print(f"  ERROR during GridSearchCV: {e}")
        raise
    
    # Evaluate on outer test fold
    try:
        y_pred = gs.predict(X_test_outer)
        
        # Check for invalid predictions
        unique_preds = np.unique(y_pred)
        print(f"  Predictions: {unique_preds}")
        
        # Calculate metrics
        acc = accuracy_score(y_test_outer, y_pred)
        prec = precision_score(y_test_outer, y_pred, zero_division=0)
        rec = recall_score(y_test_outer, y_pred, zero_division=0)
        f1 = f1_score(y_test_outer, y_pred, zero_division=0)
        
        print(f"  Outer test accuracy: {acc:.4f}")
        print(f"  Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}")
        
        outer_scores.append(acc)
        outer_y_true.extend(y_test_outer)
        outer_y_pred.extend(y_pred)
        best_params_list.append(gs.best_params_)
        
    except Exception as e:
        print(f"  ERROR during evaluation: {e}")
        raise

# ============================================================================
# STEP 5: RESULTS AND FINAL MODEL
# ============================================================================

print("\n" + "="*80)
print("STEP 5: NESTED CV RESULTS")
print("="*80)

print(f"\nOuter CV Results:")
print(f"  Mean accuracy: {np.mean(outer_scores):.4f}")
print(f"  Std accuracy: {np.std(outer_scores):.4f}")
print(f"  Min accuracy: {np.min(outer_scores):.4f}")
print(f"  Max accuracy: {np.max(outer_scores):.4f}")

# Overall metrics
y_true_all = np.array(outer_y_true)
y_pred_all = np.array(outer_y_pred)

overall_acc = accuracy_score(y_true_all, y_pred_all)
overall_prec = precision_score(y_true_all, y_pred_all, zero_division=0)
overall_rec = recall_score(y_true_all, y_pred_all, zero_division=0)
overall_f1 = f1_score(y_true_all, y_pred_all, zero_division=0)

print(f"\nOverall Test Set Metrics:")
print(f"  Accuracy: {overall_acc:.4f}")
print(f"  Precision: {overall_prec:.4f}")
print(f"  Recall: {overall_rec:.4f}")
print(f"  F1-Score: {overall_f1:.4f}")

# Get best average parameters
best_C_values = [p['lr__C'] for p in best_params_list]
best_C = Counter(best_C_values).most_common(1)[0][0]

print(f"\nMost common C value: {best_C}")

# Train final model on all data
print(f"\nTraining final model on all {len(X)} samples...")

final_pipe = Pipeline([
    ('scale', StandardScaler()),
    ('lr', LogisticRegression(C=best_C, max_iter=2000, random_state=42))
])

final_pipe.fit(X, y)

print(f"✓ Final model trained")

# Get feature importance
coefs = final_pipe.named_steps['lr'].coef_[0]
feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Coefficient': coefs,
    'Abs_Coefficient': np.abs(coefs)
}).sort_values('Abs_Coefficient', ascending=False)

print(f"\nTop 10 features for thermostability prediction:")
for idx, row in feature_importance.head(10).iterrows():
    direction = "→ Archaea" if row['Coefficient'] > 0 else "→ Bacteria"
    print(f"  {row['Feature']:20s}: {row['Coefficient']:8.4f} {direction}")

# ============================================================================
# STEP 6: SAVE RESULTS
# ============================================================================

print("\n" + "="*80)
print("STEP 6: SAVE RESULTS")
print("="*80)

Path('results/models').mkdir(parents=True, exist_ok=True)
Path('results/tables').mkdir(parents=True, exist_ok=True)

# Save model
with open('results/models/best_thermostability_model.pkl', 'wb') as f:
    pickle.dump(final_pipe, f)
print(f"✓ Model saved: results/models/best_thermostability_model.pkl")

# Save feature importance
feature_importance.to_csv('results/tables/feature_importance_thermostability.csv', index=False)
print(f"✓ Features saved: results/tables/feature_importance_thermostability.csv")

# Save metrics
metrics = pd.DataFrame({
    'Metric': ['Mean_Accuracy', 'Std_Accuracy', 'Overall_Accuracy', 'Precision', 'Recall', 'F1_Score', 'Best_C'],
    'Value': [np.mean(outer_scores), np.std(outer_scores), overall_acc, overall_prec, overall_rec, overall_f1, best_C]
})
metrics.to_csv('results/tables/nested_cv_metrics.csv', index=False)
print(f"✓ Metrics saved: results/tables/nested_cv_metrics.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*80)
print("✓ NESTED CROSS-VALIDATION COMPLETE")
print("="*80)

print(f"\nKey Results:")
print(f"  Nested CV Accuracy: {np.mean(outer_scores):.1%}")
print(f"  Test Set Accuracy: {overall_acc:.1%}")
print(f"  Best Hyperparameter: C = {best_C}")
print(f"\nModel saved and ready for predictions on Nipah proteins!")
print(f"  File: results/models/best_thermostability_model.pkl")
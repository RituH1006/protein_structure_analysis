"""
MODEL VALIDATION & OVERFITTING DETECTION (UPDATED for nested CV model)
Uses cross-validation to estimate generalization of the final model.
"""

import pandas as pd
import numpy as np
import pickle
from pathlib import Path
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from sklearn.metrics import (
    confusion_matrix, classification_report, roc_curve, auc,
    precision_recall_curve, f1_score, accuracy_score, roc_auc_score,
    precision_score, recall_score
)
from sklearn.pipeline import Pipeline

print("="*80)
print("FINAL MODEL VALIDATION & OVERFITTING DETECTION")
print("="*80)

# ============================================================================
# STEP 1: LOAD FINAL MODEL AND DATA
# ============================================================================

print("\nSTEP 1: LOAD FINAL MODEL AND DATA")
print("-"*80)

# Load the logistic regression model trained on all data
model_path = Path('results/models/best_thermostability_model.pkl')
if not model_path.exists():
    raise FileNotFoundError(f"Model not found at {model_path}. Run train_models.py first.")

with open(model_path, 'rb') as f:
    final_pipeline = pickle.load(f)
    print(f"✓ Loaded final model: {type(final_pipeline.named_steps['lr']).__name__}")
    print(f"  Best C = {final_pipeline.named_steps['lr'].C}")

# Load feature data
df = pd.read_csv('data/processed/protein_features_100.csv')
print(f"✓ Loaded feature data: {df.shape}")

# ============================================================================
# STEP 2: CLEAN DATA (same as in train_models.py)
# ============================================================================

print("\nSTEP 2: DATA CLEANING")
print("-"*80)

# If protein_class is invalid (all -1), re-create from 'type'
if not df['protein_class'].isin([0, 1]).any():
    print("⚠ Invalid protein_class values detected. Re‑creating from 'type' column.")
    if 'type' in df.columns:
        type_to_class = {'Thermophile': 1, 'Mesophile': 0}
        df['protein_class'] = df['type'].map(type_to_class)
        df = df.dropna(subset=['protein_class']).reset_index(drop=True)
        print(f"✓ Re‑created protein_class: {(df['protein_class']==1).sum()} Archaea, {(df['protein_class']==0).sum()} Bacteria")
    else:
        raise ValueError("Cannot fix protein_class: 'type' column missing.")

# Keep only valid classes (0 and 1)
df = df[df['protein_class'].isin([0, 1])].reset_index(drop=True)

print(f"\nData after cleaning:")
print(f"  Samples: {len(df)}")
print(f"  Archaea (1): {(df['protein_class']==1).sum()}")
print(f"  Bacteria (0): {(df['protein_class']==0).sum()}")

# ============================================================================
# STEP 3: PREPARE FEATURES AND TARGET
# ============================================================================

print("\nSTEP 3: PREPARE FEATURES")
print("-"*80)

# Feature columns (exclude metadata)
exclude_cols = ['uniprot_id', 'organism', 'protein_name', 'protein_class', 'type', 'temperature', 'sequence']
feature_cols = [c for c in df.columns if c not in exclude_cols]

X = df[feature_cols].fillna(0).values
y = df['protein_class'].values

print(f"  Features: {len(feature_cols)}")
print(f"  X shape: {X.shape}")
print(f"  y shape: {y.shape}")

# ============================================================================
# STEP 4: CROSS-VALIDATION (Honest Generalization Estimate)
# ============================================================================

print("\n" + "="*80)
print("STEP 4: CROSS-VALIDATION PERFORMANCE")
print("="*80)

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Predictions and probabilities via cross-validation
y_pred_cv = cross_val_predict(final_pipeline, X, y, cv=cv, method='predict')
y_prob_cv = cross_val_predict(final_pipeline, X, y, cv=cv, method='predict_proba')[:, 1]

# Calculate metrics
acc_cv = accuracy_score(y, y_pred_cv)
prec_cv = precision_score(y, y_pred_cv, zero_division=0)
rec_cv = recall_score(y, y_pred_cv, zero_division=0)
f1_cv = f1_score(y, y_pred_cv, zero_division=0)
roc_cv = roc_auc_score(y, y_prob_cv)

print(f"\nCross-Validation Metrics (5-fold):")
print(f"  Accuracy:  {acc_cv:.4f}")
print(f"  Precision: {prec_cv:.4f}")
print(f"  Recall:    {rec_cv:.4f}")
print(f"  F1-Score:  {f1_cv:.4f}")
print(f"  ROC-AUC:   {roc_cv:.4f}")

# Also per-fold scores for variance
scores_acc = cross_val_score(final_pipeline, X, y, cv=cv, scoring='accuracy')
scores_roc = cross_val_score(final_pipeline, X, y, cv=cv, scoring='roc_auc')

print(f"\nPer-fold accuracy: {scores_acc}")
print(f"  Mean accuracy: {scores_acc.mean():.4f} (+/- {scores_acc.std():.4f})")
print(f"  Mean ROC-AUC: {scores_roc.mean():.4f} (+/- {scores_roc.std():.4f})")

# ============================================================================
# STEP 5: OVERFITTING DETECTION (Compare CV train vs test)
# ============================================================================

print("\n" + "="*80)
print("STEP 5: OVERFITTING DETECTION (Train vs CV Test)")
print("="*80)

# To detect overfitting, we need to compare training score (on full training fold) vs validation score.
# We can perform a manual loop storing train scores.
train_scores = []
valid_scores = []

for train_idx, val_idx in cv.split(X, y):
    X_train_fold, X_val_fold = X[train_idx], X[val_idx]
    y_train_fold, y_val_fold = y[train_idx], y[val_idx]
    
    # Clone pipeline and fit
    from sklearn.base import clone
    fold_model = clone(final_pipeline)
    fold_model.fit(X_train_fold, y_train_fold)
    
    train_acc = accuracy_score(y_train_fold, fold_model.predict(X_train_fold))
    val_acc = accuracy_score(y_val_fold, fold_model.predict(X_val_fold))
    
    train_scores.append(train_acc)
    valid_scores.append(val_acc)

mean_train_acc = np.mean(train_scores)
mean_val_acc = np.mean(valid_scores)
overfit_score = mean_train_acc - mean_val_acc

print(f"\nAverage training accuracy (across folds): {mean_train_acc:.4f}")
print(f"Average validation accuracy:               {mean_val_acc:.4f}")
print(f"Overfitting score (train - val):           {overfit_score:.4f}")

if overfit_score > 0.10:
    print("⚠ Status: SEVERE OVERFITTING (model too complex for data size)")
elif overfit_score > 0.05:
    print("⚡ Status: MILD OVERFITTING (consider regularization)")
else:
    print("✓ Status: GOOD GENERALIZATION")

# ============================================================================
# STEP 6: CONFUSION MATRIX & CLASSIFICATION REPORT
# ============================================================================

print("\n" + "="*80)
print("STEP 6: CONFUSION MATRIX (Cross-Validation Predictions)")
print("="*80)

cm = confusion_matrix(y, y_pred_cv)
tn, fp, fn, tp = cm.ravel()

print(f"\nConfusion Matrix:")
print(f"  True Negatives (TN):  {tn}")
print(f"  False Positives (FP): {fp}")
print(f"  True Positives (TP):  {tp}")
print(f"  False Negatives (FN): {fn}")

# Per-class metrics
sensitivity = tp / (tp + fn) if (tp+fn) > 0 else 0
specificity = tn / (tn + fp) if (tn+fp) > 0 else 0
precision = tp / (tp + fp) if (tp+fp) > 0 else 0

print(f"\nSensitivity (Recall for Archaea): {sensitivity:.4f}")
print(f"Specificity (for Bacteria):        {specificity:.4f}")
print(f"Precision (for Archaea):           {precision:.4f}")

print(f"\nClassification Report:")
print(classification_report(y, y_pred_cv, target_names=['Bacteria (0)', 'Archaea (1)']))

# ============================================================================
# STEP 7: FEATURE IMPORTANCE (from final model)
# ============================================================================

print("\n" + "="*80)
print("STEP 7: FEATURE IMPORTANCE (Logistic Regression Coefficients)")
print("="*80)

# Extract coefficients from the final pipeline (which includes scaler + lr)
lr_model = final_pipeline.named_steps['lr']
coefs = lr_model.coef_[0]

feature_importance = pd.DataFrame({
    'Feature': feature_cols,
    'Coefficient': coefs,
    'Abs_Coefficient': np.abs(coefs)
}).sort_values('Abs_Coefficient', ascending=False)

print(f"\nTop 10 features driving thermostability:")
for idx, row in feature_importance.head(10).iterrows():
    direction = "→ Archaea" if row['Coefficient'] > 0 else "→ Bacteria"
    print(f"  {row['Feature']:20s}: {row['Coefficient']:8.4f} {direction}")

# Save feature importance
Path('results/tables').mkdir(parents=True, exist_ok=True)
feature_importance.to_csv('results/tables/feature_importance_final.csv', index=False)
print(f"\n✓ Saved: results/tables/feature_importance_final.csv")

# ============================================================================
# STEP 8: PROBABILITY CALIBRATION
# ============================================================================

print("\n" + "="*80)
print("STEP 8: PROBABILITY CALIBRATION")
print("="*80)

high_conf = (y_prob_cv > 0.8).sum() + (y_prob_cv < 0.2).sum()
low_conf = ((y_prob_cv >= 0.3) & (y_prob_cv <= 0.7)).sum()

print(f"High confidence (>0.8 or <0.2): {high_conf}/{len(y)} ({100*high_conf/len(y):.1f}%)")
print(f"Low confidence (0.3-0.7):       {low_conf}/{len(y)} ({100*low_conf/len(y):.1f}%)")
print(f"Mean predicted probability: {y_prob_cv.mean():.4f}")
print(f"Actual class frequency: {y.mean():.4f}")
calib_diff = abs(y_prob_cv.mean() - y.mean())
print(f"Calibration difference: {calib_diff:.4f}")

if calib_diff < 0.05:
    print("Status: ✓ WELL-CALIBRATED")
elif calib_diff < 0.10:
    print("Status: ⚡ MODERATELY-CALIBRATED")
else:
    print("Status: ⚠ POORLY-CALIBRATED")

# ============================================================================
# STEP 9: SAVE ALL RESULTS
# ============================================================================

print("\n" + "="*80)
print("STEP 9: SAVE VALIDATION RESULTS")
print("="*80)

# Summary metrics
metrics_summary = pd.DataFrame({
    'Metric': ['Accuracy', 'Precision', 'Recall', 'F1-Score', 'ROC-AUC', 'Mean_CV_Accuracy', 'Std_CV_Accuracy'],
    'Value': [acc_cv, prec_cv, rec_cv, f1_cv, roc_cv, scores_acc.mean(), scores_acc.std()]
})
metrics_summary.to_csv('results/tables/validation_metrics_final.csv', index=False)
print(f"✓ Saved: results/tables/validation_metrics_final.csv")

# Overfitting report
overfit_df = pd.DataFrame({
    'Metric': ['Mean_Train_Accuracy', 'Mean_Validation_Accuracy', 'Overfit_Score'],
    'Value': [mean_train_acc, mean_val_acc, overfit_score]
})
overfit_df.to_csv('results/tables/overfit_report.csv', index=False)
print(f"✓ Saved: results/tables/overfit_report.csv")

# Confusion matrix as CSV
cm_df = pd.DataFrame(cm, index=['Actual Bacteria', 'Actual Archaea'], columns=['Pred Bacteria', 'Pred Archaea'])
cm_df.to_csv('results/tables/confusion_matrix.csv')
print(f"✓ Saved: results/tables/confusion_matrix.csv")

# ============================================================================
# FINAL SUMMARY
# ============================================================================

print("\n" + "="*80)
print("VALIDATION COMPLETE")
print("="*80)

print(f"\nKey Findings:")
print(f"  • Cross-validated accuracy: {acc_cv:.1%}")
print(f"  • ROC-AUC: {roc_cv:.3f}")
print(f"  • Overfitting score: {overfit_score:.4f} ({'low' if overfit_score<0.05 else 'moderate' if overfit_score<0.1 else 'high'})")
print(f"  • Model is {'well-calibrated' if calib_diff<0.05 else 'moderately calibrated' if calib_diff<0.1 else 'poorly calibrated'}")

print("\nFiles generated in 'results/tables/':")
print("  - validation_metrics_final.csv")
print("  - overfit_report.csv")
print("  - confusion_matrix.csv")
print("  - feature_importance_final.csv")

print("\n" + "="*80)
print("✓ VALIDATION ANALYSIS COMPLETE")
print("="*80)
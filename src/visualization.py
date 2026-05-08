"""
MODEL VISUALIZATION - PUBLICATION QUALITY
Professional figures for thermostability prediction model
"""

import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, roc_curve, auc, roc_auc_score, accuracy_score, f1_score
from sklearn.model_selection import StratifiedKFold, cross_val_predict, cross_val_score
from pathlib import Path
import warnings
warnings.filterwarnings('ignore')

# ============================================================================
# PROFESSIONAL STYLING
# ============================================================================
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 11,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'axes.labelweight': 'medium',
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'legend.fontsize': 10,
    'figure.dpi': 300,
    'savefig.dpi': 300,
    'savefig.bbox': 'tight',
    'savefig.pad_inches': 0.1
})
sns.set_style("whitegrid")
sns.set_context("paper", font_scale=1.2)

# Color palettes
ARCHAEA_COLOR = "#D55E00"   # Orange (warm)
BACTERIA_COLOR = "#0072B2"  # Blue (cool)
GRADIENT_CMAP = "viridis"
ZERO_ONE_CMAP = "RdBu_r"

out_dir = Path('results/figures')
out_dir.mkdir(parents=True, exist_ok=True)

print("="*80)
print("PROFESSIONAL MODEL VISUALIZATION")
print("="*80)

# ============================================================================
# LOAD DATA
# ============================================================================
print("\nLoading model and data...")

with open('results/models/best_thermostability_model.pkl', 'rb') as f:
    final_pipeline = pickle.load(f)

df = pd.read_csv('data/processed/protein_features_100.csv')

# Clean protein_class if needed
if not df['protein_class'].isin([0,1]).any():
    type_to_class = {'Thermophile': 1, 'Mesophile': 0}
    df['protein_class'] = df['type'].map(type_to_class)
    df = df.dropna(subset=['protein_class']).reset_index(drop=True)
df = df[df['protein_class'].isin([0,1])].reset_index(drop=True)

exclude = ['uniprot_id','organism','protein_name','protein_class','type','temperature','sequence']
feature_cols = [c for c in df.columns if c not in exclude]
X = df[feature_cols].fillna(0).values
y = df['protein_class'].values

# Cross-validated predictions
cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
y_pred = cross_val_predict(final_pipeline, X, y, cv=cv, method='predict')
y_prob = cross_val_predict(final_pipeline, X, y, cv=cv, method='predict_proba')[:, 1]

acc = accuracy_score(y, y_pred)
f1 = f1_score(y, y_pred)
roc = roc_auc_score(y, y_prob)
print(f"CV Accuracy: {acc:.3f}, F1: {f1:.3f}, ROC-AUC: {roc:.3f}")

# ============================================================================
# FIGURE 1: CONFUSION MATRIX (with percentages)
# ============================================================================
print("\n[1/5] Creating confusion matrix...")
cm = confusion_matrix(y, y_pred)
cm_norm = cm.astype('float') / cm.sum(axis=1)[:, np.newaxis] * 100

fig, ax = plt.subplots(figsize=(5.5, 4.5))
# Heatmap with custom colours
sns.heatmap(cm, annot=False, fmt='d', cmap='Blues', cbar=False,
            xticklabels=['Bacteria (Mesophile)', 'Archaea (Thermophile)'],
            yticklabels=['Bacteria (Mesophile)', 'Archaea (Thermophile)'],
            square=True, linewidths=0.5, ax=ax)

# Add annotations (count and percentage)
for i in range(2):
    for j in range(2):
        count = cm[i, j]
        pct = cm_norm[i, j]
        text = f"{count}\n({pct:.1f}%)"
        ax.text(j+0.5, i+0.5, text, ha='center', va='center',
                fontsize=11, color='white' if count > cm.max()/2 else 'black')

ax.set_title('Confusion Matrix (5‑fold Cross‑Validation)', fontweight='bold')
ax.set_ylabel('True Class', fontweight='bold')
ax.set_xlabel('Predicted Class', fontweight='bold')
plt.tight_layout()
plt.savefig(out_dir / 'fig1_confusion_matrix.svg', format='svg')
plt.savefig(out_dir / 'fig1_confusion_matrix.png')
plt.close()

# ============================================================================
# FIGURE 2: ROC CURVE (with AUC annotation)
# ============================================================================
print("[2/5] Creating ROC curve...")
fpr, tpr, _ = roc_curve(y, y_prob)
roc_auc = auc(fpr, tpr)

fig, ax = plt.subplots(figsize=(6, 5))
ax.plot(fpr, tpr, color=ARCHAEA_COLOR, lw=2.5,
        label=f'Logistic Regression (AUC = {roc_auc:.3f})')
ax.plot([0, 1], [0, 1], 'k--', lw=1.5, alpha=0.6, label='Random (AUC = 0.5)')
ax.fill_between(fpr, tpr, alpha=0.15, color=ARCHAEA_COLOR)

ax.set_xlabel('False Positive Rate (1 − Specificity)', fontweight='bold')
ax.set_ylabel('True Positive Rate (Sensitivity)', fontweight='bold')
ax.set_title('Receiver Operating Characteristic Curve', fontweight='bold')
ax.legend(loc='lower right', frameon=True)
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(out_dir / 'fig2_roc_curve.svg', format='svg')
plt.savefig(out_dir / 'fig2_roc_curve.png')
plt.close()

# ============================================================================
# FIGURE 3: PREDICTION CONFIDENCE (violin + histogram)
# ============================================================================
print("[3/5] Creating confidence distribution...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 5))

# Violin plot
data_to_plot = [y_prob[y==0], y_prob[y==1]]
parts = ax1.violinplot(data_to_plot, positions=[0,1], showmeans=True, showextrema=True)
for i, color in enumerate([BACTERIA_COLOR, ARCHAEA_COLOR]):
    parts['bodies'][i].set_facecolor(color)
    parts['bodies'][i].set_alpha(0.6)
    parts['cmeans'].set_color('black')
ax1.set_xticks([1,2])
ax1.set_xticklabels(['Mesophile', 'Thermophile'])
ax1.set_ylabel('Predicted Probability of Thermophile (Class 1)', fontweight='bold')
ax1.set_title('Prediction Confidence Distribution', fontweight='bold')
ax1.axhline(0.5, color='gray', linestyle='--', lw=1, label='Threshold')
ax1.legend()
ax1.grid(True, alpha=0.3)

# Histogram with KDE
ax2.hist(y_prob[y==0], bins=20, density=True, alpha=0.5, color=BACTERIA_COLOR, label='Mesophile', edgecolor='black')
ax2.hist(y_prob[y==1], bins=20, density=True, alpha=0.5, color=ARCHAEA_COLOR, label='Thermophile', edgecolor='black')
sns.kdeplot(y_prob[y==0], color=BACTERIA_COLOR, lw=2, ax=ax2)
sns.kdeplot(y_prob[y==1], color=ARCHAEA_COLOR, lw=2, ax=ax2)
ax2.set_xlabel('Predicted Probability of Thermophile', fontweight='bold')
ax2.set_ylabel('Density', fontweight='bold')
ax2.set_title('Probability Density', fontweight='bold')
ax2.axvline(0.5, color='gray', linestyle='--')
ax2.legend()
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig(out_dir / 'fig3_confidence_distribution.svg', format='svg')
plt.savefig(out_dir / 'fig3_confidence_distribution.png')
plt.close()

# ============================================================================
# FIGURE 4: FEATURE IMPORTANCE (Top 15, color-coded)
# ============================================================================
print("[4/5] Creating feature importance plot...")
coefs = final_pipeline.named_steps['lr'].coef_[0]
imp_df = pd.DataFrame({'Feature': feature_cols, 'Coefficient': coefs})
imp_df = imp_df.sort_values('Coefficient', key=lambda x: np.abs(x), ascending=False).head(15)
imp_df = imp_df.sort_values('Coefficient', ascending=True)  # for horizontal bar

fig, ax = plt.subplots(figsize=(9, 6))
colors = [ARCHAEA_COLOR if c > 0 else BACTERIA_COLOR for c in imp_df['Coefficient']]
bars = ax.barh(imp_df['Feature'], imp_df['Coefficient'], color=colors, alpha=0.7, edgecolor='black', linewidth=0.5)
ax.axvline(0, color='black', lw=0.8)
ax.set_xlabel('Coefficient (Positive → Thermophile)', fontweight='bold')
ax.set_title('Top 15 Features Driving Thermostability', fontweight='bold')
ax.grid(axis='x', alpha=0.3)

# Add value labels
for bar, val in zip(bars, imp_df['Coefficient']):
    ax.text(val + 0.01 if val >= 0 else val - 0.05, bar.get_y() + bar.get_height()/2,
            f'{val:.3f}', va='center', fontsize=9)

plt.tight_layout()
plt.savefig(out_dir / 'fig4_feature_importance.svg', format='svg')
plt.savefig(out_dir / 'fig4_feature_importance.png')
plt.close()

# ============================================================================
# FIGURE 5: CROSS-VALIDATION PERFORMANCE BOXPLOT
# ============================================================================
print("[5/5] Creating cross-validation boxplot...")
acc_scores = cross_val_score(final_pipeline, X, y, cv=cv, scoring='accuracy')
roc_scores = cross_val_score(final_pipeline, X, y, cv=cv, scoring='roc_auc')

fig, ax = plt.subplots(figsize=(5, 5))
data = [acc_scores, roc_scores]
bp = ax.boxplot(data, labels=['Accuracy', 'ROC-AUC'], patch_artist=True,
                boxprops=dict(facecolor='lightgray', alpha=0.7),
                medianprops=dict(color='red', linewidth=2),
                whiskerprops=dict(linewidth=1),
                capprops=dict(linewidth=1))

# Overlay swarm points
for i, scores in enumerate([acc_scores, roc_scores], start=1):
    x_jitter = np.random.normal(i, 0.04, size=len(scores))
    ax.scatter(x_jitter, scores, alpha=0.6, color='#2C3E50', s=40, edgecolor='white', linewidth=0.5)

ax.set_ylabel('Score', fontweight='bold')
ax.set_title('5‑Fold Cross‑Validation Performance', fontweight='bold')
ax.set_ylim(0.5, 1.0)
ax.grid(axis='y', alpha=0.3)

plt.tight_layout()
plt.savefig(out_dir / 'fig5_cv_performance.svg', format='svg')
plt.savefig(out_dir / 'fig5_cv_performance.png')
plt.close()

# ============================================================================
# FINAL REPORT
# ============================================================================
print("\n" + "="*80)
print("✓ All figures saved to: results/figures/")
print("   Format: PNG + SVG (vector for publication)")
print(f"\nPerformance Summary:")
print(f"  Average Accuracy: {acc:.3f} ± {np.std(acc_scores):.3f}")
print(f"  ROC-AUC: {roc:.3f}")
print("="*80)
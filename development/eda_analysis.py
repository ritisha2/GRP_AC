"""
Phase 2: Exploratory Data Analysis (EDA) - Clean Title Placement Version
Generates EDA plots with clean title margins to prevent text overlaps.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
OUTPUT_DIR = os.path.join(PROJECT_DIR, "data")
PLOT_DIR = os.path.join(PROJECT_DIR, "eda_plots")
os.makedirs(PLOT_DIR, exist_ok=True)

# Set clean white background style & padding
plt.style.use('default')
sns.set_theme(style="whitegrid", palette="tab10")
plt.rcParams['figure.dpi'] = 120
plt.rcParams['savefig.dpi'] = 150
plt.rcParams['font.size'] = 10
plt.rcParams['figure.facecolor'] = '#FFFFFF'
plt.rcParams['axes.facecolor'] = '#FFFFFF'
plt.rcParams['text.color'] = '#1A1A1A'
plt.rcParams['axes.labelcolor'] = '#1A1A1A'
plt.rcParams['xtick.color'] = '#1A1A1A'
plt.rcParams['ytick.color'] = '#1A1A1A'


def load_cleaned_data():
    df_prod = pd.read_csv(os.path.join(OUTPUT_DIR, "production_clean.csv"))
    df_qual = pd.read_csv(os.path.join(OUTPUT_DIR, "quality_clean.csv"))
    df_eval = pd.read_csv(os.path.join(OUTPUT_DIR, "evaluation_clean.csv"))
    return df_prod, df_qual, df_eval


def eda_01_quality_distributions(df_qual):
    """Histograms for all 11 quality target variables."""
    quality_cols = [c for c in df_qual.columns if c != 'Batch No.']
    
    fig, axes = plt.subplots(3, 4, figsize=(18, 12), facecolor='white')
    fig.suptitle('Distribution of Orange Quality Parameters', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    
    for idx, col in enumerate(quality_cols):
        ax = axes[idx // 4, idx % 4]
        data = df_qual[col].dropna()
        ax.hist(data, bins=20, color='#FDBA74', edgecolor='#EA580C', alpha=0.85)
        ax.axvline(data.mean(), color='#DC2626', linestyle='--', linewidth=1.5, label=f'Mean={data.mean():.2f}')
        ax.axvline(data.median(), color='#2563EB', linestyle=':', linewidth=1.5, label=f'Median={data.median():.2f}')
        ax.set_title(col, fontsize=11, fontweight='bold', color='#1F2937', pad=10)
        ax.legend(fontsize=8)
        ax.set_facecolor('white')
    
    if len(quality_cols) < 12:
        axes[2, 3].set_visible(False)
    
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(PLOT_DIR, "01_quality_distributions.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_02_production_distributions(df_prod):
    """Histograms for numeric production features."""
    numeric_cols = df_prod.select_dtypes(include=[np.number]).columns.tolist()
    n = len(numeric_cols)
    ncols = 4
    nrows = (n + ncols - 1) // ncols
    
    fig, axes = plt.subplots(nrows, ncols, figsize=(18, 3.8 * nrows), facecolor='white')
    fig.suptitle('Distribution of Production Process Parameters', fontsize=17, fontweight='bold', color='#D97706', y=0.995)
    
    for idx, col in enumerate(numeric_cols):
        ax = axes[idx // ncols, idx % ncols] if nrows > 1 else axes[idx % ncols]
        data = df_prod[col].dropna()
        if len(data) > 0:
            ax.hist(data, bins=20, color='#93C5FD', edgecolor='#2563EB', alpha=0.85)
            ax.set_title(col[:40], fontsize=9, fontweight='bold', color='#1F2937', pad=8)
            ax.tick_params(labelsize=7)
            ax.set_facecolor('white')
    
    for idx in range(n, nrows * ncols):
        ax = axes[idx // ncols, idx % ncols] if nrows > 1 else axes[idx % ncols]
        ax.set_visible(False)
    
    plt.tight_layout(rect=[0, 0, 1, 0.975])
    path = os.path.join(PLOT_DIR, "02_production_distributions.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_03_quality_by_shift(df_prod, df_qual):
    """Box plots: Quality targets grouped by Shift."""
    quality_cols = [c for c in df_qual.columns if c != 'Batch No.']
    combined = pd.concat([df_prod[['Shift']], df_qual[quality_cols]], axis=1)
    
    fig, axes = plt.subplots(3, 4, figsize=(18, 12), facecolor='white')
    fig.suptitle('Quality Parameters by Production Shift', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    
    for idx, col in enumerate(quality_cols):
        ax = axes[idx // 4, idx % 4]
        combined.boxplot(column=col, by='Shift', ax=ax, patch_artist=True,
                        boxprops=dict(facecolor='#FED7AA', color='#EA580C'),
                        medianprops=dict(color='#DC2626', linewidth=2))
        ax.set_title(col, fontsize=11, fontweight='bold', color='#1F2937', pad=10)
        ax.set_xlabel('')
        ax.set_facecolor('white')
        plt.sca(ax)
        plt.xticks(fontsize=8, rotation=15)
    
    if len(quality_cols) < 12:
        axes[2, 3].set_visible(False)
    
    fig.suptitle('Quality Parameters by Production Shift', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(PLOT_DIR, "03_quality_by_shift.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_04_quality_by_supervisor(df_prod, df_qual):
    """Box plots: Quality targets grouped by Supervisor."""
    quality_cols = [c for c in df_qual.columns if c != 'Batch No.']
    combined = pd.concat([df_prod[['Supervisor']], df_qual[quality_cols]], axis=1)
    
    fig, axes = plt.subplots(3, 4, figsize=(20, 13), facecolor='white')
    fig.suptitle('Quality Parameters by Supervisor', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    
    for idx, col in enumerate(quality_cols):
        ax = axes[idx // 4, idx % 4]
        combined.boxplot(column=col, by='Supervisor', ax=ax, patch_artist=True,
                        boxprops=dict(facecolor='#BBF7D0', color='#16A34A'),
                        medianprops=dict(color='#DC2626', linewidth=2))
        ax.set_title(col, fontsize=11, fontweight='bold', color='#1F2937', pad=10)
        ax.set_xlabel('')
        ax.set_facecolor('white')
        plt.sca(ax)
        plt.xticks(fontsize=7, rotation=45, ha='right')
    
    if len(quality_cols) < 12:
        axes[2, 3].set_visible(False)
    
    fig.suptitle('Quality Parameters by Supervisor', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(PLOT_DIR, "04_quality_by_supervisor.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_05_quality_by_customer(df_prod, df_qual):
    """Box plots: Quality targets grouped by Customer."""
    quality_cols = [c for c in df_qual.columns if c != 'Batch No.']
    combined = pd.concat([df_prod[['Customer']], df_qual[quality_cols]], axis=1)
    
    fig, axes = plt.subplots(3, 4, figsize=(18, 12), facecolor='white')
    fig.suptitle('Quality Parameters by Customer', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    
    for idx, col in enumerate(quality_cols):
        ax = axes[idx // 4, idx % 4]
        combined.boxplot(column=col, by='Customer', ax=ax, patch_artist=True,
                        boxprops=dict(facecolor='#BFDBFE', color='#2563EB'),
                        medianprops=dict(color='#DC2626', linewidth=2))
        ax.set_title(col, fontsize=11, fontweight='bold', color='#1F2937', pad=10)
        ax.set_xlabel('')
        ax.set_facecolor('white')
        plt.sca(ax)
        plt.xticks(fontsize=8, rotation=30, ha='right')
    
    if len(quality_cols) < 12:
        axes[2, 3].set_visible(False)
    
    fig.suptitle('Quality Parameters by Customer', fontsize=16, fontweight='bold', color='#D97706', y=0.99)
    plt.tight_layout(rect=[0, 0, 1, 0.96])
    path = os.path.join(PLOT_DIR, "05_quality_by_customer.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_06_correlation_heatmap(df_prod, df_qual):
    """Cross-correlation heatmap: Production (X) vs Quality (Y)."""
    quality_cols = [c for c in df_qual.columns if c != 'Batch No.']
    prod_numeric = df_prod.select_dtypes(include=[np.number])
    
    corr_matrix = pd.DataFrame(index=quality_cols, columns=prod_numeric.columns, dtype=float)
    for q_col in quality_cols:
        for p_col in prod_numeric.columns:
            mask = ~(prod_numeric[p_col].isna() | df_qual[q_col].isna())
            if mask.sum() > 10:
                corr_matrix.loc[q_col, p_col] = prod_numeric.loc[mask, p_col].corr(df_qual.loc[mask, q_col])
    
    corr_matrix = corr_matrix.astype(float)
    
    fig, ax = plt.subplots(figsize=(22, 10), facecolor='white')
    sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='RdBu_r', center=0,
                vmin=-1, vmax=1, linewidths=0.5, ax=ax,
                annot_kws={'size': 7, 'color': '#111827'},
                cbar_kws={'label': 'Pearson Correlation (r)'})
    ax.set_title('Production Features vs. Orange Quality Parameters\n(Cross-Correlation Heatmap)',
                 fontsize=16, fontweight='bold', color='#D97706', pad=20)
    ax.set_xlabel('Production Data Features (X-Axis)', fontsize=13, color='#1F2937', fontweight='bold')
    ax.set_ylabel('Orange Quality Data Parameters (Y-Axis)', fontsize=13, color='#EA580C', fontweight='bold')
    ax.set_facecolor('white')
    plt.xticks(fontsize=7, rotation=90, color='#1F2937')
    plt.yticks(fontsize=9, color='#1F2937')
    
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "06_correlation_heatmap.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_07_production_multicollinearity(df_prod):
    """Correlation heatmap among production features."""
    prod_numeric = df_prod.select_dtypes(include=[np.number])
    corr = prod_numeric.corr()
    
    fig, ax = plt.subplots(figsize=(18, 15), facecolor='white')
    mask = np.triu(np.ones_like(corr, dtype=bool))
    sns.heatmap(corr, mask=mask, annot=True, fmt='.2f', cmap='coolwarm', center=0,
                vmin=-1, vmax=1, linewidths=0.3, ax=ax, annot_kws={'size': 6})
    ax.set_title('Multi-Collinearity: Production Features Inter-Correlation',
                 fontsize=14, fontweight='bold', color='#D97706', pad=15)
    ax.set_facecolor('white')
    plt.xticks(fontsize=7, rotation=90)
    plt.yticks(fontsize=7)
    
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "07_production_multicollinearity.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_08_target_intercorrelation(df_qual):
    """Correlation among the 11 quality targets."""
    quality_cols = [c for c in df_qual.columns if c != 'Batch No.']
    corr = df_qual[quality_cols].corr()
    
    fig, ax = plt.subplots(figsize=(10, 8), facecolor='white')
    sns.heatmap(corr, annot=True, fmt='.2f', cmap='YlOrRd', center=0,
                vmin=-1, vmax=1, linewidths=0.5, ax=ax,
                annot_kws={'size': 10, 'color': '#111827'})
    ax.set_title('Inter-Correlation Among Quality Targets',
                 fontsize=14, fontweight='bold', color='#D97706', pad=15)
    ax.set_facecolor('white')
    
    plt.tight_layout()
    path = os.path.join(PLOT_DIR, "08_target_intercorrelation.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def eda_09_success_analysis(df_eval, df_qual):
    """Success % distribution and which parameters fail most."""
    if 'Success %' not in df_eval.columns:
        return
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5.5), facecolor='white')
    fig.suptitle('Quality Success Rate Analysis', fontsize=15, fontweight='bold', color='#D97706', y=0.99)
    
    ax = axes[0]
    df_eval['Success %'].dropna().hist(bins=15, ax=ax, color='#16A34A', edgecolor='white', alpha=0.85)
    ax.set_title('Distribution of Success %', fontsize=12, color='#1F2937', pad=10)
    ax.set_xlabel('Success %')
    ax.set_ylabel('Count')
    ax.set_facecolor('white')
    
    specs = {
        'AC Mooney': (50, 60), 'Ash%': (3, 7), 'C.B.%': (28, 36),
        'A.E.%': (6, 12), 'V.M.%': (0, 1), 'RHC': (50, 999),
        'Sp.Gravity': (1.12, 1.16), 'Mv': (30, 45), 'TS': (75, 999),
        'EB': (480, 999), 'Hardness': (48, 54)
    }
    
    fail_counts = {}
    for param, (lo, hi) in specs.items():
        if param in df_qual.columns:
            vals = pd.to_numeric(df_qual[param], errors='coerce').dropna()
            fails = ((vals < lo) | (vals > hi)).sum()
            fail_counts[param] = fails
    
    ax = axes[1]
    params = list(fail_counts.keys())
    counts = list(fail_counts.values())
    bars = ax.barh(params, counts, color='#DC2626', edgecolor='white')
    ax.set_title('Parameters: Out-of-Spec Failure Count', fontsize=12, color='#1F2937', pad=10)
    ax.set_xlabel('Number of Batches Failing Spec')
    ax.set_facecolor('white')
    for bar, count in zip(bars, counts):
        if count > 0:
            ax.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height()/2, str(count),
                    va='center', fontsize=9, color='#1F2937', fontweight='bold')
    
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    path = os.path.join(PLOT_DIR, "09_success_analysis.png")
    plt.savefig(path, bbox_inches='tight', facecolor='white')
    plt.close()
    print(f"  Saved: {path}")


def main():
    print("=" * 60)
    print("REGENERATING EDA PLOTS (FIXED TITLE PADDING)")
    print("=" * 60)
    
    df_prod, df_qual, df_eval = load_cleaned_data()
    
    eda_01_quality_distributions(df_qual)
    eda_02_production_distributions(df_prod)
    eda_03_quality_by_shift(df_prod, df_qual)
    eda_04_quality_by_supervisor(df_prod, df_qual)
    eda_05_quality_by_customer(df_prod, df_qual)
    eda_06_correlation_heatmap(df_prod, df_qual)
    eda_07_production_multicollinearity(df_prod)
    eda_08_target_intercorrelation(df_qual)
    eda_09_success_analysis(df_eval, df_qual)
    
    print("\nALL PLOTS REGENERATED WITH CLEAN MARGINS AND NO OVERLAPPING TITLES!")

if __name__ == "__main__":
    main()

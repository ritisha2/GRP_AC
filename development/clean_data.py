"""
Phase 1: Data Cleaning Script
Cleans production_data.csv and orange_quality_data.csv for EDA and modeling.
"""

import pandas as pd
import numpy as np
import re
import os

OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data"))

def parse_duration_to_minutes(val):
    """Convert HH:MM or HH:MM:SS strings to numeric minutes."""
    if pd.isna(val):
        return np.nan
    val_str = str(val).strip()
    if val_str in ['0', '0:0', '0:00', '00:00', '00:00:00', '0:0:0']:
        return 0.0
    parts = val_str.split(':')
    try:
        if len(parts) == 3:
            return float(parts[0]) * 60 + float(parts[1]) + float(parts[2]) / 60.0
        elif len(parts) == 2:
            return float(parts[0]) * 60 + float(parts[1])
        else:
            return float(val)
    except (ValueError, TypeError):
        return np.nan


def clean_production_data(df):
    """Clean the production dataframe."""
    
    # 1. Drop the corrupted summary row (row 145: all zeros)
    bad_rows = df[df['BT- Recipe'] == '0'].index
    df = df.drop(bad_rows).reset_index(drop=True)
    print(f"Dropped {len(bad_rows)} corrupted row(s). Remaining: {len(df)} rows.")

    # 2. Drop columns that are 99%+ zeros (almost never recorded)
    cols_to_drop_near_empty = [
        'Discharge Valve Open Temp (°C)',
        'Discharge Valve Open Pressure (kg/cm2)',
        'Discharge Valve Open Time (HH:MM)',
        'Discharge Start Time (HH:MM)',
        'Discharge Stop Time (HH:MM)',
        'Discharge Duration (HH:MM)',
        'Waiting Temp(°C)',
        'Waiting Pressure (kg/cm2)',
        'Waiting Time (HH:MM)',
        'Top door ( sample collect ) Temp(°C)',
        'Top door ( sample collect ) Pressure (kg/cm2)',
        'Top door ( sample collect ) Time (HH:MM)',
        'Sampling End Time (HH:MM)',
        'Sampling Duration (HH:MM)',
    ]
    
    # 3. Drop non-predictive / identifier columns
    cols_to_drop_identifiers = [
        'S/N',
        'Autoclave',        # Always AC10
        'Form Filled By',   # Always same operator
        'Form Filled At',   # Timestamp of form entry
        'Batch ID',          # Unique ID — not a feature
        'BT- Recipe',        # Always Recipe1
        'Comment',           # Free-text, 97% missing
        'Batch kWh',         # 97% missing
    ]
    
    # 4. Drop absolute time columns (not durations — just clock times)
    time_cols_absolute = [col for col in df.columns if 'Time (HH:MM)' in col and 'Duration' not in col]
    
    # Combine all columns to drop (only drop if they exist)
    all_drop = set(cols_to_drop_near_empty + cols_to_drop_identifiers + time_cols_absolute)
    existing_drop = [c for c in all_drop if c in df.columns]
    
    # Also try with degree symbol variations
    for col in df.columns:
        base = col
        for target in cols_to_drop_near_empty + cols_to_drop_identifiers:
            # Normalize both for comparison (remove non-ascii)
            norm_col = re.sub(r'[^\x00-\x7F]', '', col).strip()
            norm_target = re.sub(r'[^\x00-\x7F]', '', target).strip()
            if norm_col == norm_target and col not in existing_drop:
                existing_drop.append(col)
    
    # Also drop absolute time columns by pattern matching
    for col in df.columns:
        if 'Time (HH:MM)' in col and 'Duration' not in col and col not in existing_drop:
            existing_drop.append(col)
    
    df = df.drop(columns=existing_drop, errors='ignore')
    print(f"Dropped {len(existing_drop)} non-useful columns. Remaining: {df.shape[1]} columns.")

    # 5. Replace 0-as-missing with NaN in temperature/pressure columns
    #    (0°C or 0 kg/cm2 is physically invalid for autoclave readings)
    temp_pressure_cols = [c for c in df.columns 
                          if ('Temp' in c or 'Pressure' in c) 
                          and df[c].dtype in ['int64', 'float64']]
    
    for col in temp_pressure_cols:
        zero_count = (df[col] == 0).sum()
        if zero_count > 0:
            df[col] = df[col].replace(0, np.nan)
            print(f"  Replaced {zero_count} zeros with NaN in '{col}'")

    # 6. Parse duration columns to numeric minutes
    duration_cols = [c for c in df.columns if 'Duration' in c]
    for col in duration_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].apply(parse_duration_to_minutes)
            print(f"  Parsed duration column '{col}' to minutes")

    # 7. Ensure Machine Idle is clean binary
    if 'Machine Idle' in df.columns:
        df['Machine Idle'] = df['Machine Idle'].map({'Yes': 1, 'No': 0}).fillna(0).astype(int)

    return df


def clean_quality_data(df):
    """Clean the orange quality dataframe."""
    
    # 1. Drop corrupted row (Batch No. == '0')
    bad_rows = df[df['Batch No.'] == '0'].index
    df = df.drop(bad_rows).reset_index(drop=True)
    print(f"Dropped {len(bad_rows)} corrupted quality row(s). Remaining: {len(df)} rows.")

    # 2. Convert Sp.Gravity from string to float
    if df['Sp.Gravity'].dtype == 'object':
        df['Sp.Gravity'] = pd.to_numeric(df['Sp.Gravity'], errors='coerce')
        print("  Converted Sp.Gravity to float.")

    # 3. Drop the Batch No. column (it's an identifier, not a feature)
    # Keep it for now as a reference, but mark it
    
    return df


def clean_eval_data(df):
    """Clean the quality evaluation dataframe."""
    bad_rows = df[df['Batch No.'] == '0'].index
    df = df.drop(bad_rows).reset_index(drop=True)
    
    # Convert Sp.Gravity to float
    if 'Sp.Gravity' in df.columns and df['Sp.Gravity'].dtype == 'object':
        df['Sp.Gravity'] = pd.to_numeric(df['Sp.Gravity'], errors='coerce')
    
    # Clean Success % column
    if 'Success % off all parameters average' in df.columns:
        df['Success %'] = df['Success % off all parameters average'].apply(
            lambda x: float(str(x).replace('%', '')) if pd.notna(x) and str(x) not in ['0', '1'] 
            else (100.0 if str(x) == '1' else (0.0 if str(x) == '0' else np.nan))
        )
    
    return df


def main():
    print("=" * 60)
    print("PHASE 1: DATA CLEANING")
    print("=" * 60)
    
    # Load raw CSVs
    df_prod = pd.read_csv(os.path.join(OUTPUT_DIR, "production_data.csv"))
    df_qual = pd.read_csv(os.path.join(OUTPUT_DIR, "orange_quality_data.csv"))
    df_eval = pd.read_csv(os.path.join(OUTPUT_DIR, "quality_evaluation_data.csv"))
    
    print(f"\nRaw shapes: Prod={df_prod.shape}, Qual={df_qual.shape}, Eval={df_eval.shape}")
    
    # Clean each table
    print("\n--- Cleaning Production Data ---")
    df_prod_clean = clean_production_data(df_prod)
    
    print("\n--- Cleaning Orange Quality Data ---")
    df_qual_clean = clean_quality_data(df_qual)
    
    print("\n--- Cleaning Quality Evaluation Data ---")
    df_eval_clean = clean_eval_data(df_eval)
    
    # Verify row alignment
    assert len(df_prod_clean) == len(df_qual_clean) == len(df_eval_clean), \
        f"Row count mismatch! Prod={len(df_prod_clean)}, Qual={len(df_qual_clean)}, Eval={len(df_eval_clean)}"
    
    # Save cleaned CSVs
    prod_clean_path = os.path.join(OUTPUT_DIR, "production_clean.csv")
    qual_clean_path = os.path.join(OUTPUT_DIR, "quality_clean.csv")
    eval_clean_path = os.path.join(OUTPUT_DIR, "evaluation_clean.csv")
    
    df_prod_clean.to_csv(prod_clean_path, index=False, encoding="utf-8-sig")
    df_qual_clean.to_csv(qual_clean_path, index=False, encoding="utf-8-sig")
    df_eval_clean.to_csv(eval_clean_path, index=False, encoding="utf-8-sig")
    
    print("\n" + "=" * 60)
    print("CLEANING COMPLETE")
    print("=" * 60)
    print(f"\nCleaned Production Data:  {df_prod_clean.shape} -> {prod_clean_path}")
    print(f"Cleaned Quality Data:    {df_qual_clean.shape} -> {qual_clean_path}")
    print(f"Cleaned Evaluation Data: {df_eval_clean.shape} -> {eval_clean_path}")
    
    print(f"\nProduction columns remaining ({df_prod_clean.shape[1]}):")
    for i, c in enumerate(df_prod_clean.columns):
        dtype = df_prod_clean[c].dtype
        nulls = df_prod_clean[c].isnull().sum()
        print(f"  {i+1:2d}. {c:<55s} dtype={str(dtype):<10s} nulls={nulls}")
    
    print(f"\nQuality target columns ({df_qual_clean.shape[1]}):")
    for c in df_qual_clean.columns:
        print(f"  {c}: dtype={df_qual_clean[c].dtype}, nulls={df_qual_clean[c].isnull().sum()}")


if __name__ == "__main__":
    main()

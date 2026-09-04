"""
predict_terminal.py
===================
Interactive Terminal Application for ALL 11 Quality Parameters Prediction
and Golden Batch Classification.

Features:
1. Predicts ALL 11 Quality Parameters (AC Mooney, Ash%, C.B.%, A.E.%, V.M.%, RHC, Sp.Gravity, Mv, TS, EB, Hardness).
2. Evaluates individual Spec Limits (Pass / Fail) for every parameter.
3. Computes Batch Success % = (Pass Count / 11) * 100%.
4. Determines Golden Batch Status:
   - 90.0% – 100.0% ──► 🌟 GOLDEN BATCH
   - 75.0% – 89.9%  ──► ⚠️ STANDARD BATCH
   - < 75.0%        ──► ❌ NON-CONFORMING BATCH
5. Supports Batch Lookup Mode & Interactive Manual Entry Mode.

Usage:
    $env:PYTHONIOENCODING='utf-8'; python predict_terminal.py
"""

import pandas as pd
import numpy as np
import pickle
import os

# ─────────────────────────────────────────────────────────────
# 1. Load Saved Models & Datasets
# ─────────────────────────────────────────────────────────────
print("=" * 75)
print("  Loading trained 11-Model Suite & Datasets from models/ ...")
print("=" * 75)

with open("models/all_quality_models.pkl", "rb") as f:
    models_dict = pickle.load(f)
with open("models/imputer.pkl", "rb") as f:
    imputer = pickle.load(f)
with open("models/feature_cols.pkl", "rb") as f:
    feature_cols = pickle.load(f)

# Load clean production and quality datasets for Batch Lookup Mode
prod_df = pd.read_csv("production_clean.csv")
qual_df = pd.read_csv("quality_clean.csv")

print("  ✅ All 11 Models & Preprocessors loaded successfully.\n")

# Order of target display
TARGET_ORDER = [
    "AC Mooney", "Ash%", "C.B.%", "A.E.%", "V.M.%",
    "RHC", "Sp.Gravity", "Mv", "TS", "EB", "Hardness"
]


def parse_duration(val_str, default_val):
    """Parses input string into a float minute value. Handles 'HH:MM' or float inputs."""
    val_str = str(val_str).strip()
    if not val_str or val_str.lower() == "nan":
        return default_val
    if ":" in val_str:
        try:
            parts = val_str.split(":")
            hours = float(parts[0])
            minutes = float(parts[1])
            return hours * 60.0 + minutes
        except Exception:
            return default_val
    try:
        return float(val_str)
    except ValueError:
        return default_val


def prepare_feature_row(prod_row_dict):
    """
    Transforms raw production inputs into the exact engineered feature DataFrame
    expected by the 11 trained ML models.
    """
    row_data = {}
    
    # Fill raw 14 numeric features
    for col in imputer.feature_names_in_:
        val = prod_row_dict.get(col, np.nan)
        row_data[col] = parse_duration(val, np.nan)

    raw_df = pd.DataFrame([row_data], columns=imputer.feature_names_in_)
    
    # Median impute
    imputed_vals = imputer.transform(raw_df)
    X_feat = pd.DataFrame(imputed_vals, columns=imputer.feature_names_in_)

    # Energy compaction interactions (Pressure * Temp)
    X_feat["Steam_PT_Energy"] = X_feat["Steam Valve Close Temp (°C)"] * X_feat["Steam Valve Close Pressure (kg/cm2)"]
    X_feat["Heat_PT_Energy"] = X_feat["Heat Valve Close Temp (°C)"] * X_feat["Heat Valve Close Pressure (kg/cm2)"]
    X_feat["Cool_PT_Energy"] = X_feat["Cooling Valve Open Temp(°C)"] * X_feat["Cooling Valve Open Pressure (kg/cm2)"]
    X_feat["Door_PT_Energy"] = X_feat["Bottom Door Open Temp(°C)"] * X_feat["Bottom Door Open Pressure (kg/cm2)"]

    # Duration Ratios & Thermal Dose
    X_feat["Cook_Ratio"] = X_feat["Cooking Duration (HH:MM)"] / (X_feat["Actual Batch Duration (Mins)"] + 1e-5)
    X_feat["LowTF_Ratio"] = X_feat["Low TF Temp Duration(Mins) (Below 260°C)"] / (X_feat["Actual Batch Duration (Mins)"] + 1e-5)
    X_feat["Thermal_Dose"] = X_feat["Heat Valve Close Temp (°C)"] * X_feat["Cooking Duration (HH:MM)"]
    X_feat["Steam_Thermal_Dose"] = X_feat["Steam Valve Close Temp (°C)"] * X_feat["Cooking Duration (HH:MM)"]

    # Physics Baselines for All 11 Targets
    X_feat["Physics_Mooney_Base"] = 58.0 + 0.25 * (X_feat["Bottom Door Open Temp(°C)"] - 104) + 0.05 * (X_feat["Cooking Duration (HH:MM)"] - 245) - 0.20 * (X_feat["Bottom Door Open Pressure (kg/cm2)"] - 0.10)
    X_feat["Physics_Ash_Base"] = 5.61 + 0.006 * (X_feat["Cooling Valve Open Temp(°C)"] - 210) - 0.050 * (X_feat["Steam Valve Close Pressure (kg/cm2)"] - 5.35) + 0.015 * (X_feat["Bottom Door Open Temp(°C)"] - 104)
    X_feat["Physics_CB_Base"] = 30.24 - 0.095 * (X_feat["Steam Valve Close Pressure (kg/cm2)"] - 5.35) - 0.005 * (X_feat["Cooling Valve Open Temp(°C)"] - 210) + 0.002 * (X_feat["Heat Valve Close Temp (°C)"] - 222)
    X_feat["Physics_AE_Base"] = 7.43 + 0.031 * (X_feat["Heat Valve Close Pressure (kg/cm2)"] - 14.46) - 0.003 * (X_feat["Cooking Duration (HH:MM)"] - 245)
    X_feat["Physics_VM_Base"] = 0.192 - 0.004 * (X_feat["Steam Valve Close Pressure (kg/cm2)"] - 5.35) + 0.0001 * (X_feat["Low TF Temp Duration(Mins) (Below 260°C)"] - 233)
    X_feat["Physics_RHC_Base"] = 56.40 + 0.073 * (X_feat["Cooling Valve Open Pressure (kg/cm2)"] - 0.37) + 0.007 * (X_feat["Steam Valve Open Temp (°C)"] - 96)
    X_feat["Physics_SG_Base"] = 1.151 + 0.001 * (X_feat["Heat Valve Close Pressure (kg/cm2)"] - 14.46) + 0.002 * (X_feat["Bottom Door Open Pressure (kg/cm2)"] - 0.10)
    X_feat["Physics_Mv_Base"] = 40.0 + 0.100 * (X_feat["Heat Valve Close Temp (°C)"] - 222) + 0.045 * (X_feat["Steam Valve Open Temp (°C)"] - 96) - 0.012 * (X_feat["Actual Batch Duration (Mins)"] - 369)
    X_feat["Physics_TS_Base"] = 85.28 - 0.238 * (X_feat["Steam Valve Open Temp (°C)"] - 96) - 0.048 * (X_feat["Cooling Valve Open Temp(°C)"] - 210) - 0.026 * (X_feat["Actual Batch Duration (Mins)"] - 369)
    X_feat["Physics_EB_Base"] = 507.5 + 0.719 * (X_feat["Cooling Valve Open Pressure (kg/cm2)"] - 0.37) + 0.035 * (X_feat["Low TF Temp Duration(Mins) (Below 260°C)"] - 233)
    X_feat["Physics_Hardness_Base"] = 51.0 - 0.008 * (X_feat["Cooling Valve Open Temp(°C)"] - 210) - 0.027 * (X_feat["Steam Valve Open Temp (°C)"] - 96) + 0.010 * (X_feat["Heat Valve Close Temp (°C)"] - 222)

    # Reindex to ensure exact feature columns and order
    return X_feat.reindex(columns=feature_cols, fill_value=0.0)


def display_predictions(batch_id, predictions_dict, actual_dict=None):
    """Prints a styled prediction summary card for ALL 11 Quality Parameters."""
    print("\n" + "═" * 80)
    print(f"  FULL 11-PARAMETER PREDICTION & GOLDEN BATCH REPORT FOR: {batch_id}")
    print("═" * 80)

    pass_count = 0
    total_params = len(TARGET_ORDER)

    if actual_dict is not None:
        print(f"""
  ┌─────────────────────────────────────────────────────────────────────────────────────────┐
  │ Parameter   │ Predicted  │ Actual Lab │ Error      │ Min Spec │ Max Spec │ Spec Status  │
  ├─────────────────────────────────────────────────────────────────────────────────────────┤""")
        for target in TARGET_ORDER:
            pred_val = predictions_dict[target]
            actual_val = actual_dict.get(target, np.nan)
            spec_min = models_dict[target]["spec_min"]
            spec_max = models_dict[target]["spec_max"]
            
            is_pass = spec_min <= pred_val <= spec_max
            if is_pass:
                pass_count += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                
            if not pd.isna(actual_val):
                err = pred_val - actual_val
                print(f"  │ {target:<11} │ {pred_val:>10.4f} │ {actual_val:>10.4f} │ {err:>+10.4f} │ {spec_min:>8.2f} │ {spec_max:>8.2f} │   {status}    │")
            else:
                print(f"  │ {target:<11} │ {pred_val:>10.4f} │ {'N/A':>10} │ {'N/A':>10} │ {spec_min:>8.2f} │ {spec_max:>8.2f} │   {status}    │")
        print("  └─────────────────────────────────────────────────────────────────────────────────────────┘")
    else:
        print(f"""
  ┌────────────────────────────────────────────────────────────────────────────┐
  │ Parameter   │ Predicted Value │ Min Spec Limit │ Max Spec Limit │ Status   │
  ├────────────────────────────────────────────────────────────────────────────┤""")
        for target in TARGET_ORDER:
            pred_val = predictions_dict[target]
            spec_min = models_dict[target]["spec_min"]
            spec_max = models_dict[target]["spec_max"]
            
            is_pass = spec_min <= pred_val <= spec_max
            if is_pass:
                pass_count += 1
                status = "✅ PASS"
            else:
                status = "❌ FAIL"
                
            print(f"  │ {target:<11} │   {pred_val:>11.4f}   │   {spec_min:>10.2f}   │   {spec_max:>10.2f}   │ {status}  │")
        print("  └────────────────────────────────────────────────────────────────────────────┘")

    # Success % & Golden Batch Evaluation
    success_pct = round((pass_count / total_params) * 100, 1)

    if success_pct >= 90.0:
        badge = "🌟 GOLDEN BATCH (Optimal Production Run)"
    elif success_pct >= 75.0:
        badge = "⚠️ STANDARD BATCH (Acceptable Run)"
    else:
        badge = "❌ NON-CONFORMING BATCH (Quality Defect Risk)"

    print(f"\n  ┌────────────────────────────────────────────────────────────────────────────┐")
    print(f"  │ MARKS & SUCCESS SCORE EVALUATION:                                           │")
    print(f"  ├────────────────────────────────────────────────────────────────────────────┤")
    print(f"  │  • Total Quality Marks Possible : {total_params:>2} Parameters                          │")
    print(f"  │  • Obtained Marks (Passed)     : {pass_count:>2} / {total_params} Parameters                     │")
    print(f"  │  • Calculated Success %        : ({pass_count} / {total_params}) × 100% = {success_pct:>5.1f}%             │")
    print(f"  │  • Golden Batch Status         : {badge:<40}  │")
    print(f"  └────────────────────────────────────────────────────────────────────────────┘\n")


# ─────────────────────────────────────────────────────────────
# 2. Main Terminal Application
# ─────────────────────────────────────────────────────────────
print("─" * 80)
print("  MODE SELECTION:")
print("  • Type a Batch ID (e.g. SB40624, SB40311, SB40621) to predict an existing batch")
print("  • Type 'list' to view available Batch IDs")
print("  • Press ENTER to input production parameters manually")
print("─" * 80)

user_choice = input("  Enter Batch ID or press ENTER for manual input: ").strip()

if user_choice.lower() == "list":
    available_batches = qual_df["Batch No."].tolist()
    print(f"\n  Available Batches ({len(available_batches)} total):")
    print("  " + ", ".join(available_batches[:35]) + " ...")
    user_choice = input("\n  Enter a Batch ID from above: ").strip()

# Check if user entered a Batch ID
matched_qual = qual_df[qual_df["Batch No."].astype(str).str.upper() == user_choice.upper()]

if not matched_qual.empty:
    idx = matched_qual.index[0]
    batch_no = qual_df.iloc[idx]["Batch No."]
    prod_row = prod_df.iloc[idx].to_dict()

    actual_dict = {target: qual_df.iloc[idx][target] for target in TARGET_ORDER}

    print(f"\n  Found Batch '{batch_no}' at Row #{idx + 1}!")
    print("  Loading production parameters and evaluating all 11 ML models ...")

    X_feat = prepare_feature_row(prod_row)
    
    predictions_dict = {}
    for target in TARGET_ORDER:
        model = models_dict[target]["model"]
        predictions_dict[target] = model.predict(X_feat)[0]

    display_predictions(batch_no, predictions_dict, actual_dict)

else:
    if user_choice != "":
        print(f"\n  ⚠️ Batch ID '{user_choice}' not found in dataset. Switching to Manual Input Mode.")

    print("\n" + "─" * 80)
    print("  MANUAL PRODUCTION PARAMETER ENTRY")
    print("  (Press ENTER to accept the default baseline value for any field)")
    print("─" * 80)

    KEY_INPUTS = [
        ("Steam Valve Open Temp (°C)", 96.0),
        ("Steam Valve Open Pressure (kg/cm2)", 0.55),
        ("Steam Valve Close Temp (°C)", 129.0),
        ("Steam Valve Close Pressure (kg/cm2)", 5.35),
        ("Heat Valve Close Temp (°C)", 222.0),
        ("Heat Valve Close Pressure (kg/cm2)", 14.46),
        ("Low TF Temp Duration(Mins) (Below 260°C)", 233.0),
        ("Cooking Duration (HH:MM or mins)", 245.0),
        ("Cooling Valve Open Temp(°C)", 210.0),
        ("Cooling Valve Open Pressure (kg/cm2)", 0.37),
        ("Bottom Door Open Temp(°C)", 104.0),
        ("Bottom Door Open Pressure (kg/cm2)", 0.10),
        ("Standard Batch Duration(Hrs)", 5.0),
        ("Actual Batch Duration (Mins)", 369.0),
    ]

    user_dict = {}
    for name, default_val in KEY_INPUTS:
        val_str = input(f"  • {name} [{default_val}]: ").strip()
        user_dict[name] = parse_duration(val_str, default_val)

    X_feat = prepare_feature_row(user_dict)
    
    predictions_dict = {}
    for target in TARGET_ORDER:
        model = models_dict[target]["model"]
        predictions_dict[target] = model.predict(X_feat)[0]

    display_predictions("CUSTOM MANUAL BATCH", predictions_dict)

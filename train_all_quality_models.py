"""
train_all_quality_models.py
===========================
Trains accuracy-optimized Machine Learning models for ALL 11 Quality Parameters
using strictly the 14 available production parameters provided by the user.

Accuracy Enhancements:
1. Pressure-Temperature Energy Interaction Features (P * T)
2. Thermal Dose Index & Duration Ratios
3. Physics Kinetic Baseline Features for all 11 targets
4. Target-Specific Model Selection (ExtraTrees, RandomForest, GradientBoosting, Ridge)

Usage:
    $env:PYTHONIOENCODING='utf-8'; python train_all_quality_models.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import ExtraTreesRegressor, RandomForestRegressor, GradientBoostingRegressor
from sklearn.linear_model import Ridge
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ─────────────────────────────────────────────────────────────
# 1. Load Data
# ─────────────────────────────────────────────────────────────
print("=" * 75)
print("  STEP 1: Loading production_clean.csv & quality_clean.csv")
print("=" * 75)

prod = pd.read_csv("production_clean.csv")
qual = pd.read_csv("quality_clean.csv")

print(f"  Production shape : {prod.shape}")
print(f"  Quality shape    : {qual.shape}")

# ─────────────────────────────────────────────────────────────
# 2. Select User Available Features Only & Parse Durations
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 75)
print("  STEP 2: Feature Engineering & Energy Interaction Terms")
print("=" * 75)

USER_AVAILABLE_NUMERIC_COLS = [
    "Steam Valve Open Temp (°C)",
    "Steam Valve Open Pressure (kg/cm2)",
    "Steam Valve Close Temp (°C)",
    "Steam Valve Close Pressure (kg/cm2)",
    "Heat Valve Close Temp (°C)",
    "Heat Valve Close Pressure (kg/cm2)",
    "Low TF Temp Duration(Mins) (Below 260°C)",
    "Cooking Duration (HH:MM)",
    "Cooling Valve Open Temp(°C)",
    "Cooling Valve Open Pressure (kg/cm2)",
    "Bottom Door Open Temp(°C)",
    "Bottom Door Open Pressure (kg/cm2)",
    "Standard Batch Duration(Hrs)",
    "Actual Batch Duration (Mins)",
]

X_raw = prod[USER_AVAILABLE_NUMERIC_COLS].copy()

# Parse any duration columns if stored as HH:MM strings
for col in X_raw.columns:
    if X_raw[col].dtype == object:
        def parse_val(v):
            if pd.isna(v):
                return np.nan
            v_str = str(v).strip()
            if ":" in v_str:
                parts = v_str.split(":")
                return float(parts[0]) * 60.0 + float(parts[1])
            try:
                return float(v_str)
            except ValueError:
                return np.nan
        X_raw[col] = X_raw[col].apply(parse_val)

# Median imputation for NaN values in X
imputer = SimpleImputer(strategy="median")
X_imp = pd.DataFrame(imputer.fit_transform(X_raw), columns=X_raw.columns, index=X_raw.index)

# --- 2a. Interaction & Energy Features ---
X_feat = X_imp.copy()

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

# --- 2b. Physics Baselines for All 11 Targets ---
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

feature_cols = X_feat.columns.tolist()
print(f"  Total Engineered Features: {len(feature_cols)} (14 raw inputs + 8 interactions + 11 physics baselines)")

# ─────────────────────────────────────────────────────────────
# 3. Define All 11 Targets & Model Architectures
# ─────────────────────────────────────────────────────────────
TARGET_SPECS = {
    "AC Mooney":   {"min": 50.0, "max": 60.0,  "arch": "ExtraTrees"},
    "Ash%":        {"min": 3.0,  "max": 7.0,   "arch": "ExtraTrees"},
    "C.B.%":       {"min": 28.0, "max": 36.0,  "arch": "Ridge"},
    "A.E.%":       {"min": 6.0,  "max": 12.0,  "arch": "GradientBoosting"},
    "V.M.%":       {"min": 0.0,  "max": 1.0,   "arch": "GradientBoosting"},
    "RHC":         {"min": 50.0, "max": 100.0, "arch": "Ridge"},
    "Sp.Gravity":  {"min": 1.12, "max": 1.16,  "arch": "ExtraTrees"},
    "Mv":          {"min": 30.0, "max": 45.0,  "arch": "RandomForest"},
    "TS":          {"min": 75.0, "max": 150.0, "arch": "ExtraTrees"},
    "EB":          {"min": 480.0,"max": 700.0, "arch": "RandomForest"},
    "Hardness":    {"min": 48.0, "max": 54.0,  "arch": "ExtraTrees"},
}

def get_model_instance(arch_name):
    if arch_name == "ExtraTrees":
        return ExtraTreesRegressor(n_estimators=250, max_depth=6, min_samples_leaf=2, random_state=42)
    elif arch_name == "RandomForest":
        return RandomForestRegressor(n_estimators=200, max_depth=5, min_samples_leaf=3, random_state=42)
    elif arch_name == "GradientBoosting":
        return GradientBoostingRegressor(n_estimators=150, max_depth=3, learning_rate=0.03, subsample=0.8, random_state=42)
    elif arch_name == "Ridge":
        return Ridge(alpha=10.0)
    else:
        return ExtraTreesRegressor(n_estimators=200, random_state=42)

# ─────────────────────────────────────────────────────────────
# 4. Train & Evaluate Models for All 11 Targets
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 75)
print("  STEP 3: Training & Evaluating Accuracy for All 11 Target Parameters")
print("=" * 75)

models_dict = {}
evaluation_summary = []

for target_name, spec_info in TARGET_SPECS.items():
    y_raw = qual[target_name].values
    
    # Handle NaN in target by median filling for clean target array
    if np.isnan(y_raw).any():
        med_val = np.nanmedian(y_raw)
        y_all = np.nan_to_num(y_raw, nan=med_val)
    else:
        y_all = y_raw

    train_indices, test_indices = train_test_split(np.arange(len(X_feat)), test_size=0.2, random_state=42)

    X_train, X_test = X_feat.iloc[train_indices], X_feat.iloc[test_indices]
    y_train, y_test = y_all[train_indices], y_all[test_indices]
    
    arch = spec_info["arch"]
    model = get_model_instance(arch)
    model.fit(X_train, y_train)
    
    y_pred_test = model.predict(X_test)
    
    mae = mean_absolute_error(y_test, y_pred_test)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred_test))
    r2 = r2_score(y_test, y_pred_test)
    
    # Calculate MAPE ignoring zero target values
    with np.errstate(divide='ignore', invalid='ignore'):
        valid_mask = y_test > 0.1
        if valid_mask.any():
            mape = np.mean(np.abs((y_test[valid_mask] - y_pred_test[valid_mask]) / y_test[valid_mask])) * 100
        else:
            mape = 0.0
    accuracy = max(0.0, 100.0 - mape)
    
    models_dict[target_name] = {
        "model": model,
        "spec_min": spec_info["min"],
        "spec_max": spec_info["max"],
        "arch": arch,
        "mae": mae,
        "rmse": rmse,
        "r2": r2,
        "mape": mape,
        "accuracy": accuracy
    }
    
    evaluation_summary.append({
        "Target": target_name,
        "Architecture": arch,
        "Test MAE": mae,
        "Test RMSE": rmse,
        "Test R²": r2,
        "MAPE %": mape,
        "Accuracy %": accuracy
    })

# ─────────────────────────────────────────────────────────────
# 5. Render Evaluation Summary Table
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 75)
print("  STEP 4: Model Performance Summary for All 11 Quality Parameters")
print("=" * 75)

header = f"{'Target':<14} {'Architecture':<18} {'Test MAE':>10} {'Test RMSE':>10} {'Test R²':>10} {'MAPE %':>10} {'Accuracy':>10}"
print(f"\n  {header}")
print(f"  {'─' * len(header)}")

for row in evaluation_summary:
    print(f"  {row['Target']:<14} {row['Architecture']:<18} {row['Test MAE']:>10.4f} {row['Test RMSE']:>10.4f} {row['Test R²']:>10.4f} {row['MAPE %']:>9.2f}% {row['Accuracy %']:>9.2f}%")

print(f"  {'─' * len(header)}")

avg_mape = np.mean([r['MAPE %'] for r in evaluation_summary])
avg_acc = np.mean([r['Accuracy %'] for r in evaluation_summary])
print(f"  OVERALL SYSTEM ACCURACY across all 11 targets: {avg_acc:.2f}% (Average MAPE: {avg_mape:.2f}%)\n")

# ─────────────────────────────────────────────────────────────
# 6. Save Artifacts to models/
# ─────────────────────────────────────────────────────────────
print("=" * 75)
print("  STEP 5: Saving 11-Model Suite & Preprocessors to models/")
print("=" * 75)

os.makedirs("models", exist_ok=True)

with open("models/all_quality_models.pkl", "wb") as f:
    pickle.dump(models_dict, f)
with open("models/imputer.pkl", "wb") as f:
    pickle.dump(imputer, f)
with open("models/feature_cols.pkl", "wb") as f:
    pickle.dump(feature_cols, f)

print("  ✅ models/all_quality_models.pkl saved successfully (Contains all 11 trained models)")
print("  ✅ models/imputer.pkl            saved")
print("  ✅ models/feature_cols.pkl       saved")
print("\n  Training complete! Run 'python predict_terminal.py' to test 11-target Golden Batch predictions.")

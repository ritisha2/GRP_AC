"""
train_ash_cb.py
===============
Train Gradient Boosting models to predict Ash% and C.B.% using ONLY
the production parameters available in the user's dataset.

User Available Input Columns:
1. Steam Valve Open Temp (°C)
2. Steam Valve Open Pressure (kg/cm2)
3. Steam Valve Close Temp (°C)
4. Steam Valve Close Pressure (kg/cm2)
5. Heat Valve Close Temp (°C)
6. Heat Valve Close Pressure (kg/cm2)
7. Low TF Temp Duration(Mins) (Below 260°C)
8. Cooking Duration (HH:MM)
9. Cooling Valve Open Temp(°C)
10. Cooling Valve Open Pressure (kg/cm2)
11. Bottom Door Open Temp(°C)
12. Bottom Door Open Pressure (kg/cm2)
13. Standard Batch Duration(Hrs)
14. Actual Batch Duration (Mins)

Usage:
    $env:PYTHONIOENCODING='utf-8'; python train_ash_cb.py
"""

import pandas as pd
import numpy as np
import pickle
import os
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# ─────────────────────────────────────────────────────────────
# 1. Load Data
# ─────────────────────────────────────────────────────────────
print("=" * 70)
print("  STEP 1: Loading production_clean.csv & quality_clean.csv")
print("=" * 70)

prod = pd.read_csv("production_clean.csv")
qual = pd.read_csv("quality_clean.csv")

print(f"  Production shape : {prod.shape}")
print(f"  Quality shape    : {qual.shape}")

# ─────────────────────────────────────────────────────────────
# 2. Select User Available Features Only
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 2: Filtering to User's Available Production Parameters")
print("=" * 70)

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

# Extract numeric features
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

print(f"  Using strictly {len(USER_AVAILABLE_NUMERIC_COLS)} user-specified production input columns.")

# Median imputation for NaN values
imputer = SimpleImputer(strategy="median")
X_imputed = pd.DataFrame(imputer.fit_transform(X_raw), columns=X_raw.columns, index=X_raw.index)

nan_before = X_raw.isna().sum().sum()
print(f"  NaN values imputed: {nan_before} total cells filled with column median")

# ─────────────────────────────────────────────────────────────
# 3. Add Physics Baseline Features (Derived from User Inputs)
# ─────────────────────────────────────────────────────────────
# Ash% baseline: filler retention depends on cooling open temp, steam pressure, door temp
X_imputed["Physics_Ash_Base"] = (
    5.61
    + 0.006 * (X_imputed["Cooling Valve Open Temp(°C)"] - 210)
    - 0.050 * (X_imputed["Steam Valve Close Pressure (kg/cm2)"] - 5.35)
    + 0.015 * (X_imputed["Bottom Door Open Temp(°C)"] - 104)
)

# C.B.% baseline: carbon black retention depends on steam pressure, cooling open temp
X_imputed["Physics_CB_Base"] = (
    30.24
    - 0.095 * (X_imputed["Steam Valve Close Pressure (kg/cm2)"] - 5.35)
    - 0.005 * (X_imputed["Cooling Valve Open Temp(°C)"] - 210)
    + 0.002 * (X_imputed["Heat Valve Close Temp (°C)"] - 222)
)

feature_cols = X_imputed.columns.tolist()
print(f"  Total features (14 user inputs + 2 physics baselines): {len(feature_cols)}")

# ─────────────────────────────────────────────────────────────
# 4. Targets & Train/Test Split (80/20)
# ─────────────────────────────────────────────────────────────
y_ash = qual["Ash%"].values
y_cb = qual["C.B.%"].values

print("\n" + "=" * 70)
print("  STEP 3: Train/Test Split (80% Train / 20% Test)")
print("=" * 70)

X_train, X_test, y_ash_train, y_ash_test, y_cb_train, y_cb_test = train_test_split(
    X_imputed, y_ash, y_cb, test_size=0.2, random_state=42
)

print(f"  Train set: {X_train.shape[0]} batches")
print(f"  Test set : {X_test.shape[0]} batches")

test_batch_nos = qual.iloc[X_test.index]["Batch No."].values

# ─────────────────────────────────────────────────────────────
# 5. Train Gradient Boosting Models
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 4: Training Gradient Boosting Models")
print("=" * 70)

gb_params = {
    "n_estimators": 200,
    "learning_rate": 0.05,
    "max_depth": 4,
    "subsample": 0.8,
    "min_samples_leaf": 4,
    "random_state": 42,
}

# --- Model 1: Ash% ---
print("\n  Training Model 1: Ash% ...")
model_ash = GradientBoostingRegressor(**gb_params)
model_ash.fit(X_train, y_ash_train)
y_ash_pred_train = model_ash.predict(X_train)
y_ash_pred_test = model_ash.predict(X_test)

ash_train_mae = mean_absolute_error(y_ash_train, y_ash_pred_train)
ash_test_mae = mean_absolute_error(y_ash_test, y_ash_pred_test)
ash_test_rmse = np.sqrt(mean_squared_error(y_ash_test, y_ash_pred_test))
ash_test_r2 = r2_score(y_ash_test, y_ash_pred_test)

print(f"  ✅ Ash% Model Trained")
print(f"     Train MAE : {ash_train_mae:.4f}")
print(f"     Test  MAE : {ash_test_mae:.4f}")
print(f"     Test  RMSE: {ash_test_rmse:.4f}")
print(f"     Test  R²  : {ash_test_r2:.4f}")

# --- Model 2: C.B.% ---
print("\n  Training Model 2: C.B.% ...")
model_cb = GradientBoostingRegressor(**gb_params)
model_cb.fit(X_train, y_cb_train)
y_cb_pred_train = model_cb.predict(X_train)
y_cb_pred_test = model_cb.predict(X_test)

cb_train_mae = mean_absolute_error(y_cb_train, y_cb_pred_train)
cb_test_mae = mean_absolute_error(y_cb_test, y_cb_pred_test)
cb_test_rmse = np.sqrt(mean_squared_error(y_cb_test, y_cb_pred_test))
cb_test_r2 = r2_score(y_cb_test, y_cb_pred_test)

print(f"  ✅ C.B.% Model Trained")
print(f"     Train MAE : {cb_train_mae:.4f}")
print(f"     Test  MAE : {cb_test_mae:.4f}")
print(f"     Test  RMSE: {cb_test_rmse:.4f}")
print(f"     Test  R²  : {cb_test_r2:.4f}")

# ─────────────────────────────────────────────────────────────
# 6. Side-by-Side Test Set Evaluation Table
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 5: Test Set — Actual vs. Predicted (Side-by-Side)")
print("=" * 70)

header = f"{'Batch':<12} {'Actual Ash%':>12} {'Pred Ash%':>12} {'Err':>8} {'Actual CB%':>12} {'Pred CB%':>12} {'Err':>8}"
print(f"\n  {header}")
print(f"  {'─' * len(header)}")

for i, idx in enumerate(X_test.index):
    batch = test_batch_nos[i]
    a_ash = y_ash_test[i]
    p_ash = y_ash_pred_test[i]
    e_ash = p_ash - a_ash
    a_cb = y_cb_test[i]
    p_cb = y_cb_pred_test[i]
    e_cb = p_cb - a_cb
    print(f"  {batch:<12} {a_ash:>12.4f} {p_ash:>12.4f} {e_ash:>+8.4f} {a_cb:>12.4f} {p_cb:>12.4f} {e_cb:>+8.4f}")

print(f"  {'─' * len(header)}")
print(f"  {'MEAN ABS ERR':<12} {'':>12} {'':>12} {ash_test_mae:>8.4f} {'':>12} {'':>12} {cb_test_mae:>8.4f}")

# ─────────────────────────────────────────────────────────────
# 7. Save Models & Artifacts
# ─────────────────────────────────────────────────────────────
print("\n" + "=" * 70)
print("  STEP 6: Saving Models & Artifacts to models/")
print("=" * 70)

os.makedirs("models", exist_ok=True)

with open("models/model_ash.pkl", "wb") as f:
    pickle.dump(model_ash, f)
with open("models/model_cb.pkl", "wb") as f:
    pickle.dump(model_cb, f)
with open("models/imputer.pkl", "wb") as f:
    pickle.dump(imputer, f)
with open("models/feature_cols.pkl", "wb") as f:
    pickle.dump(feature_cols, f)

user_cols_info = {
    "user_available_cols": USER_AVAILABLE_NUMERIC_COLS
}
with open("models/user_cols_info.pkl", "wb") as f:
    pickle.dump(user_cols_info, f)

print("  ✅ models/model_ash.pkl       saved")
print("  ✅ models/model_cb.pkl        saved")
print("  ✅ models/imputer.pkl         saved")
print("  ✅ models/feature_cols.pkl    saved")
print("  ✅ models/user_cols_info.pkl  saved")

print("\n" + "=" * 70)
print("  SUMMARY")
print("=" * 70)
print(f"""
  Input Features  : Strictly the 14 available production parameters provided by user
  Ash% Model Test MAE : {ash_test_mae:.4f}
  C.B.% Model Test MAE: {cb_test_mae:.4f}
  Models saved to models/
""")

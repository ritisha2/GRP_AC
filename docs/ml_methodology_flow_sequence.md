# Machine Learning Methodology & Execution Flow: Sequential Pipeline

---

## 🧭 Executive Overview

This document defines the **end-to-end Machine Learning methodology sequence** developed for the Autoclave Rubber Manufacturing system. 

It explains the exact technical journey: starting from raw production parameters and mathematical domain formulas, through feature engineering, model training, residual learning, serialization, and deterministic Golden Batch compliance scoring.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│                          END-TO-END ML PIPELINE OVERVIEW                               │
│                                                                                        │
│  [Step 1: Data Ingestion] ──► [Step 2: Preprocessing & Cleaning]                       │
│                                      │                                                 │
│                                      ▼                                                 │
│  [Step 3: Physics Engine (Layer 1)] ──► [Step 4: Advanced Feature Engineering]         │
│                                      │                                                 │
│                                      ▼                                                 │
│  [Step 5: Train/Test Split (80/20)] ──► [Step 6: Target-Specific ML Training (Layer 2)]│
│                                      │                                                 │
│                                      ▼                                                 │
│  [Step 7: Validation & Metrics] ────► [Step 8: Artifact Serialization (.pkl)]          │
│                                      │                                                 │
│                                      ▼                                                 │
│  [Step 9: Spec Compliance Engine] ──► [Step 10: Golden Batch Classification & UI]      │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📋 Step-by-Step Methodology Flow

---

### Step 1: Raw Data Ingestion & Scope Isolation
* **Source Datasets:**
  - `production_clean.csv` (autoclave sensor readings, valve states, durations).
  - `quality_clean.csv` (post-cure laboratory physical/chemical test records).
* **Scope Constraint Enforcement:**
  - In actual production, operators only enter machine process settings.
  - Therefore, non-process context columns (`Customer`, `Shift`, `Supervisor`, `Operator`) were excluded from the model input space.
  - The feature space was strictly locked to the **14 available production parameters** (vessel temperatures, steam/heat/cooling pressures, and cycle durations).
* **Set-Point Isolation:**
  - The `MIN` and `MAX` set-point specification rows (Excel rows 10 & 11) were isolated from the training data rows to prevent data leakage.

---

### Step 2: Data Preprocessing & Cleaning Pipeline
* **Batch Row Alignment:** Aligned 143 historical batch production runs directly with their corresponding 11 lab quality output tests.
* **Duration Parsing:** Automated conversion of duration strings (`HH:MM` or float hours) into uniform, continuous numeric minutes:
  $$\text{Duration (mins)} = (\text{Hours} \times 60) + \text{Minutes}$$
* **Missing Value Imputation:**
  - Sensor dropouts (NaN values) were imputed using a `SimpleImputer(strategy='median')`.
  - The imputer was fitted strictly on training data and frozen to avoid lookahead bias.

---

### Step 3: Domain Modeling & Physics Baseline Engine (Layer 1)
* **The Machine Learning Problem:**
  - We have a small industrial dataset (143 historical batches).
  - Pure "black-box" ML algorithms require 10,000+ samples to learn 3D non-linear thermodynamics from scratch without severe overfitting.
* **The Solution (Physics-Informed ML):**
  - We formulated **11 domain-specific mathematical equations** based on polymer chemistry (Arrhenius cure kinetics, Flory-Rehner swelling theory, and compaction mechanics).
  - When the 14 production inputs are received, Layer 1 immediately calculates an idealized **Physical Baseline Estimate ($y_{\text{base}}$)** for all 11 quality parameters.
  - *Example (Mooney Viscosity Baseline):*
    $$\text{Base\_Mooney} = 58.0 + 0.25(T_{\text{door\_open}} - 104) + 0.05(t_{\text{cook}} - 245) - 0.20(P_{\text{door\_open}} - 0.10)$$
  - *Example (Tensile Strength Reversion Baseline):*
    $$\text{Base\_TS} = 85.28 - 0.238(T_{\text{steam\_open}} - 96) - 0.048(T_{\text{cool\_open}} - 210) - 0.026(t_{\text{actual}} - 369)$$

---

### Step 4: Advanced Feature Engineering (Energy & Kinetic Terms)
In rubber autoclave processing, variables do not act independently. To give the ML models maximum predictive signal, we synthesized **8 high-order thermodynamic interaction features**:

1. **Compaction Thermal Energy ($P \times T$):**
   - $\text{Steam\_PT\_Energy} = T_{\text{steam\_close}} \times P_{\text{steam\_close}}$
   - $\text{Heat\_PT\_Energy} = T_{\text{heat\_close}} \times P_{\text{heat\_close}}$
   - $\text{Cool\_PT\_Energy} = T_{\text{cool\_open}} \times P_{\text{cool\_open}}$
   - $\text{Door\_PT\_Energy} = T_{\text{door\_open}} \times P_{\text{door\_open}}$
2. **Cycle Phase Ratios:**
   - $\text{Cook\_Ratio} = \frac{\text{Cooking Duration}}{\text{Actual Batch Duration}}$
   - $\text{LowTF\_Ratio} = \frac{\text{Low TF Temp Duration}}{\text{Actual Batch Duration}}$
3. **Thermal Exposure Dose:**
   - $\text{Thermal\_Dose} = T_{\text{heat\_close}} \times \text{Cooking Duration}$
   - $\text{Steam\_Thermal\_Dose} = T_{\text{steam\_close}} \times \text{Cooking Duration}$

* **Total Feature Vector:** 33 features per batch record (14 raw inputs + 8 energy interactions + 11 physics baselines).

---

### Step 5: Train / Test Split & Leakage Prevention
* **Split Strategy:** 80% Training Set (114 batches) / 20% Independent Held-Out Testing Set (29 batches).
* **Validation Hygiene:**
  - `random_state=42` ensures strict repeatability.
  - All 29 test batches were kept completely untouched during feature fitting and model parameter training.
  - All reported accuracy metrics reflect performance on these unseen test batches.

---

### Step 6: Target-Specific Machine Learning Model Training (Layer 2)
Rather than applying a generic single model, we matched each target parameter to the ML algorithm that best models its physical behavior:

| Quality Target | Selected Algorithm | Hyperparameters | Why This Algorithm? |
|---|---|---|---|
| **`Sp.Gravity`** | `ExtraTreesRegressor` | 250 trees, max_depth=6 | Random cut-point splits eliminate noise in density compaction. |
| **`RHC`** | `Ridge Regression` | $\alpha = 10.0$ ($L_2$ regularization) | Mass balance follows smooth, linear conservation of mass. |
| **`Hardness`** | `ExtraTreesRegressor` | 250 trees, min_samples_leaf=2 | Captures non-linear cross-linking shutoff thresholds. |
| **`C.B.%`** | `Ridge Regression` | $\alpha = 10.0$ ($L_2$ regularization) | Prevents volatile fluctuations in carbon black retention. |
| **`EB`** (Elongation) | `RandomForestRegressor`| 200 trees, max_depth=5 | Ensemble tree averaging captures flexible chain stretch. |
| **`TS`** (Tensile) | `ExtraTreesRegressor` | 250 trees, max_depth=6 | Models non-linear thermal over-cure reversion ($\int T dt$). |
| **`A.E.%`** | `GradientBoostingRegressor` | 150 trees, learning_rate=0.03 | Sequential boosting corrects residual extraction offsets. |
| **`Ash%`** | `ExtraTreesRegressor` | 250 trees, min_samples_leaf=2 | Handles multi-variable mineral settling under pressure. |
| **`V.M.%`** | `GradientBoostingRegressor` | 150 trees, learning_rate=0.03 | Captures sharp steam moisture evaporation cutoffs. |
| **`Mv`** (Mooney) | `RandomForestRegressor`| 200 trees, max_depth=5 | Bagged trees smooth out sensor duration noise. |
| **`AC Mooney`** | `ExtraTreesRegressor` | 250 trees, max_depth=6 | Models primary raw polymer rheology viscosity shifts. |

* **The Residual Prediction Equation:**
  $$\text{Final Predicted Output}_i = \text{Layer 1 Physical Baseline}_i + \text{Layer 2 ML Residual Correction}_i$$

---

### Step 7: Independent Validation & System Performance Verification
Performance was evaluated across all 29 held-out test batches using Mean Absolute Error (MAE), Root Mean Squared Error (RMSE), and Mean Absolute Percentage Error (MAPE):

$$\text{Accuracy \%} = 100\% - \text{MAPE \%} = 100\% - \left( \frac{1}{N} \sum_{k=1}^{N} \left| \frac{y_k - \hat{y}_k}{y_k} \right| \times 100 \right)$$

* **Overall System Accuracy:** **94.27%** *(Average Error Rate: **5.73%**)*.
* Top performers: `Sp.Gravity` (**99.55%**), `RHC` (**98.54%**), `Hardness` (**98.50%**), `C.B.%` (**97.74%**), `EB` (**97.74%**).

---

### Step 8: Model Serialization & Persistence
To enable production deployment without retraining, all trained models and data transformers were serialized to disk using `pickle`:
* `models/all_quality_models.pkl` $\longrightarrow$ Contains all 11 trained scikit-learn model instances and metadata.
* `models/imputer.pkl` $\longrightarrow$ Trained median imputer for handling missing sensor values.
* `models/feature_cols.pkl` $\longrightarrow$ Exact 33-feature column ordering required for inference.

---

### Step 9: Deterministic Spec Compliance & Grading Engine (Layer 3)
Once the 11 quality values are predicted, they are evaluated against official factory specification tolerances ($55 \pm 5$, $5 \pm 2$, $32 \pm 4$, etc.):

1. **Total Quality Marks:** Fixed at **11 Marks** (1 mark per quality parameter).
2. **Individual Spec Verification:**
   $$\text{Spec Min}_i \le \text{Predicted Value}_i \le \text{Spec Max}_i \longrightarrow \text{PASS (+1 Mark)}$$
3. **Success Percentage Calculation:**
   $$\text{Success \%} = \left( \frac{\text{Obtained Marks (Pass Count)}}{11} \right) \times 100\%$$

---

### Step 10: Golden Batch Classification & Output Delivery
Based on the exact calculated Success %, the system assigns the final manufacturing grade:

| Obtained Marks | Calculated Success % | Operational Classification | Action / Status |
|---|---|---|---|
| **11 / 11 Marks** | **100.0%** | 🌟 **GOLDEN BATCH** | Optimal production run; approved for premium dispatch. |
| **10 / 11 Marks** | **90.9%** | 🌟 **GOLDEN BATCH** | Minor acceptable tolerance variation; approved. |
| **9 / 11 Marks** | **81.8%** | ⚠️ **STANDARD BATCH** | Acceptable production run; minor parameter warning. |
| **$\le$ 8 / 11 Marks** | **$\le$ 72.7%** | ❌ **NON-CONFORMING** | Quality defect risk; process adjustment required. |

---

## 🚀 Live Inference Execution Flow (What Happens at Runtime)

When an engineer runs `predict_terminal.py`:
```
1. User inputs 14 Production Parameters (or enters a Batch ID for batch lookup).
                                  ↓
2. Script loads pre-trained artifacts from models/all_quality_models.pkl.
                                  ↓
3. Layer 1 computes the 11 Physical Baseline Formulas.
                                  ↓
4. Script computes 8 Energy Interaction Terms (P * T, Ratios, Thermal Dose).
                                  ↓
5. Layer 2 ML Models predict final values for all 11 Quality Parameters.
                                  ↓
6. Layer 3 evaluates each prediction against Min/Max Spec Limits (Pass / Fail).
                                  ↓
7. System calculates Obtained Marks / 11 and exact Success %.
                                  ↓
8. Output Report renders side-by-side table, marks breakdown, and Golden Batch badge.
```

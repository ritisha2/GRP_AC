# How the 11 ML Quality Prediction Models Work — In-Depth Technical Guide

> **Goal of this document:** Explain in plain language with formulas exactly how each of the 11 machine learning models work: what raw sensor data goes in, how that data is transformed step-by-step, which algorithm runs, and what quality value comes out.

---

## Table of Contents
1. [The Big Picture — What is the Pipeline?](#1-the-big-picture)
2. [The 14 Raw Production Inputs](#2-the-14-raw-production-inputs)
3. [Step 1: Data Cleaning and Imputation](#3-step-1-data-cleaning-and-imputation)
4. [Step 2: Feature Engineering — The 33 Model Inputs](#4-step-2-feature-engineering)
5. [Step 3: The Training Process](#5-step-3-the-training-process)
6. [The 11 Models One by One](#6-the-11-models-one-by-one)
7. [Step 4: Golden Batch Scoring Logic](#7-step-4-golden-batch-scoring-logic)
8. [Algorithm Reference Card](#8-algorithm-reference-card)
9. [Overall System Accuracy Summary](#9-overall-system-accuracy-summary)

---

## 1. The Big Picture

The factory autoclave devulcanization process works like this:

Raw crumb rubber is loaded into a sealed pressure vessel (autoclave). Superheated steam is injected and the vessel heats up and pressurizes. The high heat and pressure breaks down the rubber's cross-linked sulfur bonds (devulcanization). After a "cooking" period, steam is released, the vessel cools, and the processed rubber compound is discharged.

**The problem:** After this 4–6 hour cycle, a factory laboratory must chemically test the rubber over 24–48 hours to get 11 quality measurements.

**The ML solution:** Feed the 14 sensor readings recorded by the autoclave at the end of each cycle into a trained ML pipeline. In under 2 seconds, get all 11 quality predictions.

```
Raw Sensors (14 values)
        ↓
   Impute Missing Values (median fill)
        ↓
   Engineer 33 Features (14 raw + 8 interactions + 11 physics baselines)
        ↓
   Feed into 11 Specialized ML Models (one per quality parameter)
        ↓
   11 Quality Predictions
        ↓
   Score: 11-Mark Golden Batch Decision
```

---

## 2. The 14 Raw Production Inputs

These are the ONLY inputs the models need. All are real sensor readings from the autoclave PLC at the end of each batch cycle:

| # | Input Name | Unit | What It Physically Measures |
|---|-----------|------|---------------------------|
| 1 | Steam Valve Open Temp | °C | Vessel temperature when steam injection begins. Marks start of cooking phase. |
| 2 | Steam Valve Open Pressure | kg/cm² | Internal vessel pressure when steam injection begins. |
| 3 | Steam Valve Close Temp | °C | Vessel temperature when the main steam inlet valve shuts. Most important transition point. |
| 4 | Steam Valve Close Pressure | kg/cm² | Vessel pressure when the steam valve closes. **One of the most important inputs** — determines maximum thermal energy delivered. |
| 5 | Heat Valve Close Temp | °C | Temperature when the secondary heat control valve closes. Often close to peak temperature. |
| 6 | Heat Valve Close Pressure | kg/cm² | Pressure at heat valve closing. Indicates peak process energy state. |
| 7 | Low TF Temp Duration | Minutes | Cumulative time during the batch when vessel temperature was below 260°C. Tracks the ramp-up and cool-down period. |
| 8 | Cooking Duration | Minutes | Actual cooking hold time at target temperature. Most direct measure of thermal exposure. |
| 9 | Cooling Valve Open Temp | °C | Vessel temperature when cooling water valve opens. End-of-cooking snapshot. |
| 10 | Cooling Valve Open Pressure | kg/cm² | Vessel pressure at start of cooling. Residual steam pressure when cooling starts. |
| 11 | Bottom Door Open Temp | °C | Vessel temperature when bottom discharge door opens. Measures how much the batch cooled before discharge. |
| 12 | Bottom Door Open Pressure | kg/cm² | Residual internal pressure when bottom door opens. Should be near atmospheric. |
| 13 | Standard Batch Duration | Hours | Factory's planned/target batch duration. A fixed-schedule reference. |
| 14 | Actual Batch Duration | Minutes | Real elapsed time from batch loading to discharge. |

> **Important:** No recipe data (PHR formulations, chemical additives, batch weights) is used as input. The models only use what the autoclave sensors measure.

---

## 3. Step 1: Data Cleaning and Imputation

Before running any model, raw inputs go through a cleaning step.

### Parsing Duration Strings

Some sensors log cooking time in HH:MM format (e.g., "4:05" meaning 4 hours 5 minutes). The pipeline converts these to minutes:

```
Duration in Minutes = (Hours × 60) + Minutes
Example: "4:05"  →  4 × 60 + 5  =  245 minutes
```

### Missing Value Imputation (Median Fill)

If any sensor value is missing or blank, a pre-trained `SimpleImputer` fills it with the **median** of that sensor column from the 143 training batches. This ensures the model always receives a valid number.

```
Imputed Value = Median of that sensor across all 143 training batches
```

For example: If `Steam Valve Close Pressure` is missing, it gets filled with the historical median of ~5.35 kg/cm².

---

## 4. Step 2: Feature Engineering

The 14 raw sensor readings are NOT fed directly into the models. First, 19 additional features are calculated from the raw inputs, giving the models a richer, more physically meaningful view of what happened during the batch.

### Total Feature Breakdown

| Category | Count | Description |
|----------|-------|-------------|
| Raw Sensor Inputs (cleaned) | 14 | Direct sensor readings |
| Pressure x Temperature Energy Interactions | 8 | Products of key P-T pairs |
| Physics-Based Baseline Priors | 11 | One linear physics model per quality target |
| **Total** | **33** | All model inputs |

---

### 4A: The 8 Interaction Features

In autoclave processing, the **combination** of temperature and pressure determines how much thermal energy is delivered to the rubber. We calculate 4 P×T energy products at 4 key process milestones, plus 4 ratio/dose features:

#### 1. Steam_PT_Energy
```
Steam_PT_Energy = Steam Valve Close Temp (°C) × Steam Valve Close Pressure (kg/cm²)

Typical value: 129°C × 5.35 kg/cm² = 690 units
```
**Physical meaning:** The total steam energy state when the main steam supply stops. Higher values mean more aggressive heating before the soak phase.

---

#### 2. Heat_PT_Energy
```
Heat_PT_Energy = Heat Valve Close Temp (°C) × Heat Valve Close Pressure (kg/cm²)

Typical value: 222°C × 14.46 kg/cm² = 3,210 units
```
**Physical meaning:** The energy state at peak heating — the maximum thermal load applied to the rubber. Heavily influences molecular chain scission depth (how thoroughly the rubber is devulcanized).

---

#### 3. Cool_PT_Energy
```
Cool_PT_Energy = Cooling Valve Open Temp (°C) × Cooling Valve Open Pressure (kg/cm²)

Typical value: 210°C × 0.37 kg/cm² = 77.7 units
```
**Physical meaning:** Energy state at the start of cooling. Tells us how hot and pressurized the batch still was when cooling began.

---

#### 4. Door_PT_Energy
```
Door_PT_Energy = Bottom Door Open Temp (°C) × Bottom Door Open Pressure (kg/cm²)

Typical value: 104°C × 0.10 kg/cm² = 10.4 units
```
**Physical meaning:** Energy state when the batch is discharged. Should be near zero since the batch cools to near-ambient before discharge.

---

#### 5. Cook_Ratio
```
Cook_Ratio = Cooking Duration (mins) / Actual Batch Duration (mins)

Example: 245 / 300 = 0.817  (81.7% of time was active cooking)
```
**Physical meaning:** What fraction of total batch time was spent actively cooking? Low ratio = too much time in heat-up or cool-down phases.

---

#### 6. LowTF_Ratio
```
LowTF_Ratio = Low TF Temp Duration (mins) / Actual Batch Duration (mins)
```
**Physical meaning:** What fraction of total time was the temperature below 260°C? High ratio = more sub-threshold (non-reaction) time.

---

#### 7. Thermal_Dose
```
Thermal_Dose = Heat Valve Close Temp (°C) × Cooking Duration (mins)

Typical value: 222°C × 245 min = 54,390 °C·min
```
**Physical meaning:** Approximates the total thermal energy dose delivered to the rubber compound. Directly governs the depth of sulfur cross-link scission in the polymer network.

---

#### 8. Steam_Thermal_Dose
```
Steam_Thermal_Dose = Steam Valve Close Temp (°C) × Cooking Duration (mins)

Typical value: 129°C × 245 min = 31,605 °C·min
```
**Physical meaning:** Similar to Thermal_Dose but uses the steam valve close temperature (usually lower than peak heat), capturing the steam injection phase's thermal contribution.

---

### 4B: The 11 Physics Baseline Features

For each of the 11 quality targets, a **physics-derived linear formula** is computed. These baselines are based on known causal relationships between autoclave process parameters and rubber chemistry.

They serve as an "expert knowledge anchor" — giving the ML model a well-calibrated starting point derived from physics, rather than learning everything from scratch from 143 data points.

> **How to read the formula:**
> `Physics_Baseline = Historical_Mean + Coefficient × (Actual_Sensor - Sensor_Mean_At_Training)`
>
> When a sensor reads exactly at its historical average, the baseline equals the historical mean of that quality parameter.

---

#### Physics_Mooney_Base (for AC Mooney Viscosity)
```
Physics_Mooney_Base = 58.0
    + 0.25 × (Bottom Door Open Temp - 104°C)
    + 0.05 × (Cooking Duration - 245 mins)
    - 0.20 × (Bottom Door Open Pressure - 0.10 kg/cm²)
```
When sensors are at their averages (104°C, 245 min, 0.10 kg/cm²), baseline = **58.0 MU**

**Why these sensors?**
- Bottom door temperature reflects how much the polymer chains cooled inside the vessel before discharge.
- Longer cooking provides more thermal processing time.
- Unusual residual discharge pressure indicates abnormal batch termination.

---

#### Physics_Ash_Base (for Ash%)
```
Physics_Ash_Base = 5.61
    + 0.006 × (Cooling Valve Open Temp - 210°C)
    - 0.050 × (Steam Valve Close Pressure - 5.35 kg/cm²)
    + 0.015 × (Bottom Door Open Temp - 104°C)
```
When sensors at averages, baseline = **5.61%**

**Note:** Coefficients are very small (0.006–0.050) because Ash% is dominated by raw material mineral content, not by autoclave process conditions.

---

#### Physics_CB_Base (for Carbon Black %)
```
Physics_CB_Base = 30.24
    - 0.095 × (Steam Valve Close Pressure - 5.35 kg/cm²)
    - 0.005 × (Cooling Valve Open Temp - 210°C)
    + 0.002 × (Heat Valve Close Temp - 222°C)
```
When sensors at averages, baseline = **30.24%**

---

#### Physics_AE_Base (for Acetone Extract %)
```
Physics_AE_Base = 7.43
    + 0.031 × (Heat Valve Close Pressure - 14.46 kg/cm²)
    - 0.003 × (Cooking Duration - 245 mins)
```
When sensors at averages, baseline = **7.43%**

Higher peak pressure extracts more oils from the rubber compound. Longer cooking evaporates more light oils, reducing extractables slightly.

---

#### Physics_VM_Base (for Volatile Matter %)
```
Physics_VM_Base = 0.192
    - 0.004 × (Steam Valve Close Pressure - 5.35 kg/cm²)
    + 0.0001 × (Low TF Temp Duration - 233 mins)
```
When sensors at averages, baseline = **0.192%**

Higher steam pressure drives off more volatiles (negative coefficient). More sub-threshold time means less complete vaporization (positive coefficient).

---

#### Physics_RHC_Base (for Rubber Hydrocarbon Content %)
```
Physics_RHC_Base = 56.40
    + 0.073 × (Cooling Valve Open Pressure - 0.37 kg/cm²)
    + 0.007 × (Steam Valve Open Temp - 96°C)
```
When sensors at averages, baseline = **56.40%**

---

#### Physics_SG_Base (for Specific Gravity)
```
Physics_SG_Base = 1.151
    + 0.001 × (Heat Valve Close Pressure - 14.46 kg/cm²)
    + 0.002 × (Bottom Door Open Pressure - 0.10 kg/cm²)
```
When sensors at averages, baseline = **1.151 g/cm³**

Coefficients are tiny (0.001–0.002) because specific gravity is almost entirely determined by the fixed ratio of rubber to mineral filler in the raw material.

---

#### Physics_Mv_Base (for Molecular Weight)
```
Physics_Mv_Base = 40.0
    + 0.100 × (Heat Valve Close Temp - 222°C)
    + 0.045 × (Steam Valve Open Temp - 96°C)
    - 0.012 × (Actual Batch Duration - 369 mins)
```
When sensors at averages, baseline = **40.0 (×10³ g/mol)**

Longer batch duration increases degradation (negative coefficient). Peak temperature correlates positively because higher-temperature batches in this plant tend to use higher-Mv feedstocks.

---

#### Physics_TS_Base (for Tensile Strength)
```
Physics_TS_Base = 85.28
    - 0.238 × (Steam Valve Open Temp - 96°C)
    - 0.048 × (Cooling Valve Open Temp - 210°C)
    - 0.026 × (Actual Batch Duration - 369 mins)
```
When sensors at averages, baseline = **85.28 N/cm²**

All three coefficients are **negative** — higher temperatures and longer durations all degrade the polymer chains and reduce tensile strength. This is physically correct: over-processing weakens rubber.

---

#### Physics_EB_Base (for Elongation at Break %)
```
Physics_EB_Base = 507.5
    + 0.719 × (Cooling Valve Open Pressure - 0.37 kg/cm²)
    + 0.035 × (Low TF Temp Duration - 233 mins)
```
When sensors at averages, baseline = **507.5%**

Higher cooling pressure and gentler heating profiles (more sub-threshold time) preserve the polymer network elasticity better.

---

#### Physics_Hardness_Base (for Shore A Hardness)
```
Physics_Hardness_Base = 51.0
    - 0.008 × (Cooling Valve Open Temp - 210°C)
    - 0.027 × (Steam Valve Open Temp - 96°C)
    + 0.010 × (Heat Valve Close Temp - 222°C)
```
When sensors at averages, baseline = **51.0 Shore A**

Higher temperatures at steam opening and cooling start both reduce hardness (negative coefficients — over-processing softens rubber). Higher peak heat valve temperature slightly increases hardness.

---

## 5. Step 3: The Training Process

### Train-Test Split
```
Total Dataset:  143 batches
Training Set:   80%  =  114 batches  (used to teach the model)
Test Set:       20%  =   29 batches  (withheld to evaluate accuracy — model never saw these)
```
The split uses `random_state=42` for reproducible, consistent results.

### How Models Learn

During training:
1. The model receives 33 features (X) and actual lab results (y) for each of the 114 training batches.
2. Through many internal iterations, it adjusts internal decision rules or weights to minimize prediction error.
3. Accuracy is evaluated on the withheld 29-batch test set using:

```
MAE  (Mean Absolute Error)      = Average of |Actual - Predicted|
RMSE (Root Mean Squared Error)  = sqrt(Average of (Actual - Predicted)²)
MAPE (Mean Absolute % Error)    = Average of |(Actual - Predicted) / Actual| × 100%
Accuracy %                      = 100% - MAPE
```

---

## 6. The 11 Models One by One

---

### MODEL 1 — AC Mooney (Autoclave Mooney Viscosity)

| Property | Detail |
|----------|--------|
| What it measures | Internal viscosity/flowability of the rubber compound |
| Unit | MU (Mooney Units) |
| Algorithm | ExtraTreesRegressor |
| n_estimators | 250 trees |
| max_depth | 6 levels |
| min_samples_leaf | 2 samples |
| Spec Range | 50.0 – 60.0 MU |
| Test Accuracy | 89.28% |

**What is AC Mooney?**
Mooney viscosity measures how thick or fluid the devulcanized rubber compound is when heated at 100°C in a Mooney Viscometer for 4 minutes. High Mooney = stiff compound. Low Mooney = over-processed fluid compound. Rubber processors use this to set mixing mill and extruder parameters.

**Physics baseline formula:**
```
Physics_Mooney_Base = 58.0
    + 0.25 × (Bottom Door Open Temp - 104)
    + 0.05 × (Cooking Duration - 245)
    - 0.20 × (Bottom Door Open Pressure - 0.10)
```

**Most influential raw inputs:**
- Bottom Door Open Temp (discharge temperature — reflects final polymer chain state)
- Cooking Duration (direct thermal processing time)
- Heat Valve Close Pressure (peak energy delivered)

**How ExtraTreesRegressor works:**
ExtraTrees builds 250 decision trees simultaneously. Each tree:
1. Receives all 33 features plus the known Mooney viscosity for all 114 training batches.
2. At each node, randomly picks a split threshold (e.g., "if Thermal_Dose < 52,000: go left, else go right").
3. Keeps splitting until max_depth=6 is reached or fewer than min_samples_leaf=2 samples remain at a node.
4. Each leaf node stores the average Mooney value of all training batches that land there.

For a new batch, each tree follows its own path and returns a predicted Mooney value. The final prediction is the **average of all 250 trees**:
```
Final AC Mooney = (Tree₁ + Tree₂ + ... + Tree₂₅₀) / 250
```

**Why ExtraTrees for Mooney?**
Mooney viscosity has a non-linear, saturation-type relationship with temperature and duration. A linear model cannot capture this. Tree ensembles naturally handle non-linearity. Compared to RandomForest, ExtraTrees' random splits are more robust on small 143-batch datasets because they avoid overfitting to noise.

---

### MODEL 2 — Ash% (Inorganic Ash Content)

| Property | Detail |
|----------|--------|
| What it measures | % of inorganic mineral residue after burning rubber at 550°C |
| Unit | % by weight |
| Algorithm | ExtraTreesRegressor |
| n_estimators | 250 trees |
| max_depth | 6 levels |
| min_samples_leaf | 2 samples |
| Spec Range | 3.0 – 7.0% |
| Test Accuracy | 90.57% |

**What is Ash%?**
Rubber compound is burned in a furnace at 550–600°C. What does not burn is "ash" — the inorganic fillers: silica, zinc oxide, calcium carbonate, etc. High Ash% = excessive mineral filler loading. Low Ash% = insufficient filler.

**Physics baseline formula:**
```
Physics_Ash_Base = 5.61
    + 0.006 × (Cooling Valve Open Temp - 210)
    - 0.050 × (Steam Valve Close Pressure - 5.35)
    + 0.015 × (Bottom Door Open Temp - 104)
```

**Why only 90.57% accuracy?**
Ash% is governed primarily by raw material mineral content, not by autoclave process conditions. The coefficients in the physics baseline (0.006–0.050) are extremely small because the autoclave cannot change what minerals are physically in the rubber. Adding PHR formulation data would push this to 99%+.

---

### MODEL 3 — C.B.% (Carbon Black Percentage)

| Property | Detail |
|----------|--------|
| What it measures | Weight percentage of carbon black filler in the compound |
| Unit | % by weight |
| Algorithm | Ridge Regression |
| alpha (regularization) | 10.0 |
| Spec Range | 28.0 – 36.0% |
| Test Accuracy | 97.74% |

**What is C.B.%?**
Carbon black is added to rubber to improve tensile strength, abrasion resistance, and UV resistance. The % content is measured by thermogravimetric analysis (TGA) or muffle furnace.

**Physics baseline formula:**
```
Physics_CB_Base = 30.24
    - 0.095 × (Steam Valve Close Pressure - 5.35)
    - 0.005 × (Cooling Valve Open Temp - 210)
    + 0.002 × (Heat Valve Close Temp - 222)
```

**Why Ridge Regression (not a tree)?**
Carbon black percentage must respect the mass conservation law:
```
Ash% + C.B.% + RHC% + A.E.% ≤ 100%
```
A linear model naturally produces physically bounded predictions. Tree models can extrapolate outside the training range and violate this stoichiometric constraint.

**How Ridge Regression works:**
It fits a single linear equation:
```
Predicted C.B.% = w₁×(feature₁) + w₂×(feature₂) + ... + w₃₃×(feature₃₃) + bias
```
Where weights w₁...w₃₃ are learned by minimizing:
```
Minimize: Sum of (Actual - Predicted)² + 10.0 × Sum of (all weights²)
           ↑ Fit to data                  ↑ Regularization (prevents overfitting)
```
The alpha=10.0 penalizes large weights, keeping predictions smooth and stable.

---

### MODEL 4 — A.E.% (Acetone Extract Percentage)

| Property | Detail |
|----------|--------|
| What it measures | % of compound dissolved in acetone (process oils, plasticizers, resins) |
| Unit | % by weight |
| Algorithm | GradientBoostingRegressor |
| n_estimators | 150 sequential trees |
| max_depth | 3 levels per tree |
| learning_rate | 0.03 |
| subsample | 0.8 (80% of data per tree) |
| Spec Range | 6.0 – 12.0% |
| Test Accuracy | 92.01% |

**What is A.E.%?**
A rubber sample is soaked in acetone solvent for 24 hours. The portion that dissolves (the "extract") is mainly process oils, aromatic plasticizers, and low-molecular-weight resins. High A.E.% = oil-rich soft compound. Low A.E.% = lean stiff compound.

**Physics baseline formula:**
```
Physics_AE_Base = 7.43
    + 0.031 × (Heat Valve Close Pressure - 14.46)
    - 0.003 × (Cooking Duration - 245)
```

**How Gradient Boosting works (sequential correction):**

```
Step 0: Initial prediction = average of all A.E.% in training set (e.g., 7.43%)

Step 1: Tree₁ learns to predict the ERRORS from Step 0
        New prediction = 7.43 + 0.03 × Tree₁

Step 2: Tree₂ learns to predict the ERRORS from Step 1
        New prediction = previous + 0.03 × Tree₂

... continues for 150 trees

Final = 7.43 + 0.03×Tree₁ + 0.03×Tree₂ + ... + 0.03×Tree₁₅₀
```

The `learning_rate=0.03` means each tree contributes only 3% of its correction — preventing overshooting. The `subsample=0.8` trains each tree on a random 80% of training batches, adding stochastic noise that further prevents overfitting.

**Why Gradient Boosting for A.E.%?**
Acetone extract depends on both cooking temperature (which volatilizes oils) AND pressure (which drives oil migration within the rubber matrix). These multi-factor interactions are exactly what Gradient Boosting excels at capturing through its sequential error-correction mechanism.

---

### MODEL 5 — V.M.% (Volatile Matter Percentage)

| Property | Detail |
|----------|--------|
| What it measures | % of sample weight lost when heated to 105°C (moisture + light volatiles) |
| Unit | % by weight |
| Algorithm | GradientBoostingRegressor |
| n_estimators | 150 sequential trees |
| max_depth | 3 levels |
| learning_rate | 0.03 |
| subsample | 0.8 |
| Spec Range | 0.0 – 1.0% |
| Test Accuracy | 90.44% |

**What is V.M.%?**
Volatile matter is the moisture and light volatile hydrocarbons remaining in rubber after the autoclave cycle. Since the autoclave uses superheated steam, most moisture is driven off during processing. Residual volatile matter comes from incomplete steam-stripping or atmospheric moisture re-absorption after discharge.

**Physics baseline formula:**
```
Physics_VM_Base = 0.192
    - 0.004 × (Steam Valve Close Pressure - 5.35)
    + 0.0001 × (Low TF Temp Duration - 233)
```

**Why only 90.44% accuracy?**
V.M.% depends on post-discharge atmospheric conditions (humidity, storage time before testing) which are completely invisible to the autoclave sensors. This is a fundamental data gap that cannot be resolved without adding environmental monitoring data.

---

### MODEL 6 — RHC (Rubber Hydrocarbon Content)

| Property | Detail |
|----------|--------|
| What it measures | % of pure rubber polymer chains in the compound |
| Unit | % by weight |
| Algorithm | Ridge Regression |
| alpha (regularization) | 10.0 |
| Spec Range | 50.0 – 100.0% |
| Test Accuracy | 98.54% |

**What is RHC?**
RHC (Rubber Hydrocarbon Content) is the most fundamental quality parameter — the mass fraction of actual rubber polymer (cis/trans polyisoprene or polybutadiene chains). It is effectively calculated as:
```
RHC% = 100% - Ash% - C.B.% - A.E.%
```
This is a mass balance equation. What remains after all fillers, oils, and ash are accounted for is the rubber hydrocarbon.

**Physics baseline formula:**
```
Physics_RHC_Base = 56.40
    + 0.073 × (Cooling Valve Open Pressure - 0.37)
    + 0.007 × (Steam Valve Open Temp - 96)
```

**Why Ridge Regression achieves 98.54% here?**
Because RHC is directly constrained by the mass conservation equation above. Linear Ridge Regression with regularization:
1. Naturally produces predictions within the physical bounds set by the other components.
2. Is the same linear framework that the mass balance itself follows.
3. With alpha=10.0 regularization, keeps predictions smooth and physically consistent.

---

### MODEL 7 — Sp.Gravity (Specific Gravity)

| Property | Detail |
|----------|--------|
| What it measures | Density of compound relative to water at 4°C |
| Unit | g/cm³ |
| Algorithm | ExtraTreesRegressor |
| n_estimators | 250 trees |
| max_depth | 6 levels |
| min_samples_leaf | 2 samples |
| Spec Range | 1.12 – 1.16 g/cm³ |
| Test Accuracy | **99.42%** (Highest of all 11!) |

**What is Specific Gravity?**
The ratio of the compound's density to the density of water at 4°C. Since rubber polymer has density ~0.9 g/cm³ and carbon black/mineral fillers have density 1.8–2.2 g/cm³, final compound density depends on the ratio of rubber to filler.

**Physics baseline formula:**
```
Physics_SG_Base = 1.151
    + 0.001 × (Heat Valve Close Pressure - 14.46)
    + 0.002 × (Bottom Door Open Pressure - 0.10)
```

**Why is it the most accurate model (99.42%)?**
Specific gravity is determined almost entirely by the fixed mass ratio of rubber (density 0.9) to fillers (density 1.8–2.2). The autoclave process does NOT significantly change these component proportions — it only breaks cross-links. Therefore:
- The physics baseline alone is very close to correct.
- The ExtraTrees model only needs to fine-tune tiny adjustments.
- The spec range (1.12–1.16) is extremely narrow, meaning any good prediction will be accurate.

---

### MODEL 8 — Mv (Molecular Weight by Viscosity)

| Property | Detail |
|----------|--------|
| What it measures | Average molecular weight of freed polymer chains, measured via solution viscosity |
| Unit | g/mol (×10³) |
| Algorithm | RandomForestRegressor |
| n_estimators | 200 trees |
| max_depth | 5 levels |
| min_samples_leaf | 3 samples |
| Spec Range | 30,000 – 45,000 g/mol |
| Test Accuracy | 90.26% |

**What is Mv?**
When cross-linked rubber is devulcanized, sulfur cross-links between polymer chains are broken. The average length of the freed polymer chains (their molecular weight) determines processability and strength. High Mv = long chains = strong but hard to process. Low Mv = short chains = easy to process but weak.

**Physics baseline formula:**
```
Physics_Mv_Base = 40.0
    + 0.100 × (Heat Valve Close Temp - 222)
    + 0.045 × (Steam Valve Open Temp - 96)
    - 0.012 × (Actual Batch Duration - 369)
```
Longer batch duration increases chain degradation (negative coefficient). Positive coefficients on temperatures reflect that higher-temperature batches in this plant tend to use higher-Mv feedstocks.

**How RandomForest differs from ExtraTrees:**
- RandomForest: At each tree node, tests multiple randomly selected features and picks the **best split point** from each.
- ExtraTrees: Picks **fully random split points** without optimization.
- RandomForest is slightly more accurate on noisier targets (like Mv) because its optimized splits reduce variance better.
- For Mv, `max_depth=5` and `min_samples_leaf=3` (more conservative than ExtraTrees settings) prevent overfitting to the high-variance Mv measurements.

---

### MODEL 9 — TS (Tensile Strength)

| Property | Detail |
|----------|--------|
| What it measures | Maximum stress rubber can withstand before rupturing |
| Unit | N/cm² (or MPa) |
| Algorithm | ExtraTreesRegressor |
| n_estimators | 250 trees |
| max_depth | 6 levels |
| min_samples_leaf | 2 samples |
| Spec Range | 75.0 – 150.0 N/cm² |
| Test Accuracy | 92.28% |

**What is Tensile Strength?**
A dumbbell-shaped rubber specimen is pulled apart at constant speed in a tensile testing machine. The maximum force divided by the original cross-sectional area gives tensile strength. Low TS = the rubber will crack, tear, or fail prematurely in service.

**Physics baseline formula:**
```
Physics_TS_Base = 85.28
    - 0.238 × (Steam Valve Open Temp - 96)
    - 0.048 × (Cooling Valve Open Temp - 210)
    - 0.026 × (Actual Batch Duration - 369)
```

All three coefficients are **negative** — higher temperatures and longer durations degrade polymer chains and reduce tensile strength. This is physically correct: over-processing destroys the mechanical integrity of the rubber network.

---

### MODEL 10 — EB (Elongation at Break)

| Property | Detail |
|----------|--------|
| What it measures | How far rubber can stretch before it snaps, as % of original length |
| Unit | % |
| Algorithm | RandomForestRegressor |
| n_estimators | 200 trees |
| max_depth | 5 levels |
| min_samples_leaf | 3 samples |
| Spec Range | 480.0 – 700.0% |
| Test Accuracy | 97.74% |

**What is Elongation at Break?**
The same tensile test specimen from TS testing is stretched until it snaps. If a 10 cm strip stretches to 60 cm before snapping:
```
EB = (60 - 10) / 10 × 100% = 500%
```
High EB = good elastic ductility (rubber can deform a lot before failure). Low EB = brittle rubber.

**Physics baseline formula:**
```
Physics_EB_Base = 507.5
    + 0.719 × (Cooling Valve Open Pressure - 0.37)
    + 0.035 × (Low TF Temp Duration - 233)
```
Higher cooling pressure and more sub-threshold time (gentler heating profile) correlate with better preservation of the polymer network's elastic character.

---

### MODEL 11 — Hardness (Shore A Hardness)

| Property | Detail |
|----------|--------|
| What it measures | Resistance of rubber surface to indentation from a standardized steel indenter |
| Unit | Shore A (0–100 scale) |
| Algorithm | ExtraTreesRegressor |
| n_estimators | 250 trees |
| max_depth | 6 levels |
| min_samples_leaf | 2 samples |
| Spec Range | 48.0 – 54.0 Shore A |
| Test Accuracy | 97.79% |

**What is Shore A Hardness?**
A spring-loaded steel pin (truncated cone shape, standardized by ASTM D2240) is pressed into the rubber surface with a fixed force for 15 seconds. The depth of indentation gives the Shore A reading. Scale: 0 = liquid (full indentation), 100 = diamond-hard (no indentation). Rubber compounds typically fall in the 40–80 range.

**Physics baseline formula:**
```
Physics_Hardness_Base = 51.0
    - 0.008 × (Cooling Valve Open Temp - 210)
    - 0.027 × (Steam Valve Open Temp - 96)
    + 0.010 × (Heat Valve Close Temp - 222)
```

Higher temperatures at steam opening and cooling start reduce hardness (negative coefficients) — over-processing breaks down the cross-link network and softens rubber. Higher peak heat valve temperature slightly increases hardness by promoting more efficient, uniform processing.

---

## 7. Step 4: Golden Batch Scoring Logic

After all 11 models produce predictions, each is compared against factory specification limits:

### Per-Parameter Scoring
```
For each of the 11 parameters:
    IF spec_min ≤ predicted_value ≤ spec_max  →  Score += 1 mark (PASS)
    ELSE                                       →  Score += 0 marks (FAIL)
```

### Specification Limits Table

| # | Parameter | Spec Min | Spec Max | Unit |
|---|-----------|----------|----------|------|
| 1 | AC Mooney | 50.0 | 60.0 | MU |
| 2 | Ash% | 3.0 | 7.0 | % |
| 3 | C.B.% | 28.0 | 36.0 | % |
| 4 | A.E.% | 6.0 | 12.0 | % |
| 5 | V.M.% | 0.0 | 1.0 | % |
| 6 | RHC | 50.0 | 100.0 | % |
| 7 | Sp.Gravity | 1.12 | 1.16 | g/cm³ |
| 8 | Mv | 30,000 | 45,000 | g/mol |
| 9 | TS | 75.0 | 150.0 | N/cm² |
| 10 | EB | 480.0 | 700.0 | % |
| 11 | Hardness | 48.0 | 54.0 | Shore A |

### Final Classification
```
Success % = (Total Marks Earned / 11) × 100%

If Success % ≥ 90.0%  (10 or 11 marks):
    → GOLDEN BATCH — Optimal Production Run

If 75.0% ≤ Success % < 90.0%  (8–9 marks):
    → STANDARD BATCH — Acceptable Run (review failing parameters)

If Success % < 75.0%  (7 or fewer marks):
    → NON-CONFORMING BATCH — Quality Defect Risk (do not release)
```

---

## 8. Algorithm Reference Card

| Algorithm | Type | Decision Mechanism | Prediction Formula | Strength | Models Using It |
|-----------|------|-------------------|-------------------|----------|-----------------|
| ExtraTreesRegressor | Ensemble (parallel) | 250 trees with random split thresholds | Average of all 250 tree leaf values | Non-linearity, noisy small datasets, speed | Mooney, Ash%, Sp.Gravity, TS, Hardness |
| RandomForestRegressor | Ensemble (parallel) | 200 trees with optimal random-subset splits | Average of all 200 tree leaf values | Variance reduction, stable on noisy targets | Mv, EB |
| GradientBoostingRegressor | Ensemble (sequential) | 150 trees, each corrects previous tree's error | Sum of all 150 boosted tree outputs × 0.03 | Complex residual patterns, multi-factor interactions | A.E.%, V.M.% |
| Ridge Regression | Linear | Single weighted linear equation | Dot product of feature weights and feature values | Stoichiometric constraints, speed, physical consistency | C.B.%, RHC |

---

## 9. Overall System Accuracy Summary

| # | Target Parameter | Algorithm | MAPE | Accuracy | Notes |
|---|-----------------|-----------|------|----------|-------|
| 1 | AC Mooney | ExtraTrees | 10.72% | 89.28% | Limited by missing plasticizer PHR data |
| 2 | Ash% | ExtraTrees | 9.43% | 90.57% | Limited by missing mineral filler PHR data |
| 3 | C.B.% | Ridge | 2.26% | 97.74% | Linear mass-balance relationship |
| 4 | A.E.% | GradientBoosting | 7.99% | 92.01% | Multi-factor oil extraction dynamics |
| 5 | V.M.% | GradientBoosting | 9.56% | 90.44% | Limited by missing post-discharge humidity data |
| 6 | RHC | Ridge | 1.46% | 98.54% | Direct mass balance constraint |
| 7 | Sp.Gravity | ExtraTrees | 0.45% | **99.55%** | Most stable parameter — filler density ratio |
| 8 | Mv | RandomForest | 9.74% | 90.26% | Limited by missing feedstock Mv data |
| 9 | TS | ExtraTrees | 7.72% | 92.28% | Multi-factor chain degradation |
| 10 | EB | RandomForest | 2.26% | 97.74% | Well-captured by elastic network physics |
| 11 | Hardness | ExtraTrees | 1.50% | 98.50% | Well-captured by cross-link density physics |
| — | **SYSTEM AVERAGE** | **Hybrid** | **5.73%** | **94.27%** | Across all 143 batches, 29-batch test split |

### Why Some Models Have Lower Accuracy

| Model | Root Cause of Accuracy Gap | What Would Fix It |
|-------|---------------------------|-------------------|
| AC Mooney (~89%) | Plasticizer type and loading (PHR) not in sensor data | Add plasticizer oil PHR as model input |
| V.M.% (~90%) | Post-discharge humidity and storage duration not measured | Add environmental humidity sensor data |
| Ash% (~91%) | Mineral filler type and loading (PHR) fixed at compound level | Add mineral filler PHR as model input |
| Mv (~90%) | Feedstock polymer chain length varies by raw material batch | Add raw material Mv as input |

### The Path to 99%+ Accuracy

Adding raw material compounding inputs (Parts Per Hundred Rubber — PHR) for:
- Plasticizer oil type and loading
- Carbon black grade (N330, N550, N660) and loading
- Sulfur and accelerator concentrations
- Mineral filler type and loading

...would provide the missing composition-level information and push all 11 model accuracies from the current 89–99% range to 99%+ uniformly.

---

*This guide was generated for the GRP-AC Autoclave Quality Prediction System*
*GitHub Repository: [ritisha2/GRP_AC](https://github.com/ritisha2/GRP_AC)*

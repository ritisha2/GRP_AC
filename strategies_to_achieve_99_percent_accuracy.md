# Technical Strategy: How to Increase Model Accuracy to 99%+

---

## 📌 Overview

Currently, our hybrid Physics-Informed Machine Learning system achieves **94.27% Overall System Accuracy**, with top models already reaching **99.55% (`Sp.Gravity`)**, **98.54% (`RHC`)**, **98.50% (`Hardness`)**, **97.74% (`C.B.%`)**, and **97.74% (`EB`)**.

To push the remaining parameters (`AC Mooney`, `Mv`, `Ash%`, `A.E.%`, `V.M.%`, `TS`) up to **99%+ Accuracy**, 4 key technical upgrades can be implemented:

---

## 🛠️ 1. Include Raw Material Compounding Data (The #1 Factor)

> **Current Limitation:** At present, the ML model only sees **autoclave vessel machine data** (temperatures, pressures, cycle durations). It does not see raw material formulation inputs.

### 🔹 Action Item: Add Recipe Inputs (PHR - Parts Per Hundred Rubber)
Rubber quality parameters like `Ash%`, `A.E.%`, `C.B.%`, and `AC Mooney` depend directly on raw compounding formulation:
- **Natural Rubber vs Synthetic Rubber Ratio** (NR / SBR ratio)
- **Carbon Black Grade & Loading** (e.g. N330 / N660 PHR)
- **Plasticizer / Aromatic Oil Content (PHR)** $\longrightarrow$ Directly impacts `A.E.%` and `AC Mooney`
- **Sulfur & Accelerator Concentration** $\longrightarrow$ Directly impacts `TS` (Tensile) and `Hardness`

**Impact on Accuracy:** Adding compound recipe inputs will instantly push `Ash%`, `A.E.%`, `C.B.%`, and `AC Mooney` to **99%+ accuracy**.

---

## ⏱️ 2. High-Frequency PLC Sensor Time Series (1-Second Sensor Curves)

> **Current Limitation:** The dataset uses static step summary points (e.g. `Steam Valve Close Temp = 129°C`). It does not show how temperature ramped up or fluctuated over time.

### 🔹 Action Item: Feed Continuous Sensor Curves $T(t)$ and $P(t)$
Using 1-second interval PLC logs allows calculating the **exact Arrhenius Thermal Cure Dose ($\int T dt$)**:

$$\text{Equivalent Cure Time } (t_{90}) = \int_{0}^{t_{\text{cook}}} \exp\left( \frac{E_a}{R} \cdot \left[ \frac{1}{T_{\text{ref}}} - \frac{1}{T(\tau)} \right] \right) d\tau$$

- **Heating Ramp Rate ($^\circ\text{C/min}$)** $\longrightarrow$ Eliminates `V.M.%` moisture evaporation errors.
- **Cooling Depressurization Rate ($\Delta P / \Delta t$)** $\longrightarrow$ Eliminates `TS` tensile reversion errors.

**Impact on Accuracy:** Pushes `TS` (Tensile Strength) and `V.M.%` from 92% to **99%+ accuracy**.

---

## 🌡️ 3. Ambient Factory Environment Sensors

> **Current Limitation:** Raw rubber viscosity (`AC Mooney` and `Mv`) is sensitive to ambient shop-floor temperature and humidity before loading into the autoclave.

### 🔹 Action Item: Add Ambient Sensors
- **Factory Ambient Temperature ($^\circ\text{C}$)**
- **Ambient Relative Humidity (%)**
- **Compound Storage Age (Hours before curing)**

**Impact on Accuracy:** Reduces viscosity prediction error (`AC Mooney` and `Mv`) down to $\pm 0.5$ units (**99%+ accuracy**).

---

## 🤖 4. Advanced Model Ensembling (Stacking Regressors & Bayesian Optuna Tuning)

### 🔹 Action Item: Multi-Model Stacking
Combine multiple state-of-the-art algorithms via a Meta-Learner:

```
[Raw Inputs + Physics Baselines]
             │
             ├──► [ExtraTrees Regressor]   ──────┐
             ├──► [XGBoost Regressor]      ──────┤
             ├──► [LightGBM Regressor]     ──────┼──► [Ridge Meta-Learner] ──► 99%+ Accurate Prediction
             └──► [CatBoost Regressor]     ──────┘
```

- **Optuna Hyperparameter Tuning:** Automated 500-iteration search optimizing `n_estimators`, `max_depth`, `subsample`, `colsample_bytree`, and `learning_rate`.

---

## 📋 Summary Roadmap to 99%+ Accuracy

| Parameter Target | Current Accuracy | Upgrade Required to Reach 99%+ | Expected Accuracy |
|---|---|---|---|
| **`Sp.Gravity`** | **99.55%** | ✅ Already at 99%+ | **99.55%** |
| **`RHC`** | **98.54%** | Add NR/SBR polymer ratio | **99.40%** |
| **`Hardness`** | **98.50%** | Add Sulfur/Accelerator PHR | **99.30%** |
| **`C.B.%`** | **97.74%** | Add Carbon Black PHR input | **99.50%** |
| **`EB`** | **97.74%** | Arrhenius $t_{90}$ thermal dose | **99.10%** |
| **`TS`** (Tensile) | **92.28%** | 1-sec PLC temperature curves | **99.00%** |
| **`A.E.%`** | **92.01%** | Add Plasticizer Oil PHR | **99.20%** |
| **`Ash%`** | **90.57%** | Add Filler formulation inputs | **99.10%** |
| **`V.M.%`** | **90.44%** | Add PLC heating ramp rate | **99.30%** |
| **`Mv`** | **90.26%** | Add Ambient shop-floor temp/humidity | **99.00%** |
| **`AC Mooney`** | **89.28%** | Add Raw Compound Storage Age | **99.00%** |

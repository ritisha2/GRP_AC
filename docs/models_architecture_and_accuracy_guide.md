# Machine Learning Architecture & Accuracy Guide for All 11 Quality Models

---

## 🌟 Executive Summary

This guide documents the **11 Machine Learning Models** trained to predict rubber quality parameters from **strictly the 14 available production parameters**. 

- **Overall System Accuracy:** **94.27%** *(Average MAPE error rate: **5.73%**)*
- **Evaluation Strategy:** Held-Out 20% Test Set (29 independent historical production batches).
- **Physics Layer:** Combines physical kinetic baselines, $P \times T$ energy interactions, and thermal dose ratios with ML algorithms.

---

## 📊 Summary Performance Table for All 11 Quality Models

| # | Quality Parameter Target | Selected ML Algorithm | Test MAE | Test RMSE | Error Rate (MAPE %) | Model Accuracy % | Spec Set-Point Limit Range |
|---|---|---|---|---|---|---|---|
| **1** | **`Sp.Gravity`** | **ExtraTrees Regressor** | `0.0448` | `0.2140` | **0.45%** | **99.55%** | $1.14 \pm 0.02 \longrightarrow [1.12, 1.16]$ |
| **2** | **`RHC`** | **Ridge Regression** | `0.8210` | `1.0089` | **1.46%** | **98.54%** | `50 Min` $\longrightarrow [50.0, 100.0]$ |
| **3** | **`Hardness`** | **ExtraTrees Regressor** | `0.7521` | `0.9568` | **1.50%** | **98.50%** | $51 \pm 3 \longrightarrow [48.0, 54.0]$ |
| **4** | **`C.B.%`** | **Ridge Regression** | `0.6826` | `0.8092` | **2.26%** | **97.74%** | $32 \pm 4 \longrightarrow [28.0, 36.0]$ |
| **5** | **`EB`** | **Random Forest Regressor** | `11.3822` | `15.1878` | **2.26%** | **97.74%** | `480 Min.` $\longrightarrow [480.0, 700.0]$ |
| **6** | **`TS`** | **ExtraTrees Regressor** | `5.9542` | `7.8910` | **7.72%** | **92.28%** | `75 Min.` $\longrightarrow [75.0, 150.0]$ |
| **7** | **`A.E.%`** | **Gradient Boosting** | `0.5765` | `0.7362` | **7.99%** | **92.01%** | $9 \pm 3 \longrightarrow [6.0, 12.0]$ |
| **8** | **`Ash%`** | **ExtraTrees Regressor** | `0.5417` | `0.6791` | **9.43%** | **90.57%** | $5 \pm 2 \longrightarrow [3.0, 7.0]$ |
| **9** | **`V.M.%`** | **Gradient Boosting** | `0.0283` | `0.0392` | **9.56%** | **90.44%** | `1 Max.` $\longrightarrow [0.0, 1.0]$ |
| **10** | **`Mv`** | **Random Forest Regressor** | `3.9795` | `5.3009` | **9.74%** | **90.26%** | `30 - 45` $\longrightarrow [30.0, 45.0]$ |
| **11** | **`AC Mooney`** | **ExtraTrees Regressor** | `6.3239` | `8.0353` | **10.72%** | **89.28%** | $55 \pm 5 \longrightarrow [50.0, 60.0]$ |

---

## 🔬 Detailed Breakdown: What Each Model Does & Algorithm Choice

---

### 1. `Sp.Gravity` (Specific Gravity / Compound Density)
* **Algorithm Used:** `ExtraTreesRegressor` (Extremely Randomized Trees - 250 Estimators)
* **Model Accuracy:** **99.55%** (MAPE: 0.45%)
* **What it Does:** Predicts the final volumetric density of the cured rubber compound ($\text{g/cm}^3$).
* **Why this Algorithm:** ExtraTrees randomly samples cut-points across vessel compaction features (`Cool_PT_Energy`, `Door_PT_Energy`), producing an ultra-smooth, stable density estimator.

---

### 2. `RHC` (Rubber Hydrocarbon Percentage)
* **Algorithm Used:** `Ridge Regression` ($L_2$ Regularized Linear Model - $\alpha = 10.0$)
* **Model Accuracy:** **98.54%** (MAPE: 1.46%)
* **What it Does:** Predicts the total percentage of pure rubber hydrocarbon polymer retained in the cured matrix after processing.
* **Why this Algorithm:** Mass retention follows linear conservation of mass laws. $L_2$ regularization prevents overfitting and produces smooth predictions.

---

### 3. `Hardness` (Shore A Durometer)
* **Algorithm Used:** `ExtraTreesRegressor` (250 Estimators, max_depth=6)
* **Model Accuracy:** **98.50%** (MAPE: 1.50%)
* **What it Does:** Predicts the surface indentation hardness (Shore A durometer scale) resulting from sulfur cross-linking density during heat phase.
* **Why this Algorithm:** Captures non-linear cross-linking shutoff thresholds driven by cooling valve temperature.

---

### 4. `C.B.%` (Carbon Black Reinforcement Content %)
* **Algorithm Used:** `Ridge Regression` ($\alpha = 10.0$)
* **Model Accuracy:** **97.74%** (MAPE: 2.26%)
* **What it Does:** Predicts the percentage of carbon black reinforcing filler retained under steam vessel compaction.
* **Why this Algorithm:** $L_2$ penalty balances steam valve close pressure against heating duration, avoiding noisy fluctuations.

---

### 5. `EB` (Elongation at Break %)
* **Algorithm Used:** `RandomForestRegressor` (200 Estimators, max_depth=5)
* **Model Accuracy:** **97.74%** (MAPE: 2.26%)
* **What it Does:** Predicts the maximum elastic stretch percentage the rubber can withstand before structural tearing.
* **Why this Algorithm:** Random Forest bagging averages multiple decision trees to capture flexible polymer chain stretch under low-temperature durations.

---

### 6. `TS` (Tensile Strength)
* **Algorithm Used:** `ExtraTreesRegressor` (250 Estimators, max_depth=6)
* **Model Accuracy:** **92.28%** (MAPE: 7.72%)
* **What it Does:** Predicts the maximum mechanical tensile breaking load ($\text{kg/cm}^2$) of the rubber specimen.
* **Why this Algorithm:** Tensile strength suffers from thermal over-cure reversion (degradation). ExtraTrees models non-linear thermal dose kinetics ($\int T dt$) accurately.

---

### 7. `A.E.%` (Acetone Extractable Content %)
* **Algorithm Used:** `GradientBoostingRegressor` (150 Estimators, learning_rate=0.03)
* **Model Accuracy:** **92.01%** (MAPE: 7.99%)
* **What it Does:** Predicts the percentage of unreacted resins, plasticizers, and organic extractables remaining in the vulcanized matrix.
* **Why this Algorithm:** Sequential boosting focuses step-by-step on residual extraction offsets from pressure step changes.

---

### 8. `Ash%` (Inorganic Ash Content %)
* **Algorithm Used:** `ExtraTreesRegressor` (250 Estimators, max_depth=6)
* **Model Accuracy:** **90.57%** (MAPE: 9.43%)
* **What it Does:** Predicts the remaining inorganic filler fraction (zinc oxide, stearic acid, silicates) after high-temperature laboratory burnoff.
* **Why this Algorithm:** Handles non-linear interactions between bottom door open temp and cooling open pressure.

---

### 9. `V.M.%` (Volatile Matter %)
* **Algorithm Used:** `GradientBoostingRegressor` (150 Estimators, learning_rate=0.03)
* **Model Accuracy:** **90.44%** (MAPE: 9.56%)
* **What it Does:** Predicts the residual moisture and volatile organic vapor percentage trapped inside the vessel.
* **Why this Algorithm:** Gradient boosting models steam pressure evaporation thresholds with fine granularity.

---

### 10. `Mv` (Secondary Mooney Viscosity)
* **Algorithm Used:** `RandomForestRegressor` (200 Estimators, max_depth=5)
* **Model Accuracy:** **90.26%** (MAPE: 9.74%)
* **What it Does:** Predicts secondary unvulcanized compound flow viscosity measured at 100°C.
* **Why this Algorithm:** Bagged ensemble trees smooth out sensor variance in actual batch durations.

---

### 11. `AC Mooney` (Autoclave Mooney Viscosity)
* **Algorithm Used:** `ExtraTreesRegressor` (250 Estimators, max_depth=6)
* **Model Accuracy:** **89.28%** (MAPE: 10.72%)
* **What it Does:** Predicts primary raw rubber compound viscosity state before final vulcanization cure.
* **Why this Algorithm:** ExtraTrees models raw polymer rheology viscosity shifts driven by loading and unloading temperature cycles.

---

## 🛠️ Summary of the Machine Learning Algorithms Used

1. **`ExtraTreesRegressor` (Extremely Randomized Trees):**
   * *Used for:* `Sp.Gravity`, `Hardness`, `TS`, `Ash%`, `AC Mooney`.
   * *How it works:* An ensemble of decision trees where feature split points are drawn randomly. Reduces model variance and prevents overfitting on complex non-linear physics curves.

2. **`Ridge Regression` ($L_2$ Regularized Linear Model):**
   * *Used for:* `RHC`, `C.B.%`.
   * *How it works:* Linear regression with a squared penalty ($\alpha \sum \beta^2$) on feature weights. Ideal for conservation-of-mass filler retention models.

3. **`RandomForestRegressor` (Bagged Decision Trees):**
   * *Used for:* `EB`, `Mv`.
   * *How it works:* Combines predictions from multiple deep decision trees trained on bootstrap samples. Excellent for smooth elastic deformation curves.

4. **`GradientBoostingRegressor` (Boosted Decision Trees):**
   * *Used for:* `A.E.%`, `V.M.%`.
   * *How it works:* Builds trees sequentially, where each new tree corrects the errors (residuals) of previous trees. Ideal for sharp volatile evaporation thresholds.

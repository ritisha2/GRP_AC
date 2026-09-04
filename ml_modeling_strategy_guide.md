# Machine Learning Strategy: Predicting Quality Data from Production Data ONLY

---

## 📌 Problem Setup & Production-Only Inputs

> **Constraint:** At prediction time, **ONLY Production Process Data will be entered by the user.**
> 
> **Goal:** Predict all **11 Quality Data columns** (`AC Mooney`, `Ash%`, `C.B.%`, `A.E.%`, `V.M.%`, `RHC`, `Sp.Gravity`, `Mv`, `TS`, `EB`, `Hardness`) and calculate the overall **Success %**, using **ONLY Production Data** as inputs.

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ USER INPUTS (Production Data ONLY):                                                   │
│ • Vessel Temperatures (Loading, Steam Open/Close, Heat Close, Cooling, Unload)        │
│ • Vessel Pressures (Loading, Door Close, Steam Open/Close, Heat Close, Cooling)        │
│ • Cycle Durations (Loading, Cooking, Low TF Duration, Cooling, Unloading, Actual Batch)│
│ • Operational Context (Shift, Supervisor, Operator, Customer)                          │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ HYBRID PHYSICS + ML ARCHITECTURE (Physics-Informed Machine Learning):                  │
│                                                                                        │
│  [Production Inputs] ──► [LAYER 1: Physical Kinetic Formulas] ──► Baseline Estimate    │
│                                          │                                             │
│                                          ▼                                             │
│  [Production Inputs + Baseline] ──► [LAYER 2: ML Model Suite]  ──► Final Predicted     │
│                                      (RF, XGBoost, Ridge)          Quality Outputs     │
└────────────────────────────────────────────────────────────────────────────────────────┘
                                           │
                                           ▼
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ LAYER 3: SPEC COMPLIANCE CHECKER:                                                      │
│ • Displays 11 Predicted Quality Values                                                 │
│ • Checks each predicted value against Min & Max Spec Limits                             │
│ • Calculates Overall Batch Success % = (Pass Count / 11) * 100%                        │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## ❓ Frequently Asked Questions: Why Baselines & How They Work

### Q1: Why do we need baseline estimates?

1. **Small Dataset Anchor (143 Batches):** Machine Learning models trained on small datasets (143 historical runs) can get confused or overfit if forced to learn complex polymer thermodynamics from scratch. The baseline formula acts as a **physical anchor** grounded in real chemical laws ($\int T dt$, thermodynamics, kinetics).
2. **Eliminates Wild/Impossible Predictions:** Without a baseline anchor, pure ML models might output physically impossible numbers (e.g. negative viscosity or 200° Shore Hardness) when given unusual user inputs. The baseline estimate guarantees predictions stay within realistic physical boundaries.

---

### Q2: What happens after the ML model predicts the output?

Instead of forcing the ML model to guess the entire output from zero, the ML model predicts the **Residual Correction ($\Delta$)** — the small adjustment needed for specific factory operating conditions (`Customer`, `Operator`, `Shift`, ambient factory temperature, sensor drift):

$$\text{Final Predicted Quality Output} = \text{Baseline Estimate (Physics)} + \text{Model Residual Correction (ML)}$$

#### Example in Action (`AC Mooney` Prediction):
* User enters vessel parameters: $T_{\text{unload}} = 105^\circ\text{C}$, $t_{\text{cook}} = 250\text{ mins}$, $P_{\text{door}} = 0.08\text{ kg/cm}^2$.
* **Step 1 (Physical Baseline):** Formula calculates baseline $\text{Base\_Mooney} = 58.0 + 0.25(105-100) + 0.05(250-245) = 59.5$.
* **Step 2 (ML Correction):** Random Forest recognizes that Customer `Pirelli` on `Shift 2` usually runs $+0.8$ units higher viscosity due to compounding grade.
* **Step 3 (Final Output):** $\text{Final Mooney} = 59.5 + 0.8 = \mathbf{60.3}$.

---

### Q3: What will the baseline estimate then do during analysis?

The baseline estimate provides **Operational Explainability & Root-Cause Diagnosis**:

If a predicted batch is flagged as **FAILing** quality specifications (e.g. Tensile Strength is too low):
* **The Baseline Estimate tells the engineer:** *"The physical heat duration caused 85% of the strength drop."* $\longrightarrow$ **Fix:** Adjust vessel steam valve temperature.
* **The ML Residual tells the engineer:** *"The remaining 15% drop is due to customer-specific formulation or operator shift timing."* $\longrightarrow$ **Fix:** Adjust shift procedural timing.

This allows factory engineers to know **EXACTLY** whether a quality problem requires a **machine physics adjustment** or an **operational/process adjustment**.

---

## 🔬 Breakdown of the 3 Architecture Layers

### Layer 1: The Physical Formula Layer (Domain Baseline)
Computes baseline physical estimates directly from user inputs using chemical kinetics:
* **Viscosity Baseline:** $\text{Base\_Mooney} = 58.0 + 0.25(T_{\text{unload}}-100) + 0.05(t_{\text{cook}}-245) - 0.20(P_{\text{door}}-0.08)$
* **Tensile Reversion Baseline:** $\text{Base\_TS} = 85.28 - 0.238(T_{\text{steam\_open}}-96) - 0.048(T_{\text{cool}}-99) - 0.026(t_{\text{actual}}-369)$
* **Hardness Cross-Link Baseline:** $\text{Base\_Hardness} = 51.0 - 0.008(T_{\text{cool}}-99) - 0.027(T_{\text{steam\_open}}-96) + 0.010(T_{\text{heat}}-222)$

### Layer 2: The Machine Learning Layer (Residual Error Correction)
Predicts the operational adjustment $\Delta$ using specialized model groups:
* **Random Forest Regressor** predicts non-linear rheology: `AC Mooney`, `Mv`, `TS`, `EB`, `Hardness`.
* **Gradient Boosting (XGBoost)** predicts thermal evaporation & density thresholds: `V.M.%`, `Sp.Gravity`, `Ash%`, `C.B.%`, `A.E.%`.
* **Ridge Linear Regression** predicts polymer mass retention: `RHC`.

### Layer 3: The Deterministic Spec Compliance Engine (`Success %`)
Compares each final predicted value against Min & Max Spec Limits, assigns **PASS (Green)** or **FAIL (Red)** badges, and computes the overall compliance rate:
$$\text{Success \%} = \frac{\text{Number of Passed Parameters}}{11} \times 100\%$$

---

## 📋 Complete Execution Table for All 11 Quality Parameters

| Quality Target | Layer 1: Physical Formula Baseline | Layer 2: ML Residual Predictor | Layer 3: Spec Check Rule |
|---|---|---|---|
| **`AC Mooney`** | $58.0 + 0.25(T_{\text{unload}}-100) + 0.05(t_{\text{cook}}-245) - 0.20(P_{\text{door}}-0.08)$ | **Random Forest** corrects for `Customer` & duration interactions | Check $50.0 \le \text{Val} \le 60.0$ |
| **`Ash%`** | $5.61 + 0.006(T_{\text{cool}}-99) - 3.0(P_{\text{load}}-0.07) + 0.015(T_{\text{door}}-104)$ | **Gradient Boosting** corrects for vessel heating compaction | Check $3.0 \le \text{Val} \le 7.0$ |
| **`C.B.%`** | $30.24 + 3.0(P_{\text{load}}-0.07) - 0.095(P_{\text{steam}}-5.35) - 0.005(T_{\text{cool}}-99)$ | **Gradient Boosting** corrects for steam compaction | Check $28.0 \le \text{Val} \le 36.0$ |
| **`A.E.%`** | $7.43 + 0.031(P_{\text{heat}}-14.46) - 0.003(t_{\text{cook}}-245) - 0.002(T_{\text{cool}}-99)$ | **Gradient Boosting** corrects for resin extraction | Check $6.0 \le \text{Val} \le 12.0$ |
| **`V.M.%`** | $0.192 - 0.004(P_{\text{steam}}-5.35) - 0.0007(T_{\text{load}}-103) + 0.0001(t_{\text{low\_tf}}-233)$ | **Gradient Boosting** corrects for evaporation thresholds | Check $0.0 \le \text{Val} \le 1.0$ |
| **`RHC`** | $56.40 + 0.073(P_{\text{cool}}-0.08) + 0.007(T_{\text{steam}}-129) - 0.009(T_{\text{unload}}-101.5)$ | **Ridge Regression** corrects for polymer retention | Check $\text{Val} \ge 50.0$ |
| **`Sp.Gravity`** | $1.151 + 0.001(P_{\text{heat}}-14.46) + 0.023(P_{\text{load}}-0.07) - 0.029(P_{\text{door}}-0.07)$ | **Gradient Boosting** corrects for volumetric compression | Check $1.12 \le \text{Val} \le 1.16$ |
| **`Mv`** | $40.0 + 0.100(T_{\text{heat}}-222) + 0.045(T_{\text{steam}}-129) - 0.012(t_{\text{actual}}-369)$ | **Random Forest** corrects for secondary thermal dose | Check $30.0 \le \text{Val} \le 45.0$ |
| **`TS`** | $85.28 - 0.238(T_{\text{steam\_open}}-96) - 0.048(T_{\text{cool}}-99) - 0.026(t_{\text{actual}}-369)$ | **Random Forest** corrects for thermal over-cure reversion | Check $\text{Val} \ge 75.0$ |
| **`EB`** | $507.5 + 0.719(P_{\text{cool}}-0.08) + 0.035(t_{\text{low\_tf}}-233) - 0.165(T_{\text{load}}-103)$ | **Random Forest** corrects for elastic polymer chain stretch | Check $\text{Val} \ge 480.0$ |
| **`Hardness`** | $51.0 - 0.008(T_{\text{cool}}-99) - 0.027(T_{\text{steam\_open}}-96) + 0.010(T_{\text{heat}}-222)$ | **Random Forest** corrects for cross-link density shutoff | Check $48.0 \le \text{Val} \le 54.0$ |
| **`Success %`** | Sum of Pass Badges across all 11 Quality Parameters | **Deterministic Rule Engine** computes exact % | Output Final Batch Score |

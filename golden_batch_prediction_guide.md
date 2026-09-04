# Golden Batch Prediction & Quality Classification Guide

---

## 🌟 Executive Overview: What is a "Golden Batch"?

In autoclave manufacturing, a **Golden Batch** represents a production batch where the process operating conditions produce optimal rubber quality, meeting or exceeding strict specification standards across almost all parameters.

### 📜 The Official Golden Batch Classification Rule:

```
┌────────────────────────────────────────────────────────────────────────────────────────┐
│ STEP 1: Predict 11 Quality Parameters from Production Inputs                           │
│ STEP 2: Evaluate each predicted value against Min & Max Spec Limits (Pass / Fail)      │
│ STEP 3: Compute Overall Batch Success % = (Passed Parameters Count / 11) * 100%       │
│                                                                                        │
│ STEP 4: Golden Batch Classification Decision Rule:                                     │
│ • If Success % is between 90.0% and 100.0% ──► 🌟 GOLDEN BATCH (Optimal Quality)        │
│ • If Success % is between 75.0% and 89.9%  ──► ⚠️ STANDARD BATCH (Acceptable Quality)   │
│ • If Success % is below 75.0%              ──► ❌ NON-CONFORMING BATCH (Defect Risk)    │
└────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 🔬 Step-by-Step Architecture: How We Achieve Golden Batch Predictions

Here is the complete step-by-step pipeline showing how production inputs transform into quality predictions, success percentages, and Golden Batch status:

```
[User Inputs Production Settings]
               │
               ▼
[Hybrid Physics + ML Models] ──► Predicts 11 Quality Parameters
               │
               ▼
[Spec Limits Checker]        ──► Evaluates Pass / Fail for each Parameter
               │
               ▼
[Success % Calculator]       ──► Computes Overall Success %
               │
               ▼
[Golden Batch Decision Engine] ──► Classifies Batch & Displays Visual Badges
```

---

### Step 1: User Inputs Production Settings ONLY
The operator enters the autoclave process parameters into the web application:
* **Vessel Temperatures:** Loading Temp, Steam Open/Close Temp, Heat Close Temp, Cooling Close Temp, Unload Temp.
* **Vessel Pressures:** Loading Pressure, Door Close Pressure, Steam Open/Close Pressure, Heat Close Pressure.
* **Cycle Durations:** Cooking Duration, Low TF Duration, Actual Batch Duration.
* **Operational Context:** Customer (`Pirelli`, `Other`, etc.), Shift, Operator.

---

### Step 2: Quality Parameter Prediction
The hybrid **Physics-Informed Machine Learning** suite predicts the 11 quality values:
$$\text{Predicted Quality Output}_i = \text{Physical Baseline Formula}_i + \text{ML Model Residual Correction}_i$$

---

### Step 3: Individual Parameter Spec Check (Pass / Fail)

Each predicted value is checked against its official specification limits:

| Quality Parameter | Min Spec Limit | Max Spec Limit | Pass Condition |
|---|---|---|---|
| **`AC Mooney`** | 50.0 | 60.0 | $50.0 \le \text{Predicted Mooney} \le 60.0$ |
| **`Ash%`** | 3.0 | 7.0 | $3.0 \le \text{Predicted Ash\%} \le 7.0$ |
| **`C.B.%`** | 28.0 | 36.0 | $28.0 \le \text{Predicted C.B.\%} \le 36.0$ |
| **`A.E.%`** | 6.0 | 12.0 | $6.0 \le \text{Predicted A.E.\%} \le 12.0$ |
| **`V.M.%`** | 0.0 | 1.0 (Max) | $\text{Predicted V.M.\%} \le 1.0$ |
| **`RHC`** | 50.0 (Min) | 100.0 | $\text{Predicted RHC} \ge 50.0$ |
| **`Sp.Gravity`** | 1.12 | 1.16 | $1.12 \le \text{Predicted Density} \le 1.16$ |
| **`Mv`** | 30.0 | 45.0 | $30.0 \le \text{Predicted Mv} \le 45.0$ |
| **`TS`** (Tensile) | 75.0 (Min) | 150.0 | $\text{Predicted TS} \ge 75.0$ |
| **`EB`** (Elongation) | 480.0 (Min) | 700.0 | $\text{Predicted EB} \ge 480.0$ |
| **`Hardness`** | 48.0 | 54.0 | $48.0 \le \text{Predicted Hardness} \le 54.0$ |

---

### Step 4: Overall Success % Calculation

The Success % is calculated using a deterministic exact mathematical formula:

$$\text{Success \%} = \left( \frac{\text{Number of Passed Parameters}}{11} \right) \times 100\%$$

#### Possible Discrete Success % Outcomes:
* **11 out of 11 Pass:** $(11 / 11) \times 100\% = \mathbf{100.0\%}$
* **10 out of 11 Pass:** $(10 / 11) \times 100\% = \mathbf{90.9\%}$
* **9 out of 11 Pass:** $(9 / 11) \times 100\% = \mathbf{81.8\%}$
* **8 out of 11 Pass:** $(8 / 11) \times 100\% = \mathbf{72.7\%}$

---

### Step 5: Golden Batch Classification Engine

Based on the calculated Success %, the system assigns the final Batch Status:

| Success % Range | Passed Parameters Count | Golden Batch Status | Badge Color | Operator Action |
|---|---|---|---|---|
| **90.0% – 100.0%** | **10 or 11 out of 11** | 🌟 **GOLDEN BATCH** | **Bright Green (`#22C55E`)** | Approve batch for premium shipment. |
| **75.0% – 89.9%** | **9 out of 11** | ⚠️ **STANDARD BATCH** | **Amber Orange (`#F59E0B`)** | Acceptable batch; minor parameter warning. |
| **< 75.0%** | **8 or fewer out of 11** | ❌ **NON-CONFORMING BATCH** | **Red (`#EF4444`)** | Flag for quality inspection & process adjustment. |

---

## 💻 Python Implementation Code for Streamlit Frontend

Here is the exact Python implementation logic for your web application:

```python
# 1. Official Spec Limits
SPEC_RANGES = {
    'AC Mooney':  (50.0, 60.0),
    'Ash%':       (3.0, 7.0),
    'C.B.%':      (28.0, 36.0),
    'A.E.%':      (6.0, 12.0),
    'V.M.%':      (0.0, 1.0),
    'RHC':        (50.0, 100.0),
    'Sp.Gravity': (1.12, 1.16),
    'Mv':         (30.0, 45.0),
    'TS':         (75.0, 150.0),
    'EB':         (480.0, 700.0),
    'Hardness':   (48.0, 54.0),
}

def evaluate_golden_batch(predictions_dict):
    """
    Evaluates 11 predicted quality parameters and returns:
    1. Pass/Fail status per parameter
    2. Overall Success %
    3. Golden Batch Classification
    """
    pass_count = 0
    total_params = len(SPEC_RANGES)
    param_results = []

    for param, pred_val in predictions_dict.items():
        min_spec, max_spec = SPEC_RANGES[param]
        is_pass = min_spec <= pred_val <= max_spec
        
        if is_pass:
            pass_count += 1
            status = "PASS"
        else:
            status = "FAIL"
            
        param_results.append({
            'Parameter': param,
            'Predicted Value': round(pred_val, 3),
            'Spec Min': min_spec,
            'Spec Max': max_spec,
            'Status': status
        })

    # Calculate Success %
    success_pct = round((pass_count / total_params) * 100, 1)

    # Classify Golden Batch Status (90% - 100% threshold)
    if success_pct >= 90.0:
        batch_status = "🌟 GOLDEN BATCH"
        status_color = "#22C55E"
        description = "Optimal rubber quality. Approved for premium customer dispatch."
    elif success_pct >= 75.0:
        batch_status = "⚠️ STANDARD BATCH"
        status_color = "#F59E0B"
        description = "Acceptable quality. Minor operational variance detected."
    else:
        batch_status = "❌ NON-CONFORMING BATCH"
        status_color = "#EF4444"
        description = "Quality defect risk. Requires process adjustment before next batch."

    return {
        'success_pct': success_pct,
        'pass_count': pass_count,
        'total_params': total_params,
        'batch_status': batch_status,
        'status_color': status_color,
        'description': description,
        'param_results': param_results
    }
```

---

## 🌟 Real-World Scenario Examples

### Example A: Golden Batch (Success % = 100.0%)
* **Operator Inputs:** Standard Pirelli production recipe ($T_{\text{cook}} = 222^\circ\text{C}$, $P_{\text{heat}} = 14.5\text{ kg/cm}^2$, $t_{\text{cook}} = 245\text{ mins}$).
* **Predicted Outputs:** All 11 parameters fall within spec limits (e.g. Mooney = 58.2, TS = 86.5, Hardness = 51.0).
* **Result:** **11/11 Pass (100.0%)** $\longrightarrow$ **🌟 GOLDEN BATCH** badge displayed in green.

### Example B: Golden Batch (Success % = 90.9%)
* **Operator Inputs:** Slight variation in loading temperature ($T_{\text{load}} = 115^\circ\text{C}$).
* **Predicted Outputs:** 10 parameters pass; Mooney = 60.4 (slightly above 60.0 max spec).
* **Result:** **10/11 Pass (90.9%)** $\longrightarrow$ **🌟 GOLDEN BATCH** badge displayed in green.

### Example C: Standard Batch (Success % = 81.8%)
* **Operator Inputs:** Unloading temperature too high ($T_{\text{unload}} = 120^\circ\text{C}$).
* **Predicted Outputs:** 9 parameters pass; Mooney = 62.5 (fails) and Tensile Strength = 73.0 (fails).
* **Result:** **9/11 Pass (81.8%)** $\longrightarrow$ **⚠️ STANDARD BATCH** badge displayed in orange.

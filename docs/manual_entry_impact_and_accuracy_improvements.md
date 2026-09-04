# Impact Analysis: Manual Google Form Entry vs. Sensor-Logged Data
## And: How to Increase Prediction Accuracy Given the Current Real-World Constraint

---

> **The Core Issue Revealed:**
> The 14 "sensor" values currently used as model inputs are **not** automatic PLC sensor readings.
> They are **manually typed by operators into a Google Form at random intervals during the batch cycle.**
> The autoclave sensors are under maintenance and not logging data automatically.

---

## Part 1: How This Changes Everything — Problem Statement

### What Was Assumed (Original Design)
```
Autoclave PLC sensors
    → Automatically log exact temperature/pressure at each process event
    → e.g., the moment the steam valve physically closes, PLC records: Temp=129.0°C, Pressure=5.35 kg/cm²
    → Values are precise, timestamped, and event-triggered
```

### What Is Actually Happening (Current Reality)
```
Autoclave runs its cycle (6 hours)
    → Operator watches the process (or doesn't watch continuously)
    → At some point, operator goes to a Google Form on their phone/computer
    → Types in what they remember seeing on the pressure gauge / thermometer
    → At random intervals (not event-triggered)
    → Values are: estimated, recalled from memory, read from analog dials at the wrong moment
```

### The Gap — What This Means for the Data

| Issue | Original Assumption | Current Reality | Impact on Accuracy |
|-------|--------------------|-----------------|--------------------|
| **Timing** | Values recorded at exact process event millisecond | Recorded whenever operator finds time | HIGH — wrong timing = wrong value |
| **Precision** | Digital sensor: ±0.1°C | Manual reading of analog dial: ±5°C or more | MEDIUM — adds noise to inputs |
| **Completeness** | 100% — every batch, every field | Some fields: **23–43% missing** | HIGH — median fill loses real variation |
| **Consistency** | Same sensor, same calibration, every time | Different operators read differently | MEDIUM — inter-operator variability |
| **Honesty** | Machine cannot lie | Operator may estimate or copy from last entry | LOW-MEDIUM — possible duplication |

---

## Part 2: Specific Problems Found in the Data

From analysing `production_clean.csv`, here are the confirmed issues:

### Missing Values — Severe in Several Columns

| Column | Missing Entries | Missing % | Current Fix | What's Lost |
|--------|----------------|-----------|-------------|-------------|
| Cooling Valve Close Pressure | 62 / 143 | **43.4%** | Filled with median | Real process variation wiped out |
| Cooling Valve Close Temp | 57 / 143 | **39.9%** | Filled with median | Real process variation wiped out |
| Unload Complete Pressure | 38 / 143 | **26.6%** | Filled with median | Always predicts average |
| Loading Pressure | 43 / 143 | **30.1%** | Filled with median | Always predicts average |
| Close Top Door Pressure | 34 / 143 | **23.8%** | Filled with median | Always predicts average |

> **The 43% missing Cooling Valve Close Pressure** means the model effectively sees the same value (the median) for nearly half of all training batches. This is a major source of noise and reduced accuracy.

### Timing Problem — The "Random Interval" Issue

When an operator records "Steam Valve Close Temp = 129°C" in the Google Form, they are supposed to record the temperature **at the exact moment the steam valve closed**. But:

- If they enter it 10 minutes later → the temperature may have risen to 140°C by then
- If they enter it from memory at the end of the shift → the value could be anything
- If the process was fast and they missed it → they may copy from the previous batch

This adds **random noise directly to the model's inputs**. The model cannot distinguish between:
- "This batch genuinely had a Steam Valve Close Temp of 140°C"
- "The operator wrote 140°C because they checked the gauge 10 minutes too late"

### The "Random Interval" Error — Quantified

```
If an operator records Steam Valve Close Temp 10 minutes LATE:
  Autoclave typically heats at ~2-3°C per minute during this phase
  10-minute delay → reading is 20-30°C higher than it should be

In the physics baseline formula:
  Physics_TS_Base = 85.28 - 0.238 × (Recorded_Temp - 96)
  
  Correct recording  (129°C): 85.28 - 0.238 × (129 - 96) = 85.28 - 7.85 = 77.43
  10-min late (149°C): 85.28 - 0.238 × (149 - 96) = 85.28 - 12.61 = 72.67

  Difference in TS prediction: 4.76 N/cm² from a single recording error.
  At a mean TS of 85.3, that's a 5.6% error from ONE bad entry.
```

---

## Part 3: What the Data IS Giving Us That's Reliable

Not everything is broken. Some inputs are much more reliable than others:

### High-Reliability Inputs (Operator Can Record Accurately)

| Input | Why It's Reliable |
|-------|-------------------|
| **Customer** | Known before the batch starts — no estimation needed |
| **Shift** | Operator knows their own shift |
| **Supervisor / Operator name** | Known to the person filling the form |
| **Standard Batch Duration** | Fixed by recipe — just looked up from a sheet |
| **Actual Batch Duration (Total Minutes)** | Easy to calculate: end time minus start time |
| **Bottom Door Open Temp** | Operator is physically present at discharge — can check gauge carefully |

### Medium-Reliability Inputs (Some Estimation Required)

| Input | Risk |
|-------|------|
| **Heat Valve Close Temp/Pressure** | Operator must be watching at exact moment heat valve closes |
| **Cooking Duration** | Likely derived from total batch time minus other phases — not a direct reading |

### Low-Reliability Inputs (High Error Risk)

| Input | Risk |
|-------|------|
| **Steam Valve Open Temp/Pressure** | Early in the batch, operator may not be present |
| **Steam Valve Close Temp/Pressure** | Must be recorded at exact moment — easy to miss |
| **Cooling Valve Close Temp/Pressure** | 43% missing — clearly being missed regularly |
| **Low TF Temp Duration (mins below 260°C)** | Requires calculating cumulative time — very hard to do manually |

---

## Part 4: The Hidden Gold — What's Being Ignored

Looking at the data structure, there are inputs that are **currently being discarded** by the ML model that carry high-quality information:

### 1. Customer Field → Effectively Encodes the Formulation Recipe

Each customer gets a specific rubber compound formulation (specific recipe). If Pirelli always gets Recipe A with N330 carbon black at 35 PHR, and Alfredo always gets Recipe B with N660 at 30 PHR, then:

```
Customer = "Pirelli"  →  Implicitly tells the model: PHR_CB=35, PHR_Plasticizer=12, Grade=N330
Customer = "Alfredo"  →  Implicitly tells the model: PHR_CB=30, PHR_Plasticizer=10, Grade=N660
```

**The customer field is a proxy for the entire compounding recipe that we said we don't have!**

From the data analysis:
- Pirelli batches: Ash% mean = 5.79%, RHC mean = 56.42%
- Alfredo batches: Ash% mean = 5.31%, RHC mean = 56.82% (measurably different formulation)

However, the current model **does not use the Customer field at all** — it was excluded because only numeric features were selected. This is a missed opportunity.

### 2. Supervisor/Operator → Encodes Process Know-How

Different supervisors have different operating styles — how they heat the batch, when they close valves, how precisely they follow the recipe. The data shows:
- 8 different supervisors
- 11 different operators

This categorical information captures the "human process variability" that the sensor readings fail to capture accurately.

### 3. Additional Temperature/Pressure Columns Not Being Used

The production CSV has **34 columns total** but the model only uses **14**. Unused columns include:
- Loading Temp & Pressure (batch start state)
- Close Top Door Temp & Pressure (sealing state)
- Heat Valve Open Temp & Pressure (early heating state)
- Cooling Valve Close Temp & Pressure (end of cooling state)
- Unload Complete Temp & Pressure (discharge state)

---

## Part 5: Concrete Recommendations — What to Change

### Priority 1 — Add Customer, Shift, and Supervisor as Model Inputs (HIGHEST IMPACT)

**Change in `train_all_quality_models.py`:** Add one-hot encoded categorical features.

```python
# Add these categorical features (they are reliably filled in the Google Form)
from sklearn.preprocessing import OneHotEncoder

categorical_features = ['Customer', 'Shift', 'Supervisor']

# One-hot encode
ohe = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
cat_matrix = ohe.fit_transform(prod[categorical_features].fillna('Unknown'))
cat_df = pd.DataFrame(cat_matrix, columns=ohe.get_feature_names_out(categorical_features))

# Merge with existing 33 engineered features
X_feat = pd.concat([X_feat.reset_index(drop=True), cat_df], axis=1)
```

**Why this helps:** Customer = recipe proxy, Supervisor = process consistency proxy. These are reliably entered in the Google Form and carry composition information that sensor readings can't.

**Expected accuracy improvement:** +3-8% for Ash%, C.B.%, A.E.%, RHC (composition-sensitive parameters).

---

### Priority 2 — Add All Unused Production Columns (MEDIUM IMPACT)

The CSV has columns with data that the model ignores. Add them:

```python
# Expanded feature list — use ALL available numeric columns, not just 14
ALL_NUMERIC_COLS = [
    # Currently used (14)
    "Steam Valve Open Temp (°C)", "Steam Valve Open Pressure (kg/cm2)",
    "Steam Valve Close Temp (°C)", "Steam Valve Close Pressure (kg/cm2)",
    "Heat Valve Close Temp (°C)", "Heat Valve Close Pressure (kg/cm2)",
    "Low TF Temp Duration(Mins) (Below 260°C)", "Cooking Duration (HH:MM)",
    "Cooling Valve Open Temp(°C)", "Cooling Valve Open Pressure (kg/cm2)",
    "Bottom Door Open Temp(°C)", "Bottom Door Open Pressure (kg/cm2)",
    "Standard Batch Duration(Hrs)", "Actual Batch Duration (Mins)",
    # NEW — currently in CSV but ignored
    "Loading Temp (°C)", "Loading Pressure (kg/cm2)",
    "Close Top Door Temp (°C)", "Close Top Door Pressure (kg/cm2)",
    "Heat Valve Open Temp (°C)", "Heat Valve Open Pressure (kg/cm2)",
    "Cooling Valve Close Temp(°C)", "Cooling Valve Close Pressure (kg/cm2)",
    "Bottom Door Close Temp(°C)", "Bottom Door Close Pressure (kg/cm2)",
]
```

**Caveat:** Some of these (Cooling Valve Close Pressure: 43% missing) are highly unreliable from manual entry. The median imputation will reduce their contribution, but they still add useful signal for the batches where they ARE recorded.

---

### Priority 3 — Fix the Google Form Data Entry Protocol (HIGHEST REAL-WORLD IMPACT)

This is not a code change — it is a **process change** that will improve the quality of every new batch recorded and steadily improve model accuracy as better data accumulates.

#### Redesign the Google Form with these rules:

**A. Define EXACTLY when each value must be entered (not at "random intervals"):**

| Field | Exactly When to Record |
|-------|----------------------|
| Steam Valve Open Temp/Pressure | At the moment you OPEN the steam valve (record immediately, before doing anything else) |
| Steam Valve Close Temp/Pressure | At the moment you CLOSE the steam valve |
| Heat Valve Close Temp/Pressure | At the moment you CLOSE the heat valve |
| Cooking Duration | When cooking phase ends: note the clock time when cooking starts and when it ends |
| Cooling Valve Open Temp/Pressure | At the moment you OPEN the cooling valve |
| Bottom Door Open Temp/Pressure | At the moment you OPEN the bottom door |
| Actual Batch Duration | End time minus start time (total elapsed minutes) |

**B. Add validation in the Google Form:**

| Field | Min Value | Max Value | Cross-Validation Rule |
|-------|-----------|-----------|----------------------|
| Steam Valve Open Temp | 60°C | 160°C | Must be < Steam Valve Close Temp |
| Steam Valve Close Temp | 100°C | 220°C | Must be > Steam Valve Open Temp |
| Heat Valve Close Temp | 150°C | 250°C | Must be > Steam Valve Close Temp |
| Steam Valve Close Pressure | 2.0 | 18.0 kg/cm² | — |
| Actual Batch Duration | 200 min | 800 min | — |
| Cooking Duration | 100 min | 500 min | Must be < Actual Batch Duration |

**C. Add a mandatory "Batch Start Time" and "Batch End Time" field:**
- Actual Batch Duration = automatically calculated = End Time - Start Time
- Removes the biggest source of manual calculation error

**D. Add "Was this value estimated or directly read?" checkbox for each critical field:**
- This flags uncertain entries so the model training can optionally downweight them

---

### Priority 4 — Reliability-Weighted Training (MEDIUM IMPACT)

Since some data entries are more reliable than others, train models with **sample weights** — giving less weight to batches with many missing values or potential operator entry errors:

```python
# Calculate data quality score per batch
def calculate_data_quality_weight(row):
    # How many of the 14 key fields are non-NaN?
    non_null_count = row[USER_AVAILABLE_NUMERIC_COLS].notna().sum()
    # Weight = fraction of fields that were actually recorded (not imputed)
    return non_null_count / len(USER_AVAILABLE_NUMERIC_COLS)

sample_weights = X_raw.apply(calculate_data_quality_weight, axis=1).values

# Then in training:
model.fit(X_train, y_train, sample_weight=sample_weights[train_indices])
```

This tells the model: "Trust the batches with complete data more than batches where half the fields were missing and filled with median values."

---

### Priority 5 — Switch to More Robust Models for Noisy Input (MEDIUM IMPACT)

For manually-entered, noisy data, some model configurations are better than others:

| Current Config | Problem | Better Config for Manual Data |
|---------------|---------|-------------------------------|
| ExtraTrees, n=250, max_depth=6 | Can overfit to noise patterns in training data | ExtraTrees, n=300, max_depth=4 (shallower = less overfit) |
| GradientBoosting, lr=0.03, n=150 | Sequential boosting can amplify input noise | GradientBoosting, lr=0.01, n=200 (slower learning = more robust) |
| Ridge alpha=10.0 | Good as-is for noisy data — regularization helps | Keep alpha=10.0 or increase to 50.0 |

---

## Part 6: What NOT to Change

### Do NOT change the physics baseline formulas
The physics baselines are **sensor-independent** — they represent the underlying physical truth of how autoclave parameters relate to quality. Even if individual readings are noisy, the baselines provide a stable prior that prevents the ML models from going wildly wrong.

### Do NOT remove the median imputation
With 23-43% missing values in some columns, median imputation is the correct approach. Removing it would cause model crashes. The right fix is improving data collection (Priority 3), not removing the imputation.

### Do NOT increase model complexity
More complex models (deeper trees, more estimators) will memorise the noise in the manual entries rather than learning real patterns. The current complexity is already at the upper limit for 143 batches of manually-entered data.

---

## Part 7: Realistic Accuracy Expectations

### Current Accuracy (with noisy manually-entered data, 143 batches)

| Model | Current Accuracy | Reason for Gap |
|-------|-----------------|----------------|
| Sp.Gravity | 99.42% | Almost insensitive to process — noise doesn't matter much |
| RHC | 98.54% | Mass balance constraint limits the range |
| Hardness | 97.79% | Narrow spec range (48-54) — small noise doesn't cause misclassification |
| AC Mooney | 89.28% | Highly sensitive to correct Steam Valve timings — manual entry noise hurts most |
| Mv | 90.26% | Depends on heat valve readings — frequently mis-timed |
| V.M.% | 90.44% | Post-discharge humidity not capturable |

### Expected Accuracy After All 5 Recommendations

| Model | Current | After Fix 1 (Customer) | After Fix 3 (Better Form) | After Fix 1+2+3 |
|-------|---------|------------------------|--------------------------|-----------------|
| AC Mooney | 89.28% | 90-91% | 92-94% | **93-95%** |
| Ash% | 90.57% | 92-94% | 91-93% | **93-96%** |
| C.B.% | 97.74% | 97-98% | 98% | **98%** |
| A.E.% | 92.01% | 93-94% | 93-94% | **94-95%** |
| V.M.% | 90.44% | 90-91% | 90-91% | **90-91%** (limited by humidity) |
| RHC | 98.54% | 98-99% | 98-99% | **98-99%** |
| Sp.Gravity | 99.42% | 99.4%+ | 99.4%+ | **99.4%+** |
| Mv | 90.26% | 90-92% | 92-94% | **92-94%** |
| TS | 92.28% | 92-93% | 94-95% | **94-96%** |
| EB | 97.74% | 97-98% | 97-98% | **97-98%** |
| Hardness | 97.79% | 97-98% | 98-99% | **98-99%** |
| **AVERAGE** | **94.27%** | **~95%** | **~95-96%** | **~96-97%** |

---

## Part 8: The One Thing That Would Increase Accuracy the Most

If you could do **only one thing** to increase accuracy given the manual entry constraint, it would be:

> **Add a "Product Recipe Code" or "Rubber Grade" dropdown to the Google Form, and use it as a model input.**

This one field — if it captures what formulation was used (which PHR of plasticizer, which carbon black grade, which sulfur content) — would effectively give the model access to the raw material composition data that it currently cannot see at all.

Even a simple code like:
- `R1` = Pirelli Standard Recipe
- `R2` = Pirelli Premium Recipe
- `R3` = Alfredo Recipe

...would allow the model to condition its predictions on the formulation, pushing Ash%, C.B.%, A.E.%, and AC Mooney accuracy toward 95-99%.

---

## Part 9: Summary Action Plan

| Priority | Action | Who Does It | Code Change? | Expected Impact |
|----------|--------|-------------|--------------|-----------------|
| 1 | Add Customer, Shift, Supervisor to model inputs | Developer | YES — `train_all_quality_models.py` | +3-8% accuracy on composition-sensitive targets |
| 2 | Add all unused CSV columns to model inputs | Developer | YES — `train_all_quality_models.py` | +1-3% accuracy |
| 3 | Redesign Google Form with exact recording timing + validation | Operations Manager | NO code change | +3-7% accuracy as data improves over time |
| 4 | Add sample weights based on data completeness | Developer | YES — `train_all_quality_models.py` | +1-2% accuracy |
| 5 | Add Recipe/Grade code to Google Form | Operations Manager + Developer | Small code change | +5-10% accuracy on composition targets |
| 6 | Reduce model depth to prevent overfitting noisy data | Developer | YES — `train_all_quality_models.py` | +1-3% accuracy |

---

*This document is part of the GRP-AC Autoclave Quality Prediction System*
*GitHub Repository: [ritisha2/GRP_AC](https://github.com/ritisha2/GRP_AC)*

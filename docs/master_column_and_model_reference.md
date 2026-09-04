# Master Reference: Columns, Google Form Fields & Complete Model Logic
## GRP-AC Autoclave Quality Prediction System

---

## TABLE OF CONTENTS
1. [Current Column Inventory — Production CSV (34 columns)](#1-current-column-inventory--production-csv)
2. [Current Column Inventory — Quality CSV (12 columns)](#2-current-column-inventory--quality-csv)
3. [Column Status: Used vs Not Used in Model](#3-column-status-used-vs-not-used)
4. [Columns to Add via Google Form](#4-columns-to-add-via-google-form)
5. [Complete Model Logic: All Formulas Layer by Layer](#5-complete-model-logic-all-formulas-layer-by-layer)
   - [Layer 0: Raw Input (14 sensors)](#layer-0-raw-inputs)
   - [Layer 1: Data Cleaning](#layer-1-data-cleaning)
   - [Layer 2A: Interaction Features (8 formulas)](#layer-2a-interaction-features)
   - [Layer 2B: Physics Baseline Features (11 formulas)](#layer-2b-physics-baseline-features)
   - [Layer 3: ML Models (11 algorithms)](#layer-3-ml-models--one-per-target)
   - [Layer 4: Golden Batch Scoring](#layer-4-golden-batch-scoring)
6. [Complete Feature Map: What Feeds What](#6-complete-feature-map)

---

## 1. Current Column Inventory — Production CSV

The `production_clean.csv` file has **34 columns** across 143 batch rows.

### Section A — Administrative / Categorical Columns (No measurement)

| # | Column Name | Data Type | Missing | Values Found | Currently Used in Model? |
|---|-------------|-----------|---------|--------------|--------------------------|
| 1 | Machine Idle | Integer (0/1) | 0 | 0 or 1 | ❌ No |
| 2 | Shift | Text | 0 | Shift 1, Shift 2, Shift 3 | ❌ No |
| 3 | Supervisor | Text | 0 | Gadagi, Kamlakar, Tikore, Rangrez, Shille, Chavan, Suryvanshi, Other | ❌ No |
| 4 | Operator | Text | 0 | Dhasade, Dixit, Methre, shinde, Rajput, Ingale, Sapar, Other | ❌ No |
| 32 | Customer | Text | 0 | Pirelli (116), Other (20), Alfredo (4), Sumo Tumo (3) | ❌ No |

---

### Section B — Loading Phase Columns (Batch Start)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 5 | Loading Temp (°C) | °C | **33 (23%)** | 70–125°C | ❌ No |
| 6 | Loading Pressure (kg/cm²) | kg/cm² | **43 (30%)** | 0.01–0.26 | ❌ No |
| 7 | Loading Duration (HH:MM) | Minutes | 0 | 0–1416 min | ❌ No |

---

### Section C — Door Sealing Phase

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 8 | Close Top Door Temp (°C) | °C | **25 (17%)** | 70–116°C | ❌ No |
| 9 | Close Top Door Pressure (kg/cm²) | kg/cm² | **34 (24%)** | 0.01–0.32 | ❌ No |

---

### Section D — Heating Start Phase

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 10 | Heat Valve Open Temp (°C) | °C | **15 (10%)** | 41–227°C | ❌ No |
| 11 | Heat Valve Open Pressure (kg/cm²) | kg/cm² | **30 (21%)** | 0.01–14.42 | ❌ No |

---

### Section E — Steam Phase (USED IN MODEL)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 12 | Steam Valve Open Temp (°C) | °C | 0 | 60–154°C | ✅ **Yes — Input #1** |
| 13 | Steam Valve Open Pressure (kg/cm²) | kg/cm² | 0 | 0.04–5.70 | ✅ **Yes — Input #2** |
| 14 | Steam Valve Close Temp (°C) | °C | 0 | 74–210°C | ✅ **Yes — Input #3** |
| 15 | Steam Valve Close Pressure (kg/cm²) | kg/cm² | 0 | 0.14–16.67 | ✅ **Yes — Input #4** |

---

### Section F — Peak Heating Phase (USED IN MODEL)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 16 | Heat Valve Close Temp (°C) | °C | 0 | 137–233°C | ✅ **Yes — Input #5** |
| 17 | Heat Valve Close Pressure (kg/cm²) | kg/cm² | 0 | 0.10–18.16 | ✅ **Yes — Input #6** |

---

### Section G — Cooking Phase (USED IN MODEL)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 18 | Low TF Temp Duration (Mins) (Below 260°C) | Minutes | 0 | 70–363 min | ✅ **Yes — Input #7** |
| 19 | Cooking Duration (HH:MM) | Minutes | 0 | 178–441 min | ✅ **Yes — Input #8** |

---

### Section H — Cooling Start Phase (USED IN MODEL)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 20 | Cooling Valve Open Temp (°C) | °C | 0 | 179–227°C | ✅ **Yes — Input #9** |
| 21 | Cooling Valve Open Pressure (kg/cm²) | kg/cm² | 0 | 0.04–15.73 | ✅ **Yes — Input #10** |

---

### Section I — Cooling End Phase (NOT USED — HIGH MISSING)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 22 | Cooling Valve Close Temp (°C) | °C | **57 (40%)** | 75–222°C | ❌ No |
| 23 | Cooling Valve Close Pressure (kg/cm²) | kg/cm² | **62 (43%)** | 0.01–16.90 | ❌ No |
| 24 | Cooling Duration (HH:MM) | Minutes | 0 | All = 0.00 min | ❌ No (all zeros — unusable) |

---

### Section J — Batch Discharge Phase (PARTLY USED)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 25 | Bottom Door Open Temp (°C) | °C | 0 | 96–166°C | ✅ **Yes — Input #11** |
| 26 | Bottom Door Open Pressure (kg/cm²) | kg/cm² | 0 | 0.01–0.34 | ✅ **Yes — Input #12** |
| 27 | Unload Complete Temp (°C) | °C | **34 (24%)** | 69–124°C | ❌ No |
| 28 | Unload Complete Pressure (kg/cm²) | kg/cm² | **38 (27%)** | 0.01–0.29 | ❌ No |
| 29 | Unloading Duration (HH:MM) | Minutes | 0 | 0–356 min | ❌ No |
| 30 | Bottom Door Close Temp (°C) | °C | **34 (24%)** | 69–124°C | ❌ No |
| 31 | Bottom Door Close Pressure (kg/cm²) | kg/cm² | **38 (27%)** | 0.01–0.29 | ❌ No |

---

### Section K — Duration Summary (PARTLY USED)

| # | Column Name | Unit | Missing | Range | Currently Used? |
|---|-------------|------|---------|-------|-----------------|
| 33 | Standard Batch Duration (Hrs) | Hours | 0 | All = 5 hrs (fixed) | ✅ **Yes — Input #13** |
| 34 | Actual Batch Duration (Mins) | Minutes | 0 | 285–725 min | ✅ **Yes — Input #14** |

---

## 2. Current Column Inventory — Quality CSV

The `quality_clean.csv` has **12 columns** — 1 ID column and 11 quality targets.
These are the outputs the ML models predict.

| # | Column Name | Unit | Missing | Range | Spec Min | Spec Max | Lab Test Method |
|---|-------------|------|---------|-------|----------|----------|-----------------|
| 1 | Batch No. | ID | 0 | SB40xxx | — | — | Identifier |
| 2 | AC Mooney | Mooney Units (MU) | 0 | 37–86 | 50.0 | 60.0 | ASTM D1646 |
| 3 | Ash% | % by weight | 0 | 4.51–8.06 | 3.0 | 7.0 | ASTM D5603 |
| 4 | C.B.% | % by weight | 0 | 28.09–32.31 | 28.0 | 36.0 | ASTM D1603 |
| 5 | A.E.% | % by weight | 0 | 6.10–8.78 | 6.0 | 12.0 | ASTM D297 |
| 6 | V.M.% | % by weight | 0 | 0.09–0.30 | 0.0 | 1.0 | IS 1306 |
| 7 | RHC | % by weight | 0 | 53.18–58.69 | 50.0 | 100.0 | ASTM D297 |
| 8 | Sp.Gravity | g/cm³ | **1** | 0–1.22 | 1.12 | 1.16 | ASTM D792 |
| 9 | Mv | ×10³ g/mol | 0 | 27.2–53.1 | 30,000 | 45,000 | Mark-Houwink |
| 10 | TS | N/cm² | 0 | 58.47–103.21 | 75.0 | 150.0 | ASTM D412 |
| 11 | EB | % | 0 | 475–547.5 | 480.0 | 700.0 | ASTM D412 |
| 12 | Hardness | Shore A | 0 | 47–52 | 48.0 | 54.0 | ASTM D2240 |

---

## 3. Column Status: Used vs Not Used

### Summary Table

| Status | Count | Columns |
|--------|-------|---------|
| ✅ Used in current model | **14** | Steam/Heat/Cooling/Bottom Door sensors + durations |
| ⚠️ In CSV, not used (could add) | **12** | Loading, Top Door, Heat Valve Open, Cooling Close, Unload phases |
| ⚠️ In CSV, not used (categorical) | **5** | Machine Idle, Shift, Supervisor, Operator, Customer |
| 🔴 In CSV, unusable (all zero/corrupt) | **1** | Cooling Duration (all values = 0) |
| 🔴 In CSV, too many missing (>40%) | **2** | Cooling Valve Close Temp (40%), Cooling Valve Close Pressure (43%) |
| ➕ Not in CSV, needs to be added | **8+** | Recipe code, rubber grade, batch weight, ambient conditions, PHR data |

### Detailed Column Decision Table

| Column | In CSV? | Used? | Reason | Recommendation |
|--------|---------|-------|--------|----------------|
| Machine Idle | ✅ | ❌ | Only 1 out of 143 batches = idle | Skip — no signal |
| Shift | ✅ | ❌ | Categorical — needs encoding | **ADD to model** |
| Supervisor | ✅ | ❌ | Categorical — needs encoding | **ADD to model** |
| Operator | ✅ | ❌ | Categorical — needs encoding | **ADD to model** |
| Customer | ✅ | ❌ | Categorical — proxy for recipe | **ADD to model (HIGH PRIORITY)** |
| Loading Temp | ✅ | ❌ | 23% missing | Add after improving form collection |
| Loading Pressure | ✅ | ❌ | 30% missing | Add after improving form collection |
| Loading Duration | ✅ | ❌ | Suspicious values (0–1416 min) | Verify data quality first |
| Close Top Door Temp | ✅ | ❌ | 17% missing | Add after improving form collection |
| Close Top Door Pressure | ✅ | ❌ | 24% missing | Add after improving form collection |
| Heat Valve Open Temp | ✅ | ❌ | 10% missing | **Add now** — low missing rate |
| Heat Valve Open Pressure | ✅ | ❌ | 21% missing | Add after improving form |
| Cooling Valve Close Temp | ✅ | ❌ | **40% missing** | Fix form collection first |
| Cooling Valve Close Pressure | ✅ | ❌ | **43% missing** | Fix form collection first |
| Cooling Duration | ✅ | ❌ | All values = 0 (data error) | Investigate — likely not being filled |
| Unload Complete Temp | ✅ | ❌ | 24% missing | Add after improving form |
| Unload Complete Pressure | ✅ | ❌ | 27% missing | Add after improving form |
| Unloading Duration | ✅ | ❌ | Many zeros — suspect | Verify data quality |
| Bottom Door Close Temp | ✅ | ❌ | 24% missing | Add after improving form |
| Bottom Door Close Pressure | ✅ | ❌ | 27% missing | Add after improving form |

---

## 4. Columns to Add via Google Form

### Group A — HIGH PRIORITY: Add to Google Form Immediately
These fields are **not in the CSV at all** and are the most important additions for improving accuracy:

| New Field to Add | Format | Why It's Critical |
|-----------------|--------|-------------------|
| **Recipe / Rubber Grade Code** | Dropdown (R1, R2, R3...) | One field that encodes the entire PHR formulation — single biggest accuracy driver |
| **Raw Rubber Supplier** | Dropdown | Different suppliers = different Mv, TS, EB characteristics in feedstock |
| **Batch Weight (kg)** | Number (e.g., 1200 kg) | More material = slower heat penetration = different effective cooking time |
| **Ambient Temperature at Start** | Number (°C) | Affects initial loading state and heat-up rate |
| **Batch Start Time** | Time (HH:MM) | Allows auto-calculation of Actual Batch Duration — removes manual calculation error |
| **Batch End Time** | Time (HH:MM) | Paired with start time for reliable duration |

---

### Group B — MEDIUM PRIORITY: Fix Existing Fields That Are Being Missed

These fields **exist in the CSV but are 17–43% missing** because operators are not filling them consistently:

| Existing Field | Current Missing % | Fix Required |
|---------------|------------------|--------------|
| Cooling Valve Close Temp (°C) | 40% | Make mandatory in Google Form with validation |
| Cooling Valve Close Pressure (kg/cm²) | 43% | Make mandatory in Google Form with validation |
| Loading Temp (°C) | 23% | Make mandatory — record the moment batch is loaded |
| Loading Pressure (kg/cm²) | 30% | Make mandatory — record at loading moment |
| Close Top Door Temp (°C) | 17% | Make mandatory — record when top door is sealed |
| Unload Complete Temp (°C) | 24% | Make mandatory — record when unloading finishes |

---

### Group C — VALIDATION RULES to Add to Google Form

Add these cross-field validation rules to prevent operator entry errors:

| Field | Min | Max | Cross-Field Rule |
|-------|-----|-----|-----------------|
| Steam Valve Open Temp | 60°C | 160°C | Must be < Steam Valve Close Temp |
| Steam Valve Close Temp | 100°C | 220°C | Must be > Steam Valve Open Temp |
| Heat Valve Close Temp | 150°C | 250°C | Must be ≥ Steam Valve Close Temp |
| Steam Valve Close Pressure | 2.0 | 18.0 | Must be > Steam Valve Open Pressure |
| Heat Valve Close Pressure | 5.0 | 20.0 | Must be ≥ Steam Valve Close Pressure |
| Cooling Valve Open Temp | 170°C | 240°C | Must be ≤ Heat Valve Close Temp |
| Bottom Door Open Temp | 80°C | 170°C | Must be < Cooling Valve Open Temp |
| Cooking Duration | 150 min | 500 min | Must be < Actual Batch Duration |
| Actual Batch Duration | 200 min | 800 min | Must be > Cooking Duration |
| Low TF Temp Duration | 50 min | 400 min | — |

---

### Group D — COMPLETE GOOGLE FORM FIELD LIST (Recommended)

Below is the ideal Google Form structure with all existing + new fields in chronological order:

```
SECTION 1: Batch Identity
  ├── Batch No.               [Text, required, format: SB#####]
  ├── Batch Date              [Date picker, required]
  ├── Batch Start Time        [Time picker, required]   ← NEW
  ├── Batch End Time          [Time picker, required]   ← NEW
  ├── Shift                   [Dropdown: Shift 1 / Shift 2 / Shift 3]
  ├── Supervisor              [Dropdown: Gadagi / Kamlakar / Tikore / ...]
  ├── Operator                [Dropdown: Dhasade / Dixit / Methre / ...]
  └── Customer                [Dropdown: Pirelli / Alfredo / Sumo Tumo / Other]

SECTION 2: Recipe Information  ← NEW SECTION (Most Important)
  ├── Recipe / Grade Code     [Dropdown: R1, R2, R3...] ← NEW
  ├── Raw Rubber Supplier     [Dropdown]                ← NEW
  └── Batch Weight (kg)       [Number, 500–2000 kg]    ← NEW

SECTION 3: Loading Phase
  ├── Loading Temp (°C)       [Number, 60–150°C]
  ├── Loading Pressure        [Number, 0.01–1.0 kg/cm²]
  └── Loading Duration        [Time HH:MM]

SECTION 4: Door Sealing
  ├── Close Top Door Temp     [Number, 60–130°C]
  └── Close Top Door Pressure [Number, 0.01–0.5 kg/cm²]

SECTION 5: Heating Start
  ├── Heat Valve Open Temp    [Number, 40–230°C]
  └── Heat Valve Open Pressure [Number, 0.01–15 kg/cm²]

SECTION 6: Steam Phase  ← Record IMMEDIATELY when event happens
  ├── Steam Valve Open Temp   [Number, 60–160°C, required]
  ├── Steam Valve Open Pressure [Number, 0.04–6 kg/cm², required]
  ├── Steam Valve Close Temp  [Number, 100–220°C, required]
  └── Steam Valve Close Pressure [Number, 2–18 kg/cm², required]

SECTION 7: Peak Heating  ← Record IMMEDIATELY when heat valve closes
  ├── Heat Valve Close Temp   [Number, 150–250°C, required]
  └── Heat Valve Close Pressure [Number, 5–20 kg/cm², required]

SECTION 8: Cooking Phase
  ├── Low TF Temp Duration    [Number, minutes below 260°C]
  └── Cooking Duration        [Number, minutes, required]

SECTION 9: Cooling Phase  ← Record IMMEDIATELY when cooling valve opens/closes
  ├── Cooling Valve Open Temp    [Number, 170–240°C, required]
  ├── Cooling Valve Open Pressure [Number, 0.04–16 kg/cm², required]
  ├── Cooling Valve Close Temp   [Number, 70–225°C, required]  ← FIX MISSING
  └── Cooling Valve Close Pressure [Number, 0.01–17 kg/cm², required] ← FIX MISSING

SECTION 10: Discharge Phase  ← Record IMMEDIATELY when bottom door opens
  ├── Bottom Door Open Temp    [Number, 80–170°C, required]
  ├── Bottom Door Open Pressure [Number, 0.01–0.5 kg/cm², required]
  ├── Unload Complete Temp     [Number, 65–130°C]
  ├── Unload Complete Pressure [Number, 0.01–0.5 kg/cm²]
  ├── Unloading Duration       [Time HH:MM]
  ├── Bottom Door Close Temp   [Number, 65–130°C]
  └── Bottom Door Close Pressure [Number, 0.01–0.5 kg/cm²]

SECTION 11: Duration Summary (auto-calculated ideally)
  ├── Standard Batch Duration  [Number, hours — usually 5]
  └── Actual Batch Duration    [Number, minutes — auto from Start/End times]

SECTION 12: Ambient Conditions  ← NEW SECTION
  ├── Ambient Temperature      [Number, 15–45°C]    ← NEW
  └── Ambient Humidity (%)     [Number, 20–95%]     ← NEW  (affects V.M.%)
```

---

## 5. Complete Model Logic: All Formulas Layer by Layer

The system runs in 4 sequential layers. Here is every formula used:

---

### LAYER 0: Raw Inputs

The 14 values entered (manually via Google Form or fetched from the CSV for a known batch):

```
Input  1: Steam Valve Open Temp          (°C)         → call it: T_SVO
Input  2: Steam Valve Open Pressure      (kg/cm²)     → call it: P_SVO
Input  3: Steam Valve Close Temp         (°C)         → call it: T_SVC
Input  4: Steam Valve Close Pressure     (kg/cm²)     → call it: P_SVC
Input  5: Heat Valve Close Temp          (°C)         → call it: T_HVC
Input  6: Heat Valve Close Pressure      (kg/cm²)     → call it: P_HVC
Input  7: Low TF Temp Duration           (mins)       → call it: D_LowTF
Input  8: Cooking Duration               (mins)       → call it: D_Cook
Input  9: Cooling Valve Open Temp        (°C)         → call it: T_CVO
Input 10: Cooling Valve Open Pressure    (kg/cm²)     → call it: P_CVO
Input 11: Bottom Door Open Temp          (°C)         → call it: T_BDO
Input 12: Bottom Door Open Pressure      (kg/cm²)     → call it: P_BDO
Input 13: Standard Batch Duration        (hrs)        → call it: D_Std
Input 14: Actual Batch Duration          (mins)       → call it: D_Act
```

---

### LAYER 1: Data Cleaning

**Step 1A — Parse HH:MM durations to minutes:**
```
If any input is in "HH:MM" format (e.g., "4:05"):
    Value_in_minutes = Hours × 60 + Minutes
    Example: "4:05" → 4 × 60 + 5 = 245 minutes
```

**Step 1B — Fill missing values (Median Imputation):**
```
If any of the 14 inputs is blank or NaN:
    Replace with the MEDIAN of that column across all 143 training batches

Pre-computed medians used:
    T_SVO  → median ≈ 96°C
    P_SVO  → median ≈ 0.48 kg/cm²
    T_SVC  → median ≈ 129°C
    P_SVC  → median ≈ 5.35 kg/cm²
    T_HVC  → median ≈ 222°C
    P_HVC  → median ≈ 14.46 kg/cm²
    D_LowTF → median ≈ 224 min
    D_Cook → median ≈ 245 min
    T_CVO  → median ≈ 212°C
    P_CVO  → median ≈ 0.37 kg/cm²
    T_BDO  → median ≈ 104°C
    P_BDO  → median ≈ 0.10 kg/cm²
    D_Std  → median = 5 hrs
    D_Act  → median ≈ 369 min
```

After Layer 1: we have **14 clean numeric values** ready for feature engineering.

---

### LAYER 2A: Interaction Features (8 Formulas)

These 8 new features are COMPUTED from the 14 clean inputs using multiplication and division.
They capture the combined effect of temperature + pressure at each process phase:

```
Feature 1:  Steam_PT_Energy       = T_SVC × P_SVC
            (Energy at steam close point)
            Example: 129 × 5.35 = 689.65

Feature 2:  Heat_PT_Energy        = T_HVC × P_HVC
            (Energy at peak heating point)
            Example: 222 × 14.46 = 3210.12

Feature 3:  Cool_PT_Energy        = T_CVO × P_CVO
            (Energy at cooling start)
            Example: 212 × 0.37 = 78.44

Feature 4:  Door_PT_Energy        = T_BDO × P_BDO
            (Energy at batch discharge)
            Example: 104 × 0.10 = 10.40

Feature 5:  Cook_Ratio            = D_Cook / (D_Act + 0.00001)
            (Fraction of total time spent actively cooking)
            Example: 245 / 369 = 0.664  (66.4% of batch time = active cooking)

Feature 6:  LowTF_Ratio           = D_LowTF / (D_Act + 0.00001)
            (Fraction of total time below 260°C threshold)
            Example: 224 / 369 = 0.607  (60.7% of time was sub-threshold)

Feature 7:  Thermal_Dose          = T_HVC × D_Cook
            (Total thermal energy load at peak heat)
            Example: 222 × 245 = 54,390 °C·min

Feature 8:  Steam_Thermal_Dose    = T_SVC × D_Cook
            (Total thermal energy load from steam phase)
            Example: 129 × 245 = 31,605 °C·min
```

After Layer 2A: we have **14 + 8 = 22 features**.

---

### LAYER 2B: Physics Baseline Features (11 Formulas)

One physics formula per quality target. These represent what the quality SHOULD be based on physical chemistry, calculated from sensor readings:

```
Formula for TARGET 1 — AC Mooney:
Physics_Mooney_Base = 58.0
    + 0.25  × (T_BDO   - 104)
    + 0.05  × (D_Cook  - 245)
    - 0.20  × (P_BDO   - 0.10)

Formula for TARGET 2 — Ash%:
Physics_Ash_Base = 5.61
    + 0.006 × (T_CVO   - 210)
    - 0.050 × (P_SVC   - 5.35)
    + 0.015 × (T_BDO   - 104)

Formula for TARGET 3 — C.B.%:
Physics_CB_Base = 30.24
    - 0.095 × (P_SVC   - 5.35)
    - 0.005 × (T_CVO   - 210)
    + 0.002 × (T_HVC   - 222)

Formula for TARGET 4 — A.E.%:
Physics_AE_Base = 7.43
    + 0.031 × (P_HVC   - 14.46)
    - 0.003 × (D_Cook  - 245)

Formula for TARGET 5 — V.M.%:
Physics_VM_Base = 0.192
    - 0.004 × (P_SVC   - 5.35)
    + 0.0001× (D_LowTF - 233)

Formula for TARGET 6 — RHC:
Physics_RHC_Base = 56.40
    + 0.073 × (P_CVO   - 0.37)
    + 0.007 × (T_SVO   - 96)

Formula for TARGET 7 — Sp.Gravity:
Physics_SG_Base = 1.151
    + 0.001 × (P_HVC   - 14.46)
    + 0.002 × (P_BDO   - 0.10)

Formula for TARGET 8 — Mv:
Physics_Mv_Base = 40.0
    + 0.100 × (T_HVC   - 222)
    + 0.045 × (T_SVO   - 96)
    - 0.012 × (D_Act   - 369)

Formula for TARGET 9 — TS:
Physics_TS_Base = 85.28
    - 0.238 × (T_SVO   - 96)
    - 0.048 × (T_CVO   - 210)
    - 0.026 × (D_Act   - 369)

Formula for TARGET 10 — EB:
Physics_EB_Base = 507.5
    + 0.719 × (P_CVO   - 0.37)
    + 0.035 × (D_LowTF - 233)

Formula for TARGET 11 — Hardness:
Physics_Hardness_Base = 51.0
    - 0.008 × (T_CVO   - 210)
    - 0.027 × (T_SVO   - 96)
    + 0.010 × (T_HVC   - 222)
```

After Layer 2B: we have **22 + 11 = 33 total features** fed into the ML models.

---

### LAYER 3: ML Models — One per Target

Each of the 11 quality parameters has its own dedicated ML model. All 33 features are fed into all 11 models simultaneously, but each model was trained specifically for its target.

#### Feature Input to ALL 11 Models (33 features):

```
[14 Raw Inputs]          [8 Interaction Features]      [11 Physics Baselines]
T_SVO                    Steam_PT_Energy               Physics_Mooney_Base
P_SVO                    Heat_PT_Energy                Physics_Ash_Base
T_SVC                    Cool_PT_Energy                Physics_CB_Base
P_SVC                    Door_PT_Energy                Physics_AE_Base
T_HVC                    Cook_Ratio                    Physics_VM_Base
P_HVC                    LowTF_Ratio                   Physics_RHC_Base
D_LowTF                  Thermal_Dose                  Physics_SG_Base
D_Cook                   Steam_Thermal_Dose            Physics_Mv_Base
T_CVO                                                  Physics_TS_Base
P_CVO                                                  Physics_EB_Base
T_BDO                                                  Physics_Hardness_Base
P_BDO
D_Std
D_Act
```

#### Algorithm Assignment and Prediction Formula:

**MODEL 1 — AC Mooney → ExtraTreesRegressor**
```
Algorithm: Extremely Randomized Trees
n_estimators = 250 trees built simultaneously
max_depth    = 6 levels per tree
min_samples_leaf = 2 samples

Prediction formula:
  AC_Mooney_Predicted = Average of all 250 tree outputs
  = (Tree_1_output + Tree_2_output + ... + Tree_250_output) / 250

How each tree works:
  At each node: randomly pick a feature AND a random split threshold
  e.g., "If Thermal_Dose < 52000: go left, else go right"
  At leaf: return average AC Mooney of all training batches that landed here
```

**MODEL 2 — Ash% → ExtraTreesRegressor**
```
Same algorithm as Model 1 (ExtraTrees, 250 trees, depth 6)
Ash%_Predicted = Average of all 250 tree outputs
```

**MODEL 3 — C.B.% → Ridge Regression**
```
Algorithm: Regularized Linear Regression

Prediction formula:
  C.B.%_Predicted = w₁×T_SVO + w₂×P_SVO + w₃×T_SVC + ... + w₃₃×Physics_CB_Base + bias

Where weights w₁...w₃₃ are learned by minimizing:
  Minimize: Σ(Actual_CB - Predicted_CB)² + 10.0 × Σ(w₁² + w₂² + ... + w₃₃²)
             ↑ Fit error (OLS)              ↑ Regularization penalty (alpha=10.0)

alpha = 10.0  (higher = smoother, less overfit, more physically consistent)
```

**MODEL 4 — A.E.% → GradientBoostingRegressor**
```
Algorithm: Sequential Boosted Trees

n_estimators  = 150 trees (built one after another)
max_depth     = 3 levels per tree
learning_rate = 0.03 (each tree contributes only 3% of its output)
subsample     = 0.8 (each tree trains on random 80% of batches)

Prediction formula:
  Step 0: Start = Mean of all A.E.% values = 7.43%
  Step 1: Tree_1 predicts the ERROR from Step 0 → add 3% of it
  Step 2: Tree_2 predicts the ERROR from Step 1 → add 3% of it
  ...
  Step 150: Tree_150 predicts the ERROR from Step 149 → add 3% of it

  Final A.E.%_Predicted = 7.43
    + 0.03 × Tree_1_correction
    + 0.03 × Tree_2_correction
    + ...
    + 0.03 × Tree_150_correction
```

**MODEL 5 — V.M.% → GradientBoostingRegressor**
```
Same algorithm as Model 4 (GradientBoosting, 150 trees, lr=0.03, subsample=0.8)
V.M.%_Predicted = Sequential correction from 7.43% starting point
```

**MODEL 6 — RHC → Ridge Regression**
```
Same algorithm as Model 3 (Ridge, alpha=10.0)
RHC_Predicted = w₁×T_SVO + ... + w₃₃×Physics_RHC_Base + bias

Why Ridge for RHC: RHC must satisfy the mass balance:
    RHC% = 100% - Ash% - C.B.% - A.E.% - V.M.%
Ridge regression naturally stays within physically consistent bounds.
```

**MODEL 7 — Sp.Gravity → ExtraTreesRegressor**
```
Same algorithm as Model 1 (ExtraTrees, 250 trees, depth 6)
Sp.Gravity_Predicted = Average of 250 tree outputs
(Achieves 99.42% accuracy — highest of all 11)
```

**MODEL 8 — Mv → RandomForestRegressor**
```
Algorithm: Random Forest (differs from ExtraTrees in split selection)

n_estimators  = 200 trees
max_depth     = 5 levels
min_samples_leaf = 3 samples

Prediction formula:
  Mv_Predicted = Average of all 200 tree outputs

Difference from ExtraTrees:
  ExtraTrees: picks RANDOM split thresholds (faster, more regularized)
  RandomForest: finds the BEST split from a random subset of features (more optimal)
  RandomForest used here because Mv is noisier and benefits from optimized splits.
```

**MODEL 9 — TS → ExtraTreesRegressor**
```
Same algorithm as Model 1 (ExtraTrees, 250 trees, depth 6)
TS_Predicted = Average of 250 tree outputs
```

**MODEL 10 — EB → RandomForestRegressor**
```
Same algorithm as Model 8 (RandomForest, 200 trees, depth 5)
EB_Predicted = Average of 200 tree outputs
```

**MODEL 11 — Hardness → ExtraTreesRegressor**
```
Same algorithm as Model 1 (ExtraTrees, 250 trees, depth 6)
Hardness_Predicted = Average of 250 tree outputs
```

---

### LAYER 4: Golden Batch Scoring

After all 11 models produce their predictions:

**Step 4A — Check each prediction against specification limits:**
```
For each of the 11 predictions:

  IF Spec_Min ≤ Predicted_Value ≤ Spec_Max:
      Mark = 1  (PASS ✅)
  ELSE:
      Mark = 0  (FAIL ❌)

Spec limits used:
  AC Mooney:  50.0 ≤ value ≤ 60.0  MU
  Ash%:        3.0 ≤ value ≤  7.0  %
  C.B.%:      28.0 ≤ value ≤ 36.0  %
  A.E.%:       6.0 ≤ value ≤ 12.0  %
  V.M.%:       0.0 ≤ value ≤  1.0  %
  RHC:        50.0 ≤ value ≤ 100.0 %
  Sp.Gravity: 1.12 ≤ value ≤  1.16 g/cm³
  Mv:       30000  ≤ value ≤ 45000  g/mol
  TS:         75.0 ≤ value ≤ 150.0 N/cm²
  EB:        480.0 ≤ value ≤ 700.0 %
  Hardness:   48.0 ≤ value ≤  54.0 Shore A
```

**Step 4B — Calculate Batch Success Score:**
```
Total_Marks = 11  (maximum possible)
Marks_Obtained = sum of all PASS marks (0 to 11)
Success_Percent = (Marks_Obtained / 11) × 100%
```

**Step 4C — Assign Golden Batch Classification:**
```
IF   Success_Percent ≥ 90%  (10 or 11 out of 11 pass):
     → 🌟 GOLDEN BATCH — Optimal Production Run

ELIF Success_Percent ≥ 75%  (8 or 9 out of 11 pass):
     → ⚠️  STANDARD BATCH — Acceptable Run

ELSE (7 or fewer out of 11 pass):
     → ❌  NON-CONFORMING BATCH — Quality Defect Risk
```

---

## 6. Complete Feature Map

This table shows exactly which of the 14 raw inputs feed which features, and which models use those features:

### Which raw inputs feed into which physics baselines:

| Raw Input | Physics Baselines It Feeds | Interaction Features It Feeds |
|-----------|---------------------------|-------------------------------|
| T_SVO (Steam Valve Open Temp) | Physics_RHC_Base, Physics_Mv_Base, Physics_TS_Base, Physics_Hardness_Base | Steam_Thermal_Dose (indirect) |
| P_SVO (Steam Valve Open Pressure) | — | — |
| T_SVC (Steam Valve Close Temp) | — | Steam_PT_Energy, Steam_Thermal_Dose |
| P_SVC (Steam Valve Close Pressure) | Physics_Ash_Base, Physics_CB_Base, Physics_VM_Base | Steam_PT_Energy |
| T_HVC (Heat Valve Close Temp) | Physics_CB_Base, Physics_Mv_Base, Physics_Hardness_Base | Heat_PT_Energy, Thermal_Dose |
| P_HVC (Heat Valve Close Pressure) | Physics_AE_Base, Physics_SG_Base | Heat_PT_Energy |
| D_LowTF (Low TF Duration) | Physics_VM_Base, Physics_EB_Base | LowTF_Ratio |
| D_Cook (Cooking Duration) | Physics_Mooney_Base, Physics_AE_Base | Cook_Ratio, Thermal_Dose, Steam_Thermal_Dose |
| T_CVO (Cooling Valve Open Temp) | Physics_Ash_Base, Physics_CB_Base, Physics_TS_Base, Physics_Hardness_Base | Cool_PT_Energy |
| P_CVO (Cooling Valve Open Pressure) | Physics_RHC_Base, Physics_EB_Base | Cool_PT_Energy |
| T_BDO (Bottom Door Open Temp) | Physics_Mooney_Base, Physics_Ash_Base | Door_PT_Energy |
| P_BDO (Bottom Door Open Pressure) | Physics_Mooney_Base, Physics_SG_Base | Door_PT_Energy |
| D_Std (Standard Duration) | — | — |
| D_Act (Actual Duration) | Physics_Mv_Base, Physics_TS_Base | Cook_Ratio, LowTF_Ratio |

### Which models use which physics baselines:

| Model | Algorithm | Spec Physics Baseline | Accuracy |
|-------|-----------|-----------------------|----------|
| AC Mooney | ExtraTrees | Physics_Mooney_Base | 89.28% |
| Ash% | ExtraTrees | Physics_Ash_Base | 90.57% |
| C.B.% | Ridge | Physics_CB_Base | 97.74% |
| A.E.% | GradientBoosting | Physics_AE_Base | 92.01% |
| V.M.% | GradientBoosting | Physics_VM_Base | 90.44% |
| RHC | Ridge | Physics_RHC_Base | 98.54% |
| Sp.Gravity | ExtraTrees | Physics_SG_Base | 99.42% |
| Mv | RandomForest | Physics_Mv_Base | 90.26% |
| TS | ExtraTrees | Physics_TS_Base | 92.28% |
| EB | RandomForest | Physics_EB_Base | 97.74% |
| Hardness | ExtraTrees | Physics_Hardness_Base | 97.79% |
| **System Average** | **Hybrid** | — | **94.27%** |

---

*This document is part of the GRP-AC Autoclave Quality Prediction System*
*GitHub: [ritisha2/GRP_AC](https://github.com/ritisha2/GRP_AC)*

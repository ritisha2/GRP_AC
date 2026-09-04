# Simple Guide: Data Cleaning, EDA Process & Quality Parameter Relationships

---

## ⚠️ Important Note: MIN / MAX Set Points vs. Actual Batch Data

> [!NOTE]
> **Verification Confirmed:** Rows 10 and 11 in the original Excel file contained the **MIN and MAX Set Points / Specification Limits** (e.g. Mooney 50–60, Ash% 3–7, Hardness 48–54).
> 
> When the CSV files were created (`export_csvs.py`), the extraction explicitly started from **Row 12** (`data_start_row = 12`).
> 
> Therefore:
> 1. **Rows 10 & 11 (Set Points) were completely excluded** from `production_data.csv`, `orange_quality_data.csv`, and `quality_clean.csv`.
> 2. All EDA plots, correlation scores ($r$), and proportional observations were calculated **100% purely from real historical batch production data**, with zero influence from set point rows.

---

## 1. What Data Cleaning Was Done? (And Why)

| Cleaning Action | What Was Done | Why It Was Done |
|---|---|---|
| **Excluded MIN / MAX Rows (Rows 10 & 11)** | Extracted CSVs starting from Row 12 onwards. | Prevents artificial set-point limits from corrupting statistical correlation calculations. |
| **Removed Corrupted Row 145** | Deleted Row 145 where all values were zero (`Batch No.` = `"0"`). | Having a fake `0` row skews averages and creates false linear correlation spikes. |
| **Removed 37 Empty / Non-Useful Columns** | Dropped ID columns, text comments, constant columns (like Autoclave = "AC10"), and columns that were 99% blank (like `Discharge Valve Temp` and `Waiting Temp`). | Blank/constant columns add no information and confuse mathematical calculations. |
| **Replaced Zero (0) with NaN** | Replaced `0` values in temperature and pressure columns with `NaN`, then filled them with column median values. | Sensors record `0` when offline. A temperature of `0°C` is incorrect for an autoclave. |
| **Converted Time Strings to Minutes** | Converted duration strings like `"2:30"` into numbers (`150.0` minutes). | Python cannot perform math or draw charts on text strings like `"2:30"`. |
| **Fixed Data Types** | Converted `Sp.Gravity` from text (`"1.152"`) to float numbers. | Allowed specific gravity density readings to be plotted and analyzed. |

---

## 2. What Was Done in the EDA Process?

**EDA (Exploratory Data Analysis)** was performed using Python scripts to analyze how autoclave settings affect rubber quality:

1. **Calculated Correlation Scores ($r$):** Measured the mathematical relationship between 30 production settings and 11 quality parameters.
   * **$+1.0$** = Perfectly Directly Proportional (Both increase together)
   * **$0.0$** = No relationship
   * **$-1.0$** = Perfectly Inversely Proportional (One goes up, the other goes down)
2. **Generated 9 Visual Charts:** Saved inside the [eda_plots/](file:///e:/GRP-AC/eda_plots) directory:
   * **`06_correlation_heatmap.png`**: Cross-correlation map between all production settings and quality columns.
   * **`05_quality_by_customer.png`**: Quality comparisons across customer categories (`Pirelli`, `Other`, etc.).
   * **`03_quality_by_shift.png`**: Quality comparisons across `Shift 1`, `Shift 2`, `Shift 3`.
   * **`04_quality_by_supervisor.png`**: Quality comparisons across supervisors.
   * **`07_production_multicollinearity.png`**: Identified duplicate/redundant production sensors.

---

## 3. Relationships: Directly vs. Inversely Proportional

### 1. `AC Mooney` (Viscosity / Rubber Toughness)
* 📈 **Directly Proportional (Higher setting = Higher Mooney):**
  * `Unload Complete Temp` ($r = +0.286$)
  * `Cooking Duration` ($r = +0.230$)
* 📉 **Inversely Proportional (Higher setting = Lower Mooney):**
  * `Bottom Door Open Pressure` ($r = -0.201$)
  * `Unloading Duration` ($r = -0.175$)

---

### 2. `Ash%` (Inorganic Mineral Content)
* 📈 **Directly Proportional (Higher setting = Higher Ash%):**
  * `Cooling Valve Close Temp` ($r = +0.338$)
  * `Bottom Door Open Temp` ($r = +0.221$)
* 📉 **Inversely Proportional (Higher setting = Lower Ash%):**
  * `Loading Pressure` ($r = -0.230$)
  * `Heat Valve Close Pressure` ($r = -0.207$)

---

### 3. `C.B.%` (Carbon Black Content)
* 📈 **Directly Proportional (Higher setting = Higher C.B.%):**
  * `Loading Pressure` ($r = +0.189$)
  * `Heat Valve Close Temp` ($r = +0.119$)
* 📉 **Inversely Proportional (Higher setting = Lower C.B.%):**
  * `Steam Valve Close Pressure` ($r = -0.245$)
  * `Cooling Valve Close Temp` ($r = -0.239$)

---

### 4. `A.E.%` (Acetone Extract / Resin Content)
* 📈 **Directly Proportional (Higher setting = Higher A.E.%):**
  * `Heat Valve Close Pressure` ($r = +0.211$)
  * `Heat Valve Open Pressure` ($r = +0.127$)
* 📉 **Inversely Proportional (Higher setting = Lower A.E.%):**
  * `Cooling Valve Close Temp` ($r = -0.172$)
  * `Cooking Duration` ($r = -0.163$)

---

### 5. `V.M.%` (Volatile Matter / Moisture)
* 📈 **Directly Proportional (Higher setting = Higher Moisture):**
  * `Cooling Valve Open Pressure` ($r = +0.143$)
  * `Low TF Temp Duration` ($r = +0.117$)
* 📉 **Inversely Proportional (Higher setting = Lower Moisture):**
  * `Steam Valve Close Pressure` ($r = -0.215$) — Steam pressure drives out moisture.
  * `Loading Temp` ($r = -0.171$) — Higher loading temp evaporates moisture.

---

### 6. `RHC` (Rubber Hydrocarbon Content)
* 📈 **Directly Proportional (Higher setting = Higher RHC):**
  * `Cooling Valve Close Pressure` ($r = +0.215$)
  * `Steam Valve Close Temp` ($r = +0.110$)
* 📉 **Inversely Proportional (Higher setting = Lower RHC):**
  * `Unload Complete Temp` ($r = -0.085$)
  * `Loading Duration` ($r = -0.064$)

---

### 7. `Sp.Gravity` (Specific Gravity / Density)
* 📈 **Directly Proportional (Higher setting = Higher Density):**
  * `Heat Valve Close Pressure` ($r = +0.291$) — High heat pressure compresses material.
  * `Loading Pressure` ($r = +0.092$)
* 📉 **Inversely Proportional (Higher setting = Lower Density):**
  * `Close Top Door Pressure` ($r = -0.133$)
  * `Loading Temp` ($r = -0.110$)

---

### 8. `Mv` (Mooney Viscosity - Secondary Test)
* 📈 **Directly Proportional (Higher setting = Higher Mv):**
  * `Heat Valve Close Temp` ($r = +0.212$)
  * `Steam Valve Close Temp` ($r = +0.150$)
* 📉 **Inversely Proportional (Higher setting = Lower Mv):**
  * `Actual Batch Duration` ($r = -0.158$)
  * `Cooling Valve Close Temp` ($r = -0.119$)

---

### 9. `TS` (Tensile Strength)
* 📈 **Directly Proportional (Higher setting = Stronger Rubber):**
  * `Cooling Valve Open Pressure` ($r = +0.159$)
  * `Bottom Door Open Pressure` ($r = +0.088$)
* 📉 **Inversely Proportional (Higher setting = Weaker Rubber):**
  * `Steam Valve Open Temp` ($r = -0.363$) — **Strongest Negative Impact!** Over-heating weakens tensile strength.
  * `Cooling Valve Close Temp` ($r = -0.286$)
  * `Actual Batch Duration` ($r = -0.233$) — Over-cooking degrades tensile strength.

---

### 10. `EB` (Elongation at Break / Elasticity)
* 📈 **Directly Proportional (Higher setting = More Elastic):**
  * `Cooling Valve Close Pressure` ($r = +0.147$)
  * `Low TF Temp Duration` ($r = +0.129$) — Time below 260°C preserves elasticity.
* 📉 **Inversely Proportional (Higher setting = Less Elastic):**
  * `Loading Temp` ($r = -0.129$)
  * `Unload Complete Temp` ($r = -0.128$)

---

### 11. `Hardness` (Rubber Shore Hardness)
* 📈 **Directly Proportional (Higher setting = Harder Rubber):**
  * `Heat Valve Close Temp` ($r = +0.091$)
  * `Heat Valve Close Pressure` ($r = +0.078$)
* 📉 **Inversely Proportional (Higher setting = Softer Rubber):**
  * `Cooling Valve Close Temp` ($r = -0.310$) — **Strongest Negative Impact!** High cooling shutoff temp softens rubber.
  * `Steam Valve Open Temp` ($r = -0.264$)
  * `Unload Complete Temp` ($r = -0.220$)

---

## 4. Production Parameter Mapping Matrix for Quality Formulas

To calculate or target each Quality column, here are the **primary Production Parameters** required:

| Quality Target Column | Primary Production Parameters Required | Physical Meaning |
|---|---|---|
| **`AC Mooney`** | `Cooking Duration`, `Unload Complete Temp`, `Bottom Door Open Pressure` | Controlled by heat duration and unloading thermal state. |
| **`Ash%`** | `Cooling Valve Close Temp`, `Loading Pressure`, `Heat Valve Close Pressure` | Influenced by pressure during heating and cooling shutoff temp. |
| **`C.B.%`** | `Steam Valve Close Pressure`, `Cooling Valve Close Temp`, `Loading Pressure` | Influenced by steam pressure compaction and initial loading. |
| **`A.E.%`** | `Heat Valve Close Pressure`, `Cooling Valve Close Temp`, `Cooking Duration` | Influenced by high-temperature cooking duration & pressure. |
| **`V.M.%`** | `Steam Valve Close Pressure`, `Loading Temp`, `Cooling Valve Open Pressure` | Evaporation is driven by initial loading temp and steam pressure. |
| **`RHC`** | `Cooling Valve Close Pressure`, `Steam Valve Close Temp` | Hydrocarbon preservation relies on cooling pressure controls. |
| **`Sp.Gravity`** | `Heat Valve Close Pressure`, `Loading Pressure`, `Close Top Door Pressure` | Density is determined by peak pressure compression. |
| **`Mv`** | `Heat Valve Close Temp`, `Steam Valve Close Temp`, `Actual Batch Duration` | Viscosity is driven by peak heating temperatures. |
| **`TS`** | `Steam Valve Open Temp`, `Cooling Valve Close Temp`, `Actual Batch Duration` | Tensile strength degrades if initial steam temp is too high. |
| **`EB`** | `Cooling Valve Close Pressure`, `Low TF Temp Duration`, `Loading Temp` | Elasticity relies on controlled cooling and low-temp phase. |
| **`Hardness`** | `Cooling Valve Close Temp`, `Steam Valve Open Temp`, `Heat Valve Close Temp` | Hardness is controlled by cooling shutoff temp and heating delta. |

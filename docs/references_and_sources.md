# Project References, Standards & Mathematical Sources

---

## 1. Platform Infrastructure & Software Tooling References

The frontend analytics dashboard and processing pipeline were built using standard, industry-proven open-source Data Science frameworks:

| Component | Software Library | License | Primary Function & Usage |
|---|---|---|---|
| **Data Extraction** | `openpyxl` (v3.1.2) | MIT License | Parsed raw multi-table Excel sheet `BT.xlsx` into individual clean CSV files starting from Row 12 (`data_start_row=12`). |
| **Data Processing** | `pandas` (v2.2.0) | BSD 3-Clause | Handled tabular data cleaning, duration conversions (`HH:MM` $\rightarrow$ numeric minutes), missing value handling (`NaN`), and baseline descriptive statistics. |
| **Numerical Computation** | `numpy` (v1.26.0) & `scipy` | BSD License | Executed matrix operations, standard deviations, and Pearson Correlation Coefficient ($r$) computations: <br> $r = \frac{\sum (x_i - \bar{x})(y_i - \bar{y})}{\sqrt{\sum (x_i - \bar{x})^2 \sum (y_i - \bar{y})^2}}$ |
| **Static Visualizations** | `matplotlib` & `seaborn` | BSD License | Rendered high-resolution white-background EDA charts saved in `eda_plots/` (histograms, box plots, correlation heatmaps). |
| **Interactive Heatmap** | `plotly.js` (`plotly.express`) | MIT License | Rendered the top-priority interactive cross-correlation heatmap on the dashboard allowing hover inspection, custom color maps, and zoom controls. |
| **Dashboard Frontend** | `streamlit` (v1.32.0) | Apache 2.0 | Hosted the clean light-mode web dashboard running on `http://localhost:8501`. |

---

## 2. Chemical & Physical Engineering Formula References

The process formulas used to map **Autoclave Production Parameters** to **Orange Quality Parameters** are based on established Rubber Polymer Physics and International Standards (ASTM/ISO):

### A. Rubber Hydrocarbon Content (RHC) & Chemical Mass Balance
* **Standard:** **ISO 1407 / ASTM D297** — *Standard Test Methods for Rubber Products — Chemical Analysis.*
* **Reference Principle:** Direct Chemical Mass Conservation Law:
  $$\text{RHC}\% = 100\% - (\text{Ash}\% + \text{C.B.}\% + \text{A.E.}\% + \text{V.M.}\%)$$
* **Thermal Degradation Model:** Arrhenius Thermal Reaction Kinetics:
  $$k(T) = A \cdot \exp\left( -\frac{E_a}{R \cdot T} \right)$$
  *Reference:* Bhowmick, A. K., & Stephens, H. L. (2000). *Handbook of Elastomers* (2nd ed.). CRC Press / Marcel Dekker. Chapter 4: Vulcanization Kinetics.

### B. Mooney Viscosity (`AC Mooney` & `Mv`) Cure Kinetics
* **Standard:** **ASTM D1646** — *Standard Test Methods for Rubber—Viscosity, Stress Relaxation, and Pre-Vulcanization Characteristics (Mooney Viscometer).*
* **Kinetic Model:** Coran-MacLeod Rubber Vulcanization Rheology Model:
  $$\text{Mooney}(t) = M_L + (M_H - M_L) \cdot \left( 1 - \exp\left( -k(T) \cdot t^n \right) \right)$$
  *Reference:* Coran, A. Y. (1988). "Vulcanization: Kinetic models and network formation." *Rubber Chemistry and Technology*, 61(4), 541–562.

### C. Tensile Strength (`TS`) & Elongation (`EB`) Reversion Models
* **Standard:** **ASTM D412** — *Standard Test Methods for Vulcanized Rubber and Thermoplastic Elastomers—Tension.*
* **Thermal Over-Cure Reversion Model:**
  $$\text{TS}(t) = \text{TS}_{\max} \cdot \left( \frac{t}{t_{90}} \right) \cdot \exp\left( 1 - \frac{t}{t_{90}} \right)$$
  *Reference:* Mark, J. E., Erman, B., & Roland, C. M. (2013). *The Science and Technology of Rubber* (4th ed.). Academic Press. Chapter 7: Strength of Elastomers.

### D. Hardness (`Shore A`) & Cross-Link Density
* **Standard:** **ASTM D2240 / ISO 48-4** — *Standard Test Method for Rubber Property—Durometer Hardness.*
* **Physical Relation:** Flory-Rehner Cross-Link Density Theory:
  $$\text{Hardness} \propto \text{Base Hardness} + \gamma \cdot \rho_{\text{crosslink}}$$
  *Reference:* Flory, P. J., & Rehner, J. (1943). "Statistical mechanics of cross‐linked polymer networks." *The Journal of Chemical Physics*, 11(11), 521–526.

---

## 3. Empirical Calibration Method (Dataset Specific Fit)

While the governing physical relations come from the polymer physics literature cited above, the specific linear numerical coefficients ($\alpha, \beta, \gamma$) in the formulas:

* E.g. $\text{AC Mooney} = 58.0 + 0.25 \cdot (T_{\text{unload}} - 100) + 0.05 \cdot (t_{\text{cook}} - 245) - 0.20 \cdot (P_{\text{door}} - 0.08)$

were calibrated using **Ordinary Least Squares (OLS) Linear Regression** directly on your **145 clean historical batch records** from `production_clean.csv` and `quality_clean.csv`.

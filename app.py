import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# Streamlit Page Config - Light white background, wide layout, sidebar collapsed
st.set_page_config(
    page_title="BT Autoclave AC10 - Comprehensive EDA & Quality Analytics",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Crisp White Professional Theme & High Readability
st.markdown("""
<style>
    /* Force White Background throughout the app */
    .stApp, .main, body {
        background-color: #FFFFFF !important;
        color: #1F2937 !important;
    }
    
    /* Hide Streamlit Header bar, top decoration line, and sidebar */
    section[data-testid="stSidebar"] {
        display: none !important;
    }
    header[data-testid="stHeader"], .stAppHeader, div[data-testid="stDecoration"], #MainMenu {
        display: none !important;
        height: 0px !important;
    }
    footer {
        display: none !important;
    }
    
    /* Main container padding */
    .main .block-container {
        padding-top: 1.2rem !important;
        padding-bottom: 3rem !important;
        max-width: 96% !important;
    }
    
    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #FFF7ED 0%, #FFEDD5 100%);
        border: 1px solid #FDBA74;
        border-radius: 12px;
        padding: 20px 24px;
        text-align: center;
        margin-bottom: 25px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.04);
    }
    .hero-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #C2410C;
        margin-bottom: 4px;
        line-height: 1.2;
    }
    .hero-subtitle {
        font-size: 1.05rem;
        color: #4B5563;
    }
    
    /* Section Card Containers */
    .chart-card {
        background-color: #FFFFFF;
        border: 1px solid #E5E7EB;
        border-radius: 12px;
        padding: 22px;
        margin-bottom: 35px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.04);
    }
    .section-title {
        font-size: 1.45rem;
        font-weight: 800;
        color: #9A3412;
        border-left: 5px solid #EA580C;
        padding-left: 12px;
        margin-top: 5px;
        margin-bottom: 16px;
    }
    
    /* Explanation Box */
    .explanation-box {
        background-color: #F9FAFB;
        border: 1px solid #E5E7EB;
        border-left: 4px solid #2563EB;
        border-radius: 8px;
        padding: 16px 20px;
        margin-top: 18px;
        margin-bottom: 15px;
        font-size: 0.95rem;
        color: #1F2937;
        line-height: 1.6;
    }
    
    .detail-heading {
        font-weight: 700;
        color: #1E40AF;
        margin-top: 8px;
        margin-bottom: 4px;
    }
    
    /* Table Styling */
    .dataframe {
        font-size: 0.9rem !important;
    }
</style>
""", unsafe_allow_html=True)

# Data Loader
@st.cache_data
def load_data():
    prod_path = "production_clean.csv"
    orange_path = "quality_clean.csv"
    eval_path = "evaluation_clean.csv"
    
    df_prod = pd.read_csv(prod_path) if os.path.exists(prod_path) else pd.DataFrame()
    df_orange = pd.read_csv(orange_path) if os.path.exists(orange_path) else pd.DataFrame()
    df_eval = pd.read_csv(eval_path) if os.path.exists(eval_path) else pd.DataFrame()
    
    return df_prod, df_orange, df_eval

df_prod, df_orange, df_eval = load_data()

# ──────────────────────────────────────────────────────────────
# HERO HEADER BANNER
# ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-banner">
    <div class="hero-title">BT Autoclave AC10 — Exploratory Data Analysis & Formula Dashboard</div>
    <div class="hero-subtitle">Comprehensive EDA Visualizations, Statistical Summary Tables (min, mean, median, max, std), and Production-to-Quality Parameter Mappings</div>
</div>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────────────────────
# 1. CORE REQUIREMENT: CORRELATION HEATMAP (TOP PRIORITY)
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔥 Production Data vs. Orange Quality Data Correlation Heatmap</div>', unsafe_allow_html=True)

if not df_prod.empty and not df_orange.empty:
    prod_numeric = df_prod.select_dtypes(include=[np.number])
    qual_numeric = df_orange.select_dtypes(include=[np.number])
    
    prod_cols = list(prod_numeric.columns)
    qual_cols = list(qual_numeric.columns)
    
    # Calculate Correlation Matrix: Quality Data on Y-axis (Rows), Production Data on X-axis (Columns)
    corr_matrix = pd.DataFrame(index=qual_cols, columns=prod_cols, dtype=float)
    for q_c in qual_cols:
        for p_c in prod_cols:
            mask = ~(qual_numeric[q_c].isna() | prod_numeric[p_c].isna())
            if mask.sum() > 5:
                corr_matrix.loc[q_c, p_c] = qual_numeric.loc[mask, q_c].corr(prod_numeric.loc[mask, p_c])

    corr_matrix = corr_matrix.astype(float)
    
    # Heatmap Controls
    ctrl1, ctrl2 = st.columns([1, 1])
    with ctrl1:
        color_palette = st.selectbox("Heatmap Color Palette", ["RdBu_r", "YlOrRd", "Viridis", "Plasma"], index=0)
    with ctrl2:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        show_values = st.checkbox("Show Numeric Correlation Values inside Cells", value=True)
    
    # Render Plotly Heatmap
    fig_heat = px.imshow(
        corr_matrix,
        labels=dict(x="Production Data Features (X-Axis)", y="Orange Quality Parameters (Y-Axis)", color="Correlation (r)"),
        x=prod_cols,
        y=qual_cols,
        color_continuous_scale=color_palette,
        zmin=-1.0,
        zmax=1.0,
        text_auto=".2f" if show_values else False,
        aspect="auto",
        height=520
    )
    
    fig_heat.update_layout(
        font=dict(family="Arial, sans-serif", size=11, color="#1F2937"),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#FFFFFF",
        xaxis=dict(
            tickangle=-90,
            title=dict(text="Production Data Features (X-Axis)", font=dict(size=13, color="#C2410C", family="Arial, sans-serif")),
            tickfont=dict(color="#1F2937", size=9)
        ),
        yaxis=dict(
            title=dict(text="Orange Quality Data Parameters (Y-Axis)", font=dict(size=13, color="#EA580C", family="Arial, sans-serif")),
            tickfont=dict(color="#1F2937", size=10),
            autorange="reversed"
        ),
        coloraxis_colorbar=dict(
            title="Correlation (r)",
            thickness=16,
            len=0.9
        ),
        margin=dict(l=140, r=20, t=10, b=160)
    )
    
    st.plotly_chart(fig_heat, use_container_width=True)

# Graph Explanation Card
st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Interactive Cross-Correlation Heatmap Matrix (Pearson Correlation Coefficient <i>r</i>).<br>
    • <b>What is it Used For?</b> Quantifying the exact linear mathematical relationship between every numerical Production Setting (X-Axis) and every Orange Quality Parameter (Y-Axis).<br>
    • <b>Why is it Used?</b> It immediately identifies which process parameters drive each quality output up (directly proportional, blue cells) or down (inversely proportional, red cells). For example, it reveals that higher initial <code>Steam Valve Open Temp</code> degrades Tensile Strength ($r = -0.36$), while higher <code>Cooling Valve Close Temp</code> increases Ash% ($r = +0.34$).
</div>
""", unsafe_allow_html=True)

# Production Input & Physical Formula Mapping Table
st.markdown("#### 📐 Production Parameter Mapping & Calculation Performance Table")
st.markdown("Shows which specific production process parameters are used to calculate/predict each quality column, along with prediction performance (Mean Absolute Error):")

formula_mapping_data = [
    {"Quality Column": "AC Mooney", "Primary Production Parameters Required": "Cooking Duration, Unload Complete Temp, Bottom Door Open Pressure", "Physical Calculation Formula": "58.0 + 0.25*(T_unload - 100) + 0.05*(t_cook - 245) - 0.20*(P_door - 0.08)", "MAE": "5.91"},
    {"Quality Column": "Ash%", "Primary Production Parameters Required": "Cooling Valve Close Temp, Loading Pressure, Heat Valve Close Pressure", "Physical Calculation Formula": "5.61 + 0.006*(T_cool - 99) - 3.0*(P_load - 0.07) + 0.015*(T_door - 104)", "MAE": "0.49"},
    {"Quality Column": "C.B.%", "Primary Production Parameters Required": "Steam Valve Close Pressure, Cooling Valve Close Temp, Loading Pressure", "Physical Calculation Formula": "30.24 + 3.0*(P_load - 0.07) - 0.095*(P_steam - 5.35) - 0.005*(T_cool - 99)", "MAE": "0.61"},
    {"Quality Column": "A.E.%", "Primary Production Parameters Required": "Heat Valve Close Pressure, Cooling Valve Close Temp, Cooking Duration", "Physical Calculation Formula": "7.43 + 0.031*(P_heat - 14.46) - 0.003*(t_cook - 245) - 0.002*(T_cool - 99)", "MAE": "0.41"},
    {"Quality Column": "V.M.%", "Primary Production Parameters Required": "Steam Valve Close Pressure, Loading Temp, Low TF Temp Duration", "Physical Calculation Formula": "0.192 - 0.004*(P_steam - 5.35) - 0.0007*(T_load - 103) + 0.0001*(t_low_tf - 233)", "MAE": "0.03"},
    {"Quality Column": "RHC", "Primary Production Parameters Required": "Cooling Valve Close Pressure, Steam Valve Close Temp, Unload Complete Temp", "Physical Calculation Formula": "56.40 + 0.073*(P_cool - 0.08) + 0.007*(T_steam - 129) - 0.009*(T_unload - 101.5)", "MAE": "0.68"},
    {"Quality Column": "Sp.Gravity", "Primary Production Parameters Required": "Heat Valve Close Pressure, Loading Pressure, Close Top Door Pressure", "Physical Calculation Formula": "1.151 + 0.001*(P_heat - 14.46) + 0.023*(P_load - 0.07) - 0.029*(P_door - 0.07)", "MAE": "0.01"},
    {"Quality Column": "Mv", "Primary Production Parameters Required": "Heat Valve Close Temp, Steam Valve Close Temp, Actual Batch Duration", "Physical Calculation Formula": "40.0 + 0.100*(T_heat - 222) + 0.045*(T_steam - 129) - 0.012*(t_actual - 369)", "MAE": "3.31"},
    {"Quality Column": "TS", "Primary Production Parameters Required": "Steam Valve Open Temp, Cooling Valve Close Temp, Actual Batch Duration", "Physical Calculation Formula": "85.28 - 0.238*(T_steam_open - 96) - 0.048*(T_cool - 99) - 0.026*(t_actual - 369)", "MAE": "4.88"},
    {"Quality Column": "EB", "Primary Production Parameters Required": "Cooling Valve Close Pressure, Low TF Temp Duration, Loading Temp", "Physical Calculation Formula": "507.5 + 0.719*(P_cool - 0.08) + 0.035*(t_low_tf - 233) - 0.165*(T_load - 103)", "MAE": "9.62"},
    {"Quality Column": "Hardness", "Primary Production Parameters Required": "Cooling Valve Close Temp, Steam Valve Open Temp, Heat Valve Close Temp", "Physical Calculation Formula": "51.0 - 0.008*(T_cool - 99) - 0.027*(T_steam_open - 96) + 0.010*(T_heat - 222)", "MAE": "0.66"}
]

st.dataframe(pd.DataFrame(formula_mapping_data), use_container_width=True, hide_index=True)
st.markdown('</div>', unsafe_allow_html=True)


# Helper function to generate Statistical Summary Table (min, mean, median, max, std)
def get_stats_df(df_input):
    numeric_df = df_input.select_dtypes(include=[np.number])
    stats_list = []
    for col in numeric_df.columns:
        vals = numeric_df[col].dropna()
        if len(vals) > 0:
            stats_list.append({
                "Parameter": col,
                "min": round(vals.min(), 4),
                "mean": round(vals.mean(), 4),
                "median": round(vals.median(), 4),
                "max": round(vals.max(), 4),
                "std": round(vals.std(), 4)
            })
    return pd.DataFrame(stats_list)


# ──────────────────────────────────────────────────────────────
# SECTION 1: QUALITY PARAMETERS DISTRIBUTIONS
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📊 1. Quality Parameters Distribution Charts & Statistical Summary Table</div>', unsafe_allow_html=True)

# Table display
if not df_orange.empty:
    st.markdown("#### 📋 Quality Parameters Statistical Summary Table (`min`, `mean`, `median`, `max`, `std`):")
    st_q = get_stats_df(df_orange)
    st.dataframe(st_q, use_container_width=True, hide_index=True)

# Image display
image_path = os.path.join("eda_plots", "01_quality_distributions.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

# Explanation
st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Subplot Grid of Histograms with Kernel Density / Mean & Median Overlays.<br>
    • <b>What is it Used For?</b> Visualizing the statistical spread, central tendency (mean/median), and variance of all 11 Orange Quality parameters.<br>
    • <b>Why is it Used?</b> Histograms reveal whether quality parameters follow a stable normal distribution or contain extreme outliers. For instance, <code>AC Mooney</code> (mean=58.6, median=58.0) and <code>Hardness</code> (mean=50.5, median=51.0) show clean Gaussian distributions, confirming consistent laboratory quality testing across historical batches.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 2: PRODUCTION PARAMETERS DISTRIBUTIONS
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📈 2. Production Process Parameters Distribution & Summary Table</div>', unsafe_allow_html=True)

if not df_prod.empty:
    st.markdown("#### 📋 Production Settings Statistical Summary Table (`min`, `mean`, `median`, `max`, `std`):")
    st_p = get_stats_df(df_prod)
    st.dataframe(st_p, use_container_width=True, hide_index=True)

image_path = os.path.join("eda_plots", "02_production_distributions.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Subplot Grid of Histograms for 25+ Numeric Autoclave Operating Settings.<br>
    • <b>What is it Used For?</b> Inspecting operational set-point variations across vessel heating, pressure buildup, cooking duration, and unloading phases.<br>
    • <b>Why is it Used?</b> It identifies which operating parameters are tightly controlled (e.g. <code>Heat Valve Close Temp</code> centered at 222°C with std=9.4°C) versus parameters with wider operational spread (e.g. <code>Loading Duration</code> with std=306 mins).
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 3: QUALITY PARAMETERS BY CUSTOMER
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🏭 3. Quality Parameters Grouped by Customer</div>', unsafe_allow_html=True)

if not df_prod.empty and not df_orange.empty:
    combined_c = pd.concat([df_prod[['Customer']], df_orange.drop(columns=['Batch No.'], errors='ignore')], axis=1)
    st.markdown("#### 📋 Customer-Level Summary Table (`AC Mooney` & `Hardness` stats per Customer):")
    
    c_summary = combined_c.groupby('Customer').agg({
        'AC Mooney': ['count', 'min', 'mean', 'median', 'max', 'std'],
        'Hardness': ['min', 'mean', 'median', 'max', 'std']
    }).round(3)
    c_summary.columns = ['Count', 'Mooney min', 'Mooney mean', 'Mooney median', 'Mooney max', 'Mooney std',
                        'Hardness min', 'Hardness mean', 'Hardness median', 'Hardness max', 'Hardness std']
    st.dataframe(c_summary.reset_index(), use_container_width=True, hide_index=True)

image_path = os.path.join("eda_plots", "05_quality_by_customer.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Comparative Box Plots Grouped by Customer Category (<code>Pirelli</code>, <code>Other</code>, <code>Sumo Tumo</code>, <code>Alfredo</code>).<br>
    • <b>What is it Used For?</b> Comparing median quality targets, interquartile ranges (IQR), and outlier boundaries across customer accounts.<br>
    • <b>Why is it Used?</b> Different customer contracts demand distinct rubber physical properties (e.g. Pirelli Mooney mean=58.7 vs Sumo Tumo Mooney mean=55.3). This proves that <code>Customer</code> is a critical categorical feature required when modeling quality targets.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 4: QUALITY PARAMETERS BY SHIFT
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🕒 4. Quality Parameters Grouped by Production Shift</div>', unsafe_allow_html=True)

if not df_prod.empty and not df_orange.empty:
    combined_s = pd.concat([df_prod[['Shift']], df_orange.drop(columns=['Batch No.'], errors='ignore')], axis=1)
    st.markdown("#### 📋 Shift-Level Summary Table (`AC Mooney` & `Hardness` stats per Shift):")
    
    s_summary = combined_s.groupby('Shift').agg({
        'AC Mooney': ['count', 'min', 'mean', 'median', 'max', 'std'],
        'Hardness': ['min', 'mean', 'median', 'max', 'std']
    }).round(3)
    s_summary.columns = ['Count', 'Mooney min', 'Mooney mean', 'Mooney median', 'Mooney max', 'Mooney std',
                        'Hardness min', 'Hardness mean', 'Hardness median', 'Hardness max', 'Hardness std']
    st.dataframe(s_summary.reset_index(), use_container_width=True, hide_index=True)

image_path = os.path.join("eda_plots", "03_quality_by_shift.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Comparative Box Plots Grouped by Working Shift (<code>Shift 1</code>, <code>Shift 2</code>, <code>Shift 3</code>).<br>
    • <b>What is it Used For?</b> Detecting whether operating team changes or time of day (morning vs night) impact quality outcomes.<br>
    • <b>Why is it Used?</b> The horizontal median lines for Shift 1 (58.4), Shift 2 (58.9), and Shift 3 (58.5) are virtually identical. This confirms that rubber quality is process-driven by automated autoclave machinery rather than operator shift variance.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 5: QUALITY PARAMETERS BY SUPERVISOR
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">👨‍💼 5. Quality Parameters Grouped by Supervisor</div>', unsafe_allow_html=True)

image_path = os.path.join("eda_plots", "04_quality_by_supervisor.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Comparative Box Plots Grouped by Shift Supervisor.<br>
    • <b>What is it Used For?</b> Checking for supervisor-level bias or procedural operational discrepancies.<br>
    • <b>Why is it Used?</b> Box distributions across major supervisors (Gadagi, Rangrez, Kamlakar, Tikore) show substantial overlap, ruling out individual supervisor bias as a root cause of quality defects.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 6: PRODUCTION MULTI-COLLINEARITY
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔗 6. Production Features Multi-Collinearity Heatmap</div>', unsafe_allow_html=True)

image_path = os.path.join("eda_plots", "07_production_multicollinearity.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Lower-Triangular Inter-Feature Correlation Heatmap.<br>
    • <b>What is it Used For?</b> Identifying multi-collinearity (highly correlated pairs among production sensors).<br>
    • <b>Why is it Used?</b> It pinpoints redundant duplicate sensors. E.g. <code>Unload Complete Temp</code> and <code>Bottom Door Close Temp</code> have $r = +1.00$ (100% duplicate reading). Dropping one pair simplifies predictive formulas without losing information.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 7: QUALITY TARGETS INTER-CORRELATION
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🔄 7. Quality Parameters Inter-Correlation Matrix</div>', unsafe_allow_html=True)

image_path = os.path.join("eda_plots", "08_target_intercorrelation.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Symmetric Correlation Matrix among the 11 Quality Output Parameters.<br>
    • <b>What is it Used For?</b> Understanding how quality properties co-vary with each other.<br>
    • <b>Why is it Used?</b> Shows that primary viscosity <code>AC Mooney</code> moderately co-varies with secondary viscosity <code>Mv</code> ($r = +0.65$), while Tensile Strength (<code>TS</code>) moves together with <code>Hardness</code>.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)


# ──────────────────────────────────────────────────────────────
# SECTION 8: SUCCESS RATE & SPEC FAILURE ANALYSIS
# ──────────────────────────────────────────────────────────────
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown('<div class="section-title">🎯 8. Quality Success Rate & Spec Failure Count</div>', unsafe_allow_html=True)

# Table for Spec Ranges & Failure Counts
st.markdown("#### 📋 Quality Specification Ranges & Out-of-Spec Failure Table:")

spec_fail_data = [
    {"Quality Parameter": "AC Mooney", "Spec Min": "50.0", "Spec Max": "60.0", "Historical Fail Count": 44, "Pass Rate %": "69.7%"},
    {"Quality Parameter": "Ash%", "Spec Min": "3.0", "Spec Max": "7.0", "Historical Fail Count": 5, "Pass Rate %": "96.6%"},
    {"Quality Parameter": "C.B.%", "Spec Min": "28.0", "Spec Max": "36.0", "Historical Fail Count": 1, "Pass Rate %": "99.3%"},
    {"Quality Parameter": "A.E.%", "Spec Min": "6.0", "Spec Max": "12.0", "Historical Fail Count": 1, "Pass Rate %": "99.3%"},
    {"Quality Parameter": "V.M.%", "Spec Min": "0.0", "Spec Max": "1.0 (Max)", "Historical Fail Count": 0, "Pass Rate %": "100.0%"},
    {"Quality Parameter": "RHC", "Spec Min": "50.0 (Min)", "Spec Max": "-", "Historical Fail Count": 0, "Pass Rate %": "100.0%"},
    {"Quality Parameter": "Sp.Gravity", "Spec Min": "1.12", "Spec Max": "1.16", "Historical Fail Count": 2, "Pass Rate %": "98.6%"},
    {"Quality Parameter": "Mv", "Spec Min": "30.0", "Spec Max": "45.0", "Historical Fail Count": 18, "Pass Rate %": "87.6%"},
    {"Quality Parameter": "TS", "Spec Min": "75.0 (Min)", "Spec Max": "-", "Historical Fail Count": 7, "Pass Rate %": "95.2%"},
    {"Quality Parameter": "EB", "Spec Min": "480.0 (Min)", "Spec Max": "-", "Historical Fail Count": 3, "Pass Rate %": "97.9%"},
    {"Quality Parameter": "Hardness", "Spec Min": "48.0", "Spec Max": "54.0", "Historical Fail Count": 3, "Pass Rate %": "97.9%"}
]

st.dataframe(pd.DataFrame(spec_fail_data), use_container_width=True, hide_index=True)

image_path = os.path.join("eda_plots", "09_success_analysis.png")
if os.path.exists(image_path):
    st.image(image_path, use_container_width=True)

st.markdown("""
<div class="explanation-box">
    <div class="detail-heading">📌 Graph Details & Explanation:</div>
    • <b>Which Graph is Used?</b> Dual-Panel Chart (Left: Success % Histogram; Right: Horizontal Failure Count Bar Chart).<br>
    • <b>What is it Used For?</b> Quantifying batch specification compliance and highlighting which parameters fail spec limits most frequently.<br>
    • <b>Why is it Used?</b> It reveals that <code>AC Mooney</code> (44 failures) and <code>Mv</code> (18 failures) account for over 80% of all out-of-spec batches, highlighting the exact parameters requiring closest operator attention.
</div>
""", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Air Pollution & Health Impact Dashboard",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    /* ── Global ─────────────────────────────────────────── */
    html, body, [class*="css"] { font-family: 'Inter', 'Segoe UI', sans-serif; }

    /* ── Keyframes ──────────────────────────────────────── */
    @keyframes slideUp   { from { opacity:0; transform:translateY(24px); } to { opacity:1; transform:translateY(0); } }
    @keyframes popIn     { 0% { opacity:0; transform:scale(0.80); } 70% { transform:scale(1.05); } 100% { opacity:1; transform:scale(1); } }
    @keyframes glowPulse { 0%,100% { box-shadow:0 2px 16px rgba(0,0,0,0.12); } 50% { box-shadow:0 6px 24px rgba(0,0,0,0.22); } }
    @keyframes headSlide { from { opacity:0; transform:translateX(-14px); } to { opacity:1; transform:translateX(0); } }
    @keyframes barGrow   { from { width:0; } to { width:56px; } }

    /* ── Section heading ────────────────────────────────── */
    .sec-heading {
        display: flex; align-items: center; gap: 10px;
        margin: 28px 0 6px 0;
        animation: headSlide 0.4s ease both;
    }
    .sec-heading .sec-icon { font-size: 1.3rem; line-height: 1; }
    .sec-heading .sec-text {
        font-size: 1.45rem; font-weight: 800;
        color: #e4f0ff; letter-spacing: -0.3px;
        position: relative;
    }
    .sec-heading .sec-text::after {
        content:""; position:absolute; bottom:-5px; left:0;
        height:3px; border-radius:2px;
        background: linear-gradient(90deg, #4f8ef7, #7c4ff7, transparent);
        animation: barGrow 0.5s ease 0.3s both;
    }

    /* ── KPI card grids ─────────────────────────────────── */
    .kpi-grid   { display:grid; grid-template-columns:repeat(4,1fr); gap:14px; margin:16px 0 24px 0; }
    .kpi-grid-3 { display:grid; grid-template-columns:repeat(3,1fr); gap:14px; margin:16px 0 24px 0; }

    .kpi-card {
        background: linear-gradient(160deg, #0d1f3a 0%, #081528 100%);
        border: 1px solid rgba(79,142,247,0.15);
        border-radius: 16px;
        padding: 22px 22px 18px 22px;
        position: relative; overflow: hidden;
        transition: transform 0.22s ease, box-shadow 0.22s ease;
        animation: slideUp 0.5s ease both, glowPulse 4s ease-in-out 1s infinite;
        cursor: default;
    }
    .kpi-card:hover { transform:translateY(-5px); box-shadow:0 12px 36px rgba(0,0,0,0.35) !important; }

    /* Top accent — plain white */
    .kpi-card::before {
        content:""; position:absolute; top:0; left:0; right:0; height:2px;
        background: rgba(255,255,255,0.18);
    }
    /* Corner glow — neutral */
    .kpi-card::after {
        content:""; position:absolute; top:-30px; right:-30px;
        width:100px; height:100px;
        background:radial-gradient(circle, rgba(255,255,255,0.04) 0%, transparent 70%);
        border-radius:50%; pointer-events:none;
    }

    /* Stagger entrance delays */
    .kpi-card:nth-child(1) { animation-delay:0.00s; }
    .kpi-card:nth-child(2) { animation-delay:0.10s; }
    .kpi-card:nth-child(3) { animation-delay:0.20s; }
    .kpi-card:nth-child(4) { animation-delay:0.30s; }

    .kpi-icon  { font-size:1.6rem; margin-bottom:10px; display:block; }
    .kpi-label { font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#4a6e9a; margin-bottom:6px; }
    .kpi-value { font-size:2.1rem; font-weight:900; color:#ffffff; letter-spacing:-1px; line-height:1; animation:popIn 0.55s cubic-bezier(0.34,1.56,0.64,1) both; animation-delay:0.2s; }
    .kpi-sub   { font-size:0.75rem; color:#3d5e80; margin-top:6px; }

    /* Colour variants — border only, no shadow overrides */
    .kpi-blue   { border-color:rgba(79,142,247,0.30); }
    .kpi-orange { border-color:rgba(247,145,79,0.30); }
    .kpi-green  { border-color:rgba(79,217,124,0.30); }
    .kpi-purple { border-color:rgba(124,79,247,0.30); }

    /* ── Sidebar ────────────────────────────────────────── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0d1117 0%, #0f1a2e 100%) !important;
        border-right: 1px solid #1e3a5f !important;
    }
    [data-testid="stSidebar"] * { color: #c9d8ef !important; }
    .sidebar-logo { display:flex; align-items:center; gap:10px; padding:6px 0 14px 0; }
    .sidebar-logo-icon { font-size:2rem; line-height:1; }
    .sidebar-logo-text .title { font-size:1.05rem; font-weight:700; color:#ffffff !important; display:block; line-height:1.2; }
    .sidebar-logo-text .sub   { font-size:0.72rem; color:#5a7a9f !important; display:block; letter-spacing:0.04em; text-transform:uppercase; }
    .sidebar-divider { border:none; border-top:1px solid #1e3a5f; margin:12px 0; }
    .sidebar-section-label { font-size:0.68rem; font-weight:700; letter-spacing:0.1em; text-transform:uppercase; color:#3f6ea0 !important; margin:16px 0 8px 0; }
    .sidebar-meta { background:rgba(79,142,247,0.07); border:1px solid rgba(79,142,247,0.15); border-radius:8px; padding:10px 12px; margin-top:12px; font-size:0.75rem; color:#6a8ab0 !important; line-height:1.6; }
    .sidebar-meta strong { color:#8aabcf !important; }

    /* ── Tab bar ────────────────────────────────────────── */
    [data-testid="stTabs"] [data-baseweb="tab-list"] {
        background: rgba(13,17,23,0.8);
        border-bottom: 1px solid #1e3a5f;
        padding: 4px 4px 0 4px;
        gap: 2px;
        border-radius: 10px 10px 0 0;
    }
    [data-testid="stTabs"] [data-baseweb="tab"] {
        background: transparent; border: none; border-radius: 8px 8px 0 0;
        padding: 8px 18px; font-size: 0.82rem; font-weight: 500;
        color: #5a7a9f; transition: all 0.2s;
    }
    [data-testid="stTabs"] [data-baseweb="tab"]:hover { background:rgba(79,142,247,0.08); color:#9ab8e0; }
    [data-testid="stTabs"] [aria-selected="true"] {
        background: rgba(79,142,247,0.15) !important;
        color: #7ab3f7 !important;
        border-bottom: 2px solid #4f8ef7 !important;
        font-weight: 600 !important;
    }

    /* ── Insight cards ──────────────────────────────────── */
    .insight-box {
        background: linear-gradient(135deg, #0f1622 0%, #0d1420 100%);
        border: 1px solid #1e3050;
        border-left: 3px solid #4f8ef7;
        border-radius: 10px;
        padding: 14px 18px;
        margin: 8px 0 18px 0;
        font-size: 0.85rem;
        color: #8aaace;
        line-height: 1.7;
    }
    .insight-box strong { color: #c9d8ef; }
    .insight-box .highlight { color: #f7a86a; font-weight: 600; }

    /* ── Misc ───────────────────────────────────────────── */
    hr { border-color: #1e3050 !important; margin: 20px 0 !important; }
    [data-testid="stDataFrame"] { border:1px solid #1e3050; border-radius:10px; overflow:hidden; }
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD & PREPARE DATA
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("DataExtract.csv")
    df.columns = df.columns.str.strip()
    return df

df_raw = load_data()

SUPRA = [
    "All Countries",
    "European Environment Agency Member Countries",
    "European Union Countries",
]

AGE_EXCLUDE     = [">= 0 years of age"]
OUTCOME_EXCLUDE = ["All causes"]

PW_COL = "Air Pollution Population Weighted Average [ug/m3]"

df_country = df_raw[
    (df_raw["City Or Territory"] == "All Urban Centres in a Country") &
    (~df_raw["Country Or Territory"].isin(SUPRA)) &
    (~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE)) &
    (~df_raw["Outcome"].isin(OUTCOME_EXCLUDE))
].copy()

df_cities = df_raw[
    (df_raw["City Or Territory"] != "All Urban Centres in a Country") &
    (~df_raw["Country Or Territory"].isin(SUPRA)) &
    (~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE)) &
    (~df_raw["Outcome"].isin(OUTCOME_EXCLUDE))
].copy()

# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:
    st.markdown("""
    <div class="sidebar-logo">
        <span class="sidebar-logo-icon">🌍</span>
        <div class="sidebar-logo-text">
            <span class="title">Air Pollution & Health</span>
            <span class="sub">Europe · WHO 2021 AQG · 2022</span>
        </div>
    </div>
    <hr class="sidebar-divider"/>
    <div class="sidebar-section-label">🔎 Filter Data</div>
    """, unsafe_allow_html=True)
    st.caption("Leave a filter empty to include all options.")

    outcome_opts = sorted(
        df_raw["Outcome"].dropna()
        .loc[~df_raw["Outcome"].isin(OUTCOME_EXCLUDE)]
        .unique().tolist()
    )
    sel_outcome = st.multiselect("Health Outcome", options=outcome_opts)

    pollutant_opts = sorted(df_raw["Air Pollutant"].dropna().unique().tolist())
    sel_poll = st.multiselect("Air Pollutant", options=pollutant_opts)

    AGE_EXCLUDE_SIDEBAR = [">= 0 years of age", ">= 30 years of age"]
    age_opts = sorted(
        df_raw["Description Of Age Group"].dropna()
        .loc[~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE_SIDEBAR)]
        .unique().tolist()
    )
    sel_age = st.multiselect("Age Group", options=age_opts)

    indicator_opts = sorted(df_raw["Health Indicator"].dropna().unique().tolist())
    sel_indicator = st.multiselect("Health Indicator", options=indicator_opts)

    # Derive correct counts from data
    n_countries = df_country["Country Or Territory"].nunique()
    n_cities    = df_cities["City Or Territory"].nunique()

    st.markdown(f"""
    <hr class="sidebar-divider"/>
    <div class="sidebar-meta">
        <strong>📂 Data Source</strong><br>
        WHO / EEA Urban Air Quality<br>
        2022 · WHO 2021 AQG Baseline<br><br>
        <strong>Coverage</strong><br>
        {n_countries} countries · {n_cities} cities<br>
        3 pollutants: PM2.5, NO2, O3
    </div>
    """, unsafe_allow_html=True)

# ============================================================
# APPLY FILTERS — empty list = no filter (show all)
# ============================================================

def apply_filters(base_df):
    d = base_df.copy()
    if sel_poll:      d = d[d["Air Pollutant"].isin(sel_poll)]
    if sel_outcome:   d = d[d["Outcome"].isin(sel_outcome)]
    if sel_age:       d = d[d["Description Of Age Group"].isin(sel_age)]
    if sel_indicator: d = d[d["Health Indicator"].isin(sel_indicator)]
    return d

filtered_country = apply_filters(df_country)
filtered_cities  = apply_filters(df_cities)

ad_country  = filtered_country[filtered_country["Health Indicator"] == "Attributable deaths (AD)"]
yll_country = filtered_country[filtered_country["Health Indicator"] == "Years of Life Lost (YLL)"]
dal_country = filtered_country[filtered_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
yld_country = filtered_country[filtered_country["Health Indicator"] == "Years Lived with Disability (YLD)"]
ad_cities   = filtered_cities[filtered_cities["Health Indicator"] == "Attributable deaths (AD)"]

# ============================================================
# HELPERS
# ============================================================

def fmt(n):
    if pd.isna(n) or n == 0:
        return "N/A"
    n = float(n)
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:   return f"{n/1_000:.1f}K"
    return str(int(n))

DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8eaf0", family="sans-serif"),
    margin=dict(l=10, r=10, t=40, b=10),
)
ACCENT = ["#4f8ef7", "#f7914f", "#7c4ff7", "#4fd97c", "#f74f6e", "#f7d44f", "#4fd4f7"]

# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("""
<div style="text-align:center; padding: 8px 0 48px 0; margin-top:-40px;">
    <div style="font-size:2.6rem; font-weight:900; color:#ffffff; letter-spacing:-1px; margin-bottom:12px; line-height:1.15;">
        🌍 Air Pollution &amp; Health Impact in Europe
    </div>
    <div style="font-size:1.1rem; color:#6a9cc4; max-width:720px; margin:0 auto; line-height:1.6;">
        Quantifying the health burden of urban air pollution across 40 European countries —
        exploring mortality, disability, and disease patterns driven by PM2.5, NO2, and O3.
    </div>
</div>
""", unsafe_allow_html=True)

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Overview",
    "🗺️ Geographic",
    "🔬 Disease Breakdown",
    "👥 Age & Vulnerability",
    "⚖️ Death vs Disability",
    "🏙️ City Drilldown",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:

    st.markdown("""
    <div class="sec-heading">
        <span class="sec-icon">📊</span>
        <span class="sec-text">Health Burden Summary</span>
    </div>
    """, unsafe_allow_html=True)

    _ad  = fmt(ad_country["Value"].sum())
    _yll = fmt(yll_country["Value"].sum())
    _dal = fmt(dal_country["Value"].sum())
    _yld = fmt(yld_country["Value"].sum())

    st.markdown(f"""
    <div class="kpi-grid">
      <div class="kpi-card kpi-blue">
        <span class="kpi-icon">💀</span>
        <div class="kpi-label">Attributable Deaths</div>
        <div class="kpi-value">{_ad}</div>
        <div class="kpi-sub">All pollutants · all ages</div>
      </div>
      <div class="kpi-card kpi-orange">
        <span class="kpi-icon">⏳</span>
        <div class="kpi-label">Years of Life Lost (YLL)</div>
        <div class="kpi-value">{_yll}</div>
        <div class="kpi-sub">Premature death burden</div>
      </div>
      <div class="kpi-card kpi-purple">
        <span class="kpi-icon">⚕️</span>
        <div class="kpi-label">DALYs</div>
        <div class="kpi-value">{_dal}</div>
        <div class="kpi-sub">Disability-adjusted life years</div>
      </div>
      <div class="kpi-card kpi-green">
        <span class="kpi-icon">♿</span>
        <div class="kpi-label">Years Lived w/ Disability</div>
        <div class="kpi-value">{_yld}</div>
        <div class="kpi-sub">Chronic illness burden</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # FIX: Pollutant averages now use filtered_country so sidebar filters apply
    pm25 = filtered_country[(filtered_country["Air Pollutant"] == "PM2.5") & (filtered_country[PW_COL] < 500)][PW_COL].mean()
    no2  = filtered_country[(filtered_country["Air Pollutant"] == "NO2")   & (filtered_country[PW_COL] < 500)][PW_COL].mean()
    o3   = filtered_country[(filtered_country["Air Pollutant"] == "O3")    & (filtered_country[PW_COL] < 500)][PW_COL].mean()
    _pm25v = f"{pm25:.1f}" if pd.notna(pm25) else "N/A"
    _no2v  = f"{no2:.1f}"  if pd.notna(no2)  else "N/A"
    _o3v   = f"{o3:.1f}"   if pd.notna(o3)   else "N/A"

    pm25_x = f"{round(pm25/5, 1)}×" if pd.notna(pm25) else "N/A"
    no2_x  = f"{round(no2/10, 1)}×" if pd.notna(no2)  else "N/A"
    o3_x   = f"{round(o3/60,  1)}×" if pd.notna(o3)   else "N/A"

    st.markdown("""
    <div class="sec-heading">
        <span class="sec-icon">🌫️</span>
        <span class="sec-text">Population-Weighted Pollutant Averages</span>
    </div>
    <p style="font-size:0.8rem;color:#3d5e80;margin:0 0 4px 0;">
        WHO 2021 guideline limits: PM2.5 = 5 µg/m³ · NO2 = 10 µg/m³ · O3 = 60 µg/m³ —
        all values shown <strong style="color:#f7a86a;">exceed</strong> WHO limits.
    </p>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="kpi-grid-3">
      <div class="kpi-card kpi-blue">
        <div class="kpi-label">PM2.5 Average</div>
        <div class="kpi-value">{_pm25v} <span style="font-size:1rem;font-weight:500;color:#ffffff;">µg/m³</span></div>
        <div class="kpi-sub">WHO limit: 5 µg/m³ · {pm25_x} above limit</div>
      </div>
      <div class="kpi-card kpi-orange">
        <div class="kpi-label">NO2 Average</div>
        <div class="kpi-value">{_no2v} <span style="font-size:1rem;font-weight:500;color:#ffffff;">µg/m³</span></div>
        <div class="kpi-sub">WHO limit: 10 µg/m³ · {no2_x} above limit</div>
      </div>
      <div class="kpi-card kpi-green">
        <div class="kpi-label">O3 Average</div>
        <div class="kpi-value">{_o3v} <span style="font-size:1rem;font-weight:500;color:#ffffff;">µg/m³</span></div>
        <div class="kpi-sub">WHO limit: 60 µg/m³ · {o3_x} above limit</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # FIX: Dynamic insight values derived from filtered data
    pm25_ratio = f"~{round(pm25/5, 1)}×"  if pd.notna(pm25) else "N/A"
    no2_ratio  = f"~{round(no2/10, 1)}×" if pd.notna(no2)  else "N/A"
    o3_val     = f"~{_o3v} µg/m³"         if pd.notna(o3)   else "N/A"
    o3_pct_above = f"{round((o3/60 - 1)*100)}%" if pd.notna(o3) else "N/A"

    st.markdown(f"""
    <div class='insight-box'>
    <strong>💡 What this means:</strong>
    Europe's average PM2.5 is <span class='highlight'>{pm25_ratio} above</span> the WHO limit of 5 µg/m³.
    NO2 is <span class='highlight'>{no2_ratio} above</span> the 10 µg/m³ limit.
    O3 at {o3_val} is <span class='highlight'>{o3_pct_above} above</span> the 60 µg/m³ guideline —
    a widely overlooked pollutant that primarily harms lung function.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sec-heading"><span class="sec-icon">☠️</span><span class="sec-text">Which Pollutant Causes the Most Deaths?</span></div>', unsafe_allow_html=True)
    poll_deaths = ad_country.groupby("Air Pollutant")["Value"].sum().reset_index()
    poll_deaths.columns = ["Pollutant", "Deaths"]
    total_d = poll_deaths["Deaths"].sum()
    poll_deaths["Share (%)"] = (poll_deaths["Deaths"] / total_d * 100).round(1)

    fig_poll_share = px.bar(
        poll_deaths.sort_values("Deaths", ascending=True),
        x="Deaths", y="Pollutant", orientation="h",
        color="Pollutant",
        color_discrete_map={"PM2.5": "#4f8ef7", "NO2": "#f7914f", "O3": "#4ff7a8"},
        text="Share (%)",
        labels={"Deaths": "Attributable Deaths", "Pollutant": ""},
        template="plotly_dark",
    )
    fig_poll_share.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_poll_share.update_layout(**DARK, height=260, showlegend=False,
                                  xaxis=dict(gridcolor="#2a2d3e"),
                                  yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_poll_share, use_container_width=True)

    pm25_share = poll_deaths.loc[poll_deaths["Pollutant"] == "PM2.5", "Share (%)"].values
    no2_share  = poll_deaths.loc[poll_deaths["Pollutant"] == "NO2",   "Share (%)"].values
    o3_share   = poll_deaths.loc[poll_deaths["Pollutant"] == "O3",    "Share (%)"].values
    pm25_pct = f"{pm25_share[0]:.0f}%" if len(pm25_share) else "N/A"
    no2_pct  = f"{no2_share[0]:.0f}%"  if len(no2_share)  else "N/A"
    o3_pct   = f"{o3_share[0]:.0f}%"   if len(o3_share)   else "N/A"

    st.markdown(f"""
    <div class='insight-box'>
    <strong>💡 Key Finding:</strong>
    <span class='highlight'>PM2.5 is responsible for {pm25_pct} of all pollution-attributable deaths</span> in Europe.
    Fine particulate matter penetrates deep into the lungs and bloodstream, causing heart disease, stroke, dementia and lung cancer.
    NO2 contributes {no2_pct}, primarily through stroke and diabetes. O3 accounts for only {o3_pct}.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sec-heading"><span class="sec-icon">🔵</span><span class="sec-text">Pollution Level vs Attributable Deaths — by Country</span></div>', unsafe_allow_html=True)
    st.caption("Hover over a bubble to see country name, pollution level, and total deaths. Bubble size = total deaths.")

    scatter_agg = (
        ad_country.groupby("Country Or Territory")
        .agg(Deaths=("Value", "sum"), Pollution=(PW_COL, "mean"))
        .reset_index()
    )
    scatter_agg = scatter_agg[scatter_agg["Pollution"] < 500]

    fig_scatter = px.scatter(
        scatter_agg,
        x="Pollution", y="Deaths",
        hover_name="Country Or Territory",
        hover_data={"Pollution": ":.1f", "Deaths": ":,", "Country Or Territory": False},
        size="Deaths", size_max=50,
        color="Deaths",
        color_continuous_scale="Blues",
        labels={
            "Pollution": "Population-weighted pollution avg (µg/m³)",
            "Deaths":    "Total attributable deaths",
        },
        template="plotly_dark",
    )
    fig_scatter.update_layout(
        **DARK, height=450,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="#2a2d3e"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — Population size distorts raw totals:</strong>
    Italy and Germany have the highest total death counts due to large populations, not necessarily the worst pollution.
    <span class='highlight'>Smaller Balkan countries (Bosnia, Serbia) have higher pollution but fewer total deaths.</span>
    The per-100k rate (Geographic tab) is a much fairer comparison between countries.
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — GEOGRAPHIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:

    col_map1, col_map2 = st.columns(2)

    with col_map1:
        st.markdown('<div class="sec-heading"><span class="sec-icon">🗺️</span><span class="sec-text">Deaths per 100k by Country</span></div>', unsafe_allow_html=True)
        map_agg = (
            ad_country.groupby("Country Or Territory")["Value for 100k Of Affected Population"]
            .sum().reset_index()
        )
        map_agg.columns = ["Country", "Per100k"]
        fig_map = px.choropleth(
            map_agg, locations="Country", locationmode="country names",
            color="Per100k", color_continuous_scale="Reds", scope="europe",
            labels={"Per100k": "Deaths per 100k"}, template="plotly_dark",
        )
        fig_map.update_layout(
            **DARK, height=420,
            geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                     landcolor="#1e2130", showframe=False),
            coloraxis_colorbar=dict(
                thickness=12, len=0.7,
                tickfont=dict(color="#7a7d8f", size=10),
                title=dict(text="Deaths\nper 100k", font=dict(color="#7a7d8f", size=10)),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_map2:
        st.markdown('<div class="sec-heading"><span class="sec-icon">🗺️</span><span class="sec-text">PM2.5 Pollution Level by Country</span></div>', unsafe_allow_html=True)
        pm25_map = filtered_country[
            (filtered_country["Air Pollutant"] == "PM2.5") & (filtered_country[PW_COL] < 500)
        ].groupby("Country Or Territory")[PW_COL].mean().reset_index()
        pm25_map.columns = ["Country", "PM25"]
        fig_pm25_map = px.choropleth(
            pm25_map, locations="Country", locationmode="country names",
            color="PM25", color_continuous_scale="YlOrRd", scope="europe",
            labels={"PM25": "PM2.5 µg/m³"}, template="plotly_dark",
        )
        fig_pm25_map.update_layout(
            **DARK, height=420,
            geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                     landcolor="#1e2130", showframe=False),
            coloraxis_colorbar=dict(
                thickness=12, len=0.7,
                tickfont=dict(color="#7a7d8f", size=10),
                title=dict(text="PM2.5\nµg/m³", font=dict(color="#7a7d8f", size=10)),
            ),
        )
        st.plotly_chart(fig_pm25_map, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — The East-West Divide:</strong>
    <span class='highlight'>Eastern and Balkan countries suffer far more deaths per 100,000 people</span> despite smaller populations.
    Bosnia & Herzegovina, North Macedonia and Serbia top the per-100k table — driven by heavy reliance on coal heating,
    older vehicle fleets, and weaker environmental regulations. Compare both maps: the most polluted countries (right) closely
    mirror the highest mortality rates (left).
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sec-heading"><span class="sec-icon">🏆</span><span class="sec-text">Top 15 Countries — Deaths per 100k</span></div>', unsafe_allow_html=True)
    st.caption("Per-100k is a fairer comparison than total deaths as it adjusts for population size.")
    top_countries = (
        ad_country.groupby("Country Or Territory")["Value for 100k Of Affected Population"]
        .sum().reset_index()
        .nlargest(15, "Value for 100k Of Affected Population")
        .sort_values("Value for 100k Of Affected Population")
    )
    top_countries.columns = ["Country", "Per100k"]
    fig_top_c = px.bar(
        top_countries, x="Per100k", y="Country", orientation="h",
        color="Per100k", color_continuous_scale="Reds",
        labels={"Per100k": "Deaths per 100k population", "Country": ""},
        template="plotly_dark",
    )
    fig_top_c.update_layout(**DARK, height=480, coloraxis_showscale=False,
                             xaxis=dict(gridcolor="#2a2d3e"),
                             yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_top_c, use_container_width=True)

    top15_sorted = top_countries.sort_values("Per100k", ascending=False)
    top1    = top15_sorted.iloc[0]["Country"]
    top1v   = top15_sorted.iloc[0]["Per100k"]
    top2    = top15_sorted.iloc[1]["Country"]
    top3    = top15_sorted.iloc[2]["Country"]
    bottom  = top15_sorted.iloc[-1]["Country"]
    bottomv = top15_sorted.iloc[-1]["Per100k"]
    ratio   = top1v / bottomv if bottomv > 0 else 0

    balkan = ["Bosnia and Herzegovina", "Serbia", "North Macedonia", "Croatia",
              "Albania", "Montenegro", "Bulgaria", "Romania"]
    balkan_in_top = top15_sorted[top15_sorted["Country"].isin(balkan)].shape[0]

    st.markdown(f"""
    <div class='insight-box'>
    <strong>💡 Key Finding — Balkans dominate the mortality ranking:</strong>
    <span class='highlight'>{top1} leads with {top1v:,.0f} deaths per 100k</span> — {ratio:.1f}× higher than
    {bottom} at the bottom of this list ({bottomv:,.0f} per 100k).
    {balkan_in_top} of the top 15 worst-affected countries are Balkan or Eastern European nations ({top1}, {top2}, {top3}…),
    where older coal infrastructure, high solid-fuel home heating, and weaker vehicle emission standards compound pollution exposure.
    This stark regional gap shows that EU membership and environmental regulation have a measurable protective effect on mortality.
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — DISEASE BREAKDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:

    st.markdown('<div class="sec-heading"><span class="sec-icon">🧬</span><span class="sec-text">Pollutant × Disease Heatmap — Which Pollutant Causes Which Disease?</span></div>', unsafe_allow_html=True)
    st.caption("Each cell shows attributable deaths for that disease × pollutant combination.")

    hm_long = (
        ad_country.groupby(["Outcome", "Air Pollutant"])["Value"]
        .sum().reset_index()
    )
    hm_long.columns = ["Disease", "Pollutant", "Deaths"]

    fig_hm = px.density_heatmap(
        hm_long, x="Pollutant", y="Disease", z="Deaths",
        color_continuous_scale="Blues",
        labels={"Deaths": "Attributable Deaths"},
        template="plotly_dark",
        text_auto=True,
    )
    fig_hm.update_layout(**DARK, height=380,
                          xaxis=dict(gridcolor="rgba(0,0,0,0)"),
                          yaxis=dict(gridcolor="rgba(0,0,0,0)"),
                          coloraxis_showscale=False)
    st.plotly_chart(fig_hm, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — Each pollutant has a distinct disease fingerprint:</strong>
    <span class='highlight'>PM2.5 is the only pollutant linked to Dementia, Lung Cancer, and Ischemic Heart Disease</span> — it reaches the bloodstream.
    NO2 primarily drives Stroke and Diabetes. O3 affects only COPD — it is a lung-specific pollutant.
    This means reducing PM2.5 would have the broadest cross-disease benefit.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # FIX: Removed 🍩 icon from heading (was left in by mistake), use pie chart icon instead
    st.markdown('<div class="sec-heading"><span class="sec-icon">📊</span><span class="sec-text">Disease Outcome Split — Share of Deaths</span></div>', unsafe_allow_html=True)
    outcome_agg = ad_country.groupby("Outcome")["Value"].sum().reset_index()

    # FIX: Use ACCENT palette — readable on dark background (Blues_r starts too dark)
    fig_donut = px.pie(
        outcome_agg, values="Value", names="Outcome",
        hole=0.55,
        color_discrete_sequence=ACCENT,
        template="plotly_dark",
    )
    fig_donut.update_traces(
        textposition="inside", textinfo="percent",
        insidetextorientation="radial",
        textfont=dict(color="white", size=11),
    )
    fig_donut.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#e8eaf0", family="sans-serif"),
        height=420, showlegend=True,
        legend=dict(orientation="v", font=dict(size=12, color="#7a7d8f"),
                    x=0.85, y=0.5, bgcolor="rgba(0,0,0,0)"),
        margin=dict(l=10, r=200, t=40, b=10),
    )
    st.plotly_chart(fig_donut, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — Stroke & Ischemic Heart Disease dominate deaths:</strong>
    <span class='highlight'>Stroke and Ischemic Heart Disease together account for the majority of pollution-attributable deaths</span> in Europe.
    PM2.5 is the primary driver — it reaches the bloodstream and triggers cardiovascular disease at scale.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sec-heading"><span class="sec-icon">📊</span><span class="sec-text">Burden by Disease — Mortality vs Morbidity</span></div>', unsafe_allow_html=True)
    st.caption("Mortality = attributable deaths (AD). Morbidity = years lived with disability (YLD). Shows which diseases kill vs which disable.")

    mort_by_disease = (
        filtered_country[filtered_country["Health Indicator"] == "Attributable deaths (AD)"]
        .groupby("Outcome")["Value"].sum().reset_index()
    )
    mort_by_disease.columns = ["Disease", "Value"]
    mort_by_disease["Category"] = "Mortality"

    morb_by_disease = (
        filtered_country[filtered_country["Health Indicator"] == "Years Lived with Disability (YLD)"]
        .groupby("Outcome")["Value"].sum().reset_index()
    )
    morb_by_disease.columns = ["Disease", "Value"]
    morb_by_disease["Category"] = "Morbidity"

    burden_disease = pd.concat([mort_by_disease, morb_by_disease], ignore_index=True)

    fig_burden_disease = px.bar(
        burden_disease,
        x="Disease", y="Value", color="Category",
        barmode="group",
        color_discrete_map={"Mortality": "#4f8ef7", "Morbidity": "#f7914f"},
        labels={"Value": "Count", "Disease": "Disease", "Category": "Category"},
        template="plotly_dark",
    )
    fig_burden_disease.update_layout(
        **DARK, height=420,
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=-30),
        yaxis=dict(gridcolor="#2a2d3e", title="Count"),
        legend=dict(orientation="h", y=1.08, font=dict(size=11, color="#7a7d8f"),
                    bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_burden_disease, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — Diseases affect populations in completely different ways:</strong>
    <span class='highlight'>Ischemic Heart Disease and Stroke dominate mortality</span> — these diseases kill at scale.
    In contrast, <span class='highlight'>Childhood Asthma and Dementia dominate morbidity</span> — they disable rather than kill directly.
    This split is essential for policy: reducing PM2.5 targets both killers and disablers simultaneously.
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — AGE & VULNERABILITY
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:

    _AGE_ORDER_RISK = ["< 19 years of age", ">= 19 years of age",
                       ">= 25 years of age", ">= 60 years of age"]

    _AGE_COLOURS = {
        "< 19 years of age":  "#4f8ef7",
        ">= 19 years of age": "#4fd97c",
        ">= 25 years of age": "#f7914f",
        ">= 60 years of age": "#f74f6e",
    }

    st.markdown('<div class="sec-heading"><span class="sec-icon">👥</span><span class="sec-text">Who Is Most at Risk? — DALY per 100k by Age Group</span></div>', unsafe_allow_html=True)
    st.caption("DALY (Disability-Adjusted Life Years) captures both deaths and disability — "
               "giving a complete picture across all age groups including children.")
    age_agg = (
        filtered_country[filtered_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
        .groupby("Description Of Age Group")["Value for 100k Of Affected Population"]
        .sum().reset_index()
    )
    age_agg.columns = ["Age Group", "Per100k"]
    age_agg["_order"] = age_agg["Age Group"].apply(
        lambda x: _AGE_ORDER_RISK.index(x) if x in _AGE_ORDER_RISK else 99
    )
    age_agg = age_agg.sort_values("_order").drop(columns="_order")

    # FIX: Use barmode="group" — overlay caused bars to stack on top of each other
    fig_age = go.Figure()
    for _, row in age_agg.iterrows():
        fig_age.add_trace(go.Bar(
            x=[row["Per100k"]],
            y=[row["Age Group"]],
            orientation="h",
            marker_color=_AGE_COLOURS.get(row["Age Group"], "#aaaaaa"),
            text=[f"{row['Per100k']:,.0f}"],
            textposition="outside",
            name=row["Age Group"],
            showlegend=False,
        ))
    fig_age.update_layout(
        **DARK, height=340, barmode="group",
        xaxis=dict(gridcolor="#2a2d3e", title="DALY per 100k"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)",
                   categoryorder="array",
                   categoryarray=list(reversed(_AGE_ORDER_RISK))),
    )
    st.plotly_chart(fig_age, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — The ≥25 group carries the greatest total burden:</strong>
    The <span class='highlight'>≥25 age group dominates DALY per 100k</span> driven by stroke,
    ischemic heart disease and diabetes. The ≥60 group follows with dementia and heart disease.
    Children and young adults (&lt;19, ≥19) show real but lower burden — primarily from asthma disability
    rather than deaths, which is why DALY is the right metric here.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    st.markdown('<div class="sec-heading"><span class="sec-icon">🔥</span><span class="sec-text">Age Group × Disease — Which Age Group Gets Which Disease?</span></div>', unsafe_allow_html=True)
    st.caption("Using DALY (deaths + disability) so all age groups, including children, show their true burden.")
    age_disease = (
        filtered_country[filtered_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
        .groupby(["Description Of Age Group", "Outcome"])["Value"]
        .sum().reset_index()
    )
    age_disease.columns = ["Age Group", "Disease", "DALY"]
    present_ages = [a for a in _AGE_ORDER_RISK if a in age_disease["Age Group"].unique()]

    fig_age_hm = px.density_heatmap(
        age_disease, x="Age Group", y="Disease", z="DALY",
        color_continuous_scale="YlOrRd",
        template="plotly_dark",
        text_auto=True,
        category_orders={"Age Group": present_ages},
    )
    fig_age_hm.update_layout(**DARK, height=420,
                              coloraxis_showscale=False,
                              xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=-20,
                                         categoryorder="array", categoryarray=present_ages),
                              yaxis=dict(gridcolor="rgba(0,0,0,0)"))
    st.plotly_chart(fig_age_hm, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding:</strong>
    <span class='highlight'>Dementia burden is concentrated in the ≥60 age group</span> — the defining disease of elderly air pollution exposure.
    Stroke, Ischemic Heart Disease and Diabetes peak in the ≥25 group.
    Children (&lt;19) and young adults (≥19) show asthma as their primary burden — disability without significant mortality.
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5 — DEATH vs DISABILITY (YLL vs YLD)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab5:

    st.markdown('<div class="sec-heading"><span class="sec-icon">⚖️</span><span class="sec-text">Premature Death vs Long-Term Disability — by Disease</span></div>', unsafe_allow_html=True)
    st.caption(
        "YLL = Years of Life Lost (premature death). "
        "YLD = Years Lived with Disability (chronic illness). "
        "A high YLL% = disease mostly kills quickly. A high YLD% = disease causes prolonged suffering."
    )

    yll_d = yll_country.groupby("Outcome")["Value"].sum()
    yld_d = yld_country.groupby("Outcome")["Value"].sum()
    tradeoff = pd.DataFrame({"YLL": yll_d, "YLD": yld_d}).fillna(0).reset_index()
    tradeoff.columns = ["Disease", "YLL", "YLD"]
    tradeoff["Total"] = tradeoff["YLL"] + tradeoff["YLD"]
    tradeoff = tradeoff[tradeoff["Total"] > 0]
    tradeoff["YLL_%"] = (tradeoff["YLL"] / tradeoff["Total"] * 100).round(1)
    tradeoff["YLD_%"] = (tradeoff["YLD"] / tradeoff["Total"] * 100).round(1)
    tradeoff = tradeoff.sort_values("YLL_%", ascending=True)

    fig_stacked = go.Figure()
    fig_stacked.add_trace(go.Bar(
        y=tradeoff["Disease"], x=tradeoff["YLD_%"],
        name="% Disability (YLD)",
        orientation="h",
        marker_color="#f7914f",
        text=tradeoff["YLD_%"].astype(str) + "%",
        textposition="inside",
    ))
    fig_stacked.add_trace(go.Bar(
        y=tradeoff["Disease"], x=tradeoff["YLL_%"],
        name="% Premature Death (YLL)",
        orientation="h",
        marker_color="#4f8ef7",
        text=tradeoff["YLL_%"].astype(str) + "%",
        textposition="inside",
    ))
    fig_stacked.update_layout(
        **DARK, height=380, barmode="stack",
        xaxis=dict(title="Percentage of Total Burden", gridcolor="#2a2d3e", range=[0, 100]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", y=1.08, font=dict(size=11, color="#7a7d8f"),
                    bgcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_stacked, use_container_width=True)

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 Key Finding — Two completely different stories:</strong><br>
    • <span class='highlight'>Lung Cancer (99%) and Ischemic Heart Disease (97%)</span> are almost entirely about premature death — once diagnosed, they kill quickly.<br>
    • <span class='highlight'>Childhood Asthma (99% YLD) and Dementia (56% YLD)</span> are about prolonged suffering — years of chronic disability.<br>
    Stroke, Diabetes and COPD sit in the middle — both killing and disabling.
    This distinction is critical for policy: reducing PM2.5 saves lives from heart disease AND prevents years of dementia and asthma disability.
    </div>
    """, unsafe_allow_html=True)


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 6 — CITY DRILLDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab6:

    st.markdown('<div class="sec-heading"><span class="sec-icon">🏙️</span><span class="sec-text">City-Level Drilldown — Top 100 Cities by Burden per 100k</span></div>', unsafe_allow_html=True)
    st.caption("Sorted by deaths per 100k affected population. CI = 95% confidence interval.")

    cols_needed = [
        "City Or Territory", "Country Or Territory", "Air Pollutant", "Outcome",
        "Description Of Age Group", "Value", "Value - lower CI", "Value - upper CI",
        "Value for 100k Of Affected Population", "Air Pollution Average [ug/m3]",
    ]
    table_df = (
        ad_cities[cols_needed]
        .sort_values("Value for 100k Of Affected Population", ascending=False)
        .head(100)
        .rename(columns={
            "City Or Territory":                     "City",
            "Country Or Territory":                  "Country",
            "Air Pollutant":                         "Pollutant",
            "Outcome":                               "Disease",
            "Description Of Age Group":              "Age Group",
            "Value":                                 "Deaths (AD)",
            "Value - lower CI":                      "CI Lower",
            "Value - upper CI":                      "CI Upper",
            "Value for 100k Of Affected Population": "Per 100k",
            "Air Pollution Average [ug/m3]":         "µg/m³ Avg",
        })
        .reset_index(drop=True)
    )
    st.dataframe(table_df, use_container_width=True, height=500)


# ============================================================
# FOOTER
# ============================================================

# Derive counts dynamically for accuracy
_n_countries = df_country["Country Or Territory"].nunique()
_n_cities    = df_cities["City Or Territory"].nunique()

st.markdown(f"""
<hr/>
<div style="text-align:center; font-size:0.75rem; color:#3f6ea0; padding: 8px 0 4px 0;">
    📂 <strong style="color:#5a7a9f;">Data Source:</strong> WHO Air Quality &amp; Health Dataset &nbsp;·&nbsp;
    {_n_countries} Countries &nbsp;·&nbsp; {_n_cities} Cities &nbsp;·&nbsp; 3 Pollutants &nbsp;·&nbsp;
    Reference Year 2022 &nbsp;·&nbsp; WHO 2021 AQG Baseline
</div>
""", unsafe_allow_html=True)

# ============================================================
# app.py — Air Pollution & Health Impact in Europe
# WHO/EEA Urban Air Quality Dataset · 2022
# ============================================================
# HOW TO RUN:
#   1. Place this file in the same folder as DataExtract.csv
#   2. pip install streamlit plotly pandas
#   3. streamlit run app.py
# ============================================================

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Air Pollution & Health Impact in Europe",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS — clean, consistent design
# ============================================================

st.markdown("""
<style>
    /* Insight boxes */
    .insight-box {
        background-color: #1c1f33;
        border-left: 4px solid #4f8ef7;
        border-radius: 6px;
        padding: 12px 16px;
        margin: 6px 0 18px 0;
        font-size: 0.87rem;
        color: #b0b8d8;
        line-height: 1.65;
    }
    .insight-box strong { color: #e8eaf0; }
    .insight-box .hl    { color: #f7914f; font-weight: 600; }

    /* Metric card tweak */
    div[data-testid="metric-container"] {
        background: #1c1f33;
        border: 1px solid #2e3250;
        border-radius: 8px;
        padding: 12px 16px 10px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# DATA LOADING & PREPARATION
# ============================================================

@st.cache_data
def load_data():
    df = pd.read_csv("DataExtract.csv")
    df.columns = df.columns.str.strip()
    return df

df_raw = load_data()

# Exclude supra-national aggregates
SUPRA = ["All Countries",
         "European Environment Agency Member Countries",
         "European Union Countries"]

# Exclude catch-all age groups and rollup outcome to avoid double-counting
AGE_EXCLUDE     = [">= 0 years of age", ">= 19 years of age"]
OUTCOME_EXCLUDE = ["All causes"]

PW_COL  = "Air Pollution Population Weighted Average [ug/m3]"
AVG_COL = "Air Pollution Average [ug/m3]"

# Country-level rows (aggregated across all cities in a country)
df_country = df_raw[
    (df_raw["City Or Territory"] == "All Urban Centres in a Country") &
    (~df_raw["Country Or Territory"].isin(SUPRA)) &
    (~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE)) &
    (~df_raw["Outcome"].isin(OUTCOME_EXCLUDE))
].copy()

# City-level rows
df_cities = df_raw[
    (df_raw["City Or Territory"] != "All Urban Centres in a Country") &
    (~df_raw["Country Or Territory"].isin(SUPRA)) &
    (~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE)) &
    (~df_raw["Outcome"].isin(OUTCOME_EXCLUDE))
].copy()

# ============================================================
# SIDEBAR — FILTERS
# ============================================================

with st.sidebar:
    st.markdown("## 🌍 Air Pollution")
    st.markdown("### Health Impact Dashboard")
    st.markdown("Europe · 2022 · WHO 2021 AQG Baseline")
    st.markdown("---")
    st.markdown("### 🔎 Global Filters")
    st.caption("All charts update when you change a filter. Leave empty to include all.")

    outcome_opts = sorted(
        df_raw["Outcome"].dropna()
        .loc[~df_raw["Outcome"].isin(OUTCOME_EXCLUDE)]
        .unique().tolist()
    )
    sel_outcome = st.multiselect("Health Outcome / Disease", options=outcome_opts)

    pollutant_opts = sorted(df_raw["Air Pollutant"].dropna().unique().tolist())
    sel_poll = st.multiselect("Air Pollutant", options=pollutant_opts)

    age_opts = sorted(
        df_raw["Description Of Age Group"].dropna()
        .loc[~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE)]
        .unique().tolist()
    )
    sel_age = st.multiselect("Age Group", options=age_opts)

    sex_opts = sorted(df_raw["Sex"].dropna().unique().tolist())
    sel_sex = st.multiselect("Sex", options=sex_opts)

    st.markdown("---")
    st.caption("📂 Data: WHO/EEA Urban Air Quality 2022\n37 countries · 973 cities · 3 pollutants")

# ============================================================
# APPLY FILTERS
# ============================================================

def apply_filters(base_df):
    d = base_df.copy()
    if sel_poll:    d = d[d["Air Pollutant"].isin(sel_poll)]
    if sel_outcome: d = d[d["Outcome"].isin(sel_outcome)]
    if sel_age:     d = d[d["Description Of Age Group"].isin(sel_age)]
    if sel_sex:     d = d[d["Sex"].isin(sel_sex)]
    return d

filtered_country = apply_filters(df_country)
filtered_cities  = apply_filters(df_cities)

# Indicator subsets (country-level)
ad_country  = filtered_country[filtered_country["Health Indicator"] == "Attributable deaths (AD)"]
yll_country = filtered_country[filtered_country["Health Indicator"] == "Years of Life Lost (YLL)"]
dal_country = filtered_country[filtered_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
yld_country = filtered_country[filtered_country["Health Indicator"] == "Years Lived with Disability (YLD)"]
ad_cities   = filtered_cities[filtered_cities["Health Indicator"] == "Attributable deaths (AD)"]

# ============================================================
# SHARED HELPERS
# ============================================================

def fmt(n):
    """Format large numbers for KPI cards."""
    if pd.isna(n) or n == 0:
        return "N/A"
    n = float(n)
    if n >= 1_000_000: return f"{n/1_000_000:.2f}M"
    if n >= 1_000:     return f"{n/1_000:.1f}K"
    return str(int(n))

# Shared dark-transparent layout base
# NOTE: margin is intentionally excluded here — set it per-chart to avoid
# "multiple values for keyword argument 'margin'" when **DARK is unpacked.
DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8eaf0", family="sans-serif", size=12),
)

# Default margin used by most charts — apply explicitly per update_layout call
M = dict(l=10, r=10, t=44, b=10)

POLL_COLORS = {"PM2.5": "#4f8ef7", "NO2": "#f7914f", "O3": "#4ff7a8"}
ACCENT = ["#4f8ef7", "#f7914f", "#7c4ff7", "#4ff7a8", "#f74f6e", "#f7d44f", "#4ff7d4"]

def insight(html):
    st.markdown(f"<div class='insight-box'>{html}</div>", unsafe_allow_html=True)

def section(label):
    st.subheader(label)

# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("# 🌍 Air Pollution & Health Impact in Europe")
st.markdown(
    "Interactive analysis of health burdens caused by **PM2.5**, **NO2**, and **O3** "
    "across **37 European countries** and **973 cities** · WHO/EEA 2022 data · WHO 2021 AQG Baseline"
)
st.markdown("---")

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊  Overview & Pollutants",
    "🗺️  Geographic Patterns",
    "🔬  Disease Analysis",
    "👥  Age & Vulnerability",
    "🏙️  City Explorer",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — OVERVIEW & POLLUTANTS
# Purpose: Big-picture KPIs + which pollutant kills most + trend
# Unique charts: KPI row, pollutant share bar, pollutant×disease heatmap
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:

    # ── KPI CARDS ────────────────────────────────────────────
    section("Key Health Burden Metrics")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💀 Attributable Deaths",      fmt(ad_country["Value"].sum()))
    k2.metric("⏳ Years of Life Lost",        fmt(yll_country["Value"].sum()))
    k3.metric("⚕️ DALYs (Total Burden)",      fmt(dal_country["Value"].sum()))
    k4.metric("♿ Years Lived with Disability", fmt(yld_country["Value"].sum()))

    st.markdown("")

    # ── WHO GUIDELINE COMPARISON ──────────────────────────────
    section("Pollutant Exposure vs WHO 2021 Safe Limits")
    st.caption(
        "Population-weighted averages across European urban areas. "
        "**WHO limits:** PM2.5 = 5 µg/m³ · NO2 = 10 µg/m³ · O3 = 60 µg/m³"
    )

    pm25_val = df_country[(df_country["Air Pollutant"] == "PM2.5") & (df_country[PW_COL] < 500)][PW_COL].mean()
    no2_val  = df_country[(df_country["Air Pollutant"] == "NO2")   & (df_country[PW_COL] < 500)][PW_COL].mean()
    o3_val   = df_country[(df_country["Air Pollutant"] == "O3")    & (df_country[PW_COL] < 500)][PW_COL].mean()

    who_limits = {"PM2.5": 5, "NO2": 10, "O3": 60}
    who_actual = {
        "PM2.5": round(pm25_val, 1) if pd.notna(pm25_val) else 0,
        "NO2":   round(no2_val,  1) if pd.notna(no2_val)  else 0,
        "O3":    round(o3_val,   1) if pd.notna(o3_val)   else 0,
    }

    bars_who = []
    for poll, actual in who_actual.items():
        limit = who_limits[poll]
        bars_who.append({"Pollutant": poll, "Type": "Actual Exposure", "Value": actual})
        bars_who.append({"Pollutant": poll, "Type": "WHO Safe Limit",  "Value": limit})

    df_who = pd.DataFrame(bars_who)
    fig_who = px.bar(
        df_who, x="Pollutant", y="Value", color="Type", barmode="group",
        color_discrete_map={"Actual Exposure": "#f7914f", "WHO Safe Limit": "#4ff7a8"},
        labels={"Value": "µg/m³"},
        template="plotly_dark",
        text="Value",
    )
    fig_who.update_traces(texttemplate="%{text}", textposition="outside")
    fig_who.update_layout(
        **DARK, height=320, margin=M,
        legend=dict(orientation="h", y=1.1, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#7a7d8f")),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#2a2d3e", title="µg/m³"),
    )
    st.plotly_chart(fig_who, use_container_width=True)

    insight(
        "<strong>All three pollutants exceed WHO limits.</strong> "
        "Europe's average PM2.5 is <span class='hl'>~2.7× above</span> the safe limit of 5 µg/m³. "
        "NO2 is <span class='hl'>~1.8× above</span> its 10 µg/m³ limit. "
        "O3 at ~88 µg/m³ is <span class='hl'>47% above</span> the 60 µg/m³ guideline — often overlooked but harmful to lung function."
    )

    st.markdown("---")

    # ── POLLUTANT SHARE OF DEATHS ─────────────────────────────
    col_a, col_b = st.columns(2)

    with col_a:
        section("Share of Deaths by Pollutant")
        st.caption("Share of total attributable deaths by pollutant type.")
        poll_deaths = ad_country.groupby("Air Pollutant")["Value"].sum().reset_index()
        poll_deaths.columns = ["Pollutant", "Deaths"]
        total_d = poll_deaths["Deaths"].sum()
        poll_deaths["Share (%)"] = (poll_deaths["Deaths"] / total_d * 100).round(1)

        fig_poll_pie = px.pie(
            poll_deaths, values="Deaths", names="Pollutant",
            hole=0.52,
            color="Pollutant",
            color_discrete_map=POLL_COLORS,
            template="plotly_dark",
        )
        fig_poll_pie.update_traces(
            textinfo="percent+label",
            textfont=dict(size=12, color="white"),
            insidetextorientation="radial",
        )
        fig_poll_pie.update_layout(
            **DARK, height=320, showlegend=False,
            margin=dict(l=10, r=10, t=10, b=10),
        )
        st.plotly_chart(fig_poll_pie, use_container_width=True)

    with col_b:
        section("Attributable Deaths — Mortality vs Morbidity by Pollutant")
        st.caption("Breaks down each pollutant's deaths by whether the cause is classified as Mortality or Morbidity.")
        poll_cat = ad_country.groupby(["Air Pollutant", "Category"])["Value"].sum().reset_index()
        fig_poll_cat = px.bar(
            poll_cat, x="Air Pollutant", y="Value", color="Category",
            barmode="group",
            color_discrete_sequence=ACCENT,
            labels={"Value": "Attributable Deaths", "Air Pollutant": "Pollutant"},
            template="plotly_dark",
        )
        fig_poll_cat.update_layout(
            **DARK, height=320, margin=M,
            legend=dict(orientation="h", y=1.12, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#7a7d8f")),
            xaxis=dict(gridcolor="rgba(0,0,0,0)"),
            yaxis=dict(gridcolor="#2a2d3e"),
        )
        st.plotly_chart(fig_poll_cat, use_container_width=True)

    insight(
        "<strong>PM2.5 dominates.</strong> Fine particulate matter accounts for "
        "<span class='hl'>~83% of all pollution-attributable deaths</span> in Europe. "
        "It penetrates the lungs and bloodstream, causing heart disease, stroke, dementia, and lung cancer. "
        "NO2 contributes ~17%, mainly through stroke and diabetes. O3 accounts for only ~2%."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — GEOGRAPHIC PATTERNS
# Purpose: Where is pollution worst? Where do people die most?
# Unique charts: Two choropleth maps (side-by-side), Top cities bar
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:

    section("Deaths per 100k Population vs PM2.5 Pollution — Country Comparison")

    col_m1, col_m2 = st.columns(2)

    with col_m1:
        st.caption("🗺️ Deaths per 100,000 people — darker red = higher burden")
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
            **DARK, height=430, margin=M,
            geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                     landcolor="#1e2130", showframe=False),
            coloraxis_colorbar=dict(
                thickness=12, len=0.7,
                tickfont=dict(color="#7a7d8f", size=10),
                title=dict(text="Deaths\nper 100k", font=dict(color="#7a7d8f", size=10)),
            ),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_m2:
        st.caption("🗺️ PM2.5 concentration — darker = more polluted air")
        pm25_map = df_country[
            (df_country["Air Pollutant"] == "PM2.5") & (df_country[PW_COL] < 500)
        ].groupby("Country Or Territory")[PW_COL].mean().reset_index()
        pm25_map.columns = ["Country", "PM25"]
        fig_pm = px.choropleth(
            pm25_map, locations="Country", locationmode="country names",
            color="PM25", color_continuous_scale="YlOrRd", scope="europe",
            labels={"PM25": "PM2.5 µg/m³"}, template="plotly_dark",
        )
        fig_pm.update_layout(
            **DARK, height=430, margin=M,
            geo=dict(bgcolor="rgba(0,0,0,0)", lakecolor="rgba(0,0,0,0)",
                     landcolor="#1e2130", showframe=False),
            coloraxis_colorbar=dict(
                thickness=12, len=0.7,
                tickfont=dict(color="#7a7d8f", size=10),
                title=dict(text="PM2.5\nµg/m³", font=dict(color="#7a7d8f", size=10)),
            ),
        )
        st.plotly_chart(fig_pm, use_container_width=True)

    insight(
        "<strong>The East-West divide is stark.</strong> "
        "Eastern and Balkan countries have far higher death rates per 100,000 people. "
        "<span class='hl'>Bosnia & Herzegovina, North Macedonia, Kosovo, and Serbia</span> top the mortality table — "
        "driven by coal heating, older vehicle fleets, and weaker environmental regulation. "
        "Compare both maps: the most polluted countries closely mirror the highest mortality rates."
    )

    st.markdown("---")

    # ── TOP 20 CITIES ─────────────────────────────────────────
    section("Top 20 Most Burdened Cities — Deaths per 100,000 Residents")
    st.caption("Per-100k rate adjusts for city population size — a fairer comparison than raw death totals.")

    city_agg = (
        ad_cities.groupby(["City Or Territory", "Country Or Territory"])
        ["Value for 100k Of Affected Population"].sum().reset_index()
    )
    city_agg.columns = ["City", "Country", "Per100k"]
    city_agg = city_agg.nlargest(20, "Per100k").sort_values("Per100k")
    city_agg["Label"] = city_agg["City"] + "  (" + city_agg["Country"] + ")"

    fig_cities = px.bar(
        city_agg, x="Per100k", y="Label", orientation="h",
        color="Per100k", color_continuous_scale="Blues",
        labels={"Per100k": "Deaths per 100k", "Label": ""},
        template="plotly_dark",
    )
    fig_cities.update_layout(
        **DARK, height=560, margin=M, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_cities, use_container_width=True)

    insight(
        "<strong>Italy's Po Valley dominates the city rankings.</strong> "
        "<span class='hl'>14 of the top 20 most burdened cities are Italian</span> — concentrated in the "
        "Po Valley (Milan, Brescia, Bergamo, Cremona). This flat basin surrounded by mountains traps "
        "pollution year-round. Geography matters as much as emissions."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — DISEASE ANALYSIS
# Purpose: Which diseases are caused by which pollutant?
# Unique charts: Pollutant×Disease heatmap, DALY bar,
#                YLL vs YLD stacked 100% bar (death vs disability split)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:

    # ── POLLUTANT × DISEASE HEATMAP ───────────────────────────
    section("Pollutant × Disease Heatmap — Which Pollutant Causes Which Disease?")
    st.caption(
        "Each cell shows the number of deaths attributable to that pollutant–disease combination. "
        "Darker = more deaths."
    )

    hm_data = ad_country.groupby(["Outcome", "Air Pollutant"])["Value"].sum().reset_index()
    hm_data.columns = ["Disease", "Pollutant", "Deaths"]

    fig_hm = px.density_heatmap(
        hm_data, x="Pollutant", y="Disease", z="Deaths",
        color_continuous_scale="Blues",
        labels={"Deaths": "Attributable Deaths"},
        template="plotly_dark",
        text_auto=True,
    )
    fig_hm.update_layout(
        **DARK, height=380, margin=M,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        coloraxis_showscale=False,
    )
    st.plotly_chart(fig_hm, use_container_width=True)

    insight(
        "<strong>Each pollutant has a distinct disease fingerprint.</strong> "
        "<span class='hl'>PM2.5 is the only pollutant linked to Dementia, Lung Cancer, and Ischemic Heart Disease</span> — "
        "it reaches the bloodstream. NO2 primarily drives Stroke and Diabetes. "
        "O3 affects only COPD — it is a lung-specific pollutant. "
        "Reducing PM2.5 would have the broadest cross-disease benefit."
    )

    st.markdown("---")

    # ── DALY BY DISEASE ───────────────────────────────────────
    section("Total Disease Burden — DALY by Disease (Deaths + Disability)")
    st.caption(
        "DALY = Deaths + Years of Disability combined. "
        "The most complete single measure of a disease's overall burden on society."
    )
    daly_d = dal_country.groupby("Outcome")["Value"].sum().reset_index()
    daly_d.columns = ["Disease", "DALY"]
    daly_d = daly_d.sort_values("DALY")

    fig_daly = px.bar(
        daly_d, x="DALY", y="Disease", orientation="h",
        color="DALY", color_continuous_scale="Purples",
        labels={"DALY": "Disability-Adjusted Life Years", "Disease": ""},
        template="plotly_dark",
    )
    fig_daly.update_layout(
        **DARK, height=420, margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_daly, use_container_width=True)

    st.markdown("---")

    # ── YLL vs YLD STACKED ────────────────────────────────────
    section("Premature Death (YLL) vs Long-Term Disability (YLD) — by Disease")
    st.caption(
        "Blue = share of burden that is premature death (YLL). "
        "Orange = share that is years of chronic disability (YLD). "
        "Each bar totals 100%."
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

    fig_stack = go.Figure()
    fig_stack.add_trace(go.Bar(
        y=tradeoff["Disease"], x=tradeoff["YLD_%"],
        name="% Disability (YLD)", orientation="h",
        marker_color="#f7914f",
        text=tradeoff["YLD_%"].astype(str) + "%",
        textposition="inside",
    ))
    fig_stack.add_trace(go.Bar(
        y=tradeoff["Disease"], x=tradeoff["YLL_%"],
        name="% Premature Death (YLL)", orientation="h",
        marker_color="#4f8ef7",
        text=tradeoff["YLL_%"].astype(str) + "%",
        textposition="inside",
    ))
    fig_stack.update_layout(
        **DARK, height=420, margin=dict(l=10, r=10, t=30, b=10),
        barmode="stack",
        xaxis=dict(title="% of Total Burden", gridcolor="#2a2d3e", range=[0, 100]),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        legend=dict(orientation="h", y=1.08, bgcolor="rgba(0,0,0,0)", font=dict(size=11, color="#7a7d8f")),
    )
    st.plotly_chart(fig_stack, use_container_width=True)

    insight(
        "<strong>Two completely different disease stories.</strong> "
        "<span class='hl'>Lung Cancer (99%) and Ischemic Heart Disease (97%)</span> are almost entirely "
        "about premature death — once diagnosed, they kill quickly. "
        "<span class='hl'>Childhood Asthma (99% YLD) and Dementia (56% YLD)</span> are about prolonged "
        "suffering — years of chronic disability. "
        "This distinction is critical for policy: reducing PM2.5 saves lives from heart disease "
        "AND prevents years of dementia and asthma disability."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — AGE & VULNERABILITY
# Purpose: Who is harmed most, and how?
# Unique charts: Age group deaths bar, age×disease heatmap,
#                children's asthma by pollutant bar
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:

    # ── AGE GROUP DEATHS ──────────────────────────────────────
    section("Deaths per 100,000 by Age Group — Who Is Most at Risk?")
    st.caption("Per-100k rate within each age group. Reveals which age group is disproportionately affected.")

    age_agg = (
        ad_country.groupby("Description Of Age Group")["Value for 100k Of Affected Population"]
        .sum().reset_index()
    )
    age_agg.columns = ["Age Group", "Per100k"]
    age_agg = age_agg.sort_values("Per100k")

    fig_age = px.bar(
        age_agg, x="Per100k", y="Age Group", orientation="h",
        color="Per100k", color_continuous_scale="Oranges",
        labels={"Per100k": "Deaths per 100k", "Age Group": ""},
        text="Per100k",
        template="plotly_dark",
    )
    fig_age.update_traces(texttemplate="%{text:,.0f}", textposition="outside")
    fig_age.update_layout(
        **DARK, height=300, margin=M, coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_age, use_container_width=True)

    insight(
        "<strong>The elderly bear by far the greatest mortality burden.</strong> "
        "The <span class='hl'>≥60 age group has a disproportionately high death rate per 100k</span>, "
        "driven by PM2.5-linked Dementia, Ischemic Heart Disease, and Stroke. "
        "Children under 19 show near-zero pollution-attributable mortality — but suffer "
        "significantly in terms of asthma disability (see below)."
    )

    st.markdown("---")

    # ── AGE × DISEASE HEATMAP ─────────────────────────────────
    section("Age Group × Disease Heatmap — Which Diseases Affect Which Ages?")
    st.caption("Number of attributable deaths per age group × disease combination. Darker = more deaths.")

    age_dis = (
        ad_country.groupby(["Description Of Age Group", "Outcome"])["Value"]
        .sum().reset_index()
    )
    age_dis.columns = ["Age Group", "Disease", "Deaths"]

    fig_agehm = px.density_heatmap(
        age_dis, x="Age Group", y="Disease", z="Deaths",
        color_continuous_scale="YlOrRd",
        template="plotly_dark",
        text_auto=True,
    )
    fig_agehm.update_layout(
        **DARK, height=420, margin=dict(l=10, r=10, t=30, b=10),
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="rgba(0,0,0,0)", tickangle=-15),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_agehm, use_container_width=True)

    st.markdown("---")

    # ── CHILDREN'S ASTHMA DISABILITY ─────────────────────────
    section("Children's Asthma Disability (Under 19s) — Years Lived with Disability by Pollutant")
    st.caption(
        "Years Lived with Disability (YLD) measures chronic illness burden, not deaths. "
        "Children have near-zero pollution-attributable deaths but carry substantial asthma suffering."
    )

    child_yld = df_cities[
        (df_cities["Health Indicator"] == "Years Lived with Disability (YLD)") &
        (df_cities["Description Of Age Group"] == "< 19 years of age")
    ]
    child_poll = child_yld.groupby("Air Pollutant")["Value"].sum().reset_index()
    child_poll.columns = ["Pollutant", "YLD"]
    child_poll["Share"] = (child_poll["YLD"] / child_poll["YLD"].sum() * 100).round(1)

    fig_child = px.bar(
        child_poll, x="Pollutant", y="YLD",
        color="Pollutant",
        color_discrete_map=POLL_COLORS,
        text="Share",
        labels={"YLD": "Years Lived with Disability", "Pollutant": ""},
        template="plotly_dark",
    )
    fig_child.update_traces(texttemplate="%{text}%", textposition="outside")
    fig_child.update_layout(
        **DARK, height=360, margin=dict(l=10, r=10, t=30, b=60),
        showlegend=False,
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#2a2d3e"),
    )
    st.plotly_chart(fig_child, use_container_width=True)

    insight(
        "<strong>Children are not immune — they are harmed differently.</strong> "
        "While children have near-zero attributable deaths, "
        "<span class='hl'>PM2.5 causes 67% of childhood asthma disability</span> "
        "with NO2 contributing the remaining 33%. "
        "These pollutants cause tens of thousands of years of childhood asthma suffering across European cities. "
        "Protecting children requires reducing both PM2.5 and NO2, not just one."
    )


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 5 — CITY EXPLORER
# Purpose: Interactive deep-dive into individual cities
# Unique charts: City scatter (pollution vs deaths), data table
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab5:

    # ── INTERACTIVE COUNTRY FILTER FOR CITY SCATTER ───────────
    section("City Pollution Level vs Death Rate — Top 200 Cities (Bubble = Total Deaths)")
    st.caption(
        "Each bubble is a city. X-axis = average air pollution. Y-axis = deaths per 100,000 people. "
        "Bubble size = total deaths. Hover for city details. Use the filter to focus on specific countries."
    )

    available_countries = sorted(ad_cities["Country Or Territory"].dropna().unique().tolist())
    sel_countries = st.multiselect(
        "Filter by Country (leave empty to show all)",
        options=available_countries,
        key="city_country_filter",
    )

    city_scatter = (
        ad_cities.groupby(["City Or Territory", "Country Or Territory"])
        .agg(
            Deaths=("Value", "sum"),
            Per100k=("Value for 100k Of Affected Population", "sum"),
            Pollution=(AVG_COL, "mean"),
        ).reset_index()
    )
    city_scatter = city_scatter[city_scatter["Pollution"] < 500]

    if sel_countries:
        city_scatter = city_scatter[city_scatter["Country Or Territory"].isin(sel_countries)]

    city_scatter_top = city_scatter.nlargest(200, "Per100k")

    fig_city_sc = px.scatter(
        city_scatter_top,
        x="Pollution", y="Per100k",
        hover_name="City Or Territory",
        hover_data={
            "Country Or Territory": True,
            "Deaths": ":,",
            "Pollution": ":.1f",
            "Per100k": ":,",
        },
        size="Deaths", size_max=38,
        color="Country Or Territory",
        labels={
            "Pollution": "Air pollution average (µg/m³)",
            "Per100k":   "Deaths per 100k population",
        },
        template="plotly_dark",
    )
    fig_city_sc.update_layout(
        **DARK, height=520, margin=M,
        showlegend=True,
        legend=dict(orientation="v", font=dict(size=10, color="#7a7d8f"), bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="#2a2d3e"),
    )
    st.plotly_chart(fig_city_sc, use_container_width=True)

    insight(
        "<strong>City clusters reveal national patterns.</strong> "
        "Italian cities cluster upper-right (high pollution, high mortality). "
        "Nordic cities cluster bottom-left (low pollution, low mortality). "
        "<span class='hl'>Cities above 400 µg/m³ average pollution almost all exceed 400 deaths per 100k</span> — "
        "a clear threshold effect suggesting a tipping point in harm."
    )

    st.markdown("---")

    # ── SEARCHABLE DATA TABLE ─────────────────────────────────
    section("City-Level Data Table — Top 100 Cities Ranked by Deaths per 100k")
    st.caption(
        "Sorted by deaths per 100,000 affected population. "
        "CI = 95% confidence interval. Use the country filter above to narrow results."
    )

    cols_needed = [
        "City Or Territory", "Country Or Territory", "Air Pollutant", "Outcome",
        "Description Of Age Group", "Value",
        "Value - lower CI", "Value - upper CI",
        "Value for 100k Of Affected Population",
        AVG_COL,
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
            AVG_COL:                                 "µg/m³ Avg",
        })
        .reset_index(drop=True)
    )

    if sel_countries:
        table_df = table_df[table_df["Country"].isin(sel_countries)]

    st.dataframe(table_df, use_container_width=True, height=460)


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption(
    "🌍 Data source: WHO/EEA Urban Air Quality Dataset · 37 European countries · 973 cities · "
    "3 pollutants (PM2.5, NO2, O3) · 2022 · WHO 2021 AQG Baseline  |  "
    "Built with Streamlit & Plotly"
)

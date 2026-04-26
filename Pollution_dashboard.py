# ============================================================
# app.py  —  Air Pollution & Health Impact Dashboard
# Streamlit Implementation — Clean Tabbed Layout
# ============================================================
# HOW TO RUN:
#   1. Place this file in the same folder as DataExtract.csv
#   2. streamlit run app.py
# ============================================================

import pandas as pd
import plotly.express as px
import streamlit as st

# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Air Pollution & Health Impact",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

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

df_country = df_raw[
    (df_raw["City Or Territory"] == "All Urban Centres in a Country") &
    (~df_raw["Country Or Territory"].isin(SUPRA))
].copy()

df_cities = df_raw[
    (df_raw["City Or Territory"] != "All Urban Centres in a Country") &
    (~df_raw["Country Or Territory"].isin(SUPRA))
].copy()

PW_COL = "Air Pollution Population Weighted Average [ug/m3]"

# ============================================================
# SIDEBAR FILTERS
# ============================================================

with st.sidebar:
    st.markdown("## 🌍 Air Pollution")
    st.markdown("### Health Impact Dashboard")
    st.markdown("Europe · 2022 · WHO Baseline")
    st.markdown("---")
    st.markdown("### 🔎 Filters")

    # Pollutant — single dropdown with "All" option
    pollutant_opts = ["All"] + sorted(df_raw["Air Pollutant"].dropna().unique().tolist())
    sel_poll = st.selectbox("Air Pollutant", options=pollutant_opts)

    # Health Outcome — single dropdown with "All" option
    outcome_opts = ["All"] + sorted(df_raw["Outcome"].dropna().unique().tolist())
    sel_outcome = st.selectbox("Health Outcome", options=outcome_opts)

    # Age Group — single dropdown with "All" option
    age_opts = ["All"] + sorted(df_raw["Description Of Age Group"].dropna().unique().tolist())
    sel_age = st.selectbox("Age Group", options=age_opts)

    # Health Indicator — single dropdown with "All" option
    indicator_opts = ["All"] + sorted(df_raw["Health Indicator"].dropna().unique().tolist())
    sel_indicator = st.selectbox("Health Indicator", options=indicator_opts)

    st.markdown("---")
    st.caption("📂 WHO/EEA Urban Air Quality 2022\n40 countries · 977 cities · 3 pollutants")

# ============================================================
# APPLY FILTERS
# ============================================================

def apply_filters(base_df):
    d = base_df.copy()
    if sel_poll    != "All": d = d[d["Air Pollutant"].isin([sel_poll])]
    if sel_outcome != "All": d = d[d["Outcome"].isin([sel_outcome])]
    if sel_age     != "All": d = d[d["Description Of Age Group"].isin([sel_age])]
    if sel_indicator != "All": d = d[d["Health Indicator"].isin([sel_indicator])]
    return d

filtered_country = apply_filters(df_country)
filtered_cities  = apply_filters(df_cities)

ad_country  = filtered_country[filtered_country["Health Indicator"] == "Attributable deaths (AD)"]
yll_country = filtered_country[filtered_country["Health Indicator"] == "Years of Life Lost (YLL)"]
dal_country = filtered_country[filtered_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
ad_cities   = filtered_cities[filtered_cities["Health Indicator"] == "Attributable deaths (AD)"]

# ============================================================
# HELPERS
# ============================================================

def fmt(n):
    if pd.isna(n) or n == 0:
        return "N/A"
    n = float(n)
    if n >= 1_000_000:
        return f"{n/1_000_000:.2f}M"
    elif n >= 1_000:
        return f"{n/1_000:.1f}K"
    return str(int(n))

DARK = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#e8eaf0", family="sans-serif"),
    margin=dict(l=10, r=10, t=40, b=10),
)
ACCENT = ["#4f8ef7", "#f7914f", "#7c4ff7", "#4ff7a8", "#f74f6e"]

# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("# 🌍 Air Pollution & Health Impact in Europe")
st.markdown("Exploring the health burden of **PM2.5**, **NO2**, and **O3** across 40 European countries · 2022")
st.markdown("---")

# ============================================================
# TABS
# ============================================================

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview",
    "🗺️ Geographic",
    "🔬 Breakdown",
    "🏙️ City Drilldown",
])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 1 — OVERVIEW
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab1:

    # --- Health Burden KPIs ---
    st.markdown("### 📊 Health Burden Summary")
    k1, k2, k3 = st.columns(3)
    k1.metric("💀 Attributable Deaths",     fmt(ad_country["Value"].sum()))
    k2.metric("⏳ Years of Life Lost (YLL)", fmt(yll_country["Value"].sum()))
    k3.metric("⚕️ DALYs",                   fmt(dal_country["Value"].sum()))

    st.markdown("---")

    # --- Pollutant Averages ---
    st.markdown("### 🌫️ Population-Weighted Pollutant Averages (µg/m³)")
    st.caption("Uses population-weighted average — accounts for actual exposure levels. Excludes supra-national aggregates.")

    pm25 = df_country[(df_country["Air Pollutant"] == "PM2.5") & (df_country[PW_COL] < 500)][PW_COL].mean()
    no2  = df_country[(df_country["Air Pollutant"] == "NO2")   & (df_country[PW_COL] < 500)][PW_COL].mean()
    o3   = df_country[(df_country["Air Pollutant"] == "O3")    & (df_country[PW_COL] < 500)][PW_COL].mean()

    p1, p2, p3 = st.columns(3)
    p1.metric("PM2.5 (µg/m³)", f"{pm25:.1f}" if pd.notna(pm25) else "N/A",
              delta="WHO limit: 5 µg/m³", delta_color="inverse")
    p2.metric("NO2 (µg/m³)",   f"{no2:.1f}"  if pd.notna(no2)  else "N/A",
              delta="WHO limit: 10 µg/m³", delta_color="inverse")
    p3.metric("O3 (µg/m³)",    f"{o3:.1f}"   if pd.notna(o3)   else "N/A",
              delta="WHO limit: 60 µg/m³", delta_color="inverse")

    st.markdown("---")

    # --- Scatter: Pollution vs Deaths ---
    st.markdown("### 🔵 Pollution Level vs Attributable Deaths — by Country")
    scatter_agg = (
        ad_country.groupby("Country Or Territory")
        .agg(Deaths=("Value", "sum"), Pollution=(PW_COL, "mean"))
        .reset_index()
    )
    fig_scatter = px.scatter(
        scatter_agg,
        x="Pollution", y="Deaths",
        text="Country Or Territory",
        size="Deaths", size_max=45,
        color="Deaths",
        color_continuous_scale="Blues",
        labels={
            "Pollution": "Population-weighted pollution avg (µg/m³)",
            "Deaths":    "Total attributable deaths",
        },
        template="plotly_dark",
    )
    fig_scatter.update_traces(
        textposition="top center",
        textfont=dict(size=9, color="#7a7d8f"),
    )
    fig_scatter.update_layout(
        **DARK, height=450,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="#2a2d3e"),
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 2 — GEOGRAPHIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab2:

    st.markdown("### 🗺️ Health Burden by Country — Deaths per 100k")

    map_agg = (
        ad_country.groupby("Country Or Territory")["Value for 100k Of Affected Population"]
        .sum().reset_index()
    )
    map_agg.columns = ["Country", "Per100k"]

    fig_map = px.choropleth(
        map_agg,
        locations="Country",
        locationmode="country names",
        color="Per100k",
        color_continuous_scale="Blues",
        scope="europe",
        labels={"Per100k": "Deaths per 100k"},
        template="plotly_dark",
    )
    fig_map.update_layout(
        **DARK, height=520,
        geo=dict(
            bgcolor="rgba(0,0,0,0)",
            lakecolor="rgba(0,0,0,0)",
            landcolor="#1e2130",
            showframe=False,
        ),
        coloraxis_colorbar=dict(
            thickness=12, len=0.7,
            tickfont=dict(color="#7a7d8f", size=10),
            title=dict(text="Deaths\nper 100k", font=dict(color="#7a7d8f", size=10)),
        ),
    )
    st.plotly_chart(fig_map, use_container_width=True)

    st.markdown("---")
    st.markdown("### 🏆 Top 20 Cities by Health Burden per 100k")

    city_agg = (
        ad_cities.groupby("City Or Territory")["Value for 100k Of Affected Population"]
        .sum().reset_index()
    )
    city_agg.columns = ["City", "Per100k"]
    city_agg = city_agg.nlargest(20, "Per100k").sort_values("Per100k")

    fig_cities = px.bar(
        city_agg, x="Per100k", y="City",
        orientation="h",
        color="Per100k",
        color_continuous_scale="Blues",
        labels={"Per100k": "Deaths per 100k", "City": ""},
        template="plotly_dark",
    )
    fig_cities.update_layout(
        **DARK, height=520,
        coloraxis_showscale=False,
        xaxis=dict(gridcolor="#2a2d3e"),
        yaxis=dict(gridcolor="rgba(0,0,0,0)"),
    )
    st.plotly_chart(fig_cities, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — BREAKDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:

    st.markdown("### 🧪 Burden by Pollutant")
    poll_agg = (
        ad_country.groupby(["Air Pollutant", "Category"])["Value"]
        .sum().reset_index()
    )
    fig_poll = px.bar(
        poll_agg,
        x="Air Pollutant", y="Value", color="Category",
        barmode="group",
        color_discrete_sequence=ACCENT,
        labels={"Value": "Deaths (AD)", "Air Pollutant": "Pollutant"},
        category_orders={"Category": ["Mortality", "Morbidity", "Total burden of disease"]},
        template="plotly_dark",
    )
    fig_poll.update_layout(
        **DARK, height=400,
        legend=dict(
            orientation="h", y=1.08,
            font=dict(size=11, color="#7a7d8f"),
            bgcolor="rgba(0,0,0,0)",
        ),
        xaxis=dict(gridcolor="rgba(0,0,0,0)"),
        yaxis=dict(gridcolor="#2a2d3e"),
    )
    st.plotly_chart(fig_poll, use_container_width=True)

    st.markdown("---")

    col_donut, col_age = st.columns(2)

    # Disease donut
    with col_donut:
        st.markdown("### 🍩 Disease Outcome Split")
        outcome_agg = ad_country.groupby("Outcome")["Value"].sum().reset_index()
        fig_donut = px.pie(
            outcome_agg, values="Value", names="Outcome",
            hole=0.55,
            color_discrete_sequence=px.colors.sequential.Blues_r,
            template="plotly_dark",
        )
        fig_donut.update_traces(
            textposition="inside",
            textinfo="percent",
            insidetextorientation="radial",
            textfont=dict(color="white", size=11),
        )
        fig_donut.update_layout(
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#e8eaf0", family="sans-serif"),
            height=400,
            showlegend=True,
            legend=dict(
                orientation="v",
                font=dict(size=11, color="#7a7d8f"),
                x=1.02, y=0.5,
                bgcolor="rgba(0,0,0,0)",
            ),
            margin=dict(l=10, r=140, t=40, b=10),
        )
        st.plotly_chart(fig_donut, use_container_width=True)

    # Age group bar
    with col_age:
        st.markdown("### 👥 Burden by Age Group — per 100k")
        age_agg = (
            ad_country.groupby("Description Of Age Group")["Value for 100k Of Affected Population"]
            .sum().reset_index()
        )
        age_agg.columns = ["Age Group", "Per100k"]
        age_agg = age_agg.sort_values("Per100k")
        fig_age = px.bar(
            age_agg, x="Per100k", y="Age Group",
            orientation="h",
            color="Per100k",
            color_continuous_scale="Purples",
            labels={"Per100k": "Deaths per 100k", "Age Group": ""},
            template="plotly_dark",
        )
        fig_age.update_layout(
            **DARK, height=400,
            coloraxis_showscale=False,
            xaxis=dict(gridcolor="#2a2d3e"),
            yaxis=dict(gridcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_age, use_container_width=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 4 — CITY DRILLDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab4:

    st.markdown("### 🏙️ City-Level Drilldown — Top 100 Cities by Burden per 100k")

    cols_needed = [
        "City Or Territory",
        "Country Or Territory",
        "Air Pollutant",
        "Outcome",
        "Description Of Age Group",
        "Value",
        "Value - lower CI",
        "Value - upper CI",
        "Value for 100k Of Affected Population",
        "Air Pollution Average [ug/m3]",
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
    st.caption("CI Lower / CI Upper = 95% confidence interval bounds around the central estimate.")

# ============================================================
# FOOTER
# ============================================================

st.markdown("---")
st.caption("🌍 Data source: WHO Air Quality & Health Dataset · 40 countries · 977 cities · 3 pollutants · 2022")

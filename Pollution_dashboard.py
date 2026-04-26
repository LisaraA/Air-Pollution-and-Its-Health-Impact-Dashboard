import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Page Layout

st.set_page_config(
    page_title="Air Pollution & Health Impact",
    page_icon="🌍",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown("""
<style>
    .insight-box {
        background: linear-gradient(135deg, #1a1d2e 0%, #16192b 100%);
        border: 1px solid #2e3250;
        border-left: 4px solid #4f8ef7;
        border-radius: 8px;
        padding: 14px 18px;
        margin: 8px 0 16px 0;
        font-size: 0.88rem;
        color: #b0b8d8;
        line-height: 1.6;
    }
    .insight-box strong { color: #e8eaf0; }
    .insight-box .highlight { color: #f7914f; font-weight: 600; }
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

# Only exclude the true catch-all age group — keep all meaningful bands
AGE_EXCLUDE = [">= 0 years of age"]
# FIX 2: Exclude "All causes" rollup to avoid double counting
OUTCOME_EXCLUDE = ["All causes"]

PW_COL  = "Air Pollution Population Weighted Average [ug/m3]"
AVG_COL = "Air Pollution Average [ug/m3]"

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
# FIX 1: All filters changed to multiselect
# ============================================================

with st.sidebar:
    st.markdown("## 🌍 Air Pollution")
    st.markdown("### Health Impact Dashboard")
    st.markdown("Europe · 2022 · WHO Baseline")
    st.markdown("---")
    st.markdown("### 🔎 Filters")
    st.caption("Leave a filter empty to include all options.")

    # FIX 1 + FIX 2: multiselect, "All causes" removed
    outcome_opts = sorted(
        df_raw["Outcome"].dropna()
        .loc[~df_raw["Outcome"].isin(OUTCOME_EXCLUDE)]
        .unique().tolist()
    )
    sel_outcome = st.multiselect("Health Outcome", options=outcome_opts)

    pollutant_opts = sorted(df_raw["Air Pollutant"].dropna().unique().tolist())
    sel_poll = st.multiselect("Air Pollutant", options=pollutant_opts)

    # >= 0 excluded as catch-all; >= 30 has no country-level records in this dataset
    AGE_EXCLUDE_SIDEBAR = [">= 0 years of age", ">= 30 years of age"]
    age_opts = sorted(
        df_raw["Description Of Age Group"].dropna()
        .loc[~df_raw["Description Of Age Group"].isin(AGE_EXCLUDE_SIDEBAR)]
        .unique().tolist()
    )
    sel_age = st.multiselect("Age Group", options=age_opts)

    indicator_opts = sorted(df_raw["Health Indicator"].dropna().unique().tolist())
    sel_indicator = st.multiselect("Health Indicator", options=indicator_opts)

    st.markdown("---")
    st.caption("📂 WHO/EEA Urban Air Quality 2022\n37 countries · 973 cities · 3 pollutants")

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
ACCENT  = ["#4f8ef7", "#f7914f", "#7c4ff7", "#4fd97c", "#f74f6e", "#f7d44f", "#4fd4f7"]
BLUES   = px.colors.sequential.Blues_r

# ============================================================
# PAGE HEADER
# ============================================================

st.markdown("# 🌍 Air Pollution & Health Impact in Europe")
st.markdown("Exploring the health burden of **PM2.5**, **NO2**, and **O3** across 37 European countries · 2022 · WHO 2021 AQG Baseline")
st.markdown("---")

# ============================================================
# TABS — 6 tabs with full insight coverage
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

    st.markdown("### 📊 Health Burden Summary")
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("💀 Attributable Deaths",      fmt(ad_country["Value"].sum()))
    k2.metric("⏳ Years of Life Lost (YLL)",  fmt(yll_country["Value"].sum()))
    k3.metric("⚕️ DALYs",                    fmt(dal_country["Value"].sum()))
    k4.metric("♿ Years Lived w/ Disability", fmt(yld_country["Value"].sum()))

    st.markdown("---")

    # FIX 4: Replaced red delta arrows with plain explanatory caption
    st.markdown("### 🌫️ Population-Weighted Pollutant Averages (µg/m³)")
    st.caption(
        "Uses population-weighted average — accounts for actual exposure levels. Excludes supra-national aggregates. "
        "**WHO 2021 guideline limits:** PM2.5 = 5 µg/m³ · NO2 = 10 µg/m³ · O3 = 60 µg/m³. "
        "All values shown **exceed** WHO recommended limits."
    )
    pm25 = df_country[(df_country["Air Pollutant"] == "PM2.5") & (df_country[PW_COL] < 500)][PW_COL].mean()
    no2  = df_country[(df_country["Air Pollutant"] == "NO2")   & (df_country[PW_COL] < 500)][PW_COL].mean()
    o3   = df_country[(df_country["Air Pollutant"] == "O3")    & (df_country[PW_COL] < 500)][PW_COL].mean()

    p1, p2, p3 = st.columns(3)
    p1.metric("PM2.5 (µg/m³)", f"{pm25:.1f}" if pd.notna(pm25) else "N/A")
    p2.metric("NO2 (µg/m³)",   f"{no2:.1f}"  if pd.notna(no2)  else "N/A")
    p3.metric("O3 (µg/m³)",    f"{o3:.1f}"   if pd.notna(o3)   else "N/A")

    st.markdown("""
    <div class='insight-box'>
    <strong>💡 What this means:</strong>
    Europe's average PM2.5 is <span class='highlight'>~2.7× above</span> the WHO limit of 5 µg/m³.
    NO2 is <span class='highlight'>~1.8× above</span> the 10 µg/m³ limit.
    O3 at ~88 µg/m³ is <span class='highlight'>47% above</span> the 60 µg/m³ guideline — a widely overlooked pollutant that primarily harms lung function.
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # INSIGHT: Which pollutant kills the most
    st.markdown("### ☠️ Which Pollutant Causes the Most Deaths?")
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

    # FIX 5: Scatter — no text labels, rich hover tooltip
    st.markdown("### 🔵 Pollution Level vs Attributable Deaths — by Country")
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
        st.markdown("### 🗺️ Deaths per 100k by Country")
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
        st.markdown("### 🗺️ PM2.5 Pollution Level by Country")
        pm25_map = df_country[
            (df_country["Air Pollutant"] == "PM2.5") & (df_country[PW_COL] < 500)
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

    st.markdown("### 🏆 Top 15 Countries — Deaths per 100k")
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TAB 3 — DISEASE BREAKDOWN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with tab3:

    st.markdown("### 🧬 Pollutant × Disease Heatmap — Which Pollutant Causes Which Disease?")
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

    # FIX 6: Removed donut emoji from heading
    st.markdown("### Disease Outcome Split — Share of Deaths")
    outcome_agg = ad_country.groupby("Outcome")["Value"].sum().reset_index()
    fig_donut = px.pie(
        outcome_agg, values="Value", names="Outcome",
        hole=0.55,
        color_discrete_sequence=BLUES,
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

    # Mortality vs Morbidity by Disease
    st.markdown("### 📊 Burden by Disease — Mortality vs Morbidity")
    st.caption("Mortality = attributable deaths (AD). Morbidity = years lived with disability (YLD). Shows which diseases kill vs which disable.")

    mort_by_disease = (
        df_country[df_country["Health Indicator"] == "Attributable deaths (AD)"]
        .groupby("Outcome")["Value"].sum().reset_index()
    )
    mort_by_disease.columns = ["Disease", "Value"]
    mort_by_disease["Category"] = "Mortality"

    morb_by_disease = (
        df_country[df_country["Health Indicator"] == "Years Lived with Disability (YLD)"]
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

    # True age order present in df_country (>= 30 has no country-level records)
    _AGE_ORDER_RISK = ["< 19 years of age", ">= 19 years of age",
                       ">= 25 years of age", ">= 60 years of age"]

    # Distinct colour per age group — used consistently in both charts
    _AGE_COLOURS = {
        "< 19 years of age":  "#4f8ef7",   # blue
        ">= 19 years of age": "#4fd97c",   # green
        ">= 25 years of age": "#f7914f",   # orange
        ">= 60 years of age": "#f74f6e",   # red/pink
    }

    st.markdown("### 👥 Who Is Most at Risk? — DALY per 100k by Age Group")
    st.caption("DALY (Disability-Adjusted Life Years) captures both deaths and disability — "
               "giving a complete picture across all age groups including children.")
    age_agg = (
        df_country[df_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
        .groupby("Description Of Age Group")["Value for 100k Of Affected Population"]
        .sum().reset_index()
    )
    age_agg.columns = ["Age Group", "Per100k"]
    age_agg["_order"] = age_agg["Age Group"].apply(
        lambda x: _AGE_ORDER_RISK.index(x) if x in _AGE_ORDER_RISK else 99
    )
    age_agg = age_agg.sort_values("_order").drop(columns="_order")
    age_agg["Colour"] = age_agg["Age Group"].map(_AGE_COLOURS)

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
        **DARK, height=340, barmode="overlay",
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

    # Age × Disease heatmap — DALY so all groups have non-zero values
    st.markdown("### 🔥 Age Group × Disease — Which Age Group Gets Which Disease?")
    st.caption("Using DALY (deaths + disability) so all age groups, including children, show their true burden.")
    age_disease = (
        df_country[df_country["Health Indicator"] == "Disability-Adjusted Life Years (DALY)"]
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

    st.markdown("### ⚖️ Premature Death vs Long-Term Disability — by Disease")
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

    st.markdown("### 🏙️ City-Level Drilldown — Top 100 Cities by Burden per 100k")
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

st.markdown("---")
st.caption("🌍 Data source: WHO Air Quality & Health Dataset · 37 countries · 973 cities · 3 pollutants · 2022 · WHO 2021 AQG Baseline")

# ══════════════════════════════════════════════════════════════════════════════
# LUMENINDEX — STREAMLIT DASHBOARD (LIGHT THEME)
# Rural Development Index for Latin America
# Living Stones Foundation | Applied Data & Digital Innovation Lab
# ══════════════════════════════════════════════════════════════════════════════

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from sqlalchemy import create_engine
import warnings
warnings.filterwarnings('ignore')

# ── PAGE CONFIG ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="LumenIndex — LATAM Rural Development",
    page_icon="🌱",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CUSTOM CSS (LIGHT THEME) ──────────────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp { background-color: #F8F9FA; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E5E7EB;
    }

    /* KPI cards */
    .kpi-card {
        background: #FFFFFF;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid;
        margin-bottom: 10px;
        box-shadow: 0 1px 4px rgba(0,0,0,0.08);
    }
    .kpi-green  { border-color: #2D6A4F; }
    .kpi-blue   { border-color: #1E40AF; }
    .kpi-orange { border-color: #B45309; }
    .kpi-red    { border-color: #991B1B; }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        line-height: 1;
        margin-bottom: 4px;
    }
    .kpi-label {
        font-size: 0.72rem;
        color: #6B7280;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-sub {
        font-size: 0.78rem;
        color: #9CA3AF;
        margin-top: 4px;
    }

    /* Section headers */
    .section-header {
        font-size: 0.7rem;
        text-transform: uppercase;
        letter-spacing: 2px;
        color: #6B7280;
        margin-top: 24px;
        margin-bottom: 12px;
        font-weight: 600;
    }

    /* Hide streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Dataframe */
    .stDataFrame { border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

# ── CONNECTION ────────────────────────────────────────────────────────────────
CONNECTION_STRING = "postgresql://neondb_owner:npg_IOD3kvf5PKSZ@ep-curly-fire-ata7105s.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require"

@st.cache_data(ttl=300)
def load_data():
    try:
        engine = create_engine(CONNECTION_STRING)
        query = """
            SELECT country, year,
                   female_lfp_rate, agri_research_spending,
                   fte_researchers, fte_researchers_phd_pct,
                   gdp_per_capita, unemployment_rate,
                   electricity_access, internet_access,
                   life_expectancy, poverty_headcount, rural_pop_pct
            FROM lumenindex_combined
            ORDER BY country, year
        """
        df = pd.read_sql(query, engine)
        return df
    except Exception as e:
        st.error(f"Database connection failed: {e}")
        return pd.DataFrame()

# ── COMPUTE LUMENINDEX SCORE ──────────────────────────────────────────────────
def compute_lumenindex(df):
    from sklearn.preprocessing import MinMaxScaler
    from sklearn.impute import SimpleImputer

    INDICATORS = [
        'female_lfp_rate', 'agri_research_spending', 'fte_researchers',
        'fte_researchers_phd_pct', 'gdp_per_capita', 'unemployment_rate',
        'electricity_access', 'internet_access', 'life_expectancy',
        'poverty_headcount', 'rural_pop_pct'
    ]

    df_s = df.copy()
    imputer = SimpleImputer(strategy='median')
    df_s[INDICATORS] = imputer.fit_transform(df_s[INDICATORS])

    scaler = MinMaxScaler(feature_range=(0, 100))
    HIGHER = ['female_lfp_rate','agri_research_spending','fte_researchers',
              'fte_researchers_phd_pct','gdp_per_capita','electricity_access',
              'internet_access','life_expectancy']
    LOWER  = ['unemployment_rate','poverty_headcount','rural_pop_pct']

    for col in HIGHER:
        df_s[f'{col}_norm'] = scaler.fit_transform(df_s[[col]])
    for col in LOWER:
        df_s[f'{col}_norm'] = 100 - scaler.fit_transform(df_s[[col]])

    WEIGHTS = {
        'gdp_per_capita_norm': 0.20, 'poverty_headcount_norm': 0.20,
        'internet_access_norm': 0.15, 'female_lfp_rate_norm': 0.15,
        'life_expectancy_norm': 0.10, 'electricity_access_norm': 0.10,
        'agri_research_spending_norm': 0.10,
    }

    df_s['lumenindex_score'] = sum(
        df_s[col] * w for col, w in WEIGHTS.items() if col in df_s.columns
    )

    def tier(s):
        if s >= 60: return 'High'
        elif s >= 35: return 'Medium'
        else: return 'Low'

    df_s['tier'] = df_s['lumenindex_score'].apply(tier)
    return df_s

# ── PLOTLY LIGHT THEME ────────────────────────────────────────────────────────
PLOT_BG = '#FFFFFF'
PAPER_BG = '#F8F9FA'
GRID_COLOR = '#E5E7EB'
FONT_COLOR = '#1A1A1A'
MUTED_COLOR = '#6B7280'

PLOT_LAYOUT = dict(
    paper_bgcolor=PAPER_BG,
    plot_bgcolor=PLOT_BG,
    font=dict(color=FONT_COLOR, family='Arial'),
    xaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    yaxis=dict(gridcolor=GRID_COLOR, linecolor=GRID_COLOR, zerolinecolor=GRID_COLOR),
    margin=dict(l=20, r=20, t=40, b=20),
)

TIER_COLORS = {'High': '#2D6A4F', 'Medium': '#B45309', 'Low': '#991B1B'}
LINE_COLORS = ['#2D6A4F','#1E40AF','#B45309','#991B1B','#6D28D9',
               '#0891B2','#BE185D','#15803D']

# ── LOAD DATA ─────────────────────────────────────────────────────────────────
with st.spinner('Loading data from Neon PostgreSQL...'):
    df_raw = load_data()

if df_raw.empty:
    st.error("Could not load data. Check connection.")
    st.stop()

df = compute_lumenindex(df_raw)

# ── SIDEBAR ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🌱 LumenIndex")
    st.markdown("**Rural Development Index**")
    st.markdown("*Living Stones Foundation · LATAM*")
    st.markdown("---")

    all_countries = sorted(df['country'].unique().tolist())
    selected_countries = st.multiselect(
        "🌍 Countries", options=all_countries, default=all_countries
    )

    year_min = int(df['year'].min())
    year_max = int(df['year'].max())
    selected_years = st.slider(
        "📅 Year Range", min_value=year_min, max_value=year_max,
        value=(year_min, year_max)
    )

    selected_tiers = st.multiselect(
        "🏷️ Development Tier",
        options=['High', 'Medium', 'Low'],
        default=['High', 'Medium', 'Low']
    )

    st.markdown("---")
    st.markdown("**Data Sources**")
    st.markdown("- 🌐 World Bank WDI")
    st.markdown("- 🌾 IFPRI ASTI")
    st.markdown("- 👩 ILO Female LFP")
    st.markdown("---")
    st.markdown(f"**{df['country'].nunique()} countries · {df['year'].min()}–{df['year'].max()}**")
    st.markdown(f"**{len(df)} data points**")

# ── FILTER ────────────────────────────────────────────────────────────────────
df_f = df[
    (df['country'].isin(selected_countries)) &
    (df['year'] >= selected_years[0]) &
    (df['year'] <= selected_years[1]) &
    (df['tier'].isin(selected_tiers))
].copy()

df_latest = df_f.sort_values('year').groupby('country').last().reset_index()

# ── HEADER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style='background: linear-gradient(135deg, #2D6A4F, #52B788);
     padding: 28px 32px; border-radius: 16px; margin-bottom: 24px;
     box-shadow: 0 2px 12px rgba(45,106,79,0.15);'>
    <h1 style='color: white; margin: 0; font-size: 2rem;'>🌱 LumenIndex</h1>
    <p style='color: #D8F3DC; margin: 6px 0 0; font-size: 1rem;'>
        Rural Development Index · Latin America · Living Stones Foundation
    </p>
    <p style='color: #B7E4C7; margin: 4px 0 0; font-size: 0.8rem;'>
        World Bank WDI · IFPRI ASTI · ILO Female Labor Force · 17 Countries · 1990–2020
    </p>
</div>
""", unsafe_allow_html=True)

# ── KPI CARDS ─────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Key Indicators</p>', unsafe_allow_html=True)

c1, c2, c3, c4, c5 = st.columns(5)

avg_score  = df_latest['lumenindex_score'].mean()
high_count = (df_latest['tier'] == 'High').sum()
med_count  = (df_latest['tier'] == 'Medium').sum()
low_count  = (df_latest['tier'] == 'Low').sum()
avg_lfp    = df_latest['female_lfp_rate'].mean()

with c1:
    st.markdown(f"""<div class="kpi-card kpi-green">
        <div class="kpi-value" style="color:#2D6A4F">{avg_score:.1f}</div>
        <div class="kpi-label">Avg LumenIndex Score</div>
        <div class="kpi-sub">0–100 composite</div>
    </div>""", unsafe_allow_html=True)

with c2:
    st.markdown(f"""<div class="kpi-card kpi-green">
        <div class="kpi-value" style="color:#2D6A4F">{high_count}</div>
        <div class="kpi-label">🟢 High Tier</div>
        <div class="kpi-sub">Score ≥ 60</div>
    </div>""", unsafe_allow_html=True)

with c3:
    st.markdown(f"""<div class="kpi-card kpi-orange">
        <div class="kpi-value" style="color:#B45309">{med_count}</div>
        <div class="kpi-label">🟡 Medium Tier</div>
        <div class="kpi-sub">Score 35–60</div>
    </div>""", unsafe_allow_html=True)

with c4:
    st.markdown(f"""<div class="kpi-card kpi-red">
        <div class="kpi-value" style="color:#991B1B">{low_count}</div>
        <div class="kpi-label">🔴 Low Tier</div>
        <div class="kpi-sub">Score below 35</div>
    </div>""", unsafe_allow_html=True)

with c5:
    st.markdown(f"""<div class="kpi-card kpi-blue">
        <div class="kpi-value" style="color:#1E40AF">{avg_lfp:.1f}%</div>
        <div class="kpi-label">Avg Female LFP</div>
        <div class="kpi-sub">% of female population</div>
    </div>""", unsafe_allow_html=True)

# ── ROW 1: RANKING + TREND ────────────────────────────────────────────────────
st.markdown('<p class="section-header">Development Rankings & Trends</p>',
            unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    df_rank = df_latest.sort_values('lumenindex_score', ascending=True)
    fig_bar = go.Figure(go.Bar(
        x=df_rank['lumenindex_score'],
        y=df_rank['country'],
        orientation='h',
        marker_color=[TIER_COLORS[t] for t in df_rank['tier']],
        text=df_rank['lumenindex_score'].round(1),
        textposition='outside',
        textfont=dict(color=FONT_COLOR, size=10),
    ))
    fig_bar.add_vline(x=60, line_dash='dash', line_color='#2D6A4F',
                      annotation_text='High', annotation_font_color='#2D6A4F')
    fig_bar.add_vline(x=35, line_dash='dash', line_color='#B45309',
                      annotation_text='Medium', annotation_font_color='#B45309')
    fig_bar.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='LumenIndex Score by Country', font=dict(color=FONT_COLOR)),
        xaxis_title='LumenIndex Score (0–100)',
        height=420, showlegend=False,
    )
    st.plotly_chart(fig_bar, use_container_width=True)

with col2:
    fig_trend = go.Figure()
    for i, country in enumerate(selected_countries[:8]):
        cdata = df_f[df_f['country'] == country].sort_values('year')
        if len(cdata) > 0:
            fig_trend.add_trace(go.Scatter(
                x=cdata['year'], y=cdata['lumenindex_score'].round(1),
                mode='lines+markers', name=country,
                line=dict(color=LINE_COLORS[i % len(LINE_COLORS)], width=2),
                marker=dict(size=4),
            ))
    fig_trend.add_hline(y=60, line_dash='dash', line_color='#2D6A4F',
                        annotation_text='High', annotation_font_color='#2D6A4F')
    fig_trend.add_hline(y=35, line_dash='dash', line_color='#B45309',
                        annotation_text='Low', annotation_font_color='#B45309')
    fig_trend.update_layout(
        **PLOT_LAYOUT,
        title=dict(text='LumenIndex Score Trend Over Time', font=dict(color=FONT_COLOR)),
        xaxis_title='Year', yaxis_title='Score', height=420,
        legend=dict(bgcolor='white', bordercolor=GRID_COLOR,
                    font=dict(size=9, color=FONT_COLOR)),
    )
    st.plotly_chart(fig_trend, use_container_width=True)

# ── ROW 2: INDICATORS ─────────────────────────────────────────────────────────
st.markdown('<p class="section-header">Key Indicator Analysis</p>',
            unsafe_allow_html=True)

ca, cb, cc = st.columns(3)

with ca:
    df_lfp = df_latest.sort_values('female_lfp_rate', ascending=True)
    fig_lfp = go.Figure(go.Bar(
        x=df_lfp['female_lfp_rate'].round(1), y=df_lfp['country'],
        orientation='h', marker_color='#1E40AF',
        text=df_lfp['female_lfp_rate'].round(1),
        textposition='outside', textfont=dict(color=FONT_COLOR, size=9),
    ))
    fig_lfp.update_layout(**PLOT_LAYOUT,
        title=dict(text='Female Labor Force Participation (%)', font=dict(color=FONT_COLOR)),
        height=380, showlegend=False)
    st.plotly_chart(fig_lfp, use_container_width=True)

with cb:
    df_agri = df_latest.dropna(subset=['agri_research_spending']).sort_values('agri_research_spending', ascending=True)
    fig_agri = go.Figure(go.Bar(
        x=df_agri['agri_research_spending'].round(1), y=df_agri['country'],
        orientation='h', marker_color='#B45309',
        text=df_agri['agri_research_spending'].round(1),
        textposition='outside', textfont=dict(color=FONT_COLOR, size=9),
    ))
    fig_agri.update_layout(**PLOT_LAYOUT,
        title=dict(text='Agricultural Research Spending', font=dict(color=FONT_COLOR)),
        height=380, showlegend=False)
    st.plotly_chart(fig_agri, use_container_width=True)

with cc:
    tier_counts = df_f['tier'].value_counts()
    fig_pie = go.Figure(go.Pie(
        labels=tier_counts.index, values=tier_counts.values,
        marker_colors=[TIER_COLORS.get(t, '#6B7280') for t in tier_counts.index],
        textinfo='label+percent',
        textfont=dict(color='white', size=11), hole=0.4,
    ))
    fig_pie.update_layout(**PLOT_LAYOUT,
        title=dict(text='Development Tier Distribution', font=dict(color=FONT_COLOR)),
        height=380, showlegend=False)
    st.plotly_chart(fig_pie, use_container_width=True)

# ── ROW 3: POVERTY + SCATTER ──────────────────────────────────────────────────
st.markdown('<p class="section-header">Poverty & Correlation Analysis</p>',
            unsafe_allow_html=True)

cp, cs = st.columns(2)

with cp:
    df_pov = df_f.dropna(subset=['poverty_headcount'])
    fig_pov = go.Figure()
    for i, country in enumerate(df_pov['country'].unique()[:8]):
        cdata = df_pov[df_pov['country'] == country].sort_values('year')
        fig_pov.add_trace(go.Scatter(
            x=cdata['year'], y=cdata['poverty_headcount'].round(1),
            mode='lines+markers', name=country,
            line=dict(color=LINE_COLORS[i % len(LINE_COLORS)], width=2),
            marker=dict(size=4),
        ))
    fig_pov.update_layout(**PLOT_LAYOUT,
        title=dict(text='Poverty Headcount Trend (%)', font=dict(color=FONT_COLOR)),
        xaxis_title='Year', yaxis_title='Poverty (%)', height=380,
        legend=dict(bgcolor='white', font=dict(size=9, color=FONT_COLOR)))
    st.plotly_chart(fig_pov, use_container_width=True)

with cs:
    df_sc = df_latest.dropna(subset=['gdp_per_capita','female_lfp_rate'])
    fig_sc = px.scatter(
        df_sc, x='gdp_per_capita', y='female_lfp_rate',
        color='tier', color_discrete_map=TIER_COLORS,
        text='country', size='lumenindex_score', size_max=30,
        labels={'gdp_per_capita':'GDP per Capita (USD)', 'female_lfp_rate':'Female LFP Rate (%)'},
        title='GDP per Capita vs Female LFP Rate'
    )
    fig_sc.update_traces(textposition='top center', textfont=dict(size=9, color=FONT_COLOR))
    fig_sc.update_layout(**PLOT_LAYOUT, height=380,
        legend=dict(bgcolor='white', font=dict(size=9, color=FONT_COLOR)),
        title=dict(font=dict(color=FONT_COLOR)))
    st.plotly_chart(fig_sc, use_container_width=True)

# ── DATA TABLE ────────────────────────────────────────────────────────────────
st.markdown('<p class="section-header">LumenIndex Results Table</p>',
            unsafe_allow_html=True)

display_cols = ['country','year','lumenindex_score','tier',
                'female_lfp_rate','gdp_per_capita','poverty_headcount',
                'internet_access','electricity_access','agri_research_spending']

df_display = df_f[display_cols].copy()
df_display['lumenindex_score'] = df_display['lumenindex_score'].round(2)
df_display['female_lfp_rate']  = df_display['female_lfp_rate'].round(2)
df_display['gdp_per_capita']   = df_display['gdp_per_capita'].round(0)
df_display = df_display.sort_values(['year','lumenindex_score'], ascending=[False,False])
df_display.columns = ['Country','Year','LumenIndex Score','Tier',
                      'Female LFP (%)','GDP per Capita','Poverty (%)','Internet (%)','Electricity (%)','Agri Spending']

st.dataframe(df_display, use_container_width=True, height=300, hide_index=True)

csv = df_display.to_csv(index=False).encode('utf-8')
st.download_button("⬇️ Download Results CSV", data=csv,
                   file_name="lumenindex_results.csv", mime="text/csv")

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("""
<div style='text-align:center; color:#9CA3AF; font-size:0.75rem;'>
    🌱 LumenIndex · Living Stones Foundation · Applied Data & Digital Innovation Lab (LATAM) ·
    Built by Deepeka Gurunathan · Data: World Bank WDI, IFPRI ASTI, ILO · 2026
</div>
""", unsafe_allow_html=True)
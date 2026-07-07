
# 🌱 LumenIndex — Rural Development Index for Latin America

> Built for **Living Stones Foundation** | Applied Data & Digital Innovation Lab (LATAM)

An open-source data analysis platform that estimates economic and social development levels across Latin American countries using World Bank open data, satellite-derived nighttime light intensity, and infrastructure indicators — transforming scattered public data into actionable, comparable development insights.

---

## 📊 Dashboards

| Dashboard | Tool | Dataset | Link |
|---|---|---|---|
| Chile Development Indicators | Excel | World Bank WDI · Chile · 2000–2023 | [chile_lumenindex.xlsx](chile_lumenindex.xlsx) |
| LATAM Female Labor Force Participation | Tableau | World Bank WDI · 18 LATAM countries · 1990–2025 | [View on Tableau Public →](https://public.tableau.com/app/profile/deepeka.gurunathan/viz/LATAMLaborForceDashboard/Dashboard1?publish=yes) |

![Dashboard Preview](lumenindex_dashboard.png)
---

## 🗂️ Data Sources

| Dataset | Source | Coverage |
|---|---|---|
| World Development Indicators (WDI) | [World Bank](https://data.worldbank.org) | Chile · 2000–2023 |
| Female Labor Force Participation | [World Bank WDI](https://data.worldbank.org) | 18 LATAM countries · 1990–2025 |
| VIIRS Nighttime Lights | [NASA EarthData](https://earthdata.nasa.gov/topics/human-dimensions/nighttime-lights) | LATAM · Annual (Phase 3) |
| Population Grids | [WorldPop](https://www.worldpop.org/geodata/listing?id=75) | LATAM · Annual (Phase 3) |
| Administrative Boundaries | [GADM](https://gadm.org/download_country.html) | Country / Municipality level (Phase 3) |

---

## 🧹 Data Cleanup Process

### Dataset 1 — Chile World Development Indicators (World Bank WDI)

**Raw format:**
World Bank country export CSV with 4 metadata header rows, one row per indicator, year columns spanning 1960 to present, 1,400+ indicators available.

**What was cleaned:**

**1. Removed metadata rows**
Skipped the first 4 rows of the raw file (World Bank metadata/source info) to reach the actual column headers.

**2. Selected relevant indicators**
Filtered from 1,400+ indicators down to 13 development-relevant ones:
- GDP per capita (current USD)
- Unemployment rate (% of labor force, ILO estimate)
- Internet penetration (% of population)
- Mobile cellular subscriptions (per 100 people)
- Electricity access — national (% of population)
- Electricity access — rural (% of rural population)
- Rural population (% of total)
- Urban population (% of total)
- Life expectancy at birth (years)
- Poverty headcount at national poverty line (%)
- Rural drinking water access (% of rural population)
- Rural sanitation access (% of rural population)
- Clean cooking fuel access (% of population)

**3. Filtered year range**
Retained years 2000–2023 only. Years prior to 2000 had significant data gaps for rural indicators and were not relevant to the current analysis scope.

**4. Handled missing values**
World Bank uses `..` (double dot) as a placeholder for missing data. All `..` values were converted to null. No imputation was applied — missing values were kept as nulls to preserve data integrity.

Notable sparse indicator: poverty headcount data is only available for select years (2006, 2009, 2011, 2013, 2015, 2017, 2020, 2022) — not annually. Kept as is.

**5. Reshaped from wide to long format**
Raw data: one row per indicator, one column per year (wide format).
After cleanup: one row per indicator per year (long format) with columns `indicator`, `year`, `value` — making it compatible with chart and dashboard tools.

**6. Standardized field names**
Renamed verbose World Bank indicator labels to short descriptive keys:
- `GDP per capita (current US$)` → `gdp_pc`
- `Access to electricity, rural (% of rural population)` → `electricity_rural`
- `Life expectancy at birth, total (years)` → `life_exp`
- (and so on for all 13 indicators)

**7. Rounded values**
All numeric values rounded to 2 decimal places for display consistency.

**Outcome:**
Clean long-format dataset — 13 indicators × 24 years = 312 rows, zero nulls except for known sparse indicators (poverty headcount).

---

### Dataset 2 — Female Labor Force Participation (World Bank WDI, LATAM)

**Raw format:**
World Bank API export CSV, one row per country per year, 235 countries, 1990–2025, with 30+ metadata columns alongside the actual data value.

**What was cleaned:**

**1. Dropped irrelevant metadata columns**
The raw export included 30+ columns, most of which are API/structural metadata not needed for analysis. Retained only 3 columns:
- `REF_AREA_LABEL` → country name
- `TIME_PERIOD` → year
- `OBS_VALUE` → female labor force participation rate (%)

Dropped columns included: `AGE`, `AGE_LABEL`, `FREQ`, `FREQ_LABEL`, `STRUCTURE`, `STRUCTURE_ID`, `OBS_CONF`, `OBS_CONF_LABEL`, `OBS_STATUS`, `OBS_STATUS_LABEL`, `UNIT_MEASURE`, `UNIT_MEASURE_LABEL`, `DECIMALS`, `DATABASE_ID`, `DATABASE_ID_LABEL`, `COMP_BREAKDOWN_1/2/3` and their labels, `UNIT_MULT`, `UNIT_MULT_LABEL`, `UNIT_TYPE`, `UNIT_TYPE_LABEL`, `URBANISATION`, `URBANISATION_LABEL`, `SEX`, `SEX_LABEL`, `TIME_FORMAT`, `TIME_FORMAT_LABEL`

**2. Filtered to 18 LATAM countries**
From 235 countries globally, filtered to the 18 Latin American countries relevant to the project:
Argentina, Bolivia, Brazil, Chile, Colombia, Costa Rica, Dominican Republic, Ecuador, El Salvador, Guatemala, Honduras, Mexico, Nicaragua, Panama, Paraguay, Peru, Uruguay, Venezuela

**3. Verified data completeness**
Checked for nulls in `OBS_VALUE` for all 18 countries across all years — confirmed no missing values. World Bank ILO modeled estimates are already interpolated at source, so no additional imputation was needed.

**4. Created calculated fields (in Tableau)**
Two derived metrics were calculated for the growth analysis charts:
- `Growth Rate` = (value at 2025 − value at 1990) / value at 1990 × 100
- `Latest Value` = participation rate at most recent available year (2025)

**5. Renamed columns for clarity**
- `REF_AREA_LABEL` → `Country`
- `TIME_PERIOD` → `Year`
- `OBS_VALUE` → `Female LFP Rate (%)`

**Outcome:**
Clean dataset — 18 countries × 36 years = 648 rows, zero nulls, ready for Tableau and SQL ingestion.

---

## 📈 Key Indicators Analyzed

**Chile (Dashboard 1):**
GDP per capita, unemployment rate, internet penetration, mobile subscriptions, electricity access (national + rural), rural/urban population split, life expectancy, poverty headcount, rural water and sanitation access, clean cooking fuel access

**LATAM 18 countries (Dashboard 2):**
Female labor force participation rate (% of female population 15+, ILO modeled estimate)

---

## 📉 Chart Insights — LATAM Female Labor Force Dashboard

### Chart 1: Country Ranking (Average 1990–2025)
Peru and Bolivia lead at ~60% average participation while Mexico sits lowest at ~40%. A 20 percentage point spread across 18 countries shows participation varies dramatically by country independent of regional income trends.

### Chart 2: Time Series Trend (Peru, Paraguay, Brazil, Mexico, Argentina)
All five countries trend upward over 35 years. Peru shows the steepest climb peaking near 72%, with a sharp COVID-19 dip in 2020. Paraguay is the most volatile year-to-year. Mexico shows steady linear growth but never closes its gap with peers throughout the entire period.

### Chart 3: Growth Rate by Country (1990–2025)
Panama, Nicaragua, and Dominican Republic grew fastest (50–65% relative growth). Venezuela is the only country with negative growth (-23.6%), reflecting its prolonged economic crisis. Honduras, Guatemala, and Colombia show minimal growth (<10%).

### Chart 4: Growth vs. Current Level — Quadrant Analysis
Scatter plot reveals four country groups: Leaders (Bolivia), Plateaued (Chile), Catching Up (Panama, Nicaragua), Struggling (Honduras, Guatemala). Chile's placement is notable — high current level but below-average growth, suggesting plateaued progress despite strong economic indicators.

---

## 🔍 Overall Summary & Conclusion

Female labor force participation has risen across nearly all LATAM countries over 35 years but the region is far from uniform. A roughly 20-point gap persists between top and bottom performers. Economic development alone does not predict participation — Chile, the highest-GDP country in this dataset, ranks in the lower half of the region on this indicator, suggesting structural, cultural, and policy factors matter more than national wealth.

For LSF's rural development index, this validates tracking social and labor indicators alongside economic and infrastructure metrics. Next steps include adding male labor force participation for a gender gap metric, integrating rural population share, and beginning Phase 3 satellite data ingestion (VIIRS nighttime lights + WorldPop).

---

## 🗃️ Repository Structure

```
lumenindex-latam/
├── data/
│   ├── chile_development_indicators_2000_2023.csv
│   └── latam_female_labor_force_participation_1990_2025.csv
├── tableau/
│   └── lumenindex_dashboard.png
├── chile_lumenindex.xlsx
└── README.md
```

---




---

*Source: World Bank World Development Indicators · 2000–2025 · LumenIndex / Living Stones Foundation LATAM Lab*

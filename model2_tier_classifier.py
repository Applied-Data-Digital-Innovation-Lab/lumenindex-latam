# ══════════════════════════════════════════════════════════════════════════════
# LUMENINDEX — MODEL 2: DEVELOPMENT TIER RULE (DETERMINISTIC)
# The LumenIndex tier is assigned directly from the composite score:
#   High   >= 60
#   Medium >= 35
#   Low    <  35
# This script reproduces that rule so tiers are auditable. It is NOT an
# independent predictive classifier, so accuracy-style metrics are not reported.
# Data: Neon PostgreSQL — lumenindex_combined table (DATABASE_URL env var)
# ══════════════════════════════════════════════════════════════════════════════

import os
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from sklearn.impute import SimpleImputer
import psycopg2

CONNECTION_STRING = os.getenv("DATABASE_URL")
if not CONNECTION_STRING:
    raise RuntimeError("DATABASE_URL is not set. Set it as an environment variable; never hard-code database passwords.")

INDICATORS = [
    'female_lfp_rate', 'agri_research_spending', 'fte_researchers',
    'fte_researchers_phd_pct', 'gdp_per_capita', 'unemployment_rate',
    'electricity_access', 'internet_access', 'life_expectancy',
    'poverty_headcount', 'rural_pop_pct'
]

HIGHER = ['female_lfp_rate', 'agri_research_spending', 'fte_researchers',
          'fte_researchers_phd_pct', 'gdp_per_capita', 'electricity_access',
          'internet_access', 'life_expectancy']
LOWER = ['unemployment_rate', 'poverty_headcount', 'rural_pop_pct']

WEIGHTS = {
    'gdp_per_capita': 0.20, 'poverty_headcount': 0.20,
    'internet_access': 0.15, 'female_lfp_rate': 0.15,
    'life_expectancy': 0.10, 'electricity_access': 0.10,
    'agri_research_spending': 0.10,
}


def tier(score: float) -> str:
    if score >= 60:
        return 'High'
    if score >= 35:
        return 'Medium'
    return 'Low'


def main():
    conn = psycopg2.connect(CONNECTION_STRING)
    df = pd.read_sql(
        f"SELECT country, year, {', '.join(INDICATORS)} FROM lumenindex_combined ORDER BY country, year",
        conn,
    )
    conn.close()

    imputed = SimpleImputer(strategy='median').fit_transform(df[INDICATORS])
    df_imp = pd.DataFrame(imputed, columns=INDICATORS)
    scaler = MinMaxScaler(feature_range=(0, 100))
    for col in HIGHER:
        df_imp[col] = scaler.fit_transform(df_imp[[col]])
    for col in LOWER:
        df_imp[col] = 100 - scaler.fit_transform(df_imp[[col]])

    df['lumenindex_score'] = sum(df_imp[col] * w for col, w in WEIGHTS.items())
    df['tier'] = df['lumenindex_score'].apply(tier)

    latest = df.sort_values('year').groupby('country').last().reset_index()
    print(latest[['country', 'year', 'lumenindex_score', 'tier']]
          .sort_values('lumenindex_score', ascending=False)
          .to_string(index=False))
    print("\nTier counts:")
    print(latest['tier'].value_counts().to_string())
    print("\nNote: tiers come from the fixed score rule above, not from a trained classifier.")


if __name__ == '__main__':
    main()

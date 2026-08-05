# ══════════════════════════════════════════════════════════════════════════════
# LUMENINDEX — MODEL 1: POVERTY PREDICTOR (XGBoost Regressor)
# Predicts poverty headcount % using development indicators
# Data: Neon PostgreSQL — lumenindex_combined table
# ══════════════════════════════════════════════════════════════════════════════

# ── STEP 0: INSTALL REQUIRED PACKAGES ────────────────────────────────────────
# Run this in Anaconda prompt FIRST (only once):
# pip install psycopg2-binary xgboost scikit-learn matplotlib seaborn pandas numpy

# ── STEP 1: IMPORT LIBRARIES ─────────────────────────────────────────────────
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_squared_error, r2_score, mean_absolute_error
from sklearn.impute import SimpleImputer

import xgboost as xgb
import psycopg2
import warnings
warnings.filterwarnings('ignore')

print("✓ All libraries imported successfully")

# ── STEP 2: LOAD DATA FROM NEON ──────────────────────────────────────────────
print("\nConnecting to Neon PostgreSQL...")

CONNECTION_STRING = "postgresql://neondb_owner:npg_IOD3kvf5PKSZ@ep-curly-fire-ata7105s.c-9.us-east-1.aws.neon.tech/neondb?sslmode=require"

conn = psycopg2.connect(CONNECTION_STRING)

query = """
    SELECT 
        country,
        year,
        female_lfp_rate,
        agri_research_spending,
        fte_researchers,
        fte_researchers_phd_pct,
        gdp_per_capita,
        unemployment_rate,
        electricity_access,
        internet_access,
        life_expectancy,
        poverty_headcount,
        rural_pop_pct
    FROM lumenindex_combined
    WHERE poverty_headcount IS NOT NULL
    ORDER BY country, year
"""

df = pd.read_sql(query, conn)
conn.close()

print(f"✓ Data loaded: {df.shape[0]} rows, {df.shape[1]} columns")
print(f"  Countries: {df['country'].nunique()}")
print(f"  Year range: {df['year'].min()} - {df['year'].max()}")
print(f"\nData preview:")
print(df.head())

# ── STEP 3: EXPLORATORY DATA ANALYSIS (EDA) ──────────────────────────────────
print("\n── STEP 3: EDA ──")
print("\nMissing values per column:")
print(df.isnull().sum())

print("\nBasic statistics:")
print(df.describe().round(2))

# Plot 1: Poverty distribution
plt.figure(figsize=(10, 4))
plt.subplot(1, 2, 1)
df['poverty_headcount'].hist(bins=20, color='#2D6A4F', edgecolor='white')
plt.title('Poverty Headcount Distribution')
plt.xlabel('Poverty Headcount (%)')
plt.ylabel('Frequency')

# Plot 2: Poverty by country
plt.subplot(1, 2, 2)
country_avg = df.groupby('country')['poverty_headcount'].mean().sort_values(ascending=False)
country_avg.plot(kind='bar', color='#52B788', edgecolor='white')
plt.title('Average Poverty by Country')
plt.xlabel('Country')
plt.ylabel('Avg Poverty Headcount (%)')
plt.xticks(rotation=45, ha='right')
plt.tight_layout()
plt.savefig('D:/Deepeka/Work/Living Foundation/model1_eda.png', dpi=150, bbox_inches='tight')
plt.show()
print("✓ EDA plot saved")

# Plot 3: Correlation heatmap
plt.figure(figsize=(12, 8))
numeric_cols = df.select_dtypes(include=[np.number]).columns.drop(['year'])
corr = df[numeric_cols].corr()
sns.heatmap(corr, annot=True, fmt='.2f', cmap='RdYlGn',
            center=0, square=True, linewidths=0.5)
plt.title('Correlation Matrix — LumenIndex Combined Dataset')
plt.tight_layout()
plt.savefig('D:/Deepeka/Work/Living Foundation/model1_correlation.png', dpi=150, bbox_inches='tight')
plt.show()
print("✓ Correlation heatmap saved")

# ── STEP 4: FEATURE ENGINEERING ──────────────────────────────────────────────
print("\n── STEP 4: FEATURE ENGINEERING ──")

# Define features and target
FEATURES = [
    'female_lfp_rate',
    'agri_research_spending',
    'fte_researchers',
    'fte_researchers_phd_pct',
    'gdp_per_capita',
    'unemployment_rate',
    'electricity_access',
    'internet_access',
    'life_expectancy',
    'rural_pop_pct'
]

TARGET = 'poverty_headcount'

# Add year as a feature (captures time trends)
FEATURES_WITH_YEAR = FEATURES + ['year']

X = df[FEATURES_WITH_YEAR].copy()
y = df[TARGET].copy()

print(f"Features: {FEATURES_WITH_YEAR}")
print(f"Target: {TARGET}")
print(f"X shape: {X.shape}")
print(f"y shape: {y.shape}")
print(f"Target range: {y.min():.1f}% - {y.max():.1f}%")

# ── STEP 5: HANDLE MISSING VALUES ────────────────────────────────────────────
print("\n── STEP 5: HANDLING MISSING VALUES ──")

imputer = SimpleImputer(strategy='median')
X_imputed = imputer.fit_transform(X)
X_imputed = pd.DataFrame(X_imputed, columns=FEATURES_WITH_YEAR)

print(f"Missing values before imputation: {X.isnull().sum().sum()}")
print(f"Missing values after imputation: {X_imputed.isnull().sum().sum()}")

# ── STEP 6: TRAIN-TEST SPLIT ──────────────────────────────────────────────────
print("\n── STEP 6: TRAIN-TEST SPLIT ──")

X_train, X_test, y_train, y_test = train_test_split(
    X_imputed, y,
    test_size=0.2,
    random_state=42
)

print(f"Training set: {X_train.shape[0]} rows")
print(f"Test set:     {X_test.shape[0]} rows")

# ── STEP 7: TRAIN XGBOOST MODEL ──────────────────────────────────────────────
print("\n── STEP 7: TRAINING XGBOOST MODEL ──")

model = xgb.XGBRegressor(
    n_estimators=200,
    max_depth=4,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42,
    verbosity=0
)

model.fit(
    X_train, y_train,
    eval_set=[(X_test, y_test)],
    verbose=False
)

print("✓ Model trained successfully")

# ── STEP 8: EVALUATE MODEL ───────────────────────────────────────────────────
print("\n── STEP 8: MODEL EVALUATION ──")

y_pred_train = model.predict(X_train)
y_pred_test  = model.predict(X_test)

# Metrics
train_rmse = np.sqrt(mean_squared_error(y_train, y_pred_train))
test_rmse  = np.sqrt(mean_squared_error(y_test,  y_pred_test))
train_r2   = r2_score(y_train, y_pred_train)
test_r2    = r2_score(y_test,  y_pred_test)
test_mae   = mean_absolute_error(y_test, y_pred_test)

print(f"\n  {'Metric':<25} {'Train':>10} {'Test':>10}")
print(f"  {'-'*45}")
print(f"  {'RMSE':<25} {train_rmse:>10.2f} {test_rmse:>10.2f}")
print(f"  {'R² Score':<25} {train_r2:>10.4f} {test_r2:>10.4f}")
print(f"  {'MAE':<25} {'':>10} {test_mae:>10.2f}")

# Cross-validation
cv_scores = cross_val_score(model, X_imputed, y, cv=5, scoring='r2')
print(f"\n  5-Fold Cross-Validation R²: {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")

# ── STEP 9: FEATURE IMPORTANCE ───────────────────────────────────────────────
print("\n── STEP 9: FEATURE IMPORTANCE ──")

importance_df = pd.DataFrame({
    'feature': FEATURES_WITH_YEAR,
    'importance': model.feature_importances_
}).sort_values('importance', ascending=False)

print(importance_df.to_string(index=False))

plt.figure(figsize=(10, 6))
plt.barh(importance_df['feature'], importance_df['importance'],
         color='#2D6A4F', edgecolor='white')
plt.xlabel('Feature Importance Score')
plt.title('XGBoost Feature Importance — Poverty Predictor')
plt.gca().invert_yaxis()
plt.tight_layout()
plt.savefig('D:/Deepeka/Work/Living Foundation/model1_feature_importance.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("✓ Feature importance plot saved")

# ── STEP 10: ACTUAL vs PREDICTED PLOT ────────────────────────────────────────
print("\n── STEP 10: ACTUAL VS PREDICTED ──")

plt.figure(figsize=(8, 6))
plt.scatter(y_test, y_pred_test, alpha=0.6, color='#52B788', edgecolors='#2D6A4F')
min_val = min(y_test.min(), y_pred_test.min())
max_val = max(y_test.max(), y_pred_test.max())
plt.plot([min_val, max_val], [min_val, max_val], 'r--', linewidth=2, label='Perfect Prediction')
plt.xlabel('Actual Poverty Headcount (%)')
plt.ylabel('Predicted Poverty Headcount (%)')
plt.title(f'Actual vs Predicted — Test Set (R² = {test_r2:.4f})')
plt.legend()
plt.tight_layout()
plt.savefig('D:/Deepeka/Work/Living Foundation/model1_actual_vs_predicted.png',
            dpi=150, bbox_inches='tight')
plt.show()
print("✓ Actual vs Predicted plot saved")

# ── STEP 11: PREDICT MISSING POVERTY VALUES ──────────────────────────────────
print("\n── STEP 11: PREDICT MISSING POVERTY VALUES ──")

# Reload full dataset including rows where poverty is NULL
conn = psycopg2.connect(CONNECTION_STRING)
df_full = pd.read_sql(
    "SELECT * FROM lumenindex_combined ORDER BY country, year", conn
)
conn.close()

# Find rows where poverty is missing
df_missing = df_full[df_full['poverty_headcount'].isna()].copy()
print(f"Rows with missing poverty data: {len(df_missing)}")

if len(df_missing) > 0:
    X_missing = df_missing[FEATURES_WITH_YEAR].copy()
    X_missing_imputed = imputer.transform(X_missing)
    df_missing['predicted_poverty'] = model.predict(X_missing_imputed).round(2)

    print("\nSample predictions for missing poverty values:")
    print(df_missing[['country','year','predicted_poverty']].head(15).to_string(index=False))

    # Save predictions
    df_missing[['country','year','predicted_poverty']].to_csv(
        'D:/Deepeka/Work/Living Foundation/model1_poverty_predictions.csv', index=False
    )
    print("\n✓ Predictions saved to model1_poverty_predictions.csv")

# ── STEP 12: SAVE MODEL ──────────────────────────────────────────────────────
print("\n── STEP 12: SAVE MODEL ──")

model.save_model('D:/Deepeka/Work/Living Foundation/model1_poverty_predictor.json')
print("✓ Model saved to model1_poverty_predictor.json")

# ── FINAL SUMMARY ─────────────────────────────────────────────────────────────
print("\n" + "="*55)
print("MODEL 1 — SUMMARY")
print("="*55)
print(f"  Model:        XGBoost Regressor")
print(f"  Target:       Poverty Headcount (%)")
print(f"  Features:     {len(FEATURES_WITH_YEAR)}")
print(f"  Training rows:{X_train.shape[0]}")
print(f"  Test rows:    {X_test.shape[0]}")
print(f"  Test RMSE:    {test_rmse:.2f}")
print(f"  Test R²:      {test_r2:.4f}")
print(f"  Test MAE:     {test_mae:.2f}")
print(f"  CV R²:        {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
print(f"\n  Top 3 predictors:")
for _, row in importance_df.head(3).iterrows():
    print(f"    - {row['feature']}: {row['importance']:.4f}")
print("\n✓ Model 1 complete. Ready for Model 2 (Development Tier Classifier)")
#!/usr/bin/env python3
import pandas as pd
import joblib
from sklearn.preprocessing import StandardScaler

# Load dataset
df = pd.read_csv('data/processed/final_dataset.csv')
print(f"Dataset loaded: {df.shape}")

# TEMPORAL SPLIT (80% earliest data)
df_sorted = df.sort_values('days_since_start')
cutoff_date = df_sorted['days_since_start'].quantile(0.8)
train_mask = df_sorted['days_since_start'] <= cutoff_date

X_train = df.loc[train_mask].drop(['phenotype_number spike muts from Wuhan-Hu-1', 'accession'], axis=1)
y_train = df.loc[train_mask, 'phenotype_number spike muts from Wuhan-Hu-1']
X_test = df.loc[~train_mask].drop(['phenotype_number spike muts from Wuhan-Hu-1', 'accession'], axis=1)
y_test = df.loc[~train_mask, 'phenotype_number spike muts from Wuhan-Hu-1']

print(f"Train: {len(X_train)} ({train_mask.mean():.1%}) | Test: {len(X_test)}")
print("\nTrain by year:\n", df.loc[train_mask, 'year'].value_counts().sort_index())
print("\nTrain by variant:\n", df.loc[train_mask, '_source_variant'].value_counts())
print("\nTest by variant:\n", df.loc[~train_mask, '_source_variant'].value_counts())

# SCALE NUMERIC FEATURES 
numeric_cols = X_train.select_dtypes(include=['number']).columns
scaler = StandardScaler().fit(X_train[numeric_cols])

X_train_scaled = pd.DataFrame(
    scaler.transform(X_train[numeric_cols]), 
    columns=numeric_cols, 
    index=X_train.index
)
X_test_scaled = pd.DataFrame(
    scaler.transform(X_test[numeric_cols]), 
    columns=numeric_cols, 
    index=X_test.index
)

# SAVE SPLITS
joblib.dump({
    'X_train': X_train_scaled,
    'y_train': y_train,
    'X_test': X_test_scaled,
    'y_test': y_test,
    'scaler': scaler,
    'numeric_cols': numeric_cols
}, 'data/processed/ml_splits_scaled.pkl')

print(f"X_train shape: {X_train_scaled.shape}")
print(f"Target range: train {y_train.min():.1f}-{y_train.max():.1f}, test {y_test.min():.1f}-{y_test.max():.1f}")

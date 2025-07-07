#!/usr/bin/env python3
"""
Quick check to compare the two main combined datasets.
"""

import pandas as pd

print("Comparing main combined datasets...")
print("=" * 50)

# Load both datasets
df1 = pd.read_csv('data/processed/berlin_housing_combined_final.csv')
df2 = pd.read_csv('data/processed/berlin_housing_combined_enriched_final.csv')

print("berlin_housing_combined_final.csv:")
print(f"Shape: {df1.shape}")
print(f"Columns: {list(df1.columns)}")

print("\nberlin_housing_combined_enriched_final.csv:")
print(f"Shape: {df2.shape}")
print(f"Columns: {list(df2.columns)}")

print("\n--- Geographic columns check ---")
geo_cols = ['lat', 'lon', 'plz', 'ortsteil', 'bezirk', 'wol']

print("Final dataset:")
for col in geo_cols:
    if col in df1.columns:
        nan_count = df1[col].isna().sum()
        total = len(df1)
        print(f"{col}: {nan_count} NaN values ({100*nan_count/total:.1f}%)")
    else:
        print(f"{col}: Column missing")

print("\nEnriched Final dataset:")
for col in geo_cols:
    if col in df2.columns:
        nan_count = df2[col].isna().sum()
        total = len(df2)
        print(f"{col}: {nan_count} NaN values ({100*nan_count/total:.1f}%)")
    else:
        print(f"{col}: Column missing")

# Show first few rows of geographic data
print("\n--- Sample geographic data ---")
print("Final dataset (first 5 rows):")
if all(col in df1.columns for col in ['plz', 'ortsteil', 'bezirk', 'lat', 'lon']):
    print(df1[['plz', 'ortsteil', 'bezirk', 'lat', 'lon']].head())
else:
    print("Geographic columns not all present")

print("\nEnriched Final dataset (first 5 rows):")
if all(col in df2.columns for col in ['plz', 'ortsteil', 'bezirk', 'lat', 'lon']):
    print(df2[['plz', 'ortsteil', 'bezirk', 'lat', 'lon']].head())
else:
    print("Geographic columns not all present")

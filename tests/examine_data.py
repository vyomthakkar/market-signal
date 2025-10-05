#!/usr/bin/env python3
"""
Quick script to examine the scraped tweet data structure
"""

import pandas as pd

print("\n" + "="*80)
print("📊 EXAMINING SCRAPED TWEET DATA")
print("="*80)

# Load the data
df = pd.read_parquet('tweets_english.parquet')

print(f"\n📏 Dataset Shape:")
print(f"  Rows (tweets): {len(df)}")
print(f"  Columns: {len(df.columns)}")

print(f"\n📋 Available Columns:")
for col in df.columns:
    print(f"  • {col}")

print(f"\n🔍 Column Details (with sample values):")
print("="*80)

for col in df.columns:
    print(f"\n{col}:")
    print(f"  Type: {df[col].dtype}")
    print(f"  Non-null: {df[col].notna().sum()}/{len(df)}")
    
    # Show sample value (first non-null)
    sample = df[col].dropna().iloc[0] if len(df[col].dropna()) > 0 else None
    if sample is not None:
        if isinstance(sample, (list, dict)):
            print(f"  Sample: {sample}")
        elif isinstance(sample, str) and len(str(sample)) > 100:
            print(f"  Sample: {str(sample)[:100]}...")
        else:
            print(f"  Sample: {sample}")

print("\n" + "="*80)
print("📊 FIRST TWEET (complete record):")
print("="*80)
print(df.iloc[0].to_dict())

print("\n" + "="*80)
print("✅ Data examination complete!")
print("="*80)

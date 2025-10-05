#!/usr/bin/env python3
"""
Compare JSON and Parquet data files
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
import pandas as pd

project_root = Path(__file__).parent.parent
json_file = project_root / 'data_store/tweets_incremental.json'
parquet_file = project_root / 'data_store/tweets_incremental.parquet'

print("="*80)
print("📊 COMPARING DATA FILES")
print("="*80 + "\n")

# Check JSON
print("1️⃣  JSON FILE:")
print(f"   Path: {json_file}")
if json_file.exists():
    with open(json_file) as f:
        json_data = json.load(f)
    print(f"   ✓ Exists: {len(json_data)} tweets")
    
    # Check hashtags in JSON
    sample = json_data[0]
    print(f"   Sample hashtags: {sample.get('hashtags', 'NOT FOUND')}")
    
    tweets_with_hashtags = sum(1 for t in json_data if t.get('hashtags') and len(t.get('hashtags', [])) > 0)
    print(f"   Tweets with hashtags: {tweets_with_hashtags}/{len(json_data)}")
else:
    print(f"   ✗ NOT FOUND")

print()

# Check Parquet
print("2️⃣  PARQUET FILE:")
print(f"   Path: {parquet_file}")
if parquet_file.exists():
    df = pd.read_parquet(parquet_file)
    print(f"   ✓ Exists: {len(df)} tweets")
    print(f"   Columns: {df.columns.tolist()}")
    
    if 'hashtags' in df.columns:
        print(f"\n   Hashtags column dtype: {df['hashtags'].dtype}")
        print(f"   Sample values:")
        for i in range(min(5, len(df))):
            val = df['hashtags'].iloc[i]
            print(f"     Row {i}: {type(val).__name__} = {repr(val)[:100]}")
        
        # Count tweets with hashtags
        def has_hashtags(val):
            if pd.isna(val):
                return False
            if isinstance(val, list) and len(val) > 0:
                return True
            if isinstance(val, str) and val and val != '[]':
                return True
            return False
        
        tweets_with_hashtags = df['hashtags'].apply(has_hashtags).sum()
        print(f"\n   Tweets with hashtags: {tweets_with_hashtags}/{len(df)}")
    else:
        print(f"   ⚠️  No 'hashtags' column found!")
else:
    print(f"   ✗ NOT FOUND")

print("\n" + "="*80)
print("RECOMMENDATION:")
print("="*80)

if json_file.exists() and not parquet_file.exists():
    print("❌ Parquet file missing! Regenerate it from JSON.")
elif json_file.exists() and parquet_file.exists():
    # Load both
    with open(json_file) as f:
        json_data = json.load(f)
    df = pd.read_parquet(parquet_file)
    
    json_hashtags = sum(1 for t in json_data if t.get('hashtags') and len(t.get('hashtags', [])) > 0)
    parquet_hashtags = df['hashtags'].apply(has_hashtags).sum() if 'hashtags' in df.columns else 0
    
    if json_hashtags > parquet_hashtags:
        print(f"⚠️  JSON has {json_hashtags} tweets with hashtags")
        print(f"⚠️  Parquet has {parquet_hashtags} tweets with hashtags")
        print(f"\n💡 Solution: Use JSON file instead or regenerate parquet")
        print(f"\nTo use JSON file:")
        print(f"  python3 2_analyze_signals.py --input data_store/tweets_incremental.json")
    else:
        print("✓ Both files look good!")

print()

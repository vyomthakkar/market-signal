#!/usr/bin/env python3
"""
Debug script to check hashtag format in the data
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd

def check_hashtags():
    print("="*80)
    print("🔍 DEBUGGING HASHTAG PARSING")
    print("="*80 + "\n")
    
    # Load data
    data_file = Path(__file__).parent.parent / 'data_store/tweets_incremental.parquet'
    print(f"Loading: {data_file}")
    df = pd.read_parquet(data_file)
    print(f"✓ Loaded {len(df)} tweets\n")
    
    # Check hashtags column
    print("📊 HASHTAG COLUMN ANALYSIS")
    print("-" * 80)
    
    if 'hashtags' not in df.columns:
        print("❌ ERROR: No 'hashtags' column found!")
        print(f"Available columns: {df.columns.tolist()}")
        return
    
    print(f"Column dtype: {df['hashtags'].dtype}")
    print(f"Non-null count: {df['hashtags'].notna().sum()} / {len(df)}")
    
    # Sample values
    print("\n📝 SAMPLE HASHTAG VALUES:")
    print("-" * 80)
    for i in range(min(10, len(df))):
        val = df['hashtags'].iloc[i]
        print(f"Row {i}:")
        print(f"  Type: {type(val)}")
        print(f"  Value: {repr(val)}")
        print()
    
    # Check if any have actual hashtags
    def has_hashtags(val):
        if pd.isna(val):
            return False
        if isinstance(val, list) and len(val) > 0:
            return True
        if isinstance(val, str) and val and val != '[]':
            return True
        return False
    
    tweets_with_hashtags = df['hashtags'].apply(has_hashtags).sum()
    print(f"\n📊 STATISTICS:")
    print(f"  Tweets with hashtags: {tweets_with_hashtags} / {len(df)}")
    print(f"  Tweets without hashtags: {len(df) - tweets_with_hashtags}")
    
    # Try to parse like the analyzer does
    print("\n🔧 TESTING HASHTAG NORMALIZATION:")
    print("-" * 80)
    
    import ast
    
    def normalize_hashtags(tags):
        if pd.isna(tags):
            return []
        if isinstance(tags, str):
            try:
                tags = ast.literal_eval(tags)
            except:
                print(f"  ⚠️ Failed to parse string: {repr(tags)}")
                return []
        if isinstance(tags, list):
            result = [str(tag).lower().strip('#') for tag in tags if tag]
            return result
        return []
    
    # Test on first 5 tweets with hashtags
    sample_df = df[df['hashtags'].apply(has_hashtags)].head(5)
    print(f"\nTesting normalization on {len(sample_df)} tweets with hashtags:\n")
    
    for idx, row in sample_df.iterrows():
        original = row['hashtags']
        normalized = normalize_hashtags(original)
        print(f"Tweet {idx}:")
        print(f"  Original: {repr(original)}")
        print(f"  Normalized: {normalized}")
        print()
    
    # Check metadata if available
    meta_file = Path(__file__).parent.parent / 'data_store/tweets_incremental.meta.json'
    if meta_file.exists():
        import json
        with open(meta_file) as f:
            meta = json.load(f)
        
        print("\n📋 METADATA INFO:")
        print("-" * 80)
        if 'hashtags_scraped' in meta:
            print(f"Hashtags scraped: {list(meta['hashtags_scraped'].keys())}")
        
    print("\n" + "="*80)
    print("✅ DEBUG COMPLETE")
    print("="*80)

if __name__ == '__main__':
    check_hashtags()

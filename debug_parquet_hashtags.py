#!/usr/bin/env python3
"""Debug script to check hashtag format in Parquet file"""

import pandas as pd

print("Loading Parquet file...")
df = pd.read_parquet('data_store/tweets_incremental.parquet')

print(f"\nTotal tweets: {len(df)}")
print(f"Columns: {df.columns.tolist()}")

# Check hashtags column
print(f"\n{'='*70}")
print("HASHTAGS COLUMN ANALYSIS")
print(f"{'='*70}")

print(f"\nColumn type: {df['hashtags'].dtype}")
print(f"\nFirst 5 hashtag values:")
for i in range(min(5, len(df))):
    value = df.iloc[i]['hashtags']
    print(f"  {i}: {repr(value)}")
    print(f"     Type: {type(value)}")
    print(f"     Is list: {isinstance(value, list)}")
    if hasattr(value, '__iter__') and not isinstance(value, str):
        try:
            print(f"     Length: {len(value)}")
            if len(value) > 0:
                print(f"     First item: {repr(value[0])}, type: {type(value[0])}")
        except:
            pass

# Try to filter
print(f"\n{'='*70}")
print("TESTING FILTER")
print(f"{'='*70}")

filter_hashtags = ['nifty', 'nifty50', 'sensex', 'banknifty', 'intraday']

def has_target_hashtag(tweet_hashtags):
    """Check if tweet has any of the target hashtags"""
    print(f"  Checking: {repr(tweet_hashtags)[:80]} (type: {type(tweet_hashtags).__name__})")
    
    if not isinstance(tweet_hashtags, list):
        print(f"    → Not a list, returning False")
        return False
    
    # Normalize tweet hashtags
    normalized = [str(h).lower().strip('#') for h in tweet_hashtags]
    print(f"    → Normalized to: {normalized[:3]}")
    
    # Check if any target hashtag is present
    result = any(h in filter_hashtags for h in normalized)
    print(f"    → Result: {result}")
    return result

print("\nTrying filter on first 3 tweets:")
for i in range(min(3, len(df))):
    result = has_target_hashtag(df.iloc[i]['hashtags'])
    print()

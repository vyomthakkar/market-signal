#!/usr/bin/env python3
"""Debug script to trace data flow through the analysis pipeline"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
import json

# Load data
data_file = Path("data_store/tweets_incremental.parquet")
print(f"Loading from: {data_file}")
print(f"File exists: {data_file.exists()}")

if data_file.suffix == '.parquet':
    df = pd.read_parquet(data_file)
else:
    with open(data_file, 'r') as f:
        data = json.load(f)
    df = pd.DataFrame(data)

print(f"\n{'='*70}")
print("STEP 1: Initial Load")
print(f"{'='*70}")
print(f"Rows loaded: {len(df)}")
print(f"Columns: {df.columns.tolist()}")
print(f"\nFirst row hashtags: {df.iloc[0]['hashtags']}")
print(f"Type: {type(df.iloc[0]['hashtags'])}")

# Check hashtag distribution
print(f"\n{'='*70}")
print("STEP 2: Hashtag Analysis")
print(f"{'='*70}")

# Count tweets with hashtags
has_hashtags = df['hashtags'].apply(lambda x: isinstance(x, list) and len(x) > 0)
print(f"Tweets with hashtags: {has_hashtags.sum()} / {len(df)}")

# Show hashtag samples
print(f"\nSample hashtags (first 10 tweets):")
for i in range(min(10, len(df))):
    print(f"  {i}: {df.iloc[i]['hashtags']}")

# Simulate what features.analyze_tweets does
print(f"\n{'='*70}")
print("STEP 3: Check Required Columns for analyze_tweets")
print(f"{'='*70}")
required_for_analysis = ['content', 'hashtags']
for col in required_for_analysis:
    present = col in df.columns
    print(f"  {col}: {'✓' if present else '✗'}")
    if present:
        sample = df[col].iloc[0]
        print(f"    Sample: {str(sample)[:100]}")

# Check what happens after analysis
print(f"\n{'='*70}")
print("STEP 4: Simulate analyze_tweets output")
print(f"{'='*70}")

# The analyze_tweets function should preserve hashtags
# Let's check if hashtags would be preserved
tweets_list = df.to_dict('records')
print(f"Converted to list of dicts: {len(tweets_list)} tweets")
print(f"First tweet has 'hashtags' key: {'hashtags' in tweets_list[0]}")
print(f"First tweet hashtags: {tweets_list[0].get('hashtags')}")

# Now simulate HashtagAnalyzer
print(f"\n{'='*70}")
print("STEP 5: Simulate HashtagAnalyzer")
print(f"{'='*70}")

# Add dummy analysis columns if not present
if 'signal_score' not in df.columns:
    print("⚠️  signal_score column missing - would be added by analyze_tweets")
    df['signal_score'] = 0.0
if 'confidence' not in df.columns:
    print("⚠️  confidence column missing - would be added by analyze_tweets")
    df['confidence'] = 0.5
if 'combined_sentiment_score' not in df.columns:
    print("⚠️  combined_sentiment_score column missing - would be added by analyze_tweets")
    df['combined_sentiment_score'] = 0.0

# Normalize hashtags like HashtagAnalyzer does
def normalize_hashtags(tags):
    if pd.isna(tags):
        return []
    if isinstance(tags, str):
        if not tags or tags == '[]':
            return []
        import ast
        try:
            tags = ast.literal_eval(tags)
        except:
            return []
    if isinstance(tags, list):
        result = [str(tag).lower().strip('#').strip() for tag in tags if tag]
        return result
    return []

df['hashtags_normalized'] = df['hashtags'].apply(normalize_hashtags)

tweets_with_hashtags = (df['hashtags_normalized'].apply(len) > 0).sum()
print(f"Tweets with hashtags after normalization: {tweets_with_hashtags}/{len(df)}")

# Explode hashtags
df_exploded = df[df['hashtags_normalized'].apply(len) > 0].copy()
df_exploded = df_exploded.explode('hashtags_normalized')
df_exploded = df_exploded.rename(columns={'hashtags_normalized': 'hashtag'})

print(f"Rows after explode: {len(df_exploded)}")
print(f"Unique hashtags: {df_exploded['hashtag'].nunique()}")

# Group by hashtag
hashtag_groups = df_exploded.groupby('hashtag')
print(f"\nHashtag groups:")
for hashtag, group in hashtag_groups:
    print(f"  #{hashtag}: {len(group)} tweets")
    if len(group) < 20:
        print(f"    ⚠️  Below minimum threshold (20)")

print(f"\n{'='*70}")
print("DIAGNOSIS")
print(f"{'='*70}")

# Count how many hashtags meet the minimum threshold
min_tweets = 20
qualified_hashtags = sum(1 for _, group in hashtag_groups if len(group) >= min_tweets)
print(f"Hashtags with >= {min_tweets} tweets: {qualified_hashtags}")

if qualified_hashtags == 0:
    print("\n❌ ROOT CAUSE: No hashtags have enough tweets!")
    print(f"   All hashtags are below the minimum threshold of {min_tweets} tweets.")
    print(f"   This is why the analysis returns 0 tweets.")
    print(f"\n💡 SOLUTION: Lower the min_tweets threshold in HashtagAnalyzer")
else:
    print(f"\n✓ {qualified_hashtags} hashtags qualify for analysis")

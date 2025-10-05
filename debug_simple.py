#!/usr/bin/env python3
"""Simple debug script to check hashtag distribution"""

import json
from collections import Counter

# Load JSON data
print("Loading data_store/tweets_incremental.json...")
with open('data_store/tweets_incremental.json', 'r') as f:
    tweets = json.load(f)

print(f"\n{'='*70}")
print(f"DATA LOADED: {len(tweets)} tweets")
print(f"{'='*70}")

# Check hashtag structure
print(f"\nFirst tweet hashtags: {tweets[0].get('hashtags')}")
print(f"Type: {type(tweets[0].get('hashtags'))}")

# Count tweets with hashtags
has_hashtags = sum(1 for t in tweets if isinstance(t.get('hashtags'), list) and len(t.get('hashtags')) > 0)
print(f"\nTweets with hashtags: {has_hashtags} / {len(tweets)}")

# Collect all hashtags
all_hashtags = []
for tweet in tweets:
    hashtags = tweet.get('hashtags', [])
    if isinstance(hashtags, list):
        # Normalize: lowercase, strip #
        normalized = [str(h).lower().strip('#').strip() for h in hashtags if h]
        all_hashtags.extend(normalized)

# Count hashtag occurrences
hashtag_counts = Counter(all_hashtags)

print(f"\n{'='*70}")
print(f"HASHTAG DISTRIBUTION")
print(f"{'='*70}")
print(f"Total hashtag instances: {len(all_hashtags)}")
print(f"Unique hashtags: {len(hashtag_counts)}")

print(f"\nTop 20 hashtags:")
for hashtag, count in hashtag_counts.most_common(20):
    print(f"  #{hashtag}: {count} tweets")

# Check minimum threshold
MIN_TWEETS = 20
print(f"\n{'='*70}")
print(f"THRESHOLD ANALYSIS (min_tweets={MIN_TWEETS})")
print(f"{'='*70}")

qualified = {h: c for h, c in hashtag_counts.items() if c >= MIN_TWEETS}
disqualified = {h: c for h, c in hashtag_counts.items() if c < MIN_TWEETS}

print(f"\n✓ Hashtags that QUALIFY (>= {MIN_TWEETS} tweets): {len(qualified)}")
for hashtag, count in sorted(qualified.items(), key=lambda x: x[1], reverse=True):
    print(f"  #{hashtag}: {count} tweets")

print(f"\n✗ Hashtags that DON'T qualify (< {MIN_TWEETS} tweets): {len(disqualified)}")
if len(disqualified) <= 20:
    for hashtag, count in sorted(disqualified.items(), key=lambda x: x[1], reverse=True):
        print(f"  #{hashtag}: {count} tweets")
else:
    print(f"  (Too many to list - showing top 10)")
    for hashtag, count in sorted(disqualified.items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"  #{hashtag}: {count} tweets")

# Diagnosis
print(f"\n{'='*70}")
print(f"🔍 DIAGNOSIS")
print(f"{'='*70}")

if len(qualified) == 0:
    print("\n❌ ROOT CAUSE FOUND!")
    print(f"   No hashtags have >= {MIN_TWEETS} tweets.")
    print(f"   The HashtagAnalyzer (min_tweets={MIN_TWEETS}) filters them ALL out.")
    print(f"   This is why you get 0 tweets in the final analysis.")
    print(f"\n💡 SOLUTIONS:")
    print(f"   1. Lower min_tweets in run/2_analyze_signals.py (line 137-138)")
    print(f"      Change: min_tweets=20  →  min_tweets=5 or 10")
    print(f"   2. Collect more tweets for each hashtag to reach the threshold")
else:
    print(f"\n✓ {len(qualified)} hashtags qualify for analysis")
    print(f"   This should work. The issue might be elsewhere in the pipeline.")
    total_qualifying_tweets = sum(qualified.values())
    print(f"   Total tweets in qualifying hashtags: {total_qualifying_tweets}")

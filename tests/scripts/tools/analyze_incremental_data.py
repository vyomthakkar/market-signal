#!/usr/bin/env python3
"""
Analyze data from incremental scraper

Usage:
    python analyze_incremental_data.py
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter
from datetime import datetime

print("\n" + "="*80)
print("📊 ANALYZING INCREMENTAL SCRAPER DATA")
print("="*80)

# Load data
data_file = Path("data_store/tweets_incremental.json")
metadata_file = Path("data_store/scraping_metadata.json")

if not data_file.exists():
    print("❌ No data found. Run the scraper first!")
    exit(1)

# Load tweets
with open(data_file, 'r') as f:
    tweets = json.load(f)

# Load metadata
with open(metadata_file, 'r') as f:
    metadata = json.load(f)

print(f"\n📈 DATASET OVERVIEW")
print("="*80)
print(f"Total Tweets: {len(tweets)}")
print(f"Hashtags Scraped: {len(metadata['hashtags_scraped'])}")
print(f"Scraping Sessions: {len(metadata['scraping_sessions'])}")
print(f"Created: {metadata.get('created_at', 'N/A')}")
print(f"Last Updated: {metadata.get('last_updated', 'N/A')}")

# Per-hashtag breakdown
print(f"\n🏷️  PER-HASHTAG BREAKDOWN")
print("="*80)
for hashtag, info in metadata['hashtags_scraped'].items():
    print(f"#{hashtag}:")
    print(f"  Scraped: {info['scraped_count']}")
    print(f"  Unique Added: {info['unique_added']}")
    print(f"  Target: {info['target_count']}")
    print(f"  Success Rate: {info['scraped_count']/info['target_count']*100:.1f}%")
    print(f"  Scraped At: {info['scraped_at']}")
    print()

# Data structure analysis
print(f"\n📋 DATA STRUCTURE")
print("="*80)
if tweets:
    first_tweet = tweets[0]
    print("Available fields:")
    for key in first_tweet.keys():
        print(f"  • {key}")

# Convert to DataFrame for analysis
df = pd.DataFrame(tweets)

print(f"\n📊 DATA QUALITY")
print("="*80)
print(f"Total tweets: {len(df)}")
print(f"\nFields completion:")
for col in df.columns:
    non_null = df[col].notna().sum()
    pct = non_null / len(df) * 100
    print(f"  {col}: {non_null}/{len(df)} ({pct:.1f}%)")

# Language distribution
if 'detected_language' in df.columns:
    print(f"\n🌍 LANGUAGE DISTRIBUTION")
    print("="*80)
    lang_dist = df['detected_language'].value_counts()
    for lang, count in lang_dist.items():
        pct = count / len(df) * 100
        print(f"  {lang}: {count} ({pct:.1f}%)")

# Hashtag analysis
if 'hashtags' in df.columns:
    print(f"\n#️⃣  HASHTAG ANALYSIS")
    print("="*80)
    all_hashtags = []
    for hashtags in df['hashtags']:
        if isinstance(hashtags, list):
            all_hashtags.extend([h.lower() for h in hashtags])
    
    hashtag_counts = Counter(all_hashtags)
    print(f"Unique hashtags found: {len(hashtag_counts)}")
    print(f"\nTop 15 hashtags:")
    for tag, count in hashtag_counts.most_common(15):
        pct = count / len(df) * 100
        print(f"  #{tag}: {count} tweets ({pct:.1f}%)")

# Engagement metrics
print(f"\n💬 ENGAGEMENT METRICS")
print("="*80)
if 'likes' in df.columns:
    print(f"Likes:")
    print(f"  Total: {df['likes'].sum()}")
    print(f"  Average: {df['likes'].mean():.2f}")
    print(f"  Max: {df['likes'].max()}")

if 'retweets' in df.columns:
    print(f"\nRetweets:")
    print(f"  Total: {df['retweets'].sum()}")
    print(f"  Average: {df['retweets'].mean():.2f}")
    print(f"  Max: {df['retweets'].max()}")

if 'replies' in df.columns:
    print(f"\nReplies:")
    print(f"  Total: {df['replies'].sum()}")
    print(f"  Average: {df['replies'].mean():.2f}")
    print(f"  Max: {df['replies'].max()}")

# Time analysis
if 'timestamp' in df.columns:
    print(f"\n⏰ TIME DISTRIBUTION")
    print("="*80)
    df['timestamp_dt'] = pd.to_datetime(df['timestamp'])
    print(f"Earliest tweet: {df['timestamp_dt'].min()}")
    print(f"Latest tweet: {df['timestamp_dt'].max()}")
    print(f"Time span: {(df['timestamp_dt'].max() - df['timestamp_dt'].min())}")
    
    # Group by hour
    df['hour'] = df['timestamp_dt'].dt.hour
    hourly = df['hour'].value_counts().sort_index()
    print(f"\nTweets by hour (UTC):")
    for hour, count in hourly.items():
        bar = "█" * int(count / len(df) * 50)
        print(f"  {hour:02d}:00 - {count:3d} {bar}")

# User analysis
if 'username' in df.columns:
    print(f"\n👥 USER ANALYSIS")
    print("="*80)
    print(f"Unique users: {df['username'].nunique()}")
    print(f"\nTop 10 most active users:")
    user_counts = df['username'].value_counts().head(10)
    for user, count in user_counts.items():
        pct = count / len(df) * 100
        print(f"  @{user}: {count} tweets ({pct:.1f}%)")

# Sample tweets
print(f"\n📝 SAMPLE TWEETS")
print("="*80)
print("\nFirst 3 tweets:\n")
for i, tweet in enumerate(tweets[:3], 1):
    print(f"{i}. @{tweet['username']} ({tweet['timestamp']})")
    print(f"   {tweet['content'][:150]}...")
    if tweet.get('hashtags'):
        print(f"   Hashtags: {', '.join(['#' + h for h in tweet['hashtags'][:5]])}")
    print()

# URLs analysis
if 'extracted_urls' in df.columns:
    url_count = sum(len(urls) if isinstance(urls, list) else 0 for urls in df['extracted_urls'])
    tweets_with_urls = sum(1 for urls in df['extracted_urls'] if isinstance(urls, list) and len(urls) > 0)
    print(f"\n🔗 URL ANALYSIS")
    print("="*80)
    print(f"Tweets with URLs: {tweets_with_urls} ({tweets_with_urls/len(df)*100:.1f}%)")
    print(f"Total URLs: {url_count}")

# Save summary
summary = {
    'total_tweets': len(tweets),
    'hashtags_scraped': list(metadata['hashtags_scraped'].keys()),
    'unique_users': int(df['username'].nunique()) if 'username' in df.columns else 0,
    'languages': dict(df['detected_language'].value_counts()) if 'detected_language' in df.columns else {},
    'time_range': {
        'earliest': str(df['timestamp_dt'].min()) if 'timestamp' in df.columns else None,
        'latest': str(df['timestamp_dt'].max()) if 'timestamp' in df.columns else None,
    },
    'engagement': {
        'total_likes': int(df['likes'].sum()) if 'likes' in df.columns else 0,
        'total_retweets': int(df['retweets'].sum()) if 'retweets' in df.columns else 0,
        'total_replies': int(df['replies'].sum()) if 'replies' in df.columns else 0,
    }
}

summary_file = Path("data_store/analysis_summary.json")
with open(summary_file, 'w') as f:
    json.dump(summary, f, indent=2, default=str)

print(f"\n💾 SUMMARY SAVED")
print("="*80)
print(f"Summary saved to: {summary_file}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE!")
print("="*80)
print("\n💡 Next steps:")
print("  • Scrape more hashtags: python incremental_scraper.py <hashtag> --count 500")
print("  • Check status: python incremental_scraper.py --status")
print("  • Re-run analysis: python analyze_incremental_data.py")
print()

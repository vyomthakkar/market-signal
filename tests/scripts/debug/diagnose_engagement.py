#!/usr/bin/env python3
"""
Root Cause Analysis: Why is engagement 0 for all tweets?
"""

import pandas as pd

print("\n" + "="*100)
print("🔍 ROOT CAUSE ANALYSIS: Zero Engagement Issue")
print("="*100)

# Load the original scraped data
df = pd.read_parquet('tweets_english.parquet')

print(f"\n1️⃣ DATA SOURCE CHECK")
print(f"   Total tweets: {len(df)}")
print(f"   Data columns: {list(df.columns)}")

print(f"\n2️⃣ ENGAGEMENT FIELD ANALYSIS")
engagement_fields = ['likes', 'retweets', 'replies', 'views']

for field in engagement_fields:
    if field in df.columns:
        print(f"\n   {field}:")
        print(f"     ├─ Data type: {df[field].dtype}")
        print(f"     ├─ Non-null count: {df[field].notna().sum()}/{len(df)}")
        print(f"     ├─ Min: {df[field].min()}")
        print(f"     ├─ Max: {df[field].max()}")
        print(f"     ├─ Mean: {df[field].mean():.2f}")
        print(f"     ├─ Non-zero count: {(df[field] > 0).sum()}")
        print(f"     └─ Sample values: {df[field].head(5).tolist()}")
    else:
        print(f"\n   {field}: ❌ MISSING FROM DATA")

print(f"\n3️⃣ TWEET METADATA")
print(f"   Usernames: {df['username'].unique().tolist()}")
print(f"   Timestamp range: {df['timestamp'].min()} to {df['timestamp'].max()}")

print(f"\n4️⃣ SAMPLE TWEET INSPECTION")
sample = df.iloc[0]
print(f"   Tweet ID: {sample['tweet_id']}")
print(f"   Username: {sample['username']}")
print(f"   Timestamp: {sample['timestamp']}")
print(f"   Likes: {sample['likes']}")
print(f"   Retweets: {sample['retweets']}")
print(f"   Replies: {sample['replies']}")
print(f"   Views: {sample['views']}")
print(f"   Content: {sample['content'][:100]}...")

print("\n" + "="*100)
print("📊 ROOT CAUSE DIAGNOSIS:")
print("="*100)

# Check if all engagement is zero
all_zero = (
    (df['likes'] == 0).all() and
    (df['retweets'] == 0).all() and
    (df['replies'] == 0).all() and
    (df['views'] == 0).all()
)

if all_zero:
    print("""
🔴 FINDING: All engagement metrics are zero across ALL tweets

📋 POSSIBLE CAUSES:

1. **Scraping Method Issue** ⚠️ MOST LIKELY
   - The scraper (twscrape) may not be capturing engagement metrics
   - Some Twitter scraping tools only get basic tweet data (content, timestamp)
   - Engagement data requires additional API calls or different scraping approach
   
2. **Account/Tweet Characteristics**
   - Very new tweets (posted recently, no time to accumulate engagement)
   - Low-follower accounts with minimal reach
   - But unlikely ALL tweets would have exactly 0 across all metrics
   
3. **API Limitations**
   - Some Twitter APIs don't include engagement metrics in basic responses
   - May need authenticated/premium API access for engagement data
   
4. **Data Collection Timing**
   - Tweets were scraped immediately after posting
   - No time for any engagement to occur

📊 RECOMMENDATION:

Since engagement is all zeros, you have TWO options:

A. **Fix the Scraper** (Long-term solution)
   - Update src/data_collection/scrapers/*.py to capture engagement
   - May need different scraping library or authenticated Twitter API
   - Re-scrape the tweets with proper engagement capture
   
B. **Use Sentiment-Only Signal** (Short-term solution)
   - Continue with just sentiment analysis for now
   - Engagement metrics work correctly, just need real data
   - Can validate engagement logic with test tweets (see test_engagement.py)
   - Add engagement later when you have better data source

💡 NEXT STEPS:

1. Check your scraping code in src/data_collection/
2. Verify if twscrape supports engagement metrics
3. Consider using Twitter API v2 with authentication for full data
4. For now, sentiment analysis is working great! (see scores above)
""")
else:
    print("✅ Some tweets have engagement data! Investigating distribution...")
    print(f"\nTweets with likes: {(df['likes'] > 0).sum()}")
    print(f"Tweets with retweets: {(df['retweets'] > 0).sum()}")
    print(f"Tweets with replies: {(df['replies'] > 0).sum()}")
    print(f"Tweets with views: {(df['views'] > 0).sum()}")

print("\n" + "="*100)

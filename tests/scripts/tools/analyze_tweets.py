#!/usr/bin/env python3
"""
Example: Custom tweet analysis
Copy and modify this for your own analysis!
"""

import pandas as pd
import json
from collections import Counter

# Load data
df = pd.read_parquet('tweets.parquet')

print(f"Loaded {len(df)} tweets")
print("\n" + "="*70)

# Example 1: Find tweets mentioning specific stocks
print("\n1. Tweets mentioning 'Nifty':")
nifty_tweets = df[df['cleaned_content'].str.contains('Nifty', case=False, na=False)]
print(f"   Found {len(nifty_tweets)} tweets")
for _, tweet in nifty_tweets.head(3).iterrows():
    print(f"   @{tweet['username']}: {tweet['cleaned_content'][:60]}...")

# Example 2: Most active users
print("\n2. Most active users:")
top_users = df['username'].value_counts().head(5)
for user, count in top_users.items():
    print(f"   @{user}: {count} tweets")

# Example 3: Tweets by language
print("\n3. Language breakdown:")
for lang, count in df['detected_language'].value_counts().items():
    print(f"   {lang}: {count} tweets")

# Example 4: All unique hashtags
print("\n4. All hashtags used:")
all_hashtags = []
for tags in df['hashtags']:
    if isinstance(tags, list):
        all_hashtags.extend([str(t).lower() for t in tags])

if all_hashtags:
    hashtag_counts = Counter(all_hashtags).most_common(20)
    for tag, count in hashtag_counts:
        print(f"   #{tag}: {count}")
else:
    print("   No hashtags found")

# Example 5: Time analysis
print("\n5. Tweet timeline:")
df['timestamp'] = pd.to_datetime(df['timestamp'])
df['hour'] = df['timestamp'].dt.hour
print(f"   Earliest: {df['timestamp'].min()}")
print(f"   Latest: {df['timestamp'].max()}")
print(f"   Most active hour: {df['hour'].mode().values[0]}:00")

# Example 6: Content length analysis
print("\n6. Content analysis:")
df['content_length'] = df['cleaned_content'].str.len()
print(f"   Average length: {df['content_length'].mean():.0f} characters")
print(f"   Shortest: {df['content_length'].min()} characters")
print(f"   Longest: {df['content_length'].max()} characters")

# Example 7: Export specific data
print("\n7. Exporting data...")

# Export just the essential columns
essential_df = df[['username', 'cleaned_content', 'timestamp', 'likes', 'retweets', 'detected_language']]
essential_df.to_csv('tweets_essential.csv', index=False)
print(f"   ✅ Exported to tweets_essential.csv")

# Export English tweets only
english_df = df[df['detected_language'] == 'en']
english_df.to_parquet('tweets_english.parquet')
print(f"   ✅ Exported {len(english_df)} English tweets to tweets_english.parquet")

# Save as JSON for compatibility
tweets_list = df.to_dict('records')
with open('tweets_clean.json', 'w', encoding='utf-8') as f:
    json.dump(tweets_list, f, indent=2, ensure_ascii=False, default=str)
print(f"   ✅ Exported to tweets_clean.json")

print("\n" + "="*70)
print("Analysis complete! ✅")
print("\n💡 Tip: Modify this script for your own custom analysis!")


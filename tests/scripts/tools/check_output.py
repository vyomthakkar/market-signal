#!/usr/bin/env python3
"""
Quick script to verify and analyze scraper output
"""

import json
import pandas as pd
from pathlib import Path
from collections import Counter

def print_header(title):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")

def check_json_output():
    """Check raw JSON output"""
    print_header("1. RAW JSON OUTPUT")
    
    json_path = Path('raw_tweets.json')
    if not json_path.exists():
        print("❌ raw_tweets.json not found!")
        return None
    
    with open(json_path, 'r', encoding='utf-8') as f:
        tweets = json.load(f)
    
    print(f"✅ Found {len(tweets)} tweets in raw_tweets.json")
    print(f"📊 File size: {json_path.stat().st_size / 1024:.1f} KB")
    
    # Show first tweet
    if tweets:
        print(f"\n📝 First tweet sample:")
        first = tweets[0]
        print(f"   ID: {first.get('tweet_id')}")
        print(f"   User: @{first.get('username')}")
        print(f"   Content: {first.get('content', '')[:60]}...")
        print(f"   Likes: {first.get('likes')}, Retweets: {first.get('retweets')}")
        
        # Check if processed
        if 'cleaned_content' in first:
            print(f"   ✅ Cleaned content: {first.get('cleaned_content', '')[:60]}...")
            print(f"   🌍 Language: {first.get('detected_language', 'unknown')}")
    
    return tweets

def check_parquet_output():
    """Check Parquet output"""
    print_header("2. PARQUET OUTPUT (Efficient Storage)")
    
    parquet_path = Path('tweets.parquet')
    if not parquet_path.exists():
        print("❌ tweets.parquet not found!")
        return None
    
    df = pd.read_parquet(parquet_path)
    
    print(f"✅ Loaded {len(df)} tweets from tweets.parquet")
    print(f"📊 File size: {parquet_path.stat().st_size / 1024:.1f} KB")
    print(f"📋 Columns: {len(df.columns)}")
    
    print(f"\n📊 DataFrame Info:")
    print(f"   Rows: {len(df)}")
    print(f"   Columns: {list(df.columns)}")
    print(f"\n   Data Types:")
    for col, dtype in df.dtypes.items():
        print(f"      {col:20s} -> {dtype}")
    
    return df

def check_stats():
    """Check collection statistics"""
    print_header("3. COLLECTION STATISTICS")
    
    stats_path = Path('collection_stats.json')
    if not stats_path.exists():
        print("❌ collection_stats.json not found!")
        return
    
    with open(stats_path, 'r', encoding='utf-8') as f:
        stats = json.load(f)
    
    print("✅ Collection Stats Loaded\n")
    
    # Hashtag stats
    if 'hashtag_stats' in stats:
        print("📊 Per-Hashtag Statistics:")
        for hashtag, stat in stats['hashtag_stats'].items():
            collected = stat.get('collected', 0)
            target = stat.get('target', 0)
            percentage = stat.get('percentage', 0)
            print(f"   #{hashtag:15s} -> {collected:3d}/{target:3d} tweets ({percentage:5.1f}%)")
    
    # Global stats
    if 'global_stats' in stats:
        print(f"\n🌍 Global Statistics:")
        gs = stats['global_stats']
        print(f"   Unique tweets: {gs.get('unique_tweets', 0)}")
        print(f"   Duplicates skipped: {gs.get('duplicates_skipped', 0)}")
        print(f"   Deduplication rate: {gs.get('deduplication_rate', 0):.1f}%")
    
    # Processing stats (if available)
    if 'processing_stats' in stats:
        print(f"\n🧹 Data Processing Statistics:")
        ps = stats['processing_stats']
        print(f"   Processed: {ps.get('processed', 0)}")
        print(f"   Errors: {ps.get('errors', 0)}")
        print(f"   Success rate: {ps.get('success_rate', 0):.1f}%")
    
    # Rate limiter stats
    if 'rate_limiter_stats' in stats:
        print(f"\n⚡ Rate Limiter Statistics:")
        rs = stats['rate_limiter_stats']
        print(f"   Current rate: {rs.get('current_rate', 0):.1f} req/s")
        print(f"   Success count: {rs.get('success_count', 0)}")
        print(f"   Rate limit hits: {rs.get('rate_limit_count', 0)}")

def analyze_data(df):
    """Analyze the scraped data"""
    print_header("4. DATA ANALYSIS")
    
    print("📊 Dataset Overview:")
    print(f"   Total tweets: {len(df)}")
    print(f"   Unique users: {df['username'].nunique()}")
    print(f"   Time range: {df['timestamp'].min()} to {df['timestamp'].max()}")
    
    # Language distribution
    if 'detected_language' in df.columns:
        print(f"\n🌍 Language Distribution:")
        lang_counts = df['detected_language'].value_counts()
        for lang, count in lang_counts.items():
            percentage = (count / len(df)) * 100
            print(f"   {lang:10s} -> {count:3d} tweets ({percentage:5.1f}%)")
    
    # Engagement stats
    print(f"\n💬 Engagement Statistics:")
    print(f"   Total likes: {df['likes'].sum():,}")
    print(f"   Total retweets: {df['retweets'].sum():,}")
    print(f"   Total replies: {df['replies'].sum():,}")
    if 'views' in df.columns:
        total_views = df['views'].sum()
        if total_views > 0:
            print(f"   Total views: {total_views:,}")
    
    print(f"\n   Average per tweet:")
    print(f"   Likes: {df['likes'].mean():.1f}")
    print(f"   Retweets: {df['retweets'].mean():.1f}")
    print(f"   Replies: {df['replies'].mean():.1f}")
    
    # Top hashtags
    print(f"\n#️⃣  Top 10 Hashtags:")
    all_hashtags = []
    for tags in df['hashtags']:
        if isinstance(tags, (list, pd.Series)) and len(tags) > 0:
            all_hashtags.extend([str(t).lower() for t in tags])
    
    if all_hashtags:
        top_tags = Counter(all_hashtags).most_common(10)
        for i, (tag, count) in enumerate(top_tags, 1):
            print(f"   {i:2d}. #{tag:20s} -> {count:3d} times")
    else:
        print("   No hashtags found")
    
    # Top users
    print(f"\n👤 Top 10 Most Active Users:")
    top_users = df['username'].value_counts().head(10)
    for i, (user, count) in enumerate(top_users.items(), 1):
        print(f"   {i:2d}. @{user:20s} -> {count:3d} tweets")
    
    # Most engaging tweets
    print(f"\n🔥 Top 5 Most Engaging Tweets:")
    df['engagement'] = df['likes'] + df['retweets'] + df['replies']
    top_engaging = df.nlargest(5, 'engagement')
    
    for i, (idx, tweet) in enumerate(top_engaging.iterrows(), 1):
        print(f"\n   {i}. @{tweet['username']} (ID: {tweet['tweet_id']})")
        content = tweet.get('cleaned_content', tweet.get('content', ''))
        print(f"      Content: {content[:70]}...")
        print(f"      ❤️  {tweet['likes']:,} likes | 🔄 {tweet['retweets']:,} RTs | 💬 {tweet['replies']:,} replies")

def compare_formats():
    """Compare JSON vs Parquet formats"""
    print_header("5. FORMAT COMPARISON (JSON vs Parquet)")
    
    json_path = Path('raw_tweets.json')
    parquet_path = Path('tweets.parquet')
    
    if json_path.exists() and parquet_path.exists():
        json_size = json_path.stat().st_size
        parquet_size = parquet_path.stat().st_size
        
        print(f"📁 File Sizes:")
        print(f"   JSON:    {json_size / 1024:7.1f} KB")
        print(f"   Parquet: {parquet_size / 1024:7.1f} KB")
        
        if parquet_size < json_size:
            compression_ratio = json_size / parquet_size
            savings = ((json_size - parquet_size) / json_size) * 100
            print(f"\n   ✅ Parquet is {compression_ratio:.2f}x smaller!")
            print(f"   💾 Space saved: {savings:.1f}%")
        else:
            print(f"\n   ℹ️  For small datasets, Parquet overhead may be larger")
            print(f"   ✅ Parquet benefits scale with data size!")
        
        print(f"\n📊 Other Benefits of Parquet:")
        print(f"   ✅ Columnar storage (faster analytics)")
        print(f"   ✅ Type-safe schema (no parsing errors)")
        print(f"   ✅ Built-in compression (efficient)")
        print(f"   ✅ Selective column reads (load only what you need)")

def show_sample_data(df):
    """Show sample data"""
    print_header("6. SAMPLE DATA")
    
    print("📋 First 3 tweets:\n")
    
    for idx, tweet in df.head(3).iterrows():
        print(f"{'─'*70}")
        print(f"Tweet #{idx + 1}")
        print(f"{'─'*70}")
        print(f"ID:        {tweet.get('tweet_id')}")
        print(f"User:      @{tweet.get('username')}")
        print(f"Timestamp: {tweet.get('timestamp')}")
        print(f"Content:   {tweet.get('content', '')[:100]}...")
        
        if 'cleaned_content' in tweet and pd.notna(tweet['cleaned_content']):
            print(f"Cleaned:   {tweet['cleaned_content'][:100]}...")
        
        if 'detected_language' in tweet:
            print(f"Language:  {tweet.get('detected_language', 'unknown')}")
        
        print(f"Engagement: ❤️  {tweet.get('likes', 0)} | 🔄 {tweet.get('retweets', 0)} | 💬 {tweet.get('replies', 0)}")
        
        if 'hashtags' in tweet and len(tweet['hashtags']) > 0:
            tags = ', '.join([f"#{t}" for t in tweet['hashtags']])
            print(f"Hashtags:  {tags}")
        
        print()

def main():
    """Main verification function"""
    print("\n" + "="*70)
    print("  TWITTER SCRAPER OUTPUT VERIFICATION")
    print("="*70)
    
    # Check all outputs
    tweets = check_json_output()
    df = check_parquet_output()
    check_stats()
    
    if df is not None and len(df) > 0:
        analyze_data(df)
        show_sample_data(df)
        compare_formats()
    
    print("\n" + "="*70)
    print("  VERIFICATION COMPLETE! ✅")
    print("="*70)
    
    print("\n💡 Next Steps:")
    print("   1. Explore data: df = pd.read_parquet('tweets.parquet')")
    print("   2. Filter by language: df[df['detected_language'] == 'hi']")
    print("   3. Analyze sentiment, extract insights, etc.")
    print()

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


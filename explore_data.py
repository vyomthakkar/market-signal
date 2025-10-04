#!/usr/bin/env python3
"""
Interactive data exploration script
Usage: python explore_data.py
"""

import pandas as pd
from pathlib import Path

def main():
    print("\n" + "="*70)
    print("  INTERACTIVE DATA EXPLORER")
    print("="*70 + "\n")
    
    # Load data
    print("Loading tweets.parquet...")
    df = pd.read_parquet('tweets.parquet')
    print(f"✅ Loaded {len(df)} tweets\n")
    
    while True:
        print("\nWhat would you like to do?")
        print("  1. Show all tweets")
        print("  2. Search tweets by keyword")
        print("  3. Filter by username")
        print("  4. Show tweets with specific hashtag")
        print("  5. Show language breakdown")
        print("  6. Export to CSV")
        print("  7. Show top users")
        print("  8. Show tweet statistics")
        print("  9. View specific tweet by ID")
        print("  0. Exit")
        
        choice = input("\nEnter choice (0-9): ").strip()
        
        if choice == '0':
            print("\n👋 Goodbye!")
            break
            
        elif choice == '1':
            print(f"\n{'='*70}")
            print("ALL TWEETS")
            print(f"{'='*70}\n")
            for idx, tweet in df.iterrows():
                print(f"[{idx+1}] @{tweet['username']}: {tweet['cleaned_content'][:60]}...")
            
        elif choice == '2':
            keyword = input("Enter keyword to search: ").strip()
            if keyword:
                mask = df['cleaned_content'].str.contains(keyword, case=False, na=False)
                results = df[mask]
                print(f"\n✅ Found {len(results)} tweets containing '{keyword}':\n")
                for idx, tweet in results.iterrows():
                    print(f"@{tweet['username']}: {tweet['cleaned_content'][:70]}...")
            
        elif choice == '3':
            username = input("Enter username (without @): ").strip()
            if username:
                user_tweets = df[df['username'] == username]
                print(f"\n✅ Found {len(user_tweets)} tweets from @{username}:\n")
                for idx, tweet in user_tweets.iterrows():
                    print(f"  {tweet['cleaned_content'][:70]}...")
            
        elif choice == '4':
            hashtag = input("Enter hashtag (without #): ").strip().lower()
            if hashtag:
                # Filter tweets containing this hashtag
                mask = df['hashtags'].apply(
                    lambda tags: hashtag in [str(t).lower() for t in tags] if isinstance(tags, list) else False
                )
                results = df[mask]
                print(f"\n✅ Found {len(results)} tweets with #{hashtag}:\n")
                for idx, tweet in results.iterrows():
                    print(f"@{tweet['username']}: {tweet['cleaned_content'][:70]}...")
            
        elif choice == '5':
            print(f"\n{'='*70}")
            print("LANGUAGE BREAKDOWN")
            print(f"{'='*70}\n")
            lang_counts = df['detected_language'].value_counts()
            for lang, count in lang_counts.items():
                percentage = (count / len(df)) * 100
                print(f"  {lang:10s} -> {count:3d} tweets ({percentage:5.1f}%)")
            
        elif choice == '6':
            filename = input("Enter CSV filename (default: tweets.csv): ").strip() or "tweets.csv"
            df.to_csv(filename, index=False, encoding='utf-8')
            file_size = Path(filename).stat().st_size / 1024
            print(f"\n✅ Exported to {filename} ({file_size:.1f} KB)")
            
        elif choice == '7':
            n = int(input("How many top users? (default: 10): ").strip() or "10")
            print(f"\n{'='*70}")
            print(f"TOP {n} MOST ACTIVE USERS")
            print(f"{'='*70}\n")
            top_users = df['username'].value_counts().head(n)
            for i, (user, count) in enumerate(top_users.items(), 1):
                print(f"  {i:2d}. @{user:20s} -> {count:3d} tweets")
            
        elif choice == '8':
            print(f"\n{'='*70}")
            print("TWEET STATISTICS")
            print(f"{'='*70}\n")
            print(f"Total tweets: {len(df)}")
            print(f"Unique users: {df['username'].nunique()}")
            print(f"Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
            print(f"\nEngagement:")
            print(f"  Total likes: {df['likes'].sum():,}")
            print(f"  Total retweets: {df['retweets'].sum():,}")
            print(f"  Total replies: {df['replies'].sum():,}")
            print(f"\nAverage per tweet:")
            print(f"  Likes: {df['likes'].mean():.1f}")
            print(f"  Retweets: {df['retweets'].mean():.1f}")
            print(f"  Replies: {df['replies'].mean():.1f}")
            
        elif choice == '9':
            tweet_id = input("Enter tweet ID: ").strip()
            if tweet_id:
                tweet = df[df['tweet_id'] == tweet_id]
                if len(tweet) > 0:
                    t = tweet.iloc[0]
                    print(f"\n{'='*70}")
                    print(f"TWEET DETAILS")
                    print(f"{'='*70}\n")
                    print(f"ID:        {t['tweet_id']}")
                    print(f"User:      @{t['username']}")
                    print(f"Timestamp: {t['timestamp']}")
                    print(f"Content:   {t['content']}")
                    print(f"Cleaned:   {t['cleaned_content']}")
                    print(f"Language:  {t['detected_language']}")
                    print(f"Engagement: ❤️  {t['likes']} | 🔄 {t['retweets']} | 💬 {t['replies']}")
                    if len(t['hashtags']) > 0:
                        print(f"Hashtags:  {', '.join(['#' + str(h) for h in t['hashtags']])}")
                    if len(t['extracted_urls']) > 0:
                        print(f"URLs:      {', '.join(t['extracted_urls'])}")
                else:
                    print(f"\n❌ Tweet ID '{tweet_id}' not found")
        
        else:
            print("\n❌ Invalid choice, please try again")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()


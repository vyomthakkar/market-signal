#!/usr/bin/env python3
"""
Interactive tweet viewer

Usage:
    python view_tweets.py                  # View random 10 tweets
    python view_tweets.py --count 20       # View random 20 tweets
    python view_tweets.py --user markaphin # View tweets from specific user
    python view_tweets.py --hashtag nifty  # View tweets with specific hashtag
"""

import json
import argparse
import random
from pathlib import Path

def load_tweets():
    """Load tweets from data store"""
    data_file = Path("data_store/tweets_incremental.json")
    if not data_file.exists():
        print("❌ No data found. Run the scraper first!")
        exit(1)
    
    with open(data_file, 'r') as f:
        return json.load(f)

def display_tweet(tweet, index=None):
    """Display a single tweet in formatted way"""
    header = f"\n{'='*80}\n"
    if index is not None:
        header += f"Tweet #{index}\n"
    header += f"{'='*80}"
    
    print(header)
    print(f"👤 User: @{tweet['username']}")
    print(f"🕐 Time: {tweet['timestamp']}")
    print(f"🆔 ID: {tweet['tweet_id']}")
    print(f"\n💬 Content:")
    print(f"   {tweet['content']}")
    
    if tweet.get('hashtags'):
        print(f"\n#️⃣  Hashtags: {', '.join(['#' + h for h in tweet['hashtags']])}")
    
    if tweet.get('mentions'):
        print(f"@  Mentions: {', '.join(tweet['mentions'])}")
    
    print(f"\n📊 Engagement:")
    print(f"   ❤️  Likes: {tweet.get('likes', 0)}")
    print(f"   🔁 Retweets: {tweet.get('retweets', 0)}")
    print(f"   💬 Replies: {tweet.get('replies', 0)}")
    print(f"   👁️  Views: {tweet.get('views', 0)}")
    
    if tweet.get('detected_language'):
        print(f"\n🌍 Language: {tweet['detected_language']}")

def main():
    parser = argparse.ArgumentParser(description="View tweets from data store")
    parser.add_argument('--count', type=int, default=10, help='Number of tweets to display')
    parser.add_argument('--user', type=str, help='Filter by username')
    parser.add_argument('--hashtag', type=str, help='Filter by hashtag (case insensitive)')
    parser.add_argument('--lang', type=str, help='Filter by language (e.g., en)')
    parser.add_argument('--random', action='store_true', help='Show random tweets (default)')
    parser.add_argument('--latest', action='store_true', help='Show latest tweets')
    parser.add_argument('--oldest', action='store_true', help='Show oldest tweets')
    
    args = parser.parse_args()
    
    # Load tweets
    tweets = load_tweets()
    
    print(f"\n{'='*80}")
    print(f"📊 TWEET VIEWER")
    print(f"{'='*80}")
    print(f"Total tweets in data store: {len(tweets)}")
    
    # Apply filters
    filtered = tweets.copy()
    
    if args.user:
        filtered = [t for t in filtered if t['username'].lower() == args.user.lower()]
        print(f"Filtered by user @{args.user}: {len(filtered)} tweets")
    
    if args.hashtag:
        filtered = [t for t in filtered if any(args.hashtag.lower() in h.lower() for h in t.get('hashtags', []))]
        print(f"Filtered by hashtag #{args.hashtag}: {len(filtered)} tweets")
    
    if args.lang:
        filtered = [t for t in filtered if t.get('detected_language', '').lower() == args.lang.lower()]
        print(f"Filtered by language '{args.lang}': {len(filtered)} tweets")
    
    if not filtered:
        print("❌ No tweets match the filters!")
        return
    
    # Sort/select tweets
    if args.latest:
        # Sort by timestamp (newest first)
        filtered = sorted(filtered, key=lambda t: t['timestamp'], reverse=True)
        selection = filtered[:args.count]
        print(f"\nShowing {len(selection)} latest tweets:")
    elif args.oldest:
        # Sort by timestamp (oldest first)
        filtered = sorted(filtered, key=lambda t: t['timestamp'])
        selection = filtered[:args.count]
        print(f"\nShowing {len(selection)} oldest tweets:")
    else:
        # Random selection (default)
        selection = random.sample(filtered, min(args.count, len(filtered)))
        print(f"\nShowing {len(selection)} random tweets:")
    
    # Display tweets
    for i, tweet in enumerate(selection, 1):
        display_tweet(tweet, i)
    
    print(f"\n{'='*80}")
    print(f"✅ Displayed {len(selection)} tweets")
    print(f"{'='*80}\n")

if __name__ == "__main__":
    main()

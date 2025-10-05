#!/usr/bin/env python3
"""
Display tweets for manual sentiment labeling
"""
import pandas as pd

def display_tweets_for_labeling():
    df = pd.read_parquet('tweets_english.parquet')
    
    print(f"Total tweets: {len(df)}")
    print("\n" + "="*100 + "\n")
    
    for idx, row in df.iterrows():
        print(f"TWEET #{idx+1}")
        print(f"Hashtags: {', '.join(row['hashtags'])}")
        print(f"Engagement: Likes={row['likes']}, Retweets={row['retweets']}, Replies={row['replies']}")
        print(f"\nContent:")
        print(row['content'])
        print("\n" + "-"*100 + "\n")

if __name__ == "__main__":
    display_tweets_for_labeling()

#!/usr/bin/env python3
"""
Interactive tweet labeling tool
Makes it easy to label tweets one by one
"""
import pandas as pd
import csv
from pathlib import Path

def display_tweet(idx, row):
    """Display a single tweet with nice formatting"""
    print("\n" + "="*100)
    print(f"TWEET #{idx+1} of 23")
    print("="*100)
    print(f"\n📱 Content:")
    print(f"  {row['content']}")
    print(f"\n🏷️  Hashtags: {', '.join(row['hashtags']) if row['hashtags'] else 'None'}")
    print(f"💬 Engagement: Likes={row['likes']}, Retweets={row['retweets']}, Replies={row['replies']}")
    print(f"🕐 Posted: {row['timestamp']}")
    print("\n" + "-"*100)

def get_sentiment_input():
    """Get sentiment score from user"""
    while True:
        try:
            score = input("\n📊 Sentiment Score (-1.0 to +1.0): ").strip()
            if not score:  # Allow skip
                return None, None, None, None
            
            score = float(score)
            if -1.0 <= score <= 1.0:
                break
            print("❌ Score must be between -1.0 and +1.0")
        except ValueError:
            print("❌ Please enter a valid number")
    
    # Auto-determine label from score
    if score < -0.1:
        label = "BEARISH"
    elif score > 0.1:
        label = "BULLISH"
    else:
        label = "NEUTRAL"
    
    print(f"   → Auto-detected label: {label}")
    
    # Get confidence
    while True:
        confidence = input("🎯 Confidence (HIGH/MEDIUM/LOW): ").strip().upper()
        if confidence in ['HIGH', 'MEDIUM', 'LOW', 'H', 'M', 'L']:
            if confidence == 'H':
                confidence = 'HIGH'
            elif confidence == 'M':
                confidence = 'MEDIUM'
            elif confidence == 'L':
                confidence = 'LOW'
            break
        print("❌ Please enter HIGH, MEDIUM, or LOW (or H/M/L)")
    
    # Get notes
    notes = input("📝 Notes (optional, press Enter to skip): ").strip()
    
    return score, label, confidence, notes

def interactive_labeling():
    """Main interactive labeling function"""
    print("\n🎯 INTERACTIVE TWEET LABELING TOOL")
    print("="*100)
    print("\nQuick Guide:")
    print("  • Bearish: -1.0 to -0.1")
    print("  • Neutral: -0.1 to +0.1") 
    print("  • Bullish: +0.1 to +1.0")
    print("\n  • Press Enter without input to skip a tweet")
    print("  • Type 'quit' or 'q' to exit and save")
    print("="*100)
    
    # Load tweets
    df = pd.read_parquet('tweets_english.parquet')
    
    # Check if labels file already exists
    labels_file = Path('manual_labels.csv')
    if labels_file.exists():
        print(f"\n⚠️  Found existing labels file: {labels_file}")
        choice = input("Do you want to (c)ontinue labeling or (o)verwrite? [c/o]: ").strip().lower()
        if choice == 'o':
            labels = []
        else:
            # Load existing labels
            existing_df = pd.read_csv(labels_file)
            labels = existing_df.to_dict('records')
            print(f"✓ Loaded {len(labels)} existing labels")
    else:
        labels = []
    
    # Start from where we left off
    start_idx = len(labels)
    
    # Label tweets
    for idx in range(start_idx, len(df)):
        row = df.iloc[idx]
        
        display_tweet(idx, row)
        
        score, label, confidence, notes = get_sentiment_input()
        
        # Check for quit
        if isinstance(score, str) and score.lower() in ['quit', 'q']:
            break
        
        # Skip if no input
        if score is None:
            print("⏭️  Skipped")
            continue
        
        # Add label
        labels.append({
            'tweet_id': idx + 1,
            'content_preview': row['content'][:80] + '...' if len(row['content']) > 80 else row['content'],
            'manual_sentiment_score': score,
            'manual_sentiment_label': label,
            'confidence': confidence,
            'notes': notes
        })
        
        print(f"✓ Saved label for tweet #{idx+1}")
    
    # Save labels
    if labels:
        with open('manual_labels.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['tweet_id', 'content_preview', 'manual_sentiment_score', 
                                                   'manual_sentiment_label', 'confidence', 'notes'])
            writer.writeheader()
            writer.writerows(labels)
        
        print(f"\n✅ Saved {len(labels)} labels to manual_labels.csv")
    else:
        print("\n⚠️  No labels saved")
    
    # Summary
    if labels:
        labels_df = pd.DataFrame(labels)
        print("\n" + "="*100)
        print("LABELING SUMMARY")
        print("="*100)
        print(f"Total labeled: {len(labels_df)}")
        print(f"\nSentiment distribution:")
        print(labels_df['manual_sentiment_label'].value_counts())
        print(f"\nConfidence distribution:")
        print(labels_df['confidence'].value_counts())
        print(f"\nAverage sentiment score: {labels_df['manual_sentiment_score'].mean():.2f}")

if __name__ == "__main__":
    try:
        interactive_labeling()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user. Labels saved up to last completed tweet.")

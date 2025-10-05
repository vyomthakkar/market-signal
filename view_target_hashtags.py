#!/usr/bin/env python3
"""View analysis for specific target hashtags only"""

import json
from pathlib import Path

report_file = Path('output/signal_report.json')

# Your target hashtags
TARGET_HASHTAGS = ['nifty', 'nifty50', 'sensex', 'banknifty', 'intraday']

with open(report_file, 'r') as f:
    report = json.load(f)

print("="*80)
print("📊 TARGET HASHTAGS ANALYSIS")
print("="*80)
print(f"\nTarget hashtags: {', '.join(['#' + h for h in TARGET_HASHTAGS])}\n")

hashtags = report.get('hashtags', {})

# Filter to target hashtags only
target_data = {h: hashtags[h] for h in TARGET_HASHTAGS if h in hashtags}

if not target_data:
    print("❌ No data found for target hashtags.")
    print(f"\nAvailable hashtags in report: {list(hashtags.keys())[:10]}")
    exit(1)

print(f"Found {len(target_data)}/{len(TARGET_HASHTAGS)} target hashtags in data\n")

# Sort by signal strength
sorted_hashtags = sorted(
    target_data.items(),
    key=lambda x: abs(x[1].get('signal_score', 0)),
    reverse=True
)

# Summary table
print("="*80)
print("QUICK SUMMARY")
print("="*80)
print(f"{'Hashtag':<15} {'Signal':<12} {'Score':>8} {'Confidence':>12} {'Tweets':>8}")
print("-"*80)

for hashtag, data in sorted_hashtags:
    signal = data.get('signal_label', 'N/A')
    score = data.get('signal_score', 0)
    conf = data.get('confidence', 0)
    tweets = data.get('tweet_count', 0)
    
    # Add emoji
    if 'BUY' in signal:
        emoji = '📈'
    elif 'SELL' in signal:
        emoji = '📉'
    else:
        emoji = '⏸️'
    
    print(f"#{hashtag:<14} {signal:<12} {score:+8.3f} {conf*100:>11.1f}% {tweets:>8} {emoji}")

# Detailed view
for i, (hashtag, data) in enumerate(sorted_hashtags, 1):
    print(f"\n{'='*80}")
    print(f"#{hashtag.upper()}")
    print(f"{'='*80}")
    
    print(f"\n📈 SIGNAL:")
    print(f"   {data.get('signal_label', 'N/A')} ({data.get('signal_score', 0):+.3f})")
    print(f"   Confidence: {data.get('confidence', 0)*100:.1f}%")
    print(f"   Consensus: {data.get('consensus', 'N/A')}")
    
    print(f"\n📊 TWEETS: {data.get('tweet_count', 0)} total, {data.get('valid_tweet_count', 0)} high-confidence")
    
    sent_dist = data.get('sentiment_distribution', {})
    print(f"\n💭 SENTIMENT:")
    print(f"   🟢 Bullish: {sent_dist.get('bullish_count', 0)} ({sent_dist.get('bullish_ratio', 0)*100:.1f}%)")
    print(f"   🔴 Bearish: {sent_dist.get('bearish_count', 0)} ({sent_dist.get('bearish_ratio', 0)*100:.1f}%)")
    print(f"   ⚪ Neutral: {sent_dist.get('neutral_count', 0)} ({sent_dist.get('neutral_ratio', 0)*100:.1f}%)")
    
    engagement = data.get('engagement_metrics', {})
    if engagement and engagement.get('total_likes', 0) > 0:
        print(f"\n🔥 ENGAGEMENT:")
        print(f"   👍 Likes: {engagement.get('total_likes', 0)}")
        print(f"   🔁 Retweets: {engagement.get('total_retweets', 0)}")
        print(f"   💬 Replies: {engagement.get('total_replies', 0)}")
    
    trending = data.get('trending_terms', [])
    if trending:
        print(f"\n🔥 TRENDING TERMS:")
        for term_data in trending[:5]:
            print(f"   • {term_data.get('term', 'N/A')}")

print(f"\n{'='*80}")
print("💡 TIP: Run on full dataset for more reliable signals")
print("   python run/2_analyze_signals.py --hashtags nifty nifty50 sensex banknifty intraday")
print(f"{'='*80}\n")

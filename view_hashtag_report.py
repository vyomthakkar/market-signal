#!/usr/bin/env python3
"""View detailed hashtag analysis from signal report"""

import json
from pathlib import Path

report_file = Path('output/signal_report.json')

if not report_file.exists():
    print("❌ Report file not found. Run analysis first.")
    exit(1)

with open(report_file, 'r') as f:
    report = json.load(f)

print("="*80)
print("📊 DETAILED HASHTAG ANALYSIS")
print("="*80)

hashtags = report.get('hashtags', {})

if not hashtags:
    print("No hashtag data found in report.")
    exit(1)

print(f"\nTotal Hashtags Analyzed: {len(hashtags)}")
print(f"\nShowing detailed analysis for each hashtag:\n")

# Sort by signal score (absolute value for ranking)
sorted_hashtags = sorted(
    hashtags.items(),
    key=lambda x: abs(x[1].get('signal_score', 0)),
    reverse=True
)

for i, (hashtag, data) in enumerate(sorted_hashtags, 1):
    print(f"\n{'='*80}")
    print(f"#{i}: #{hashtag}")
    print(f"{'='*80}")
    
    # Signal
    print(f"\n📈 SIGNAL:")
    print(f"   Label: {data.get('signal_label', 'N/A')}")
    print(f"   Score: {data.get('signal_score', 0):+.3f}")
    print(f"   Confidence: {data.get('confidence', 0)*100:.1f}%")
    print(f"   Consensus: {data.get('consensus', 'N/A')}")
    
    # Tweet counts
    print(f"\n📊 TWEETS:")
    print(f"   Total: {data.get('tweet_count', 0)}")
    print(f"   Valid (high confidence): {data.get('valid_tweet_count', 0)}")
    
    # Sentiment distribution
    sent_dist = data.get('sentiment_distribution', {})
    print(f"\n💭 SENTIMENT:")
    print(f"   Bullish: {sent_dist.get('bullish_count', 0)} ({sent_dist.get('bullish_ratio', 0)*100:.1f}%)")
    print(f"   Bearish: {sent_dist.get('bearish_count', 0)} ({sent_dist.get('bearish_ratio', 0)*100:.1f}%)")
    print(f"   Neutral: {sent_dist.get('neutral_count', 0)} ({sent_dist.get('neutral_ratio', 0)*100:.1f}%)")
    print(f"   Avg Sentiment: {sent_dist.get('avg_sentiment', 0):+.3f}")
    
    # Engagement
    engagement = data.get('engagement_metrics', {})
    if engagement:
        print(f"\n🔥 ENGAGEMENT:")
        print(f"   Avg Virality: {engagement.get('avg_virality', 0):.3f}")
        print(f"   Total Likes: {engagement.get('total_likes', 0)}")
        print(f"   Total Retweets: {engagement.get('total_retweets', 0)}")
        print(f"   High Engagement: {engagement.get('high_engagement_count', 0)} tweets")
    
    # Trending terms
    trending = data.get('trending_terms', [])
    if trending:
        print(f"\n🔥 TRENDING TERMS:")
        for term_data in trending[:5]:  # Top 5
            print(f"   • {term_data.get('term', 'N/A')}: {term_data.get('score', 0):.3f}")
    
    # Time range
    time_range = data.get('time_range', {})
    if time_range:
        print(f"\n⏰ TIME RANGE:")
        print(f"   Earliest: {time_range.get('earliest', 'N/A')}")
        print(f"   Latest: {time_range.get('latest', 'N/A')}")
        print(f"   Span: {time_range.get('span_hours', 0):.1f} hours")

print(f"\n{'='*80}")
print(f"📄 Full JSON report: {report_file}")
print(f"{'='*80}\n")

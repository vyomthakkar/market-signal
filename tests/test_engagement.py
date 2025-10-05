#!/usr/bin/env python3
"""
Test script for engagement metrics
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from analysis.features import EngagementAnalyzer

print("\n" + "="*80)
print("🎯 ENGAGEMENT METRICS TEST")
print("="*80)

# Create analyzer
analyzer = EngagementAnalyzer()

# Test cases with different engagement patterns
test_tweets = [
    {
        'name': 'High Virality (lots of retweets)',
        'likes': 100,
        'retweets': 50,
        'replies': 10,
        'views': 5000
    },
    {
        'name': 'High Discussion (lots of replies)',
        'likes': 80,
        'retweets': 10,
        'replies': 40,
        'views': 3000
    },
    {
        'name': 'Low Engagement',
        'likes': 5,
        'retweets': 1,
        'replies': 0,
        'views': 1000
    },
    {
        'name': 'Zero Engagement (like our current data)',
        'likes': 0,
        'retweets': 0,
        'replies': 0,
        'views': 0
    },
]

for tweet in test_tweets:
    print(f"\n{'='*80}")
    print(f"Test: {tweet['name']}")
    print(f"{'='*80}")
    print(f"Likes: {tweet['likes']}, Retweets: {tweet['retweets']}, Replies: {tweet['replies']}, Views: {tweet['views']}")
    
    result = analyzer.analyze(tweet)
    
    print(f"\n📊 Results:")
    print(f"  Total Engagement: {result['total_engagement']}")
    print(f"  Engagement Rate: {result['engagement_rate']:.2f} per 1000 views")
    print(f"  Virality Ratio: {result['virality_ratio']:.2f} (retweets/likes)")
    print(f"  Reply Ratio: {result['reply_ratio']:.2f} (controversy indicator)")
    print(f"  Like Ratio: {result['like_ratio']:.4f} (likes/views)")
    print(f"\n  ⭐ VIRALITY SCORE: {result['virality_score']:.3f} (0-1 scale)")

print("\n" + "="*80)
print("✅ Engagement metrics test complete!")
print("="*80)
print("\n💡 Key Insights:")
print("  - Virality score combines all metrics into 0-1 scale")
print("  - Higher retweets = higher virality")
print("  - Higher replies = more discussion/controversy")
print("  - Will be combined with sentiment score for final signal")

#!/usr/bin/env python3
"""
Quick test of analysis pipeline on a small sample of data
"""

import sys
import json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("="*70)
print("🧪 TESTING ANALYSIS ON SAMPLE DATA")
print("="*70)

# Load a small sample from your data
print("\n1. Loading sample tweets...")
with open('data_store/tweets_incremental.json', 'r') as f:
    all_tweets = json.load(f)

# Take first 50 tweets that have hashtags
sample_tweets = []
for tweet in all_tweets:
    if isinstance(tweet.get('hashtags'), list) and len(tweet.get('hashtags')) > 0:
        sample_tweets.append(tweet)
    if len(sample_tweets) >= 50:
        break

print(f"✓ Loaded {len(sample_tweets)} tweets with hashtags")

# Show hashtag distribution in sample
from collections import Counter
hashtag_counts = Counter()
for tweet in sample_tweets:
    for tag in tweet.get('hashtags', []):
        hashtag_counts[str(tag).lower().strip('#')] += 1

print(f"\nTop 10 hashtags in sample:")
for tag, count in hashtag_counts.most_common(10):
    print(f"  #{tag}: {count} tweets")

# Save sample to temp file
print("\n2. Saving sample to test_sample.json...")
sample_file = Path('test_sample.json')
with open(sample_file, 'w') as f:
    json.dump(sample_tweets, f, indent=2)
print(f"✓ Saved to {sample_file}")

# Run analysis
print("\n3. Running analysis pipeline...")
print("-" * 70)

try:
    import pandas as pd
    from src.analysis.features import analyze_tweets
    from run.utils.hashtag_analyzer import HashtagAnalyzer
    from run.utils.market_aggregator import MarketAggregator
    
    print("✓ Imports successful")
    
    # Convert to list format
    tweets_list = sample_tweets
    
    print(f"\nAnalyzing {len(tweets_list)} tweets...")
    print("(First run will download ML models - ~500MB, may take 1-2 min)")
    
    # Run feature analysis
    analyzed_df = analyze_tweets(
        tweets_list,
        keyword_boost_weight=0.3,
        include_engagement=True,
        include_tfidf=True,
        calculate_signals=True
    )
    
    print(f"\n✓ Feature analysis complete!")
    print(f"  Analyzed: {len(analyzed_df)} tweets")
    print(f"  Columns: {len(analyzed_df.columns)}")
    
    # Check if hashtags column exists
    print("\n4. Checking if hashtags are preserved...")
    if 'hashtags' in analyzed_df.columns:
        print("✅ SUCCESS: 'hashtags' column is present!")
        
        # Count hashtags
        hashtag_count = analyzed_df['hashtags'].apply(
            lambda x: isinstance(x, list) and len(x) > 0
        ).sum()
        print(f"  Tweets with hashtags: {hashtag_count}/{len(analyzed_df)}")
        
        # Show sample
        print(f"\n  Sample hashtags from first 3 tweets:")
        for i in range(min(3, len(analyzed_df))):
            print(f"    Tweet {i+1}: {analyzed_df.iloc[i]['hashtags']}")
    else:
        print("❌ FAIL: 'hashtags' column is MISSING!")
        print(f"  Available columns: {analyzed_df.columns.tolist()}")
        sys.exit(1)
    
    # Run hashtag analysis
    print("\n5. Running hashtag-level analysis...")
    analyzer = HashtagAnalyzer(
        min_tweets=3,  # Lower threshold for sample
        min_confidence=0.3
    )
    
    hashtag_analyses = analyzer.analyze_by_hashtag(analyzed_df)
    
    print(f"✓ Hashtag analysis complete!")
    print(f"  Hashtags analyzed: {len(hashtag_analyses)}")
    
    if len(hashtag_analyses) > 0:
        print("\n  Top 5 hashtags by signal:")
        sorted_tags = sorted(
            hashtag_analyses.items(),
            key=lambda x: abs(x[1]['signal_score']),
            reverse=True
        )[:5]
        
        for tag, analysis in sorted_tags:
            print(f"    #{tag}:")
            print(f"      Signal: {analysis['signal_label']} ({analysis['signal_score']:+.3f})")
            print(f"      Confidence: {analysis['confidence']:.1%}")
            print(f"      Tweets: {analysis['tweet_count']}")
    else:
        print("⚠️  No hashtags met the threshold (min_tweets=3)")
        print("   This might be OK for a small sample")
    
    # Run market aggregation
    print("\n6. Running market aggregation...")
    aggregator = MarketAggregator(min_confidence=0.3)
    
    overall_market = aggregator.aggregate_market_signal(
        hashtag_analyses,
        len(analyzed_df)
    )
    
    print(f"✓ Market aggregation complete!")
    print(f"\n  Overall Market Signal:")
    print(f"    Label: {overall_market['signal_label']}")
    print(f"    Score: {overall_market['signal_score']:+.3f}")
    print(f"    Confidence: {overall_market['confidence']:.1%}")
    print(f"    Total Tweets: {overall_market['total_tweets']}")
    print(f"    Hashtags: {overall_market['hashtag_count']}")
    
    print("\n" + "="*70)
    if overall_market['total_tweets'] > 0 and overall_market['hashtag_count'] > 0:
        print("✅✅✅ SUCCESS! THE FIX WORKS! ✅✅✅")
        print("="*70)
        print("\n🎉 The pipeline is working correctly!")
        print("   Hashtags are preserved and analyzed.")
        print("\n📊 You can now run on full data:")
        print("   python run/2_analyze_signals.py")
    else:
        print("⚠️  PARTIAL SUCCESS")
        print("="*70)
        print("\nThe hashtags are preserved, but results are zero.")
        print("This might be due to the small sample size.")
        print("Try running on full data to get meaningful results.")
    
    # Cleanup
    sample_file.unlink()
    print(f"\n🧹 Cleaned up test file: {sample_file}")
    
except ImportError as e:
    print(f"\n❌ Missing dependency: {e}")
    print("\nPlease activate virtual environment and install dependencies:")
    print("  source venv/bin/activate")
    print("  pip install -r requirements.txt")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ Error during analysis: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

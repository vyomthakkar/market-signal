#!/usr/bin/env python3
"""
Simple test script for sentiment analysis
"""

import sys
from pathlib import Path
import logging

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from analysis.features import SentimentAnalyzer, analyze_from_parquet


def test_single_tweet():
    """Test on a single bullish tweet"""
    print("\n" + "="*80)
    print("TEST: Single Tweet Analysis")
    print("="*80)
    
    analyzer = SentimentAnalyzer(keyword_boost_weight=0.3)
    
    tweet_text = "Nifty breakout confirmed! Strong bullish momentum. Target hit! 🚀"
    print(f"\nTweet: {tweet_text}")
    
    result = analyzer.analyze(tweet_text)
    
    print(f"\n📊 Results:")
    print(f"  Base Sentiment: {result['base_sentiment_score']:.3f} ({result['base_sentiment_label']})")
    print(f"  Confidence: {result['base_confidence']:.3f}")
    print(f"  Probabilities: neg={result['probabilities']['negative']:.3f}, "
          f"neu={result['probabilities']['neutral']:.3f}, pos={result['probabilities']['positive']:.3f}")
    
    print(f"\n  Bullish keywords ({result['bullish_keyword_count']}): {result['bullish_keywords']}")
    print(f"  Bearish keywords ({result['bearish_keyword_count']}): {result['bearish_keywords']}")
    print(f"  Keyword boost: {result['keyword_boost']:+.3f}")
    
    print(f"\n  ✨ COMBINED: {result['combined_sentiment_score']:.3f} ({result['combined_sentiment_label']})")


def test_batch():
    """Test on the full dataset"""
    print("\n" + "="*80)
    print("TEST: Batch Analysis on tweets_english.parquet")
    print("="*80)
    
    df = analyze_from_parquet(
        'tweets_english.parquet',
        output_file='sentiment_results.parquet'
    )
    
    print(f"\n📊 Summary:")
    print(f"  Total tweets: {len(df)}")
    print(f"\n  Sentiment Distribution:")
    print(df['combined_sentiment_label'].value_counts())
    print(f"\n  Average sentiment: {df['combined_sentiment_score'].mean():.3f}")
    
    return df


def display_results_summary(df):
    """Display all tweets with sentiment in a clean, digestible format"""
    print("\n" + "="*100)
    print("📋 SENTIMENT ANALYSIS RESULTS - ALL TWEETS")
    print("="*100)
    
    for idx, row in df.iterrows():
        # Sentiment emoji
        score = row['combined_sentiment_score']
        label = row['combined_sentiment_label']
        
        if label == 'BULLISH':
            emoji = '🟢'
        elif label == 'BEARISH':
            emoji = '🔴'
        else:
            emoji = '⚪'
        
        # Score bar visualization
        bar_length = 20
        filled = int(((score + 1) / 2) * bar_length)  # Map -1 to +1 → 0 to 20
        bar = '█' * filled + '░' * (bar_length - filled)
        
        print(f"\n{emoji} Tweet #{idx+1} | Score: {score:+.2f} | {label}")
        print(f"   [{bar}] -1 ←→ +1")
        
        # Tweet content (truncated)
        content = row['content']
        if len(content) > 90:
            content = content[:87] + "..."
        print(f"   💬 {content}")
        
        # Show keywords if any
        keywords_info = []
        if row['bullish_keyword_count'] > 0:
            keywords_info.append(f"✅ {row['bullish_keyword_count']} bullish")
        if row['bearish_keyword_count'] > 0:
            keywords_info.append(f"❌ {row['bearish_keyword_count']} bearish")
        
        if keywords_info:
            print(f"   🔑 {' | '.join(keywords_info)}")
        
        print("   " + "-"*96)


if __name__ == "__main__":
    print("\n🎯 SENTIMENT ANALYSIS TEST")
    
    try:
        test_single_tweet()
        df = test_batch()
        
        # Display all results in digestible format
        display_results_summary(df)
        
        print("\n" + "="*100)
        print("✅ Analysis complete! Results saved to sentiment_results.parquet")
        print("="*100)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

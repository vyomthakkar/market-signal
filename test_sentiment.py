#!/usr/bin/env python3
"""
Complete test script for sentiment analysis, engagement, TF-IDF, and signal generation
"""

import sys
from pathlib import Path
import logging

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from analysis.features import (
    SentimentAnalyzer, 
    analyze_from_parquet,
    calculate_trading_signal,
    aggregate_signals
)


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
    print("TEST: Batch Analysis on data_store/tweets_incremental.parquet")
    print("="*80)
    
    import pandas as pd
    
    # Load and filter to English only before analysis
    df_raw = pd.read_parquet('data_store/tweets_incremental.parquet')
    df_en = df_raw[df_raw['detected_language'] == 'en']
    print(f"Loaded {len(df_en)} English tweets out of {len(df_raw)} total")
    
    # Analyze (use first 50 for testing)
    tweets = df_en.head(50).to_dict('records')
    
    from analysis.features import analyze_tweets
    df = analyze_tweets(tweets)
    
    # Save results
    df.to_parquet('sentiment_results.parquet', index=False)
    
    print(f"\n📊 Summary:")
    print(f"  Total tweets: {len(df)}")
    print(f"\n  Sentiment Distribution:")
    print(df['combined_sentiment_label'].value_counts())
    print(f"\n  Average sentiment: {df['combined_sentiment_score'].mean():.3f}")
    print(f"  Average confidence: {df['confidence'].mean():.3f}")
    
    return df


def display_results_summary(df):
    """Display all tweets with complete analysis including signals and confidence"""
    print("\n" + "="*100)
    print("📋 COMPLETE ANALYSIS WITH TRADING SIGNALS")
    print("="*100)
    
    for idx, row in df.iterrows():
        # Signal label emoji
        signal_label = row.get('signal_label', 'HOLD')
        if 'BUY' in signal_label:
            emoji = '🟢'
        elif 'SELL' in signal_label:
            emoji = '🔴'
        elif signal_label == 'IGNORE':
            emoji = '⚫'
        else:
            emoji = '⚪'
        
        # Tweet content (truncated)
        content = row['content']
        if len(content) > 80:
            content = content[:77] + "..."
        
        # Signal score and confidence
        signal_score = row.get('signal_score', 0.0)
        confidence = row.get('confidence', 0.0)
        ci_low, ci_high = row.get('confidence_interval', (0.0, 0.0))
        
        print(f"\n{emoji} Tweet #{idx+1} | Signal: {signal_score:+.2f} ({signal_label}) | Confidence: {confidence:.2f}")
        print(f"   💬 {content}")
        print(f"   📊 Sentiment: {row['combined_sentiment_score']:+.2f} | Virality: {row['virality_score']:.2f} | Finance: {row['finance_term_density']:.1%}")
        print(f"   🎯 Confidence Interval: [{ci_low:+.2f}, {ci_high:+.2f}]")
        
        # Confidence components
        if 'confidence_components' in row:
            components = row['confidence_components']
            print(f"   📈 Quality: {components['content_quality']:.2f} | Sentiment Str: {components['sentiment_strength']:.2f} | Social: {components['social_proof']:.2f}")
        
        # TF-IDF top terms
        if 'top_tfidf_terms' in row and row['top_tfidf_terms']:
            top_terms = row['top_tfidf_terms'][:3]  # Show top 3
            if top_terms:
                terms_str = ', '.join(top_terms)
                print(f"   🔍 Top Terms: {terms_str}")
        
        print("   " + "-"*96)


if __name__ == "__main__":
    print("\n🎯 COMPLETE SIGNAL GENERATION TEST")
    
    try:
        test_single_tweet()
        df = test_batch()
        
        # Display all results in digestible format
        display_results_summary(df)
        
        # Aggregate signal summary
        print("\n" + "="*100)
        print("📊 AGGREGATE MARKET SIGNAL")
        print("="*100)
        
        # Convert DataFrame rows to list of dicts for aggregation
        signals = df.to_dict('records')
        aggregate = aggregate_signals(signals, min_confidence=0.3)
        
        print(f"\n🎯 Composite Signal: {aggregate['aggregate_signal']:+.2f} ({aggregate['aggregate_label']})")
        print(f"   Confidence: {aggregate['aggregate_confidence']:.2f}")
        print(f"   Confidence Interval: [{aggregate['confidence_interval'][0]:+.2f}, {aggregate['confidence_interval'][1]:+.2f}]")
        print(f"   Market Consensus: {aggregate['consensus']}")
        print(f"\n📊 Statistics:")
        print(f"   Total tweets analyzed: {aggregate['num_tweets']}")
        print(f"   Valid signals (conf > 0.3): {aggregate['num_valid_tweets']}")
        print(f"   Signal std deviation: {aggregate['signal_std']:.3f}")
        print(f"   Bullish ratio: {aggregate['bullish_ratio']:.1%}")
        print(f"   Bearish ratio: {aggregate['bearish_ratio']:.1%}")
        
        # Signal distribution
        print(f"\n📈 Signal Distribution:")
        print(df['signal_label'].value_counts())
        
        print("\n" + "="*100)
        print("✅ Analysis complete! Results saved to sentiment_results.parquet")
        print("="*100)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

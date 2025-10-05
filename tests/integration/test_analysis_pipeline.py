"""
Integration tests for the complete analysis pipeline
"""

import pytest
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analysis.features import analyze_tweets, calculate_trading_signal, aggregate_signals


@pytest.mark.integration
class TestAnalysisPipeline:
    """Integration tests for full analysis pipeline"""
    
    def test_full_pipeline_with_sample_data(self, sample_tweets):
        """Test complete pipeline from tweets to signals"""
        # Analyze tweets (sentiment + engagement + TF-IDF + signals)
        df = analyze_tweets(
            sample_tweets,
            keyword_boost_weight=0.3,
            include_engagement=True,
            include_tfidf=True,
            calculate_signals=True
        )
        
        # Check output structure
        assert isinstance(df, pd.DataFrame)
        assert len(df) == len(sample_tweets)
        
        # Check all expected columns exist
        expected_columns = [
            'tweet_id',
            'content',
            'combined_sentiment_score',
            'combined_sentiment_label',
            'virality_score',
            'signal_score',
            'signal_label',
            'confidence'
        ]
        
        for col in expected_columns:
            assert col in df.columns, f"Missing column: {col}"
    
    def test_sentiment_only_pipeline(self, sample_tweets):
        """Test pipeline with only sentiment analysis"""
        df = analyze_tweets(
            sample_tweets,
            include_engagement=False,
            include_tfidf=False,
            calculate_signals=False
        )
        
        assert len(df) == len(sample_tweets)
        assert 'combined_sentiment_score' in df.columns
        assert 'combined_sentiment_label' in df.columns
    
    def test_pipeline_with_engagement(self, sample_tweets):
        """Test pipeline with sentiment and engagement"""
        df = analyze_tweets(
            sample_tweets,
            include_engagement=True,
            include_tfidf=False,
            calculate_signals=False
        )
        
        assert 'combined_sentiment_score' in df.columns
        assert 'virality_score' in df.columns
        assert 'total_engagement' in df.columns
    
    def test_pipeline_with_tfidf(self, sample_tweets):
        """Test pipeline with TF-IDF analysis"""
        df = analyze_tweets(
            sample_tweets,
            include_tfidf=True,
            calculate_signals=False
        )
        
        assert 'top_tfidf_terms' in df.columns
        assert 'finance_term_density' in df.columns
    
    def test_signal_calculation(self, sample_tweets):
        """Test trading signal calculation"""
        df = analyze_tweets(
            sample_tweets,
            calculate_signals=True
        )
        
        assert 'signal_score' in df.columns
        assert 'signal_label' in df.columns
        assert 'confidence' in df.columns
        assert 'confidence_interval' in df.columns
        
        # Check signal labels are valid
        valid_labels = ['STRONG_BUY', 'BUY', 'HOLD', 'SELL', 'STRONG_SELL', 'IGNORE']
        for label in df['signal_label']:
            assert label in valid_labels
    
    def test_aggregate_signals(self, sample_tweets):
        """Test signal aggregation"""
        df = analyze_tweets(sample_tweets, calculate_signals=True)
        signals = df.to_dict('records')
        
        aggregate = aggregate_signals(signals, min_confidence=0.3)
        
        # Check aggregate structure
        assert 'aggregate_signal' in aggregate
        assert 'aggregate_label' in aggregate
        assert 'aggregate_confidence' in aggregate
        assert 'num_tweets' in aggregate
        assert 'num_valid_tweets' in aggregate
        assert 'consensus' in aggregate
        
        # Check values are reasonable
        assert -1 <= aggregate['aggregate_signal'] <= 1
        assert 0 <= aggregate['aggregate_confidence'] <= 1
        assert aggregate['num_tweets'] == len(signals)
    
    def test_empty_input(self):
        """Test pipeline with empty input"""
        df = analyze_tweets([])
        
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 0
    
    def test_single_tweet(self, sample_bullish_tweet):
        """Test pipeline with single tweet"""
        df = analyze_tweets([sample_bullish_tweet], calculate_signals=True)
        
        assert len(df) == 1
        assert 'signal_score' in df.columns
    
    def test_pipeline_preserves_original_data(self, sample_tweets):
        """Test that pipeline preserves original tweet data"""
        df = analyze_tweets(sample_tweets)
        
        # Original fields should be preserved
        assert 'tweet_id' in df.columns
        assert 'username' in df.columns
        assert 'content' in df.columns
        assert 'likes' in df.columns
        
        # Check IDs match
        original_ids = {t['tweet_id'] for t in sample_tweets}
        result_ids = set(df['tweet_id'])
        assert original_ids == result_ids
    
    def test_parallel_processing(self, sample_tweets):
        """Test parallel processing produces same results as sequential"""
        # Sequential
        df_seq = analyze_tweets(
            sample_tweets,
            parallel=False,
            calculate_signals=True
        )
        
        # Parallel
        df_par = analyze_tweets(
            sample_tweets,
            parallel=True,
            n_workers=2,
            calculate_signals=True
        )
        
        assert len(df_seq) == len(df_par)
        
        # Results should be similar (might have minor numerical differences)
        # Check signal labels are consistent for most tweets
        matches = sum(df_seq['signal_label'] == df_par['signal_label'])
        assert matches >= len(df_seq) * 0.8  # At least 80% should match


@pytest.mark.integration
def test_end_to_end_workflow(sample_tweets, tmp_path):
    """Test complete end-to-end workflow"""
    # Step 1: Analyze tweets
    df = analyze_tweets(
        sample_tweets,
        include_engagement=True,
        include_tfidf=True,
        calculate_signals=True
    )
    
    # Step 2: Save results
    output_file = tmp_path / "analyzed_tweets.parquet"
    df.to_parquet(output_file, index=False)
    
    assert output_file.exists()
    
    # Step 3: Load and verify
    df_loaded = pd.read_parquet(output_file)
    
    assert len(df_loaded) == len(sample_tweets)
    assert 'signal_score' in df_loaded.columns
    
    # Step 4: Aggregate signals
    signals = df_loaded.to_dict('records')
    aggregate = aggregate_signals(signals, min_confidence=0.3)
    
    assert 'aggregate_signal' in aggregate
    assert aggregate['num_tweets'] == len(sample_tweets)


@pytest.mark.integration
def test_mixed_quality_data(self):
    """Test pipeline with mixed quality data"""
    tweets = [
        # Good quality
        {
            'tweet_id': '001',
            'content': 'Nifty50 bullish breakout!',
            'likes': 100,
            'retweets': 50,
            'replies': 10,
            'views': 1000
        },
        # Zero engagement
        {
            'tweet_id': '002',
            'content': 'Market update',
            'likes': 0,
            'retweets': 0,
            'replies': 0,
            'views': 0
        },
        # Missing some fields
        {
            'tweet_id': '003',
            'content': 'Trading today',
            'likes': 5
        },
        # Very short content
        {
            'tweet_id': '004',
            'content': 'Hi',
            'likes': 1,
            'retweets': 0,
            'replies': 0,
            'views': 10
        }
    ]
    
    df = analyze_tweets(tweets, calculate_signals=True)
    
    # Should handle all tweets
    assert len(df) == len(tweets)
    
    # All should have signal scores
    assert all(df['signal_score'].notna())


@pytest.mark.integration
def test_language_mixed_pipeline(self, mixed_language_tweets):
    """Test pipeline handles multiple languages"""
    df = analyze_tweets(mixed_language_tweets, calculate_signals=True)
    
    assert len(df) == len(mixed_language_tweets)
    
    # All should have analysis results
    assert all(df['combined_sentiment_score'].notna())
    assert all(df['signal_label'].notna())


@pytest.mark.integration
@pytest.mark.slow
def test_large_batch_processing():
    """Test processing a large batch of tweets"""
    # Generate many tweets
    large_batch = []
    for i in range(100):
        large_batch.append({
            'tweet_id': f'tweet_{i}',
            'content': f'Market analysis tweet number {i}',
            'likes': i % 50,
            'retweets': i % 20,
            'replies': i % 10,
            'views': i * 10
        })
    
    df = analyze_tweets(large_batch, calculate_signals=True)
    
    assert len(df) == 100
    assert all(df['signal_score'].notna())


@pytest.mark.integration
def test_confidence_calculations(self, sample_tweets):
    """Test that confidence scores are calculated correctly"""
    df = analyze_tweets(sample_tweets, calculate_signals=True)
    
    # All tweets should have confidence
    assert all(df['confidence'].notna())
    
    # Confidence should be in [0, 1]
    assert all(df['confidence'] >= 0)
    assert all(df['confidence'] <= 1)
    
    # Confidence intervals should exist
    assert 'confidence_interval' in df.columns
    
    # Check confidence components if available
    if 'confidence_components' in df.columns:
        for components in df['confidence_components']:
            if components:
                assert 'content_quality' in components
                assert 'sentiment_strength' in components
                assert 'social_proof' in components


@pytest.mark.integration
def test_signal_filtering(self, sample_tweets):
    """Test filtering signals by confidence"""
    df = analyze_tweets(sample_tweets, calculate_signals=True)
    signals = df.to_dict('records')
    
    # Aggregate with different confidence thresholds
    agg_low = aggregate_signals(signals, min_confidence=0.1)
    agg_high = aggregate_signals(signals, min_confidence=0.7)
    
    # Higher threshold should use fewer tweets
    assert agg_high['num_valid_tweets'] <= agg_low['num_valid_tweets']

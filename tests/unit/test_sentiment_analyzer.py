"""
Unit tests for sentiment analysis functionality
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analysis.features import SentimentAnalyzer


@pytest.fixture
def analyzer():
    """Create SentimentAnalyzer with default config"""
    return SentimentAnalyzer(keyword_boost_weight=0.3)


@pytest.mark.unit
class TestSentimentAnalyzer:
    """Test suite for SentimentAnalyzer"""
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
        assert analyzer.keyword_boost_weight == 0.3
    
    def test_bullish_sentiment(self, analyzer):
        """Test bullish sentiment detection"""
        text = "Nifty breakout confirmed! Strong bullish momentum. Target hit! 🚀"
        result = analyzer.analyze(text)
        
        # Check structure
        assert 'base_sentiment_score' in result
        assert 'combined_sentiment_score' in result
        assert 'combined_sentiment_label' in result
        assert 'bullish_keyword_count' in result
        assert 'bearish_keyword_count' in result
        
        # Check bullish detection
        assert result['combined_sentiment_score'] > 0, "Should be positive sentiment"
        assert result['bullish_keyword_count'] >= 2, "Should detect bullish keywords"
        assert result['combined_sentiment_label'] in ['positive', 'bullish']
    
    def test_bearish_sentiment(self, analyzer):
        """Test bearish sentiment detection"""
        text = "Market crash! Dump everything! Bearish trend confirmed 📉"
        result = analyzer.analyze(text)
        
        assert result['combined_sentiment_score'] < 0, "Should be negative sentiment"
        assert result['bearish_keyword_count'] >= 2, "Should detect bearish keywords"
        assert result['combined_sentiment_label'] in ['negative', 'bearish']
    
    def test_neutral_sentiment(self, analyzer):
        """Test neutral sentiment detection"""
        text = "Market is trading in a range today."
        result = analyzer.analyze(text)
        
        assert abs(result['combined_sentiment_score']) < 0.3, "Should be neutral"
        assert result['combined_sentiment_label'] == 'neutral'
    
    def test_keyword_boost_increases_score(self, analyzer):
        """Test that bullish keywords boost positive sentiment"""
        text_without_keywords = "This is good news"
        text_with_keywords = "This is good news. Bullish breakout! Rally! Moon! 🚀"
        
        result_without = analyzer.analyze(text_without_keywords)
        result_with = analyzer.analyze(text_with_keywords)
        
        assert result_with['combined_sentiment_score'] > result_without['combined_sentiment_score']
        assert result_with['bullish_keyword_count'] > 0
    
    def test_confidence_score(self, analyzer):
        """Test that confidence score is calculated"""
        text = "Strong bullish breakout confirmed!"
        result = analyzer.analyze(text)
        
        assert 'base_confidence' in result
        assert 0 <= result['base_confidence'] <= 1
    
    def test_probabilities_sum_to_one(self, analyzer):
        """Test that sentiment probabilities sum to ~1"""
        text = "Market analysis today"
        result = analyzer.analyze(text)
        
        assert 'probabilities' in result
        probs = result['probabilities']
        total = probs['negative'] + probs['neutral'] + probs['positive']
        assert abs(total - 1.0) < 0.01, "Probabilities should sum to 1"
    
    def test_empty_text(self, analyzer):
        """Test handling of empty text"""
        result = analyzer.analyze("")
        
        assert result is not None
        assert 'combined_sentiment_score' in result
        # Should default to neutral for empty text
    
    def test_emojis_in_sentiment(self, analyzer):
        """Test that emojis are handled correctly"""
        bullish_emoji = "Market update 🚀 📈"
        bearish_emoji = "Market update 📉 💔"
        
        result_bullish = analyzer.analyze(bullish_emoji)
        result_bearish = analyzer.analyze(bearish_emoji)
        
        # Emojis should influence sentiment or be handled gracefully
        assert result_bullish is not None
        assert result_bearish is not None


@pytest.mark.unit
@pytest.mark.parametrize("text,expected_label", [
    ("Buy now! Moon! Rally! 🚀", "positive"),
    ("Crash! Dump! Sell panic!", "negative"),
    ("Market is flat today", "neutral"),
    ("Bullish breakout confirmed", "positive"),
    ("Bearish trend forming", "negative"),
])
def test_sentiment_labels_parametrized(analyzer, text, expected_label):
    """Parametrized test for various sentiment labels"""
    result = analyzer.analyze(text)
    
    # Allow some flexibility in labeling
    if expected_label == "positive":
        assert result['combined_sentiment_score'] > 0
    elif expected_label == "negative":
        assert result['combined_sentiment_score'] < 0
    else:  # neutral
        assert abs(result['combined_sentiment_score']) < 0.5


@pytest.mark.unit
def test_batch_analysis_consistency(analyzer, sample_tweets):
    """Test that batch analysis is consistent"""
    results = []
    for tweet in sample_tweets:
        result = analyzer.analyze(tweet['content'])
        results.append(result)
    
    assert len(results) == len(sample_tweets)
    
    # All results should have the same structure
    for result in results:
        assert 'combined_sentiment_score' in result
        assert 'combined_sentiment_label' in result
        assert 'bullish_keyword_count' in result
        assert 'bearish_keyword_count' in result


@pytest.mark.unit
def test_keyword_boost_weight_effect():
    """Test that keyword_boost_weight parameter affects results"""
    text = "Bullish breakout! Rally confirmed! Moon! 🚀"
    
    analyzer_low = SentimentAnalyzer(keyword_boost_weight=0.1)
    analyzer_high = SentimentAnalyzer(keyword_boost_weight=0.5)
    
    result_low = analyzer_low.analyze(text)
    result_high = analyzer_high.analyze(text)
    
    # Higher weight should increase impact of keywords
    assert result_high['keyword_boost'] > result_low['keyword_boost']


@pytest.mark.unit
def test_multilingual_handling(analyzer):
    """Test that analyzer handles non-English text gracefully"""
    texts = [
        "बाजार में तेजी है",  # Hindi
        "சந்தை நன்றாக உள்ளது",  # Tamil
        "市场很好",  # Chinese
    ]
    
    for text in texts:
        result = analyzer.analyze(text)
        assert result is not None
        assert 'combined_sentiment_score' in result
        # Should return some result, even if not accurate for non-English

"""
Unit tests for engagement metrics calculation
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from analysis.features import EngagementAnalyzer


@pytest.fixture
def analyzer():
    """Create EngagementAnalyzer instance"""
    return EngagementAnalyzer()


@pytest.mark.unit
class TestEngagementAnalyzer:
    """Test suite for EngagementAnalyzer"""
    
    def test_analyzer_initialization(self, analyzer):
        """Test that analyzer initializes correctly"""
        assert analyzer is not None
        assert hasattr(analyzer, 'analyze')
    
    def test_high_virality_tweet(self, analyzer):
        """Test high virality calculation (lots of retweets)"""
        tweet = {
            'likes': 100,
            'retweets': 50,
            'replies': 10,
            'views': 5000
        }
        
        result = analyzer.analyze(tweet)
        
        # Check structure
        assert 'total_engagement' in result
        assert 'engagement_rate' in result
        assert 'virality_ratio' in result
        assert 'virality_score' in result
        
        # Check values
        assert result['total_engagement'] == 160  # 100 + 50 + 10
        assert result['virality_score'] > 0.5, "High engagement should have high virality score"
        assert result['virality_ratio'] == 0.5  # 50 retweets / 100 likes
    
    def test_high_discussion_tweet(self, analyzer):
        """Test high discussion/controversy (lots of replies)"""
        tweet = {
            'likes': 80,
            'retweets': 10,
            'replies': 40,
            'views': 3000
        }
        
        result = analyzer.analyze(tweet)
        
        assert result['total_engagement'] == 130
        assert result['reply_ratio'] == 0.5  # 40 replies / 80 likes (controversy indicator)
        assert result['virality_score'] > 0.3
    
    def test_low_engagement_tweet(self, analyzer):
        """Test low engagement tweet"""
        tweet = {
            'likes': 5,
            'retweets': 1,
            'replies': 0,
            'views': 1000
        }
        
        result = analyzer.analyze(tweet)
        
        assert result['total_engagement'] == 6
        assert result['virality_score'] < 0.3, "Low engagement should have low virality score"
    
    def test_zero_engagement_tweet(self, analyzer):
        """Test zero engagement handling"""
        tweet = {
            'likes': 0,
            'retweets': 0,
            'replies': 0,
            'views': 0
        }
        
        result = analyzer.analyze(tweet)
        
        assert result['total_engagement'] == 0
        assert result['engagement_rate'] == 0
        assert result['virality_ratio'] == 0
        assert result['virality_score'] >= 0, "Virality score should not be negative"
    
    def test_engagement_rate_calculation(self, analyzer):
        """Test engagement rate per 1000 views"""
        tweet = {
            'likes': 100,
            'retweets': 50,
            'replies': 10,
            'views': 5000
        }
        
        result = analyzer.analyze(tweet)
        
        # 160 total engagement / 5000 views * 1000 = 32 per 1000 views
        expected_rate = (160 / 5000) * 1000
        assert abs(result['engagement_rate'] - expected_rate) < 0.01
    
    def test_engagement_rate_with_zero_views(self, analyzer):
        """Test that zero views doesn't cause division by zero"""
        tweet = {
            'likes': 10,
            'retweets': 5,
            'replies': 2,
            'views': 0
        }
        
        result = analyzer.analyze(tweet)
        
        # Should handle gracefully, not crash
        assert 'engagement_rate' in result
        assert result['engagement_rate'] >= 0
    
    def test_virality_ratio_calculation(self, analyzer):
        """Test virality ratio (retweets/likes)"""
        tweet = {
            'likes': 100,
            'retweets': 25,
            'replies': 5,
            'views': 1000
        }
        
        result = analyzer.analyze(tweet)
        
        assert result['virality_ratio'] == 0.25  # 25/100
    
    def test_virality_ratio_with_zero_likes(self, analyzer):
        """Test virality ratio when likes are zero"""
        tweet = {
            'likes': 0,
            'retweets': 10,
            'replies': 2,
            'views': 500
        }
        
        result = analyzer.analyze(tweet)
        
        # Should handle gracefully
        assert 'virality_ratio' in result
        assert result['virality_ratio'] >= 0
    
    def test_reply_ratio_calculation(self, analyzer):
        """Test reply ratio (replies/likes)"""
        tweet = {
            'likes': 100,
            'retweets': 20,
            'replies': 30,
            'views': 2000
        }
        
        result = analyzer.analyze(tweet)
        
        assert result['reply_ratio'] == 0.3  # 30/100
    
    def test_like_ratio_calculation(self, analyzer):
        """Test like ratio (likes/views)"""
        tweet = {
            'likes': 100,
            'retweets': 20,
            'replies': 10,
            'views': 10000
        }
        
        result = analyzer.analyze(tweet)
        
        assert abs(result['like_ratio'] - 0.01) < 0.001  # 100/10000
    
    def test_virality_score_range(self, analyzer):
        """Test that virality score is within 0-1 range"""
        test_cases = [
            {'likes': 0, 'retweets': 0, 'replies': 0, 'views': 0},
            {'likes': 10, 'retweets': 5, 'replies': 2, 'views': 100},
            {'likes': 1000, 'retweets': 500, 'replies': 100, 'views': 50000},
            {'likes': 10000, 'retweets': 5000, 'replies': 1000, 'views': 1000000},
        ]
        
        for tweet in test_cases:
            result = analyzer.analyze(tweet)
            assert 0 <= result['virality_score'] <= 1, \
                f"Virality score {result['virality_score']} out of range for {tweet}"


@pytest.mark.unit
@pytest.mark.parametrize("tweet,expected_category", [
    ({'likes': 1000, 'retweets': 500, 'replies': 100, 'views': 50000}, 'high'),
    ({'likes': 50, 'retweets': 10, 'replies': 5, 'views': 2000}, 'medium'),
    ({'likes': 2, 'retweets': 0, 'replies': 0, 'views': 100}, 'low'),
    ({'likes': 0, 'retweets': 0, 'replies': 0, 'views': 0}, 'zero'),
])
def test_engagement_categories(analyzer, tweet, expected_category):
    """Parametrized test for engagement categories"""
    result = analyzer.analyze(tweet)
    
    if expected_category == 'high':
        assert result['virality_score'] > 0.5
        assert result['total_engagement'] > 500
    elif expected_category == 'medium':
        assert 0.2 < result['virality_score'] < 0.7
        assert 20 < result['total_engagement'] < 500
    elif expected_category == 'low':
        assert result['virality_score'] < 0.3
        assert result['total_engagement'] < 20
    elif expected_category == 'zero':
        assert result['total_engagement'] == 0


@pytest.mark.unit
def test_missing_fields(analyzer):
    """Test handling of missing engagement fields"""
    tweet = {}  # Empty tweet
    
    result = analyzer.analyze(tweet)
    
    # Should handle gracefully with defaults
    assert result is not None
    assert 'total_engagement' in result
    assert 'virality_score' in result


@pytest.mark.unit
def test_batch_analysis(analyzer, sample_tweets):
    """Test analyzing multiple tweets"""
    results = []
    
    for tweet in sample_tweets:
        result = analyzer.analyze(tweet)
        results.append(result)
    
    assert len(results) == len(sample_tweets)
    
    # All results should have consistent structure
    for result in results:
        assert 'total_engagement' in result
        assert 'virality_score' in result
        assert 'engagement_rate' in result
        assert 'virality_ratio' in result


@pytest.mark.unit
def test_high_controversy_tweet(analyzer):
    """Test tweet with high controversy (many replies relative to likes)"""
    tweet = {
        'likes': 50,
        'retweets': 5,
        'replies': 100,  # More replies than likes = controversial
        'views': 3000
    }
    
    result = analyzer.analyze(tweet)
    
    assert result['reply_ratio'] > 1.0, "Reply ratio > 1 indicates controversy"
    assert result['total_engagement'] == 155


@pytest.mark.unit
def test_viral_but_no_discussion(analyzer):
    """Test viral tweet with low discussion (high retweets, low replies)"""
    tweet = {
        'likes': 5000,
        'retweets': 3000,
        'replies': 50,
        'views': 100000
    }
    
    result = analyzer.analyze(tweet)
    
    assert result['virality_ratio'] > 0.5, "High virality ratio"
    assert result['reply_ratio'] < 0.1, "Low reply ratio"
    assert result['virality_score'] > 0.7, "Should have high virality score"

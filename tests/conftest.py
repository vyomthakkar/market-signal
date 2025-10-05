"""
Pytest configuration and shared fixtures for all tests
"""

import pytest
import sys
from pathlib import Path
import pandas as pd

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


@pytest.fixture
def sample_tweets():
    """Generate sample tweets for testing"""
    return [
        {
            'tweet_id': '001',
            'username': 'trader_ram',
            'timestamp': '2025-10-04T10:00:00.000Z',
            'content': 'Bullish on #Nifty50! Strong breakout confirmed 🚀',
            'cleaned_content': 'Bullish on Nifty50 Strong breakout confirmed',
            'replies': 5,
            'retweets': 10,
            'likes': 25,
            'views': 100,
            'hashtags': ['Nifty50'],
            'mentions': [],
            'detected_language': 'en'
        },
        {
            'tweet_id': '002',
            'username': 'market_guru',
            'timestamp': '2025-10-04T11:00:00.000Z',
            'content': 'Market crash incoming! Sell everything! 📉',
            'cleaned_content': 'Market crash incoming Sell everything',
            'replies': 15,
            'retweets': 30,
            'likes': 50,
            'views': 500,
            'hashtags': ['MarketCrash'],
            'mentions': [],
            'detected_language': 'en'
        },
        {
            'tweet_id': '003',
            'username': 'neutral_trader',
            'timestamp': '2025-10-04T12:00:00.000Z',
            'content': 'Market is trading sideways today. No clear direction.',
            'cleaned_content': 'Market is trading sideways today No clear direction',
            'replies': 2,
            'retweets': 1,
            'likes': 5,
            'views': 50,
            'hashtags': ['Trading'],
            'mentions': [],
            'detected_language': 'en'
        },
        {
            'tweet_id': '004',
            'username': 'hindi_trader',
            'timestamp': '2025-10-04T13:00:00.000Z',
            'content': 'बाजार में तेजी है #Nifty50 #India',
            'cleaned_content': 'बाजार में तेजी है',
            'replies': 3,
            'retweets': 5,
            'likes': 12,
            'views': 80,
            'hashtags': ['Nifty50', 'India'],
            'mentions': [],
            'detected_language': 'hi'
        },
        {
            'tweet_id': '005',
            'username': 'low_engagement',
            'timestamp': '2025-10-04T14:00:00.000Z',
            'content': 'Just checking the market...',
            'cleaned_content': 'Just checking the market',
            'replies': 0,
            'retweets': 0,
            'likes': 0,
            'views': 0,
            'hashtags': [],
            'mentions': [],
            'detected_language': 'en'
        }
    ]


@pytest.fixture
def sample_bullish_tweet():
    """Single bullish tweet for testing"""
    return {
        'tweet_id': 'bull_001',
        'username': 'bull_trader',
        'content': 'Nifty breakout confirmed! Strong bullish momentum. Target hit! 🚀',
        'likes': 100,
        'retweets': 50,
        'replies': 10,
        'views': 1000,
        'hashtags': ['Nifty50', 'Bullish'],
        'mentions': []
    }


@pytest.fixture
def sample_bearish_tweet():
    """Single bearish tweet for testing"""
    return {
        'tweet_id': 'bear_001',
        'username': 'bear_trader',
        'content': 'Market crash! Dump everything! Bearish trend confirmed 📉',
        'likes': 80,
        'retweets': 40,
        'replies': 20,
        'views': 800,
        'hashtags': ['MarketCrash', 'Bearish'],
        'mentions': []
    }


@pytest.fixture
def sample_neutral_tweet():
    """Single neutral tweet for testing"""
    return {
        'tweet_id': 'neutral_001',
        'username': 'neutral_trader',
        'content': 'Market is trading in a range today. No clear direction.',
        'likes': 10,
        'retweets': 2,
        'replies': 1,
        'views': 100,
        'hashtags': ['Trading'],
        'mentions': []
    }


@pytest.fixture
def sample_dataframe(sample_tweets):
    """DataFrame with sample tweets"""
    return pd.DataFrame(sample_tweets)


@pytest.fixture
def temp_output_dir(tmp_path):
    """Temporary directory for test outputs"""
    output = tmp_path / "output"
    output.mkdir()
    return output


@pytest.fixture
def temp_parquet_file(sample_dataframe, tmp_path):
    """Temporary parquet file with sample data"""
    path = tmp_path / "test_tweets.parquet"
    sample_dataframe.to_parquet(path, index=False)
    return path


@pytest.fixture
def temp_json_file(sample_tweets, tmp_path):
    """Temporary JSON file with sample data"""
    import json
    path = tmp_path / "test_tweets.json"
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(sample_tweets, f, indent=2)
    return path


@pytest.fixture
def high_engagement_tweet():
    """Tweet with high engagement for testing"""
    return {
        'tweet_id': 'high_eng_001',
        'username': 'viral_trader',
        'content': 'Breaking news! This is huge!',
        'likes': 1000,
        'retweets': 500,
        'replies': 200,
        'views': 10000,
        'hashtags': ['Breaking'],
        'mentions': []
    }


@pytest.fixture
def zero_engagement_tweet():
    """Tweet with zero engagement for testing"""
    return {
        'tweet_id': 'zero_eng_001',
        'username': 'unknown_user',
        'content': 'Nobody sees this tweet',
        'likes': 0,
        'retweets': 0,
        'replies': 0,
        'views': 0,
        'hashtags': [],
        'mentions': []
    }


@pytest.fixture
def mixed_language_tweets():
    """Tweets in multiple languages"""
    return [
        {
            'tweet_id': 'en_001',
            'content': 'English tweet about markets',
            'detected_language': 'en',
            'likes': 10, 'retweets': 5, 'replies': 2, 'views': 100
        },
        {
            'tweet_id': 'hi_001',
            'content': 'हिंदी में बाजार की बात',
            'detected_language': 'hi',
            'likes': 15, 'retweets': 8, 'replies': 3, 'views': 150
        },
        {
            'tweet_id': 'ta_001',
            'content': 'தமிழ் சந்தை செய்தி',
            'detected_language': 'ta',
            'likes': 12, 'retweets': 6, 'replies': 1, 'views': 120
        }
    ]

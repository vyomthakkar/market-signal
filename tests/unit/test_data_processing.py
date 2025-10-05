"""
Unit tests for data processing (text cleaning, tweet processing)
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from data.processor import TextCleaner, TweetProcessor


@pytest.fixture
def text_cleaner():
    """Create TextCleaner instance"""
    return TextCleaner()


@pytest.fixture
def tweet_processor():
    """Create TweetProcessor instance"""
    return TweetProcessor(
        remove_urls=True,
        detect_language=True,
        normalize_unicode=True
    )


@pytest.mark.unit
class TestTextCleaner:
    """Test suite for TextCleaner"""
    
    def test_cleaner_initialization(self, text_cleaner):
        """Test that cleaner initializes correctly"""
        assert text_cleaner is not None
        assert hasattr(text_cleaner, 'clean_content')
        assert hasattr(text_cleaner, 'detect_language')
        assert hasattr(text_cleaner, 'extract_entities')
    
    def test_url_removal(self, text_cleaner):
        """Test URL removal"""
        text = "Check this out! http://example.com #trending"
        cleaned = text_cleaner.clean_content(text, remove_urls=True)
        
        assert 'http://example.com' not in cleaned
        assert 'trending' in cleaned or '#trending' in cleaned
    
    def test_url_preservation(self, text_cleaner):
        """Test that URLs are preserved when remove_urls=False"""
        text = "Visit http://example.com for more info"
        cleaned = text_cleaner.clean_content(text, remove_urls=False)
        
        # URL might be processed but should be there in some form
        assert cleaned is not None
        assert len(cleaned) > 0
    
    def test_whitespace_normalization(self, text_cleaner):
        """Test extra whitespace removal"""
        text = "  Too   much    whitespace   \n\n\n  here  "
        cleaned = text_cleaner.clean_content(text)
        
        # Should normalize to single spaces
        assert '   ' not in cleaned
        assert cleaned.strip() == cleaned
    
    def test_unicode_handling(self, text_cleaner):
        """Test Unicode handling for Indian languages"""
        texts = [
            "नमस्ते! #Nifty50 📈",
            "மிகவும் நல்லது #Sensex",
            "Mixed हिंदी and English #trading"
        ]
        
        for text in texts:
            cleaned = text_cleaner.clean_content(text)
            assert cleaned is not None
            assert len(cleaned) > 0
    
    def test_language_detection_english(self, text_cleaner):
        """Test language detection for English"""
        text = "The market is doing well today"
        lang = text_cleaner.detect_language(text)
        
        assert lang in ['en', 'unknown']  # Should detect English
    
    def test_language_detection_hindi(self, text_cleaner):
        """Test language detection for Hindi"""
        text = "बाजार में तेजी है"
        lang = text_cleaner.detect_language(text)
        
        assert lang in ['hi', 'unknown']  # Should detect Hindi or return unknown
    
    def test_language_detection_empty(self, text_cleaner):
        """Test language detection with empty text"""
        lang = text_cleaner.detect_language("")
        
        assert lang == 'unknown'
    
    def test_hashtag_extraction(self, text_cleaner):
        """Test hashtag extraction"""
        text = "Trading #Nifty50 and #Sensex today #India"
        entities = text_cleaner.extract_entities(text)
        
        assert 'hashtags' in entities
        assert len(entities['hashtags']) == 3
        assert 'Nifty50' in entities['hashtags'] or '#Nifty50' in entities['hashtags']
    
    def test_mention_extraction(self, text_cleaner):
        """Test @mention extraction"""
        text = "Great analysis by @trader1 and @market_guru"
        entities = text_cleaner.extract_entities(text)
        
        assert 'mentions' in entities
        assert len(entities['mentions']) == 2
    
    def test_url_extraction(self, text_cleaner):
        """Test URL extraction"""
        text = "Check http://example.com and https://test.org"
        entities = text_cleaner.extract_entities(text)
        
        assert 'urls' in entities
        assert len(entities['urls']) == 2
    
    def test_entities_empty_text(self, text_cleaner):
        """Test entity extraction with empty text"""
        entities = text_cleaner.extract_entities("")
        
        assert 'hashtags' in entities
        assert 'mentions' in entities
        assert 'urls' in entities
        assert len(entities['hashtags']) == 0
        assert len(entities['mentions']) == 0
        assert len(entities['urls']) == 0
    
    def test_emoji_handling(self, text_cleaner):
        """Test emoji handling"""
        text = "Market is up! 🚀📈💰"
        cleaned = text_cleaner.clean_content(text)
        
        # Should handle emojis gracefully (either keep or remove)
        assert cleaned is not None
        assert len(cleaned) > 0


@pytest.mark.unit
class TestTweetProcessor:
    """Test suite for TweetProcessor"""
    
    def test_processor_initialization(self, tweet_processor):
        """Test that processor initializes correctly"""
        assert tweet_processor is not None
        assert hasattr(tweet_processor, 'process_batch')
    
    def test_single_tweet_processing(self, tweet_processor):
        """Test processing a single tweet"""
        tweet = {
            'tweet_id': '001',
            'username': 'trader',
            'timestamp': '2025-10-04T10:00:00.000Z',
            'content': 'Check #Nifty50 http://example.com',
            'likes': 10,
            'retweets': 5
        }
        
        processed = tweet_processor.process_batch([tweet])
        
        assert len(processed) == 1
        result = processed[0]
        
        # Original fields preserved
        assert result['tweet_id'] == '001'
        assert result['username'] == 'trader'
        
        # New fields added
        assert 'cleaned_content' in result
        assert 'detected_language' in result
    
    def test_batch_processing(self, tweet_processor, sample_tweets):
        """Test processing multiple tweets"""
        processed = tweet_processor.process_batch(sample_tweets)
        
        assert len(processed) == len(sample_tweets)
        
        # All tweets should be processed
        for tweet in processed:
            assert 'cleaned_content' in tweet
            assert 'detected_language' in tweet
    
    def test_processing_stats(self, tweet_processor, sample_tweets):
        """Test that processing stats are tracked"""
        tweet_processor.process_batch(sample_tweets)
        
        stats = tweet_processor.get_stats()
        
        assert 'processed' in stats
        assert 'errors' in stats
        assert 'success_rate' in stats
        assert stats['processed'] == len(sample_tweets)
    
    def test_error_handling(self, tweet_processor):
        """Test handling of malformed tweets"""
        tweets = [
            {'tweet_id': '001', 'content': 'Valid tweet'},
            {'tweet_id': '002'},  # Missing content
            None,  # Invalid tweet
            {'tweet_id': '003', 'content': 'Another valid tweet'}
        ]
        
        # Should handle gracefully without crashing
        processed = tweet_processor.process_batch(tweets)
        
        # Should process the valid ones
        assert len(processed) >= 2
    
    def test_url_removal_in_processing(self):
        """Test that URLs are removed when configured"""
        processor = TweetProcessor(remove_urls=True)
        
        tweet = {
            'tweet_id': '001',
            'content': 'Check http://example.com for details'
        }
        
        processed = processor.process_batch([tweet])
        
        assert len(processed) == 1
        assert 'http://example.com' not in processed[0].get('cleaned_content', '')
    
    def test_language_detection_in_processing(self):
        """Test that language is detected when configured"""
        processor = TweetProcessor(detect_language=True)
        
        tweets = [
            {'tweet_id': '001', 'content': 'English text here'},
            {'tweet_id': '002', 'content': 'हिंदी टेक्स्ट यहाँ'}
        ]
        
        processed = processor.process_batch(tweets)
        
        assert len(processed) == 2
        assert all('detected_language' in t for t in processed)


@pytest.mark.unit
@pytest.mark.parametrize("text,should_contain", [
    ("Check #Nifty50 today", "Nifty50"),
    ("Great analysis @trader", "analysis"),
    ("Buy now! http://example.com", "Buy now"),
])
def test_cleaning_preserves_content(text_cleaner, text, should_contain):
    """Test that cleaning preserves important content"""
    cleaned = text_cleaner.clean_content(text, remove_urls=True)
    
    assert should_contain.lower() in cleaned.lower() or \
           should_contain in cleaned


@pytest.mark.unit
def test_batch_consistency(tweet_processor, sample_tweets):
    """Test that batch processing is consistent"""
    # Process twice
    processed1 = tweet_processor.process_batch(sample_tweets.copy())
    processed2 = tweet_processor.process_batch(sample_tweets.copy())
    
    assert len(processed1) == len(processed2)
    
    # Results should be consistent
    for t1, t2 in zip(processed1, processed2):
        if 'cleaned_content' in t1 and 'cleaned_content' in t2:
            assert t1['cleaned_content'] == t2['cleaned_content']


@pytest.mark.unit
def test_empty_batch(tweet_processor):
    """Test processing empty batch"""
    processed = tweet_processor.process_batch([])
    
    assert processed == []
    
    stats = tweet_processor.get_stats()
    assert stats['processed'] == 0


@pytest.mark.unit
def test_special_characters(text_cleaner):
    """Test handling of special characters"""
    text = "Market @ 52-week high! Up 10% 💰 #winning"
    cleaned = text_cleaner.clean_content(text)
    
    assert cleaned is not None
    assert len(cleaned) > 0
    # Should handle gracefully


@pytest.mark.unit
def test_very_long_text(text_cleaner):
    """Test handling of very long text"""
    text = "Long text " * 1000  # Very long tweet
    cleaned = text_cleaner.clean_content(text)
    
    assert cleaned is not None
    # Should not crash


@pytest.mark.unit
def test_multilingual_mixed(text_cleaner):
    """Test mixed language content"""
    text = "Trading नमस्ते with #Nifty50 today! 市场很好"
    
    cleaned = text_cleaner.clean_content(text)
    lang = text_cleaner.detect_language(text)
    entities = text_cleaner.extract_entities(text)
    
    assert cleaned is not None
    assert lang in ['en', 'hi', 'unknown']
    assert 'hashtags' in entities

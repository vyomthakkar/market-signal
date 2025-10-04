"""
Data Processing & Cleaning Module

Handles:
- Text cleaning and normalization
- Unicode normalization for Indian languages
- URL extraction and cleaning
- Timestamp standardization
- Content validation
- Language detection
"""

import re
import unicodedata
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import logging

try:
    from langdetect import detect, LangDetectException
except ImportError:
    detect = None
    LangDetectException = Exception

logger = logging.getLogger(__name__)


class TextCleaner:
    """
    Production-ready text cleaning for Twitter data with Indian language support.
    
    Features:
    - Unicode normalization (NFKC)
    - URL extraction and removal
    - Whitespace normalization
    - Emoji handling
    - Mixed-script content support (English + Hindi/regional)
    - Special character normalization
    """
    
    # Regex patterns
    URL_PATTERN = re.compile(
        r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    )
    TWITTER_URL_PATTERN = re.compile(r'(?:http[s]?://)?(?:www\.)?(?:twitter\.com|x\.com)/\S+')
    MENTION_PATTERN = re.compile(r'@\w+')
    HASHTAG_PATTERN = re.compile(r'#\w+')
    EXTRA_WHITESPACE = re.compile(r'\s+')
    
    @staticmethod
    def normalize_unicode(text: str) -> str:
        """
        Normalize Unicode characters using NFKC normalization.
        
        NFKC (Compatibility Composition) is ideal for:
        - Indian language scripts (Devanagari, Tamil, Telugu, etc.)
        - Mixed English-Hindi content
        - Emoji normalization
        
        Args:
            text: Input text
            
        Returns:
            Unicode-normalized text
        """
        if not text:
            return text
        
        # NFKC normalization: compatibility decomposition followed by canonical composition
        normalized = unicodedata.normalize('NFKC', text)
        return normalized
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract all URLs from text"""
        if not text:
            return []
        
        urls = TextCleaner.URL_PATTERN.findall(text)
        return urls
    
    @staticmethod
    def remove_urls(text: str, replacement: str = '') -> str:
        """
        Remove URLs from text.
        
        Args:
            text: Input text
            replacement: String to replace URLs with (default: empty string)
            
        Returns:
            Text with URLs removed
        """
        if not text:
            return text
        
        # Remove standard URLs
        text = TextCleaner.URL_PATTERN.sub(replacement, text)
        # Remove Twitter-specific URLs
        text = TextCleaner.TWITTER_URL_PATTERN.sub(replacement, text)
        return text
    
    @staticmethod
    def normalize_whitespace(text: str) -> str:
        """
        Normalize whitespace: remove extra spaces, tabs, newlines.
        Preserves single spaces between words.
        """
        if not text:
            return text
        
        # Replace multiple whitespace with single space
        text = TextCleaner.EXTRA_WHITESPACE.sub(' ', text)
        # Strip leading/trailing whitespace
        text = text.strip()
        return text
    
    @staticmethod
    def clean_content(
        text: str,
        remove_urls: bool = True,
        remove_mentions: bool = False,
        remove_hashtags: bool = False,
        normalize_unicode: bool = True,
        normalize_whitespace: bool = True
    ) -> str:
        """
        Comprehensive text cleaning pipeline.
        
        Args:
            text: Input text
            remove_urls: Remove URLs (default: True)
            remove_mentions: Remove @mentions (default: False, kept for context)
            remove_hashtags: Remove #hashtags (default: False, kept for analysis)
            normalize_unicode: Apply Unicode normalization (default: True)
            normalize_whitespace: Normalize whitespace (default: True)
            
        Returns:
            Cleaned text
        """
        if not text:
            return text
        
        # 1. Unicode normalization (handle Indian languages first)
        if normalize_unicode:
            text = TextCleaner.normalize_unicode(text)
        
        # 2. Remove URLs (often spam or promotional)
        if remove_urls:
            text = TextCleaner.remove_urls(text)
        
        # 3. Optionally remove mentions
        if remove_mentions:
            text = TextCleaner.MENTION_PATTERN.sub('', text)
        
        # 4. Optionally remove hashtags
        if remove_hashtags:
            text = TextCleaner.HASHTAG_PATTERN.sub('', text)
        
        # 5. Normalize whitespace
        if normalize_whitespace:
            text = TextCleaner.normalize_whitespace(text)
        
        return text
    
    @staticmethod
    def detect_language(text: str) -> Optional[str]:
        """
        Detect language of text.
        
        Returns:
            ISO 639-1 language code (e.g., 'en', 'hi', 'ta') or None if detection fails
        """
        if not text or not detect:
            return None
        
        try:
            # Remove URLs and mentions for better detection
            clean_text = TextCleaner.remove_urls(text)
            clean_text = TextCleaner.MENTION_PATTERN.sub('', clean_text)
            clean_text = TextCleaner.HASHTAG_PATTERN.sub('', clean_text)
            
            if len(clean_text.strip()) < 10:
                return None
            
            lang = detect(clean_text)
            return lang
        except (LangDetectException, Exception) as e:
            logger.debug(f"Language detection failed: {e}")
            return None
    
    @staticmethod
    def extract_entities(text: str) -> Dict[str, List[str]]:
        """
        Extract entities (mentions, hashtags, URLs) from text.
        
        Returns:
            Dictionary with 'mentions', 'hashtags', 'urls' keys
        """
        if not text:
            return {'mentions': [], 'hashtags': [], 'urls': []}
        
        mentions = [m.lstrip('@') for m in TextCleaner.MENTION_PATTERN.findall(text)]
        hashtags = [h.lstrip('#') for h in TextCleaner.HASHTAG_PATTERN.findall(text)]
        urls = TextCleaner.extract_urls(text)
        
        return {
            'mentions': mentions,
            'hashtags': hashtags,
            'urls': urls
        }


class TweetProcessor:
    """
    Process raw tweet data into clean, normalized format.
    
    Handles:
    - Content cleaning
    - Timestamp parsing and normalization
    - Entity extraction
    - Data validation
    - Language detection
    """
    
    def __init__(
        self,
        remove_urls: bool = True,
        detect_language: bool = True,
        normalize_unicode: bool = True
    ):
        """
        Initialize processor with configuration.
        
        Args:
            remove_urls: Remove URLs from content (default: True)
            detect_language: Detect tweet language (default: True)
            normalize_unicode: Apply Unicode normalization (default: True)
        """
        self.remove_urls = remove_urls
        self.detect_language_flag = detect_language
        self.normalize_unicode = normalize_unicode
        self.cleaner = TextCleaner()
        
        # Statistics
        self.processed_count = 0
        self.error_count = 0
    
    def process_tweet(self, raw_tweet: Dict) -> Dict:
        """
        Process a single raw tweet.
        
        Args:
            raw_tweet: Raw tweet dictionary from scraper
            
        Returns:
            Processed tweet dictionary with cleaned fields
        """
        try:
            processed = raw_tweet.copy()
            
            # 1. Clean content (keep original for reference)
            if 'content' in processed and processed['content']:
                original_content = processed['content']
                
                # Clean the content
                cleaned_content = self.cleaner.clean_content(
                    original_content,
                    remove_urls=self.remove_urls,
                    remove_mentions=False,  # Keep mentions for analysis
                    remove_hashtags=False,  # Keep hashtags for analysis
                    normalize_unicode=self.normalize_unicode,
                    normalize_whitespace=True
                )
                
                processed['cleaned_content'] = cleaned_content
                
                # Detect language
                if self.detect_language_flag:
                    detected_lang = self.cleaner.detect_language(original_content)
                    processed['detected_language'] = detected_lang or 'unknown'
                
                # Extract URLs separately
                urls = self.cleaner.extract_urls(original_content)
                processed['extracted_urls'] = urls
            
            # 2. Normalize timestamp
            if 'timestamp' in processed and processed['timestamp']:
                processed['timestamp'] = self._normalize_timestamp(processed['timestamp'])
            
            # 3. Add processing metadata
            processed['processed_at'] = datetime.utcnow().isoformat()
            
            # 4. Ensure all numeric fields are integers
            for field in ['replies', 'retweets', 'likes', 'views']:
                if field in processed:
                    try:
                        processed[field] = int(processed[field]) if processed[field] else 0
                    except (ValueError, TypeError):
                        processed[field] = 0
            
            # 5. Normalize hashtags and mentions (lowercase, no symbols)
            if 'hashtags' in processed:
                processed['hashtags'] = [
                    h.lstrip('#').lower() for h in processed.get('hashtags', [])
                ]
            
            if 'mentions' in processed:
                processed['mentions'] = [
                    m.lstrip('@').lower() for m in processed.get('mentions', [])
                ]
            
            self.processed_count += 1
            return processed
            
        except Exception as e:
            logger.error(f"Error processing tweet {raw_tweet.get('tweet_id', 'unknown')}: {e}")
            self.error_count += 1
            # Return original tweet with error flag
            raw_tweet['processing_error'] = str(e)
            return raw_tweet
    
    def process_batch(self, raw_tweets: List[Dict]) -> List[Dict]:
        """
        Process a batch of tweets.
        
        Args:
            raw_tweets: List of raw tweet dictionaries
            
        Returns:
            List of processed tweet dictionaries
        """
        processed_tweets = []
        
        for tweet in raw_tweets:
            processed = self.process_tweet(tweet)
            processed_tweets.append(processed)
        
        logger.info(f"Processed {self.processed_count} tweets, {self.error_count} errors")
        
        return processed_tweets
    
    def _normalize_timestamp(self, timestamp: str) -> str:
        """
        Normalize timestamp to ISO 8601 format.
        
        Args:
            timestamp: Raw timestamp string
            
        Returns:
            ISO 8601 formatted timestamp
        """
        try:
            # Handle various timestamp formats
            if isinstance(timestamp, datetime):
                return timestamp.isoformat()
            
            # Try parsing ISO format
            if 'T' in timestamp:
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                return dt.isoformat()
            
            # If already good format, return as is
            return timestamp
            
        except Exception as e:
            logger.debug(f"Could not parse timestamp '{timestamp}': {e}")
            return timestamp
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return {
            'processed': self.processed_count,
            'errors': self.error_count,
            'success_rate': (
                (self.processed_count - self.error_count) / self.processed_count * 100
                if self.processed_count > 0 else 0
            )
        }


def process_tweets(
    tweets: List[Dict],
    remove_urls: bool = True,
    detect_language: bool = True
) -> Tuple[List[Dict], Dict]:
    """
    Convenience function to process tweets and get statistics.
    
    Args:
        tweets: List of raw tweet dictionaries
        remove_urls: Remove URLs from content
        detect_language: Detect tweet language
        
    Returns:
        Tuple of (processed_tweets, statistics)
    """
    processor = TweetProcessor(
        remove_urls=remove_urls,
        detect_language=detect_language
    )
    
    processed = processor.process_batch(tweets)
    stats = processor.get_stats()
    
    return processed, stats


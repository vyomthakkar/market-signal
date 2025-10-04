"""
Efficient tweet collection with O(1) deduplication.

Replaces O(n) list lookups with O(1) set lookups for massive performance gain.
"""
from typing import List, Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)


class TweetCollector:
    """
    Efficient tweet collector with set-based deduplication.
    
    Time Complexity:
        - add(): O(1) - set lookup
        - get_all(): O(1) - return reference
        - get_count(): O(1) - len() on list
    
    Space Complexity: O(n) where n = number of unique tweets
    
    Example:
        collector = TweetCollector()
        
        if collector.add(tweet):
            print("New tweet added!")
        else:
            print("Duplicate tweet skipped")
        
        print(f"Collected {collector.get_count()} unique tweets")
    """
    
    def __init__(self):
        self.tweets: List[Dict] = []  # Store tweets (maintains order)
        self.seen_ids: Set[str] = set()  # Track seen IDs (O(1) lookup)
        self.duplicate_count: int = 0  # Track duplicates
    
    def add(self, tweet: Dict) -> bool:
        """
        Add tweet to collection if not duplicate.
        
        Args:
            tweet: Tweet dictionary with at least 'tweet_id' field
        
        Returns:
            True if added (new tweet), False if duplicate
        
        Raises:
            ValueError: If tweet doesn't have 'tweet_id' field
        """
        if 'tweet_id' not in tweet:
            raise ValueError("Tweet must have 'tweet_id' field")
        
        tweet_id = tweet['tweet_id']
        
        # O(1) lookup in set!
        if tweet_id in self.seen_ids:
            self.duplicate_count += 1
            return False
        
        # New tweet - add to both structures
        self.seen_ids.add(tweet_id)
        self.tweets.append(tweet)
        return True
    
    def get_all(self) -> List[Dict]:
        """Get all collected tweets"""
        return self.tweets
    
    def get_count(self) -> int:
        """Get number of unique tweets collected"""
        return len(self.tweets)
    
    def get_stats(self) -> Dict:
        """Get collection statistics"""
        return {
            'unique_tweets': len(self.tweets),
            'duplicates_skipped': self.duplicate_count,
            'total_processed': len(self.tweets) + self.duplicate_count,
            'deduplication_rate': (
                self.duplicate_count / (len(self.tweets) + self.duplicate_count) * 100
                if (len(self.tweets) + self.duplicate_count) > 0 else 0
            )
        }
    
    def clear(self):
        """Clear all collected tweets"""
        self.tweets.clear()
        self.seen_ids.clear()
        self.duplicate_count = 0
    
    def __len__(self):
        return len(self.tweets)
    
    def __repr__(self):
        return f"TweetCollector(unique={len(self.tweets)}, duplicates={self.duplicate_count})"


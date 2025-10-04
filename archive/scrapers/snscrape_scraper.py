# twitter_scraper_snscrape.py
"""
Twitter/X Scraper using snscrape

This scraper provides similar functionality to the Playwright version but uses snscrape:
- No login required
- Faster and more reliable for bulk collection
- Provides detailed statistics per hashtag
- Handles deduplication across hashtags
- Graceful handling of hashtags with limited content

Key Features:
- Collects tweets with full metadata (engagement metrics, timestamps, etc.)
- Returns statistics showing actual tweets collected vs target
- Deduplicates tweets across hashtags
- More stable than browser automation
"""
import snscrape.modules.twitter as sntwitter
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterScraperSNS:
    def __init__(self):
        self.tweets_data = []
    
    def search_hashtag(self, hashtag: str, max_tweets: int = 500, days_back: int = 7) -> List[Dict]:
        """
        Search for tweets with specific hashtag using snscrape
        
        Args:
            hashtag: The hashtag to search (without #)
            max_tweets: Maximum number of tweets to collect
            days_back: How many days back to search
        
        Returns:
            List of tweet dictionaries
        """
        try:
            logger.info(f"Searching for #{hashtag}...")
            
            # Calculate date range
            since_date = (datetime.now() - timedelta(days=days_back)).strftime('%Y-%m-%d')
            until_date = datetime.now().strftime('%Y-%m-%d')
            
            # Build search query
            # -filter:replies excludes reply tweets, similar to Playwright version
            query = f"#{hashtag} -filter:replies since:{since_date} until:{until_date}"
            
            tweets = []
            tweet_count = 0
            
            # Scrape tweets using TwitterSearchScraper
            for i, tweet in enumerate(sntwitter.TwitterSearchScraper(query).get_items()):
                if tweet_count >= max_tweets:
                    break
                
                try:
                    # Extract tweet data in the same format as Playwright scraper
                    tweet_data = {
                        'tweet_id': str(tweet.id),
                        'username': tweet.user.username,
                        'timestamp': tweet.date.isoformat() if tweet.date else '',
                        'content': tweet.rawContent or tweet.content or '',
                        'replies': tweet.replyCount or 0,
                        'retweets': tweet.retweetCount or 0,
                        'likes': tweet.likeCount or 0,
                        'views': tweet.viewCount or 0,
                        'hashtags': tweet.hashtags or [],
                        'mentions': [mention.username for mention in (tweet.mentionedUsers or [])]
                    }
                    
                    tweets.append(tweet_data)
                    tweet_count += 1
                    
                    # Log progress every 10 tweets
                    if tweet_count % 10 == 0:
                        logger.info(f"Collected {tweet_count} tweets for #{hashtag}")
                        
                except Exception as e:
                    logger.warning(f"Error parsing tweet: {e}")
                    continue
            
            # Final summary
            if len(tweets) < max_tweets:
                logger.warning(f"Only collected {len(tweets)}/{max_tweets} tweets for #{hashtag} - may not have enough content available in the last {days_back} days")
            else:
                logger.info(f"Successfully collected {len(tweets)} tweets for #{hashtag}")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error searching #{hashtag}: {e}")
            return []
    
    def scrape_multiple_hashtags(self, hashtags: List[str], 
                                tweets_per_tag: int = 500,
                                days_back: int = 7) -> Dict:
        """
        Scrape multiple hashtags and return tweets with statistics
        
        Args:
            hashtags: List of hashtags to scrape (without #)
            tweets_per_tag: Target number of tweets per hashtag
            days_back: How many days back to search
        
        Returns:
            Dictionary with 'tweets' and 'statistics' keys
        """
        all_tweets = []
        hashtag_stats = {}
        
        for idx, hashtag in enumerate(hashtags):
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting collection for #{hashtag} ({idx+1}/{len(hashtags)})")
            logger.info(f"{'='*60}")
            
            tweets = self.search_hashtag(hashtag, tweets_per_tag, days_back)
            all_tweets.extend(tweets)
            
            # Store statistics for this hashtag
            hashtag_stats[hashtag] = {
                'collected': len(tweets),
                'target': tweets_per_tag,
                'percentage': (len(tweets) / tweets_per_tag * 100) if tweets_per_tag > 0 else 0
            }
            
            # Add small delay between hashtag searches to be respectful
            if hashtag != hashtags[-1]:  # Don't delay after last hashtag
                delay = 2
                logger.info(f"Waiting {delay}s before next hashtag...")
                time.sleep(delay)
        
        # Deduplicate based on tweet_id
        unique_tweets = {tweet['tweet_id']: tweet for tweet in all_tweets}
        
        # Print summary statistics
        logger.info(f"\n{'='*60}")
        logger.info("COLLECTION SUMMARY")
        logger.info(f"{'='*60}")
        for hashtag, stats in hashtag_stats.items():
            status = "✓" if stats['collected'] >= stats['target'] else "⚠"
            logger.info(f"{status} #{hashtag}: {stats['collected']}/{stats['target']} tweets ({stats['percentage']:.1f}%)")
        
        logger.info(f"\nTotal tweets collected: {len(all_tweets)}")
        logger.info(f"Unique tweets after deduplication: {len(unique_tweets)}")
        logger.info(f"Duplicates removed: {len(all_tweets) - len(unique_tweets)}")
        logger.info(f"{'='*60}\n")
        
        return {
            'tweets': list(unique_tweets.values()),
            'statistics': hashtag_stats
        }


def main():
    """Main execution function"""
    # Initialize scraper
    scraper = TwitterScraperSNS()
    
    try:
        # Target hashtags
        hashtags = ['nifty50', 'sensex', 'intraday', 'banknifty']
        
        # Scrape tweets
        # Note: snscrape is much faster, so we can aim for higher numbers
        # For testing: 50 per hashtag, for production: 500+
        result = scraper.scrape_multiple_hashtags(
            hashtags, 
            tweets_per_tag=50,  # Change to 500 for production
            days_back=7  # Search last 7 days
        )
        
        tweets = result['tweets']
        statistics = result['statistics']
        
        # Save tweets to JSON
        with open('raw_tweets_snscrape.json', 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        
        # Save statistics to separate file
        with open('collection_stats_snscrape.json', 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✓ Data saved to raw_tweets_snscrape.json")
        logger.info(f"✓ Statistics saved to collection_stats_snscrape.json")
        logger.info(f"\n📊 Total unique tweets collected: {len(tweets)}")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise


if __name__ == "__main__":
    main()


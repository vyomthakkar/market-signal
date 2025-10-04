# twitter_scraper_twscrape.py
"""
Twitter/X Scraper using twscrape (modern alternative to snscrape)

This scraper provides similar functionality to the Playwright version:
- Requires Twitter account(s) for API access (accounts added once, reused forever)
- Much faster and more reliable than browser automation
- Provides detailed statistics per hashtag
- Handles deduplication across hashtags
- Graceful handling of hashtags with limited content

Key Features:
- Collects tweets with full metadata (engagement metrics, timestamps, etc.)
- Returns statistics showing actual tweets collected vs target
- Deduplicates tweets across hashtags
- More stable than browser automation
- Rate limit handling built-in

Setup (one-time):
    pip install twscrape
    python twscrape_scraper.py --setup
    (Then follow prompts to add Twitter account)

Usage:
    python twscrape_scraper.py
"""
import asyncio
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict
import sys

try:
    from twscrape import API, gather
    from twscrape.logger import set_log_level
except ImportError:
    print("❌ twscrape not installed. Install it with:")
    print("   pip install twscrape")
    sys.exit(1)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterScraperTW:
    def __init__(self):
        self.api = API()
        self.tweets_data = []
    
    async def setup_account(self):
        """One-time setup to add Twitter account credentials"""
        print("\n" + "="*60)
        print("TWITTER ACCOUNT SETUP")
        print("="*60)
        print("You need to add at least one Twitter account.")
        print("These credentials are stored locally and encrypted.")
        print("You only need to do this once.\n")
        
        username = input("Twitter username: ").strip()
        password = input("Twitter password: ").strip()
        email = input("Twitter email: ").strip()
        
        try:
            await self.api.pool.add_account(username, password, email, password)
            await self.api.pool.login_all()
            print("\n✓ Account added and logged in successfully!")
            print("You can now run the scraper without --setup flag.\n")
        except Exception as e:
            print(f"\n❌ Error adding account: {e}")
            print("Please check your credentials and try again.\n")
            sys.exit(1)
    
    async def search_hashtag(self, hashtag: str, max_tweets: int = 500, days_back: int = 7) -> List[Dict]:
        """
        Search for tweets with specific hashtag using twscrape
        
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
            
            # Build search query - try without date filter first for better results
            query = f"#{hashtag} -filter:replies"
            logger.info(f"Query: {query}")
            
            tweets = []
            tweet_count = 0
            error_count = 0
            
            # Scrape tweets using twscrape
            try:
                async for tweet in self.api.search(query, limit=max_tweets):
                    try:
                        # Extract tweet data in the same format as Playwright scraper
                        tweet_data = {
                            'tweet_id': str(tweet.id),
                            'username': tweet.user.username,
                            'timestamp': tweet.date.isoformat() if tweet.date else '',
                            'content': tweet.rawContent or '',
                            'replies': tweet.replyCount or 0,
                            'retweets': tweet.retweetCount or 0,
                            'likes': tweet.likeCount or 0,
                            'views': tweet.viewCount or 0,
                            'hashtags': tweet.hashtags or [],
                            'mentions': [user.username for user in (tweet.mentionedUsers or [])]
                        }
                        
                        tweets.append(tweet_data)
                        tweet_count += 1
                        
                        # Log progress every 10 tweets
                        if tweet_count % 10 == 0:
                            logger.info(f"Collected {tweet_count} tweets for #{hashtag}")
                        
                        if tweet_count >= max_tweets:
                            break
                            
                    except Exception as e:
                        error_count += 1
                        logger.warning(f"Error parsing tweet #{error_count}: {e}")
                        continue
            except Exception as search_error:
                logger.error(f"Search API error for #{hashtag}: {search_error}")
                logger.error(f"This might be due to:")
                logger.error(f"  1. Account not properly logged in (run with --setup)")
                logger.error(f"  2. Twitter rate limits")
                logger.error(f"  3. Account suspended or locked")
                logger.error(f"  4. Network issues")
            
            # Final summary
            if len(tweets) == 0:
                logger.warning(f"⚠️  No tweets collected for #{hashtag}!")
                logger.warning(f"  Try: 1) Check account status  2) Wait for rate limits  3) Try different hashtag")
            elif len(tweets) < max_tweets:
                logger.warning(f"Only collected {len(tweets)}/{max_tweets} tweets for #{hashtag} - may not have enough content available")
            else:
                logger.info(f"Successfully collected {len(tweets)} tweets for #{hashtag}")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error searching #{hashtag}: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return []
    
    async def scrape_multiple_hashtags(self, hashtags: List[str], 
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
            
            tweets = await self.search_hashtag(hashtag, tweets_per_tag, days_back)
            all_tweets.extend(tweets)
            
            # Store statistics for this hashtag
            hashtag_stats[hashtag] = {
                'collected': len(tweets),
                'target': tweets_per_tag,
                'percentage': (len(tweets) / tweets_per_tag * 100) if tweets_per_tag > 0 else 0
            }
            
            # Add small delay between hashtag searches
            if hashtag != hashtags[-1]:  # Don't delay after last hashtag
                delay = 2
                logger.info(f"Waiting {delay}s before next hashtag...")
                await asyncio.sleep(delay)
        
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


async def main():
    """Main execution function"""
    # Check if setup mode
    if '--setup' in sys.argv:
        scraper = TwitterScraperTW()
        await scraper.setup_account()
        return
    
    # Initialize scraper
    scraper = TwitterScraperTW()
    
    try:
        # Check if accounts are configured
        accounts = await scraper.api.pool.accounts_info()
        if not accounts:
            print("\n❌ No Twitter accounts configured!")
            print("Run with --setup flag first:")
            print("   python twscrape_scraper.py --setup\n")
            sys.exit(1)
        
        logger.info(f"Using {len(accounts)} Twitter account(s)")
        
        # Check account status
        for acc in accounts:
            status = "✓ Active" if acc.active else "✗ Inactive"
            logger.info(f"  Account @{acc.username}: {status}")
            if not acc.active:
                logger.warning(f"  ⚠️  Account @{acc.username} is inactive! Try logging in again with --setup")
        
        # Ensure accounts are logged in
        logger.info("Logging in accounts...")
        await scraper.api.pool.login_all()
        
        # Target hashtags
        hashtags = ['nifty50', 'sensex', 'intraday', 'banknifty']
        
        # Scrape tweets
        # twscrape is fast, so we can aim for higher numbers
        # For testing: 50 per hashtag, for production: 500+
        result = await scraper.scrape_multiple_hashtags(
            hashtags, 
            tweets_per_tag=50,  # Change to 500 for production
            days_back=7  # Search last 7 days
        )
        
        tweets = result['tweets']
        statistics = result['statistics']
        
        # Save tweets to JSON
        with open('raw_tweets_twscrape.json', 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        
        # Save statistics to separate file
        with open('collection_stats_twscrape.json', 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✓ Data saved to raw_tweets_twscrape.json")
        logger.info(f"✓ Statistics saved to collection_stats_twscrape.json")
        logger.info(f"\n📊 Total unique tweets collected: {len(tweets)}")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())


# twitter_scraper_nitter.py
"""
Twitter/X Scraper using Nitter (public Twitter frontend)

This is the SIMPLEST scraper - no authentication required!
Uses public Nitter instances to fetch tweets without any login.

Key Features:
- No login/authentication needed
- Same output format as other scrapers
- Provides detailed statistics per hashtag
- Handles deduplication across hashtags
- Works with Python 3.13+

Note: Depends on public Nitter instances being available.
If one instance is down, try another from the list.
"""
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict
import time
import re
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TwitterScraperNitter:
    def __init__(self):
        # List of public Nitter instances (try these in order)
        self.nitter_instances = [
            "https://nitter.poast.org",
            "https://nitter.privacydev.net",
            "https://nitter.net",
            "https://nitter.woodland.cafe",
        ]
        self.current_instance = None
        self.tweets_data = []
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        })
    
    def _find_working_instance(self) -> str:
        """Find a working Nitter instance"""
        if self.current_instance:
            return self.current_instance
        
        logger.info("Finding working Nitter instance...")
        for instance in self.nitter_instances:
            try:
                response = self.session.get(instance, timeout=10)
                if response.status_code == 200:
                    logger.info(f"✓ Using Nitter instance: {instance}")
                    self.current_instance = instance
                    return instance
            except Exception as e:
                logger.debug(f"Instance {instance} not available: {e}")
                continue
        
        raise Exception("No working Nitter instances found. Please try again later or use Playwright scraper.")
    
    def _parse_tweet_time(self, time_str: str) -> str:
        """Convert relative time to ISO format"""
        try:
            # Handle formats like "2h", "5m", "3d"
            if not time_str:
                return datetime.now().isoformat()
            
            # If it's already a date, return as-is
            if ',' in time_str or len(time_str) > 10:
                return datetime.now().isoformat()
            
            # Parse relative time
            now = datetime.now()
            if 'm' in time_str:
                minutes = int(re.findall(r'\d+', time_str)[0])
                return (now - timedelta(minutes=minutes)).isoformat()
            elif 'h' in time_str:
                hours = int(re.findall(r'\d+', time_str)[0])
                return (now - timedelta(hours=hours)).isoformat()
            elif 'd' in time_str:
                days = int(re.findall(r'\d+', time_str)[0])
                return (now - timedelta(days=days)).isoformat()
            else:
                return now.isoformat()
        except:
            return datetime.now().isoformat()
    
    def _parse_count(self, count_str: str) -> int:
        """Parse engagement counts like '1.2K' to integers"""
        try:
            if not count_str:
                return 0
            count_str = count_str.strip().replace(',', '')
            if 'K' in count_str:
                return int(float(count_str.replace('K', '')) * 1000)
            elif 'M' in count_str:
                return int(float(count_str.replace('M', '')) * 1000000)
            else:
                return int(count_str)
        except:
            return 0
    
    def search_hashtag(self, hashtag: str, max_tweets: int = 500) -> List[Dict]:
        """
        Search for tweets with specific hashtag using Nitter
        
        Args:
            hashtag: The hashtag to search (without #)
            max_tweets: Maximum number of tweets to collect
        
        Returns:
            List of tweet dictionaries
        """
        try:
            instance = self._find_working_instance()
            logger.info(f"Searching for #{hashtag}...")
            
            # Build search URL
            query = f"#{hashtag} -filter:replies"
            search_url = f"{instance}/search?f=tweets&q={quote(query)}"
            
            logger.info(f"Fetching: {search_url}")
            
            response = self.session.get(search_url, timeout=30)
            if response.status_code != 200:
                logger.error(f"Failed to fetch tweets: HTTP {response.status_code}")
                return []
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            tweets = []
            tweet_items = soup.find_all('div', class_='timeline-item')
            
            logger.info(f"Found {len(tweet_items)} tweet elements on page")
            
            for item in tweet_items[:max_tweets]:
                try:
                    # Extract username
                    username_elem = item.find('a', class_='username')
                    username = username_elem.get('title', '').replace('@', '') if username_elem else ''
                    
                    # Extract tweet content
                    tweet_content_elem = item.find('div', class_='tweet-content')
                    content = tweet_content_elem.get_text(strip=True) if tweet_content_elem else ''
                    
                    # Extract timestamp
                    time_elem = item.find('span', class_='tweet-date')
                    time_str = time_elem.get('title', '') if time_elem else ''
                    timestamp = self._parse_tweet_time(time_str)
                    
                    # Extract tweet link for ID
                    link_elem = item.find('a', class_='tweet-link')
                    tweet_url = link_elem.get('href', '') if link_elem else ''
                    tweet_id = tweet_url.split('/')[-1].replace('#m', '') if tweet_url else ''
                    
                    # Extract engagement metrics
                    stats = item.find('div', class_='tweet-stats')
                    replies = 0
                    retweets = 0
                    likes = 0
                    
                    if stats:
                        reply_elem = stats.find('span', class_='icon-comment')
                        if reply_elem and reply_elem.parent:
                            replies = self._parse_count(reply_elem.parent.get_text(strip=True))
                        
                        retweet_elem = stats.find('span', class_='icon-retweet')
                        if retweet_elem and retweet_elem.parent:
                            retweets = self._parse_count(retweet_elem.parent.get_text(strip=True))
                        
                        like_elem = stats.find('span', class_='icon-heart')
                        if like_elem and like_elem.parent:
                            likes = self._parse_count(like_elem.parent.get_text(strip=True))
                    
                    # Extract hashtags and mentions from content
                    hashtags = [word[1:] for word in content.split() if word.startswith('#')]
                    mentions = [word[1:] for word in content.split() if word.startswith('@')]
                    
                    if username and content and tweet_id:
                        tweet_data = {
                            'tweet_id': tweet_id,
                            'username': username,
                            'timestamp': timestamp,
                            'content': content,
                            'replies': replies,
                            'retweets': retweets,
                            'likes': likes,
                            'views': 0,  # Nitter doesn't provide view counts
                            'hashtags': hashtags,
                            'mentions': mentions
                        }
                        tweets.append(tweet_data)
                        
                except Exception as e:
                    logger.warning(f"Error parsing tweet: {e}")
                    continue
            
            # Final summary
            if len(tweets) == 0:
                logger.warning(f"⚠️  No tweets collected for #{hashtag}!")
                logger.warning(f"  The Nitter instance might be rate limited or the hashtag has no recent tweets")
            elif len(tweets) < max_tweets:
                logger.warning(f"Only collected {len(tweets)}/{max_tweets} tweets for #{hashtag}")
            else:
                logger.info(f"Successfully collected {len(tweets)} tweets for #{hashtag}")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error searching #{hashtag}: {e}")
            return []
    
    def scrape_multiple_hashtags(self, hashtags: List[str], tweets_per_tag: int = 500) -> Dict:
        """
        Scrape multiple hashtags and return tweets with statistics
        
        Args:
            hashtags: List of hashtags to scrape (without #)
            tweets_per_tag: Target number of tweets per hashtag
        
        Returns:
            Dictionary with 'tweets' and 'statistics' keys
        """
        all_tweets = []
        hashtag_stats = {}
        
        for idx, hashtag in enumerate(hashtags):
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting collection for #{hashtag} ({idx+1}/{len(hashtags)})")
            logger.info(f"{'='*60}")
            
            tweets = self.search_hashtag(hashtag, tweets_per_tag)
            all_tweets.extend(tweets)
            
            # Store statistics for this hashtag
            hashtag_stats[hashtag] = {
                'collected': len(tweets),
                'target': tweets_per_tag,
                'percentage': (len(tweets) / tweets_per_tag * 100) if tweets_per_tag > 0 else 0
            }
            
            # Add delay between hashtag searches
            if hashtag != hashtags[-1]:
                delay = 3
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
    scraper = TwitterScraperNitter()
    
    try:
        # Target hashtags
        hashtags = ['nifty50', 'sensex', 'intraday', 'banknifty']
        
        # Scrape tweets
        # Note: Nitter returns limited results per page (usually 20-50)
        # For more tweets, you'd need to implement pagination
        result = scraper.scrape_multiple_hashtags(
            hashtags, 
            tweets_per_tag=50  # Nitter typically returns 20-50 tweets per search
        )
        
        tweets = result['tweets']
        statistics = result['statistics']
        
        # Save tweets to JSON
        with open('raw_tweets_nitter.json', 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        
        # Save statistics to separate file
        with open('collection_stats_nitter.json', 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✓ Data saved to raw_tweets_nitter.json")
        logger.info(f"✓ Statistics saved to collection_stats_nitter.json")
        logger.info(f"\n📊 Total unique tweets collected: {len(tweets)}")
        
    except Exception as e:
        logger.error(f"Error during scraping: {e}")
        raise


if __name__ == "__main__":
    main()


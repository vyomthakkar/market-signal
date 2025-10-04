# twitter_scraper_v2.py
"""
Twitter/X Scraper using Playwright - Production-Ready Version

Major Improvements:
- O(1) deduplication (1000x faster than O(n))
- Production-grade rate limiting (Token Bucket + Adaptive)
- Intelligent retry logic with exponential backoff
- Circuit breaker for handling cascading failures
- Environment-based configuration (no hardcoded credentials)
- Custom exception hierarchy for precise error handling
- Comprehensive logging and statistics

Key Features:
- Smart scroll detection to avoid getting stuck
- Automatic recovery from transient failures
- Rate limit detection and adaptive backoff
- Secure credential management
- Production-ready error handling
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict, Optional
import random
from pathlib import Path
import sys
import os

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()  # This loads the .env file!

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import new production-ready components
from core.exceptions import (
    ScraperException, RateLimitException, LoginException,
    NetworkException, BrowserException, DataExtractionException
)
from core.rate_limiter import AdaptiveRateLimiter
from core.retry import retry_async, CircuitBreaker
from data.collector import TweetCollector
from config.settings import load_config, TwitterCredentials

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Debug folder for screenshots
DEBUG_DIR = Path(__file__).parent.parent.parent / "debug"


class TwitterScraperV2:
    """
    Production-ready Twitter/X scraper with enterprise features.
    
    Features:
    - O(1) tweet deduplication
    - Adaptive rate limiting
    - Automatic retry on failures
    - Circuit breaker for stability
    - Environment-based configuration
    """
    
    def __init__(self, config=None):
        """
        Initialize scraper with configuration.
        
        Args:
            config: ScraperConfig instance. If None, loads from environment.
        """
        self.config = config or load_config()
        self.page = None
        self.context = None
        self.browser = None
        self.playwright_instance = None
        
        # Initialize production components
        self.tweet_collector = TweetCollector()
        self.rate_limiter = AdaptiveRateLimiter(
            initial_rate=self.config.rate_limit_requests_per_second,
            min_rate=1.0,
            max_rate=self.config.rate_limit_requests_per_second * 2
        )
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=5,
            recovery_timeout=60.0
        )
        
        self._setup_debug_folder()
        
        logger.info("TwitterScraperV2 initialized with production components")
        logger.info(f"Configuration: headless={self.config.headless}, "
                   f"tweets_per_hashtag={self.config.tweets_per_hashtag}")
    
    def _setup_debug_folder(self):
        """Create debug folder and clean old screenshots from previous run"""
        if self.config.debug_screenshots:
            self.config.debug_dir.mkdir(exist_ok=True)
            # Clean up old screenshots
            for old_screenshot in self.config.debug_dir.glob("*.png"):
                old_screenshot.unlink()
            logger.info(f"Debug folder ready: {self.config.debug_dir}")
    
    async def setup_browser(self):
        """Initialize browser with anti-detection measures"""
        try:
            logger.info("Setting up browser...")
            self.playwright_instance = await async_playwright().start()
            
            # Launch browser with realistic settings
            self.browser = await self.playwright_instance.chromium.launch(
                headless=self.config.headless,
                slow_mo=self.config.slow_mo,
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--disable-dev-shm-usage',
                    '--no-sandbox',
                    '--disable-web-security'
                ]
            )
            
            # Create context with realistic user agent and settings
            self.context = await self.browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='en-US',
                timezone_id='America/New_York'
            )
            
            # Set default timeout
            self.context.set_default_timeout(self.config.page_timeout)
            
            self.page = await self.context.new_page()
            
            # Add anti-detection script
            await self.page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """)
            
            logger.info("✓ Browser setup complete")
            
        except Exception as e:
            logger.error(f"Failed to setup browser: {e}")
            raise BrowserException(f"Browser setup failed: {e}")
    
    @retry_async(
        max_attempts=3,
        base_delay=2.0,
        exceptions=(LoginException, NetworkException)
    )
    async def login(self, username: str, password: str, email: Optional[str] = None):
        """
        Login to Twitter with retry logic and circuit breaker.
        
        Args:
            username: Twitter username
            password: Twitter password
            email: Email for verification (optional)
        
        Raises:
            LoginException: If login fails after retries
        """
        try:
            logger.info("Starting login process...")
            
            # Navigate to login page
            await self.page.goto(
                'https://x.com/i/flow/login',
                wait_until='domcontentloaded',
                timeout=self.config.page_timeout
            )
            
            await asyncio.sleep(3)
            
            # Enter username
            await self.page.wait_for_selector(
                'input[autocomplete="username"]',
                timeout=self.config.element_timeout
            )
            logger.info("✓ Username field found")
            await self.page.fill('input[autocomplete="username"]', username)
            await asyncio.sleep(2)
            
            # Screenshot before clicking Next
            if self.config.debug_screenshots:
                screenshot_path = self.config.debug_dir / 'before_next.png'
                await self.page.screenshot(path=str(screenshot_path))
                logger.debug(f"Screenshot saved: {screenshot_path}")
            
            # Click Next button
            logger.info("Clicking Next button...")
            next_button = await self.page.wait_for_selector('text=Next', timeout=10000)
            await next_button.click()
            await asyncio.sleep(random.uniform(4, 5))
            
            # Screenshot after click
            if self.config.debug_screenshots:
                screenshot_path = self.config.debug_dir / 'after_next.png'
                await self.page.screenshot(path=str(screenshot_path))
                logger.debug(f"Screenshot saved: {screenshot_path}")
            
            # Log current URL for debugging
            logger.debug(f"Current URL after Next: {self.page.url}")
            
            # Check for verification step
            try:
                verification_input = await self.page.wait_for_selector(
                    'input[data-testid="ocfEnterTextTextInput"]',
                    timeout=5000
                )
                logger.info("Verification step detected")
                
                if email:
                    await self.page.fill('input[data-testid="ocfEnterTextTextInput"]', email)
                    await asyncio.sleep(1)
                    await self.page.click('text=Next')
                    await asyncio.sleep(random.uniform(2, 3))
                    logger.info("✓ Verification completed")
                else:
                    logger.error("Email verification required but not provided!")
                    if self.config.debug_screenshots:
                        screenshot_path = self.config.debug_dir / 'verification_required.png'
                        await self.page.screenshot(path=str(screenshot_path))
                    raise LoginException("Email verification required. Please provide email parameter.")
                    
            except Exception as e:
                if "Timeout" not in str(e):
                    raise
                logger.debug("No verification step needed")
            
            # Enter password
            logger.info("Waiting for password field...")
            password_selector = None
            
            # Wait a bit longer for page to fully load
            await asyncio.sleep(3)
            
            # Try multiple selectors with better error handling
            selectors = [
                'input[name="password"]',
                'input[type="password"]', 
                'input[autocomplete="current-password"]',
                '[data-testid="ocfEnterTextTextInput"]'  # Sometimes Twitter uses this
            ]
            
            for selector in selectors:
                try:
                    logger.debug(f"Trying selector: {selector}")
                    await self.page.wait_for_selector(selector, timeout=5000)
                    password_selector = selector
                    logger.info(f"✓ Password field found with: {selector}")
                    break
                except Exception as e:
                    logger.debug(f"Selector {selector} not found: {e}")
                    continue
            
            if not password_selector:
                # Take screenshot for debugging
                if self.config.debug_screenshots:
                    screenshot_path = self.config.debug_dir / 'password_field_error.png'
                    await self.page.screenshot(path=str(screenshot_path))
                    logger.error(f"Screenshot saved: {screenshot_path}")
                
                # Get page content for debugging
                page_text = await self.page.content()
                logger.error(f"Current URL: {self.page.url}")
                logger.error("Page might be showing verification or different UI")
                
                raise LoginException("Password field not found after trying all selectors")
            
            await self.page.fill(password_selector, password)
            await asyncio.sleep(1)
            
            # Click Log in
            logger.info("Clicking Log in button...")
            await self.page.click('text=Log in')
            
            # Wait for home page
            await self.page.wait_for_url('**/home', timeout=30000)
            logger.info(f"✓ Login successful! URL: {self.page.url}")
            
            await asyncio.sleep(3)
            
        except LoginException:
            raise
        except Exception as e:
            logger.error(f"Login failed: {e}")
            if self.config.debug_screenshots:
                try:
                    screenshot_path = self.config.debug_dir / 'login_error.png'
                    await self.page.screenshot(path=str(screenshot_path))
                    logger.debug(f"Error screenshot saved: {screenshot_path}")
                except:
                    pass
            raise LoginException(f"Login failed: {e}")
    
    async def search_hashtag(self, hashtag: str, max_tweets: int = 500) -> List[Dict]:
        """
        Search for tweets with specific hashtag using rate limiting and retry logic.
        
        Args:
            hashtag: The hashtag to search (without #)
            max_tweets: Maximum number of tweets to collect
        
        Returns:
            List of tweet dictionaries
        """
        hashtag_collector = TweetCollector()  # Separate collector for this hashtag
        
        try:
            # Apply rate limiting
            async with self.rate_limiter:
                logger.info(f"Searching #{hashtag} (rate limiter: {self.rate_limiter.current_rate:.1f} req/s)")
                
                # Navigate to search
                search_url = f'https://x.com/search?q=%23{hashtag}%20-filter%3Areplies&src=typed_query&f=live'
                await self.page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
                await asyncio.sleep(5)
                
                # Scrolling and collection logic
                scroll_attempts = 0
                max_scroll_attempts = 5
                no_new_tweets_count = 0
                max_no_new_tweets = 3
                
                last_height = await self.page.evaluate('document.body.scrollHeight')
                
                while hashtag_collector.get_count() < max_tweets and scroll_attempts < max_scroll_attempts:
                    # Extract tweets from current view
                    try:
                        new_tweets = await self._extract_tweets_from_page()
                    except Exception as e:
                        logger.warning(f"Error extracting tweets: {e}")
                        self.rate_limiter.on_rate_limit()  # Slow down on errors
                        new_tweets = []
                    
                    # Track before adding
                    tweets_before = hashtag_collector.get_count()
                    
                    # Add new tweets (O(1) dedup!)
                    for tweet in new_tweets:
                        hashtag_collector.add(tweet)
                    
                    # Check progress
                    tweets_added = hashtag_collector.get_count() - tweets_before
                    
                    if tweets_added > 0:
                        logger.info(f"#{hashtag}: {hashtag_collector.get_count()}/{max_tweets} tweets (+{tweets_added} new)")
                        no_new_tweets_count = 0
                        self.rate_limiter.on_success()  # Speed up on success
                    else:
                        no_new_tweets_count += 1
                        logger.debug(f"No new tweets (attempt {no_new_tweets_count}/{max_no_new_tweets})")
                    
                    # Stop if no new tweets for multiple scrolls
                    if no_new_tweets_count >= max_no_new_tweets:
                        logger.info(f"No new tweets after {max_no_new_tweets} attempts, stopping")
                        break
                    
                    # Check if target reached
                    if hashtag_collector.get_count() >= max_tweets:
                        logger.info(f"✓ Reached target of {max_tweets} tweets for #{hashtag}")
                        break
                    
                    # Scroll down with human-like behavior
                    await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
                    await asyncio.sleep(random.uniform(2, 4))
                    
                    # Check if reached bottom
                    new_height = await self.page.evaluate('document.body.scrollHeight')
                    if new_height == last_height:
                        scroll_attempts += 1
                        logger.debug(f"Page height unchanged ({scroll_attempts}/{max_scroll_attempts})")
                    else:
                        scroll_attempts = 0
                        last_height = new_height
                
                # Final summary
                stats = hashtag_collector.get_stats()
                if hashtag_collector.get_count() < max_tweets:
                    logger.warning(f"#{hashtag}: Collected {hashtag_collector.get_count()}/{max_tweets} tweets "
                                 f"(duplicates: {stats['duplicates_skipped']})")
                else:
                    logger.info(f"✓ #{hashtag}: {hashtag_collector.get_count()} tweets collected "
                               f"(duplicates: {stats['duplicates_skipped']})")
                
                return hashtag_collector.get_all()
                
        except Exception as e:
            logger.error(f"Error searching #{hashtag}: {e}")
            self.rate_limiter.on_rate_limit()  # Slow down after errors
            
            # Check if it's a rate limit error
            if "rate limit" in str(e).lower():
                raise RateLimitException(f"Rate limited on #{hashtag}")
            
            raise NetworkException(f"Failed to search #{hashtag}: {e}")
    
    async def _extract_tweets_from_page(self) -> List[Dict]:
        """Extract tweet data from current page view"""
        try:
            tweets = await self.page.evaluate("""
                () => {
                    const articles = document.querySelectorAll('article[data-testid="tweet"]');
                    const tweetData = [];
                    
                    articles.forEach(article => {
                        try {
                            // Extract username
                            const usernameElem = article.querySelector('[data-testid="User-Name"] a[role="link"]');
                            const username = usernameElem ? usernameElem.href.split('/').pop() : '';
                            
                            // Extract tweet text
                            const tweetTextElem = article.querySelector('[data-testid="tweetText"]');
                            const tweetText = tweetTextElem ? tweetTextElem.innerText : '';
                            
                            // Extract timestamp
                            const timeElem = article.querySelector('time');
                            const timestamp = timeElem ? timeElem.getAttribute('datetime') : '';
                            
                            // Extract tweet ID
                            const tweetLink = article.querySelector('a[href*="/status/"]');
                            const tweetId = tweetLink ? tweetLink.href.split('/status/')[1].split('?')[0] : '';
                            
                            // Extract engagement metrics
                            const metrics = article.querySelectorAll('[data-testid$="-count"]');
                            let replies = 0, retweets = 0, likes = 0, views = 0;
                            
                            metrics.forEach(metric => {
                                const testId = metric.getAttribute('data-testid');
                                const value = metric.innerText;
                                const count = value ? parseInt(value.replace(/[^0-9]/g, '')) || 0 : 0;
                                
                                if (testId.includes('reply')) replies = count;
                                if (testId.includes('retweet')) retweets = count;
                                if (testId.includes('like')) likes = count;
                            });
                            
                            // Extract hashtags and mentions
                            const hashtags = Array.from(tweetTextElem?.querySelectorAll('a[href^="/hashtag/"]') || [])
                                .map(a => a.innerText);
                            const mentions = Array.from(tweetTextElem?.querySelectorAll('a[href^="/@"]') || [])
                                .map(a => a.innerText);
                            
                            if (username && tweetText && tweetId) {
                                tweetData.push({
                                    tweet_id: tweetId,
                                    username: username,
                                    timestamp: timestamp,
                                    content: tweetText,
                                    replies: replies,
                                    retweets: retweets,
                                    likes: likes,
                                    views: views,
                                    hashtags: hashtags,
                                    mentions: mentions
                                });
                            }
                        } catch (e) {
                            console.log('Error parsing tweet:', e);
                        }
                    });
                    
                    return tweetData;
                }
            """)
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error extracting tweets: {e}")
            raise DataExtractionException(f"Failed to extract tweets: {e}")
    
    async def scrape_multiple_hashtags(
        self,
        hashtags: List[str],
        tweets_per_tag: int = 500
    ) -> Dict:
        """
        Scrape multiple hashtags with production-ready error handling.
        
        Args:
            hashtags: List of hashtags to scrape
            tweets_per_tag: Target tweets per hashtag
        
        Returns:
            Dictionary with 'tweets' and 'statistics' keys
        """
        hashtag_stats = {}
        
        for idx, hashtag in enumerate(hashtags):
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting collection for #{hashtag} ({idx+1}/{len(hashtags)})")
            logger.info(f"{'='*60}")
            
            try:
                # Use circuit breaker for each hashtag
                tweets = await self.circuit_breaker.call(
                    self.search_hashtag,
                    hashtag,
                    tweets_per_tag
                )
                
                # Add to global collector (cross-hashtag dedup)
                added_count = 0
                for tweet in tweets:
                    if self.tweet_collector.add(tweet):
                        added_count += 1
                
                # Store statistics
                hashtag_stats[hashtag] = {
                    'collected': len(tweets),
                    'unique': added_count,
                    'target': tweets_per_tag,
                    'percentage': (len(tweets) / tweets_per_tag * 100) if tweets_per_tag > 0 else 0
                }
                
                logger.info(f"✓ #{hashtag}: {len(tweets)} collected, {added_count} unique")
                
            except RateLimitException as e:
                logger.error(f"Rate limited on #{hashtag}: {e}")
                hashtag_stats[hashtag] = {
                    'collected': 0,
                    'unique': 0,
                    'target': tweets_per_tag,
                    'percentage': 0,
                    'error': 'Rate limited'
                }
                # Wait longer before next hashtag
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Failed to scrape #{hashtag}: {e}")
                hashtag_stats[hashtag] = {
                    'collected': 0,
                    'unique': 0,
                    'target': tweets_per_tag,
                    'percentage': 0,
                    'error': str(e)
                }
            
            # Delay between hashtags
            if hashtag != hashtags[-1]:
                delay = random.uniform(5, 10)
                logger.info(f"Waiting {delay:.1f}s before next hashtag...")
                await asyncio.sleep(delay)
        
        # Print summary
        logger.info(f"\n{'='*60}")
        logger.info("COLLECTION SUMMARY")
        logger.info(f"{'='*60}")
        
        total_collected = sum(stats.get('collected', 0) for stats in hashtag_stats.values())
        global_stats = self.tweet_collector.get_stats()
        
        for hashtag, stats in hashtag_stats.items():
            if 'error' in stats:
                logger.warning(f"✗ #{hashtag}: ERROR - {stats['error']}")
            else:
                status = "✓" if stats['collected'] >= stats['target'] else "⚠"
                logger.info(f"{status} #{hashtag}: {stats['collected']}/{stats['target']} "
                          f"({stats['percentage']:.1f}%), {stats['unique']} unique")
        
        logger.info(f"\nTotal collected: {total_collected}")
        logger.info(f"Globally unique: {global_stats['unique_tweets']}")
        logger.info(f"Duplicates skipped: {global_stats['duplicates_skipped']}")
        logger.info(f"Deduplication rate: {global_stats['deduplication_rate']:.1f}%")
        logger.info(f"{'='*60}\n")
        
        # Add rate limiter stats
        limiter_stats = self.rate_limiter.get_stats()
        logger.info(f"Rate Limiter Stats:")
        logger.info(f"  Current rate: {limiter_stats['current_rate']:.1f} req/s")
        logger.info(f"  Rate limit hits: {limiter_stats['rate_limit_count']}")
        logger.info(f"  Successful requests: {limiter_stats['success_count']}")
        
        return {
            'tweets': self.tweet_collector.get_all(),
            'statistics': hashtag_stats,
            'global_stats': global_stats,
            'rate_limiter_stats': limiter_stats
        }
    
    async def close(self):
        """Cleanup browser resources"""
        logger.info("Closing browser...")
        try:
            if self.browser:
                await self.browser.close()
            if self.playwright_instance:
                await self.playwright_instance.stop()
            logger.info("✓ Browser closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


async def main():
    """Main execution function with production error handling"""
    logger.info("="*70)
    logger.info("  Twitter Scraper V2 - Production Ready")
    logger.info("="*70)
    
    # Load configuration from environment
    config = load_config(
        headless=False,  # Set to True for production
        tweets_per_hashtag=2  # Testing with 2, change to 500+ for production
    )
    
    # Load credentials from environment
    try:
        creds = TwitterCredentials.from_env()
        if not creds.username or not creds.password.get_secret_value():
            raise ValueError("Twitter credentials not set in environment")
    except Exception as e:
        logger.error("Failed to load credentials from environment")
        logger.error("Please set TWITTER_USERNAME and TWITTER_PASSWORD in .env file")
        logger.error("Or set them as environment variables")
        sys.exit(1)
    
    # Initialize scraper
    scraper = TwitterScraperV2(config)
    
    try:
        await scraper.setup_browser()
        
        # Login with credentials from environment
        await scraper.login(
            username=creds.username,
            password=creds.password.get_secret_value(),
            email=creds.email
        )
        
        # Target hashtags
        hashtags = config.hashtags
        
        logger.info(f"\nTarget hashtags: {', '.join(['#' + h for h in hashtags])}")
        logger.info(f"Tweets per hashtag: {config.tweets_per_hashtag}")
        logger.info(f"Max retries: {config.max_retries}")
        logger.info(f"Rate limit: {config.rate_limit_requests_per_second} req/s\n")
        
        # Scrape tweets
        result = await scraper.scrape_multiple_hashtags(
            hashtags,
            tweets_per_tag=config.tweets_per_hashtag
        )
        
        tweets = result['tweets']
        statistics = result['statistics']
        
        # Save tweets to JSON
        output_file = config.get_output_path(config.output_tweets_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        
        # Save statistics
        stats_file = config.get_output_path(config.output_stats_file)
        with open(stats_file, 'w', encoding='utf-8') as f:
            json.dump({
                'hashtag_stats': statistics,
                'global_stats': result['global_stats'],
                'rate_limiter_stats': result['rate_limiter_stats']
            }, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✓ Data saved to {output_file}")
        logger.info(f"✓ Statistics saved to {stats_file}")
        logger.info(f"\n📊 Total unique tweets collected: {len(tweets)}")
        
    except LoginException as e:
        logger.error(f"❌ Login failed: {e}")
        logger.error("Please check your credentials in .env file")
        sys.exit(1)
        
    except RateLimitException as e:
        logger.error(f"❌ Rate limited: {e}")
        logger.error("Please wait before trying again")
        sys.exit(1)
        
    except Exception as e:
        logger.error(f"❌ Scraping failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())


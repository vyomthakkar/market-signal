# twitter_scraper.py
"""
Twitter/X Scraper using Playwright

This scraper handles:
- Automatic login with verification support
- Smart scroll detection to avoid getting stuck on hashtags with limited content
- Tracks when no new tweets are found and exits gracefully
- Provides detailed statistics per hashtag
- Handles rate limiting with delays between searches

Key Features:
- Stops after 3 consecutive scrolls with no new tweets
- Stops after 5 scrolls with unchanged page height
- Returns statistics showing actual tweets collected vs target
- Deduplicates tweets across hashtags
"""
import asyncio
from playwright.async_api import async_playwright
from datetime import datetime, timedelta
import json
import logging
from typing import List, Dict
import random
from pathlib import Path
import shutil

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Debug folder for screenshots
DEBUG_DIR = Path(__file__).parent.parent.parent / "debug"

class TwitterScraper:
    def __init__(self, headless: bool = True):
        self.headless = headless
        self.tweets_data = []
        self._setup_debug_folder()
        
    def _setup_debug_folder(self):
        """Create debug folder and clean old screenshots from previous run"""
        DEBUG_DIR.mkdir(exist_ok=True)
        # Clean up old screenshots from previous run
        for old_screenshot in DEBUG_DIR.glob("*.png"):
            old_screenshot.unlink()
        logger.info(f"Debug folder ready: {DEBUG_DIR}")
        
    async def setup_browser(self):
        """Initialize browser with anti-detection measures"""
        self.playwright = await async_playwright().start()
        
        # Launch browser with realistic settings
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            slow_mo=100 if not self.headless else 0,  # Slow down actions for visibility
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
        self.context.set_default_timeout(60000)
        
        self.page = await self.context.new_page()
        
        # Add anti-detection script
        await self.page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
        """)
    
    async def login(self, username: str, password: str, email: str = None):
        """Login to Twitter - REQUIRED for search"""
        try:
            logger.info("Navigating to Twitter/X login...")
            # Use 'domcontentloaded' instead of 'networkidle' - less strict
            await self.page.goto('https://x.com/i/flow/login', 
                                wait_until='domcontentloaded',
                                timeout=60000)  # Increase timeout to 60s
            
            logger.info("Page loaded, waiting for username input...")
            await asyncio.sleep(3)  # Give page time to fully render
            
            # Wait for username input with longer timeout
            await self.page.wait_for_selector('input[autocomplete="username"]', 
                                             timeout=20000)
            logger.info("Username field found, entering username...")
            await self.page.fill('input[autocomplete="username"]', username)
            await asyncio.sleep(2)
            
            # Take a screenshot before clicking Next
            screenshot_path = DEBUG_DIR / 'before_next.png'
            await self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Click Next button and wait for navigation
            logger.info("Clicking Next button...")
            next_button = await self.page.wait_for_selector('text=Next', timeout=10000)
            await next_button.click()
            
            logger.info("Waiting for next step to load...")
            await asyncio.sleep(random.uniform(4, 5))
            
            # Take screenshot after click
            screenshot_path = DEBUG_DIR / 'after_next.png'
            await self.page.screenshot(path=str(screenshot_path))
            logger.info(f"Screenshot saved to {screenshot_path}")
            
            # Check for any error messages
            try:
                error_text = await self.page.text_content('[data-testid="error-text"]', timeout=2000)
                if error_text:
                    logger.error(f"Error message found: {error_text}")
                    raise Exception(f"Login error: {error_text}")
            except:
                pass  # No error message found
            
            # Check if we need to enter email/phone verification
            try:
                # Look for "Enter your phone number or email address" or similar
                verification_input = await self.page.wait_for_selector(
                    'input[data-testid="ocfEnterTextTextInput"]', 
                    timeout=5000
                )
                logger.info("Verification step detected, entering email/phone...")
                if email:
                    await self.page.fill('input[data-testid="ocfEnterTextTextInput"]', email)
                    await asyncio.sleep(1)
                    await self.page.click('text=Next')
                    await asyncio.sleep(random.uniform(2, 3))
                else:
                    logger.error("Email/phone verification required but not provided!")
                    screenshot_path = DEBUG_DIR / 'verification_required.png'
                    await self.page.screenshot(path=str(screenshot_path))
                    logger.info(f"Screenshot saved to {screenshot_path}")
                    raise Exception("Email/phone verification required. Please provide email parameter.")
            except Exception as e:
                if "Timeout" not in str(e):
                    raise
                logger.info("No verification step, proceeding to password...")
            
            # Enter password - try multiple selectors
            logger.info("Waiting for password field...")
            password_selector = None
            try:
                # Try common password field selectors
                selectors = [
                    'input[name="password"]',
                    'input[type="password"]',
                    'input[autocomplete="current-password"]'
                ]
                for selector in selectors:
                    try:
                        await self.page.wait_for_selector(selector, timeout=5000)
                        password_selector = selector
                        logger.info(f"Password field found with selector: {selector}")
                        break
                    except:
                        continue
                
                if not password_selector:
                    raise Exception("Password field not found with any selector")
                    
                await self.page.fill(password_selector, password)
                await asyncio.sleep(1)
                
            except Exception as e:
                logger.error(f"Error finding password field: {e}")
                screenshot_path = DEBUG_DIR / 'password_field_error.png'
                await self.page.screenshot(path=str(screenshot_path))
                logger.info(f"Screenshot saved to {screenshot_path}")
                raise
            
            # Click Log in button
            logger.info("Clicking Log in button...")
            await self.page.click('text=Log in')
            
            # Wait for home page with longer timeout (Twitter redirects to x.com)
            logger.info("Waiting for home page...")
            await self.page.wait_for_url('**/home', 
                                        timeout=30000)
            logger.info(f"Login successful! Current URL: {self.page.url}")
            
            await asyncio.sleep(3)
            
        except Exception as e:
            logger.error(f"Login failed: {e}")
            # Take a screenshot for debugging
            try:
                screenshot_path = DEBUG_DIR / 'login_error.png'
                await self.page.screenshot(path=str(screenshot_path))
                logger.info(f"Screenshot saved to {screenshot_path}")
            except:
                pass
            raise
    
    async def search_hashtag(self, hashtag: str, max_tweets: int = 500) -> List[Dict]:
        """Search for tweets with specific hashtag"""
        try:
            # Navigate to search with filters for recent tweets (using x.com)
            search_url = f'https://x.com/search?q=%23{hashtag}%20-filter%3Areplies&src=typed_query&f=live'
            logger.info(f"Searching for #{hashtag}...")
            
            await self.page.goto(search_url, wait_until='domcontentloaded', timeout=60000)
            await asyncio.sleep(5)
            
            tweets = []
            scroll_attempts = 0
            max_scroll_attempts = 5  # Max consecutive scrolls without new content
            no_new_tweets_count = 0  # Track consecutive scrolls with no new tweets
            max_no_new_tweets = 3  # Stop if no new tweets for 3 consecutive scrolls
            
            last_height = await self.page.evaluate('document.body.scrollHeight')
            previous_tweet_count = 0
            
            while len(tweets) < max_tweets and scroll_attempts < max_scroll_attempts:
                # Extract tweets from current view
                new_tweets = await self._extract_tweets_from_page()
                
                # Track count before adding new tweets
                tweets_before = len(tweets)
                
                # Add only unique tweets
                for tweet in new_tweets:
                    if tweet['tweet_id'] not in [t['tweet_id'] for t in tweets]:
                        tweets.append(tweet)
                
                # Check if we got any new tweets this iteration
                tweets_added = len(tweets) - tweets_before
                
                if tweets_added > 0:
                    logger.info(f"Collected {len(tweets)} tweets for #{hashtag} (+{tweets_added} new)")
                    no_new_tweets_count = 0  # Reset counter if we found new tweets
                else:
                    no_new_tweets_count += 1
                    logger.info(f"No new tweets found (attempt {no_new_tweets_count}/{max_no_new_tweets})")
                
                # Stop if we haven't found new tweets for multiple consecutive scrolls
                if no_new_tweets_count >= max_no_new_tweets:
                    logger.info(f"No new tweets found after {max_no_new_tweets} attempts. Ending search for #{hashtag}")
                    break
                
                # Check if we've reached our target
                if len(tweets) >= max_tweets:
                    logger.info(f"Reached target of {max_tweets} tweets for #{hashtag}")
                    break
                
                # Scroll down with human-like behavior
                await self.page.evaluate('window.scrollBy(0, window.innerHeight)')
                await asyncio.sleep(random.uniform(2, 4))  # Random delay
                
                # Check if we've reached the bottom
                new_height = await self.page.evaluate('document.body.scrollHeight')
                if new_height == last_height:
                    scroll_attempts += 1
                    logger.info(f"Page height unchanged (attempt {scroll_attempts}/{max_scroll_attempts})")
                else:
                    scroll_attempts = 0
                    last_height = new_height
            
            # Final summary
            if len(tweets) < max_tweets:
                logger.warning(f"Only collected {len(tweets)}/{max_tweets} tweets for #{hashtag} - may not have enough content available")
            else:
                logger.info(f"Successfully collected {len(tweets)} tweets for #{hashtag}")
            
            return tweets
            
        except Exception as e:
            logger.error(f"Error searching #{hashtag}: {e}")
            return []
    
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
                            
                            // Extract tweet ID from link
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
            return []
    
    async def scrape_multiple_hashtags(self, hashtags: List[str], 
                                      tweets_per_tag: int = 500) -> Dict:
        """Scrape multiple hashtags and return tweets with statistics"""
        all_tweets = []
        hashtag_stats = {}
        
        for hashtag in hashtags:
            logger.info(f"\n{'='*60}")
            logger.info(f"Starting collection for #{hashtag}")
            logger.info(f"{'='*60}")
            
            tweets = await self.search_hashtag(hashtag, tweets_per_tag)
            all_tweets.extend(tweets)
            
            # Store statistics for this hashtag
            hashtag_stats[hashtag] = {
                'collected': len(tweets),
                'target': tweets_per_tag,
                'percentage': (len(tweets) / tweets_per_tag * 100) if tweets_per_tag > 0 else 0
            }
            
            # Add delay between hashtag searches to avoid rate limiting
            if hashtag != hashtags[-1]:  # Don't delay after last hashtag
                delay = random.uniform(5, 10)
                logger.info(f"Waiting {delay:.1f}s before next hashtag...")
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
    
    async def close(self):
        """Cleanup browser resources"""
        await self.browser.close()
        await self.playwright.stop()


async def main():
    """Main execution function"""
    # Initialize scraper
    scraper = TwitterScraper(headless=False)  # Set to True for production
    
    try:
        await scraper.setup_browser()
        
        # Login credentials - YOU NEED TO PROVIDE THESE
        TWITTER_USERNAME = "curiousco4"
        TWITTER_PASSWORD = "schrodinger"
        TWITTER_EMAIL = "containercurious@gmail.com"  # Add your email if Twitter asks for verification
        
        await scraper.login(TWITTER_USERNAME, TWITTER_PASSWORD, TWITTER_EMAIL)
        
        # Target hashtags
        hashtags = ['nifty50', 'sensex', 'intraday', 'banknifty']
        
        # Scrape tweets (aim for 50 per hashtag for testing, 500+ for production)
        result = await scraper.scrape_multiple_hashtags(hashtags, tweets_per_tag=2)
        
        tweets = result['tweets']
        statistics = result['statistics']
        
        # Save tweets to JSON
        with open('raw_tweets.json', 'w', encoding='utf-8') as f:
            json.dump(tweets, f, ensure_ascii=False, indent=2)
        
        # Save statistics to separate file
        with open('collection_stats.json', 'w', encoding='utf-8') as f:
            json.dump(statistics, f, ensure_ascii=False, indent=2)
        
        logger.info(f"\n✓ Data saved to raw_tweets.json")
        logger.info(f"✓ Statistics saved to collection_stats.json")
        
    finally:
        await scraper.close()


if __name__ == "__main__":
    asyncio.run(main())
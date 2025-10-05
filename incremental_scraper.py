#!/usr/bin/env python3
"""
Incremental Twitter Scraper - Add Data One Hashtag at a Time

Usage:
    python incremental_scraper.py nifty50 --count 300
    python incremental_scraper.py banknifty --count 250
    python incremental_scraper.py sensex --count 200
    
Features:
- Scrape one hashtag at a time
- Automatically merges with existing data
- Deduplicates across all runs
- Shows running totals
- Safe - never loses previous data
"""

import asyncio
import sys
import json
from pathlib import Path
from datetime import datetime
import argparse

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from scrapers.playwright_scrapper_v2 import TwitterScraperV2
from config.settings import load_config, TwitterCredentials
from data.storage import StorageManager
from data.processor import TweetProcessor
from data.collector import TweetCollector


class IncrementalDataStore:
    """Manages incremental tweet collection with persistence"""
    
    def __init__(self, data_dir: Path = None):
        """
        Initialize data store.
        
        Args:
            data_dir: Directory to store data (default: ./data_store)
        """
        self.data_dir = data_dir or Path.cwd() / "data_store"
        self.data_dir.mkdir(exist_ok=True)
        
        # File paths
        self.tweets_file = self.data_dir / "tweets_incremental.json"
        self.parquet_file = self.data_dir / "tweets_incremental.parquet"
        self.metadata_file = self.data_dir / "scraping_metadata.json"
        
        # Load existing data
        self.tweets = self._load_existing_tweets()
        self.metadata = self._load_metadata()
        
        print(f"📂 Data store: {self.data_dir}")
        print(f"📊 Current tweets: {len(self.tweets)}")
    
    def _load_existing_tweets(self):
        """Load existing tweets from JSON"""
        if self.tweets_file.exists():
            with open(self.tweets_file, 'r', encoding='utf-8') as f:
                tweets = json.load(f)
            print(f"✅ Loaded {len(tweets)} existing tweets")
            return tweets
        return []
    
    def _load_metadata(self):
        """Load scraping metadata"""
        if self.metadata_file.exists():
            with open(self.metadata_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {
            'hashtags_scraped': {},
            'total_tweets': 0,
            'created_at': datetime.now().isoformat(),
            'last_updated': None,
            'scraping_sessions': []
        }
    
    def add_tweets(self, new_tweets, hashtag, target_count):
        """
        Add new tweets with deduplication.
        
        Args:
            new_tweets: List of new tweets to add
            hashtag: Hashtag that was scraped
            target_count: Target count for this hashtag
            
        Returns:
            dict: Statistics about the addition
        """
        # Create collector for deduplication
        collector = TweetCollector()
        
        # Add existing tweets first
        for tweet in self.tweets:
            collector.add(tweet)
        
        # Track new additions
        initial_count = len(self.tweets)
        new_unique = 0
        
        # Add new tweets
        for tweet in new_tweets:
            if collector.add(tweet):
                new_unique += 1
        
        # Update tweets
        self.tweets = collector.get_all()
        
        # Update metadata
        self.metadata['hashtags_scraped'][hashtag] = {
            'scraped_count': len(new_tweets),
            'unique_added': new_unique,
            'target_count': target_count,
            'scraped_at': datetime.now().isoformat()
        }
        self.metadata['total_tweets'] = len(self.tweets)
        self.metadata['last_updated'] = datetime.now().isoformat()
        self.metadata['scraping_sessions'].append({
            'hashtag': hashtag,
            'timestamp': datetime.now().isoformat(),
            'tweets_added': new_unique,
            'total_after': len(self.tweets)
        })
        
        stats = {
            'new_tweets_scraped': len(new_tweets),
            'unique_added': new_unique,
            'duplicates_skipped': len(new_tweets) - new_unique,
            'total_before': initial_count,
            'total_after': len(self.tweets),
            'total_unique': len(self.tweets)
        }
        
        return stats
    
    def save(self):
        """Save tweets and metadata to disk"""
        # Save JSON
        with open(self.tweets_file, 'w', encoding='utf-8') as f:
            json.dump(self.tweets, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        with open(self.metadata_file, 'w', encoding='utf-8') as f:
            json.dump(self.metadata, f, indent=2)
        
        # Save Parquet (efficient storage)
        try:
            storage = StorageManager(self.data_dir)
            storage.save_tweets(
                self.tweets,
                save_json=False,  # Already saved above
                save_parquet=True,
                parquet_filename="tweets_incremental.parquet"
            )
        except Exception as e:
            print(f"⚠️  Could not save Parquet: {e}")
        
        print(f"💾 Saved {len(self.tweets)} tweets to {self.tweets_file}")
    
    def get_summary(self):
        """Get summary of current data"""
        return {
            'total_tweets': len(self.tweets),
            'hashtags_scraped': list(self.metadata['hashtags_scraped'].keys()),
            'hashtag_details': self.metadata['hashtags_scraped'],
            'scraping_sessions': len(self.metadata['scraping_sessions'])
        }
    
    def print_summary(self):
        """Print formatted summary"""
        print("\n" + "="*70)
        print("📊 DATA STORE SUMMARY")
        print("="*70)
        
        print(f"\n📈 Total Unique Tweets: {len(self.tweets)}")
        print(f"🏷️  Hashtags Scraped: {len(self.metadata['hashtags_scraped'])}")
        print(f"🔄 Scraping Sessions: {len(self.metadata['scraping_sessions'])}")
        
        if self.metadata['hashtags_scraped']:
            print("\n📋 Per-Hashtag Breakdown:")
            for hashtag, info in self.metadata['hashtags_scraped'].items():
                print(f"   #{hashtag}: {info['scraped_count']} scraped, "
                      f"{info['unique_added']} unique added "
                      f"(target: {info['target_count']})")
        
        print("="*70 + "\n")


async def scrape_hashtag(hashtag: str, count: int = 300, headless: bool = True):
    """
    Scrape a single hashtag.
    
    Args:
        hashtag: Hashtag to scrape (without #)
        count: Number of tweets to target
        headless: Run browser in headless mode
        
    Returns:
        List of scraped tweets
    """
    print(f"\n{'='*70}")
    print(f"🔍 SCRAPING #{hashtag}")
    print(f"{'='*70}")
    print(f"Target: {count} tweets")
    print(f"Headless: {headless}")
    
    # Load configuration
    config = load_config(
        headless=headless,
        tweets_per_hashtag=count,
        hashtags=[hashtag]  # Single hashtag
    )
    
    # Load credentials
    try:
        creds = TwitterCredentials.from_env()
        if not creds.username or not creds.password.get_secret_value():
            raise ValueError("Twitter credentials not set")
    except Exception as e:
        print(f"❌ Failed to load credentials: {e}")
        print("Please set TWITTER_USERNAME and TWITTER_PASSWORD in .env file")
        sys.exit(1)
    
    # Initialize scraper
    scraper = TwitterScraperV2(config)
    
    try:
        # Setup browser
        await scraper.setup_browser()
        
        # Login
        print("\n🔐 Logging in...")
        await scraper.login(
            username=creds.username,
            password=creds.password.get_secret_value(),
            email=creds.email
        )
        
        # Scrape the hashtag
        print(f"\n🎯 Scraping #{hashtag}...")
        tweets = await scraper.search_hashtag(hashtag, max_tweets=count)
        
        print(f"\n✅ Scraped {len(tweets)} tweets from #{hashtag}")
        
        # Optional: Process tweets (clean, detect language, etc.)
        if config.enable_data_cleaning:
            print("\n🧹 Cleaning tweet data...")
            processor = TweetProcessor(
                remove_urls=config.remove_urls_from_content,
                detect_language=config.detect_language,
                normalize_unicode=config.normalize_unicode
            )
            tweets = processor.process_batch(tweets)
            print(f"✓ Processed {len(tweets)} tweets")
        
        return tweets
        
    except Exception as e:
        print(f"❌ Error scraping #{hashtag}: {e}")
        import traceback
        traceback.print_exc()
        return []
        
    finally:
        await scraper.close()


async def main():
    """Main function for incremental scraping"""
    parser = argparse.ArgumentParser(
        description="Incrementally scrape Twitter hashtags one at a time",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Scrape 300 tweets from #nifty50
  python incremental_scraper.py nifty50 --count 300
  
  # Scrape 250 tweets from #banknifty with visible browser
  python incremental_scraper.py banknifty --count 250 --no-headless
  
  # Just show current statistics
  python incremental_scraper.py --status
  
  # Export data to specific location
  python incremental_scraper.py --export ./final_output
        """
    )
    
    parser.add_argument(
        'hashtag',
        nargs='?',
        help='Hashtag to scrape (without #)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=300,
        help='Number of tweets to scrape (default: 300)'
    )
    parser.add_argument(
        '--headless',
        action='store_true',
        default=True,
        help='Run browser in headless mode (default: True)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (opposite of --headless)'
    )
    parser.add_argument(
        '--data-dir',
        type=Path,
        default=Path.cwd() / "data_store",
        help='Directory to store data (default: ./data_store)'
    )
    parser.add_argument(
        '--status',
        action='store_true',
        help='Show current data store status and exit'
    )
    parser.add_argument(
        '--export',
        type=Path,
        help='Export current data to specified directory'
    )
    
    args = parser.parse_args()
    
    # Initialize data store
    datastore = IncrementalDataStore(args.data_dir)
    
    # Handle status command
    if args.status:
        datastore.print_summary()
        return
    
    # Handle export command
    if args.export:
        export_dir = args.export
        export_dir.mkdir(exist_ok=True, parents=True)
        
        # Copy files
        import shutil
        shutil.copy(datastore.tweets_file, export_dir / "tweets.json")
        shutil.copy(datastore.metadata_file, export_dir / "metadata.json")
        
        if datastore.parquet_file.exists():
            shutil.copy(datastore.parquet_file, export_dir / "tweets.parquet")
        
        print(f"✅ Exported data to {export_dir}")
        datastore.print_summary()
        return
    
    # Require hashtag for scraping
    if not args.hashtag:
        parser.print_help()
        print("\n" + "="*70)
        print("💡 TIP: Run with --status to see current data")
        print("="*70)
        return
    
    # Determine headless mode
    headless = args.headless and not args.no_headless
    
    # Show current status
    print("\n" + "="*70)
    print("🚀 INCREMENTAL SCRAPER")
    print("="*70)
    print(f"📂 Data store: {args.data_dir}")
    print(f"📊 Current tweets: {len(datastore.tweets)}")
    print(f"🎯 Scraping: #{args.hashtag}")
    print(f"🔢 Target: {args.count} tweets")
    print("="*70)
    
    # Scrape the hashtag
    new_tweets = await scrape_hashtag(args.hashtag, args.count, headless)
    
    if not new_tweets:
        print("\n⚠️  No tweets scraped. Check errors above.")
        return
    
    # Add to data store
    print(f"\n📥 Adding {len(new_tweets)} tweets to data store...")
    stats = datastore.add_tweets(new_tweets, args.hashtag, args.count)
    
    # Save
    datastore.save()
    
    # Print statistics
    print("\n" + "="*70)
    print("📊 SCRAPING RESULTS")
    print("="*70)
    print(f"✅ New tweets scraped: {stats['new_tweets_scraped']}")
    print(f"✨ Unique tweets added: {stats['unique_added']}")
    print(f"🔄 Duplicates skipped: {stats['duplicates_skipped']}")
    print(f"📈 Total before: {stats['total_before']}")
    print(f"📈 Total after: {stats['total_after']}")
    print("="*70)
    
    # Print overall summary
    datastore.print_summary()
    
    # Show next steps
    print("💡 NEXT STEPS:")
    print(f"   • Scrape another hashtag: python incremental_scraper.py <hashtag> --count {args.count}")
    print(f"   • Check status: python incremental_scraper.py --status")
    print(f"   • Export data: python incremental_scraper.py --export ./output")
    print()


if __name__ == "__main__":
    asyncio.run(main())

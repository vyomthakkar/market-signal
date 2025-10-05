#!/usr/bin/env python3
"""
Data Collection Script

Wrapper around incremental_scraper.py for collecting tweet data.

Usage:
    python run/1_collect_data.py [--hashtags HASHTAG1 HASHTAG2 ...] [--count N]
"""

import sys
import argparse
import subprocess
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_scraper(hashtags: list, count: int = 500, headless: bool = True):
    """
    Run the incremental scraper for specified hashtags
    
    Args:
        hashtags: List of hashtags to scrape
        count: Number of tweets per hashtag
        headless: Run browser in headless mode
    """
    print("\n" + "="*80)
    print("📥 DATA COLLECTION - STARTING")
    print("="*80)
    print(f"\nHashtags: {', '.join(['#' + h for h in hashtags])}")
    print(f"Target per hashtag: {count} tweets")
    print(f"Headless mode: {headless}\n")
    
    # Get path to incremental_scraper.py
    scraper_path = Path(__file__).parent.parent / 'incremental_scraper.py'
    
    for hashtag in hashtags:
        print(f"\n📊 Scraping #{hashtag}...")
        print("-" * 80)
        
        # Build command
        cmd = [
            sys.executable,
            str(scraper_path),
            hashtag,
            '--count', str(count)
        ]
        
        if not headless:
            cmd.append('--no-headless')
        
        # Run scraper
        result = subprocess.run(cmd)
        
        if result.returncode != 0:
            print(f"⚠️  Warning: Scraper returned non-zero exit code for #{hashtag}")
        else:
            print(f"✅ Successfully scraped #{hashtag}")
    
    print("\n" + "="*80)
    print("✅ DATA COLLECTION COMPLETE!")
    print("="*80)
    print("\nData saved to: data_store/tweets_incremental.parquet")
    print("\nNext step: Run analysis with 'python run/2_analyze_signals.py'\n")


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Collect tweet data for specified hashtags'
    )
    parser.add_argument(
        '--hashtags',
        nargs='+',
        default=['nifty50', 'sensex', 'banknifty', 'intraday'],
        help='Hashtags to scrape (default: nifty50 sensex banknifty intraday)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=500,
        help='Number of tweets per hashtag (default: 500)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Show browser window (useful for debugging)'
    )
    
    args = parser.parse_args()
    
    run_scraper(
        hashtags=args.hashtags,
        count=args.count,
        headless=not args.no_headless
    )


if __name__ == '__main__':
    main()

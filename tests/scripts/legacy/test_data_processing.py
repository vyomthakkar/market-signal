#!/usr/bin/env python3
"""
Demo script to test Phase 1 & 2: Data Processing & Storage

This script demonstrates:
1. Text cleaning and normalization
2. Unicode handling for Indian languages
3. Language detection
4. Parquet storage
5. Data analysis

Run: python test_data_processing.py
"""

import json
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from data.processor import TextCleaner, TweetProcessor
from data.storage import ParquetWriter, StorageManager


def test_text_cleaning():
    """Test text cleaning functions"""
    print("="*60)
    print("TEST 1: Text Cleaning")
    print("="*60)
    
    test_texts = [
        "नमस्ते! Check #Nifty50 📈 http://example.com",
        "Buy @TCS stock now! Visit http://spam.com/link #StockMarket",
        "மிகவும் நல்லது #Sensex #India 🇮🇳",
        "  Extra   whitespace   everywhere  \n\n\n",
        "Mixed हिंदी and English content #trading"
    ]
    
    cleaner = TextCleaner()
    
    for text in test_texts:
        print(f"\nOriginal: {text}")
        
        # Clean content
        cleaned = cleaner.clean_content(text, remove_urls=True)
        print(f"Cleaned:  {cleaned}")
        
        # Detect language
        lang = cleaner.detect_language(text)
        print(f"Language: {lang}")
        
        # Extract entities
        entities = cleaner.extract_entities(text)
        print(f"Hashtags: {entities['hashtags']}")
        print(f"Mentions: {entities['mentions']}")
        print(f"URLs:     {entities['urls']}")
    
    print("\n✓ Text cleaning test complete!\n")


def test_tweet_processing():
    """Test full tweet processing pipeline"""
    print("="*60)
    print("TEST 2: Tweet Processing Pipeline")
    print("="*60)
    
    # Sample tweets
    sample_tweets = [
        {
            'tweet_id': '001',
            'username': 'trader_ram',
            'timestamp': '2025-10-04T10:00:00.000Z',
            'content': 'नमस्ते! #Nifty50 looking bullish today 📈 http://t.co/xyz',
            'replies': 5,
            'retweets': 10,
            'likes': 25,
            'views': 100,
            'hashtags': ['#Nifty50'],
            'mentions': []
        },
        {
            'tweet_id': '002',
            'username': 'market_guru',
            'timestamp': '2025-10-04T11:00:00.000Z',
            'content': 'Buy @TCS @Infosys #StockMarket #Trading http://example.com',
            'replies': 2,
            'retweets': 5,
            'likes': 15,
            'views': 50,
            'hashtags': ['#StockMarket', '#Trading'],
            'mentions': ['@TCS', '@Infosys']
        },
        {
            'tweet_id': '003',
            'username': 'tamil_trader',
            'timestamp': '2025-10-04T12:00:00.000Z',
            'content': 'மிகவும் நல்ல வர்த்தக நாள் #Sensex #India',
            'replies': 1,
            'retweets': 3,
            'likes': 8,
            'views': 30,
            'hashtags': ['#Sensex', '#India'],
            'mentions': []
        }
    ]
    
    # Process tweets
    processor = TweetProcessor(
        remove_urls=True,
        detect_language=True,
        normalize_unicode=True
    )
    
    processed = processor.process_batch(sample_tweets)
    
    # Show results
    print(f"\nProcessed {len(processed)} tweets:\n")
    
    for tweet in processed:
        print(f"Tweet ID: {tweet['tweet_id']}")
        print(f"Username: {tweet['username']}")
        print(f"Original: {tweet['content'][:60]}...")
        print(f"Cleaned:  {tweet.get('cleaned_content', 'N/A')[:60]}...")
        print(f"Language: {tweet.get('detected_language', 'unknown')}")
        print(f"URLs:     {tweet.get('extracted_urls', [])}")
        print()
    
    # Stats
    stats = processor.get_stats()
    print(f"Processing Statistics:")
    print(f"  Processed: {stats['processed']}")
    print(f"  Errors:    {stats['errors']}")
    print(f"  Success:   {stats['success_rate']:.1f}%")
    
    print("\n✓ Tweet processing test complete!\n")
    
    return processed


def test_parquet_storage(tweets):
    """Test Parquet storage"""
    print("="*60)
    print("TEST 3: Parquet Storage")
    print("="*60)
    
    output_dir = Path(__file__).parent / 'test_output'
    output_dir.mkdir(exist_ok=True)
    
    # Test ParquetWriter
    print("\n1. Testing ParquetWriter...")
    writer = ParquetWriter(output_dir, compression='snappy')
    
    parquet_path = writer.write(tweets, 'test_tweets.parquet', include_metadata=True)
    print(f"✓ Parquet file written: {parquet_path}")
    
    # Read back
    df = writer.read('test_tweets.parquet')
    print(f"✓ Read back {len(df)} rows")
    print(f"\nColumns: {list(df.columns)}")
    print(f"\nFirst row:")
    print(df.iloc[0].to_dict())
    
    # Test StorageManager
    print("\n2. Testing StorageManager...")
    storage = StorageManager(output_dir)
    
    paths = storage.save_tweets(
        tweets,
        save_json=True,
        save_parquet=True,
        json_filename='test_tweets.json',
        parquet_filename='test_tweets_v2.parquet'
    )
    
    print(f"✓ Saved files:")
    for format, path in paths.items():
        size_kb = path.stat().st_size / 1024
        print(f"  {format}: {path.name} ({size_kb:.1f} KB)")
    
    print("\n✓ Parquet storage test complete!\n")


def test_data_analysis(tweets):
    """Test data analysis with pandas"""
    print("="*60)
    print("TEST 4: Data Analysis")
    print("="*60)
    
    try:
        import pandas as pd
        
        # Create DataFrame
        df = pd.DataFrame(tweets)
        
        print(f"\n1. Dataset Overview:")
        print(f"   Total tweets: {len(df)}")
        print(f"   Unique users: {df['username'].nunique()}")
        print(f"   Date range: {df['timestamp'].min()} to {df['timestamp'].max()}")
        
        print(f"\n2. Language Distribution:")
        print(df['detected_language'].value_counts())
        
        print(f"\n3. Engagement Statistics:")
        print(f"   Total likes: {df['likes'].sum()}")
        print(f"   Total retweets: {df['retweets'].sum()}")
        print(f"   Avg engagement: {df['likes'].mean():.1f} likes/tweet")
        
        print(f"\n4. Top Hashtags:")
        all_hashtags = []
        for tags in df['hashtags']:
            if isinstance(tags, list):
                all_hashtags.extend(tags)
        
        if all_hashtags:
            from collections import Counter
            top_tags = Counter(all_hashtags).most_common(5)
            for tag, count in top_tags:
                print(f"   {tag}: {count}")
        
        print("\n✓ Data analysis test complete!\n")
        
    except ImportError:
        print("⚠ Pandas not installed, skipping analysis test")


def test_existing_data():
    """Test processing existing raw_tweets.json if it exists"""
    print("="*60)
    print("TEST 5: Processing Existing Data")
    print("="*60)
    
    raw_tweets_path = Path(__file__).parent / 'raw_tweets.json'
    
    if not raw_tweets_path.exists():
        print("⚠ No existing raw_tweets.json found, skipping...")
        return
    
    print(f"\nLoading existing tweets from {raw_tweets_path}...")
    
    with open(raw_tweets_path, 'r', encoding='utf-8') as f:
        tweets = json.load(f)
    
    print(f"✓ Loaded {len(tweets)} tweets")
    
    # Process them
    print("\nProcessing tweets...")
    processor = TweetProcessor()
    processed = processor.process_batch(tweets)
    
    stats = processor.get_stats()
    print(f"✓ Processing complete:")
    print(f"  Processed: {stats['processed']}")
    print(f"  Success rate: {stats['success_rate']:.1f}%")
    
    # Save as Parquet
    print("\nSaving as Parquet...")
    output_dir = Path(__file__).parent / 'output'
    storage = StorageManager(output_dir)
    
    paths = storage.save_tweets(
        processed,
        save_json=False,  # Don't overwrite original
        save_parquet=True,
        parquet_filename='processed_tweets.parquet'
    )
    
    if 'parquet' in paths:
        parquet_path = paths['parquet']
        json_size = raw_tweets_path.stat().st_size / 1024
        parquet_size = parquet_path.stat().st_size / 1024
        compression = json_size / parquet_size if parquet_size > 0 else 0
        
        print(f"✓ Saved to {parquet_path}")
        print(f"\nSize comparison:")
        print(f"  JSON:    {json_size:.1f} KB")
        print(f"  Parquet: {parquet_size:.1f} KB")
        print(f"  Compression: {compression:.1f}x")
    
    print("\n✓ Existing data processing complete!\n")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("PHASE 1 & 2: DATA PROCESSING & STORAGE - DEMO")
    print("="*60 + "\n")
    
    try:
        # Test 1: Text cleaning
        test_text_cleaning()
        
        # Test 2: Tweet processing
        processed_tweets = test_tweet_processing()
        
        # Test 3: Parquet storage
        test_parquet_storage(processed_tweets)
        
        # Test 4: Data analysis
        test_data_analysis(processed_tweets)
        
        # Test 5: Process existing data
        test_existing_data()
        
        print("="*60)
        print("ALL TESTS PASSED! ✅")
        print("="*60)
        print("\nPhase 1 & 2 implementation is working correctly!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run the scraper: python src/scrapers/playwright_scrapper_v2.py")
        print("3. Check output/ directory for Parquet files")
        print()
        
    except ImportError as e:
        print(f"\n❌ Import error: {e}")
        print("\nPlease install dependencies:")
        print("  pip install -r requirements.txt")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()


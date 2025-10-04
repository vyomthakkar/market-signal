# Phase 1 & 2: Quick Start Guide 🚀

## Installation

```bash
# Install new dependencies
pip install -r requirements.txt

# This installs:
# - pyarrow (Parquet storage)
# - pandas (Data analysis)
# - langdetect (Language detection)
# - unicodedata2 (Enhanced Unicode)
```

## Quick Test

```bash
# Run demo script to test all features
python test_data_processing.py
```

## Usage

### Option 1: Run Scraper (Auto-processes data)

```bash
# Run scraper - data is automatically cleaned and saved as Parquet
python src/scrapers/playwright_scrapper_v2.py
```

**Output:**
```
output/
├── raw_tweets.json          # Original JSON
├── tweets.parquet           # Efficient storage (5-10x smaller!)
├── tweets.meta.json         # Metadata
└── collection_stats.json    # Statistics with processing info
```

### Option 2: Process Existing Data

```python
from data.processor import TweetProcessor
from data.storage import StorageManager
import json

# Load existing tweets
with open('raw_tweets.json', 'r') as f:
    tweets = json.load(f)

# Process them
processor = TweetProcessor()
processed = processor.process_batch(tweets)

# Save as Parquet
storage = StorageManager('./output')
storage.save_tweets(processed, save_parquet=True)
```

### Option 3: Read Parquet Data

```python
from data.storage import StorageManager

storage = StorageManager('./output')
df = storage.load_tweets('tweets.parquet', format='parquet')

# Now you have a pandas DataFrame!
print(df.head())
print(df['detected_language'].value_counts())
```

## Features

### ✅ Data Cleaning
- Remove URLs
- Normalize whitespace
- Unicode normalization (Indian languages)
- Entity extraction (hashtags, mentions)

### ✅ Language Detection
- Automatic detection of Hindi, Tamil, Telugu, etc.
- Mixed English-Hindi support

### ✅ Parquet Storage
- 5-10x compression vs JSON
- Fast columnar reads
- Type-safe schema

### ✅ Backward Compatible
- JSON still saved for debugging
- No breaking changes

## Configuration

Edit `.env` or code:

```python
config = load_config(
    # Enable/disable features
    enable_data_cleaning=True,
    remove_urls_from_content=True,
    detect_language=True,
    
    # Storage
    save_json=True,
    save_parquet=True,
    parquet_compression='snappy'  # or 'gzip', 'zstd'
)
```

## Examples

### Example: Analyze Tweet Languages

```python
import pandas as pd

df = pd.read_parquet('output/tweets.parquet')

print("Language distribution:")
print(df['detected_language'].value_counts())

# Filter Hindi tweets
hindi_tweets = df[df['detected_language'] == 'hi']
print(f"\nFound {len(hindi_tweets)} Hindi tweets")
```

### Example: Find Popular Hashtags

```python
from collections import Counter

df = pd.read_parquet('output/tweets.parquet')

all_hashtags = []
for tags in df['hashtags']:
    if isinstance(tags, list):
        all_hashtags.extend(tags)

top_10 = Counter(all_hashtags).most_common(10)
print("Top hashtags:")
for tag, count in top_10:
    print(f"  #{tag}: {count}")
```

### Example: Engagement Analysis

```python
df = pd.read_parquet('output/tweets.parquet')

print(f"Total engagement:")
print(f"  Likes: {df['likes'].sum():,}")
print(f"  Retweets: {df['retweets'].sum():,}")
print(f"  Replies: {df['replies'].sum():,}")

print(f"\nAverage engagement per tweet:")
print(f"  Likes: {df['likes'].mean():.1f}")
print(f"  Retweets: {df['retweets'].mean():.1f}")
```

## Troubleshooting

### Import errors?
```bash
pip install pandas pyarrow langdetect
```

### Parquet files too large?
```python
config = load_config(parquet_compression='zstd')  # Best compression
```

### Language detection not working?
- Ensure text has at least 10 characters
- Remove URLs and mentions first

## Documentation

See `docs/PHASE_1_2_DATA_PROCESSING.md` for full documentation.

## Summary

**What Changed:**
- ✅ Added data cleaning & normalization
- ✅ Added Unicode/Indian language support
- ✅ Added Parquet storage (5-10x compression)
- ✅ Added language detection
- ✅ Maintained backward compatibility

**Your data is now production-ready! 🎉**


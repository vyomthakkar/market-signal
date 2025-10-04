# Market Signal Twitter Scraper 📊

A robust Twitter/X scraper for collecting market-related tweets from Indian stock market discussions.

## 🎯 Purpose

Scrape tweets about Indian stock market hashtags (#nifty50, #sensex, #intraday, #banknifty) for sentiment analysis and market signal detection.

## 📁 Project Structure

```
market-signal/
├── src/                          # Source code
│   ├── __init__.py
│   ├── model.py                  # Pydantic data models
│   └── scrapers/
│       ├── __init__.py
│       └── playwright_scrapper.py  # Working scraper (recommended)
├── archive/                      # Non-working/experimental code
│   ├── scrapers/
│   │   ├── README.md            # Why these don't work
│   │   ├── snscrape_scraper.py  # ❌ Python 3.13 incompatible
│   │   ├── twscrape_scraper.py  # ⚠️ Returns 0 tweets
│   │   └── nitter_scraper.py    # ⚠️ Unreliable
├── tests/                        # Tests (to be added)
├── docs/                         # Documentation
├── run_scraper.py               # Main entry point
├── requirements.txt             # Dependencies
├── SCRAPER_COMPARISON.md        # Detailed scraper comparison
└── README.md                    # This file
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the repository
cd market-signal

# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Configure Credentials

Edit `src/scrapers/playwright_scrapper.py` lines 403-405:

```python
TWITTER_USERNAME = "your_username"
TWITTER_PASSWORD = "your_password"
TWITTER_EMAIL = "your_email"  # If Twitter asks for verification
```

### 3. Run the Scraper

```bash
# Option 1: Use the main entry point
python run_scraper.py

# Option 2: Run directly
python src/scrapers/playwright_scrapper.py
```

## 📊 Output

The scraper produces two JSON files:

### `raw_tweets.json`
```json
[
  {
    "tweet_id": "1234567890",
    "username": "trader123",
    "timestamp": "2025-10-04T10:30:00",
    "content": "Tweet text here #nifty50",
    "replies": 5,
    "retweets": 12,
    "likes": 45,
    "views": 1200,
    "hashtags": ["nifty50"],
    "mentions": ["username"]
  }
]
```

### `collection_stats.json`
```json
{
  "nifty50": {
    "collected": 50,
    "target": 50,
    "percentage": 100.0
  },
  "sensex": {
    "collected": 48,
    "target": 50,
    "percentage": 96.0
  }
}
```

## ⚙️ Configuration

Edit `src/scrapers/playwright_scrapper.py` to customize:

```python
# Target hashtags
hashtags = ['nifty50', 'sensex', 'intraday', 'banknifty']

# Tweets per hashtag (50 for testing, 500+ for production)
tweets_per_tag = 50

# Browser visibility (False = visible, True = hidden)
headless = False
```

## 🔧 Features

✅ **Smart Scroll Detection**
- Stops after 3 consecutive scrolls with no new tweets
- Stops after 5 scrolls with unchanged page height

✅ **Deduplication**
- Removes duplicate tweets across hashtags
- Based on unique tweet IDs

✅ **Rate Limiting**
- Random delays between searches (5-10 seconds)
- Human-like scrolling behavior

✅ **Statistics**
- Per-hashtag collection statistics
- Success rate tracking
- Duplicate detection

✅ **Error Handling**
- Handles verification challenges
- Graceful degradation
- Detailed logging

## 📚 Documentation

- **`SCRAPER_COMPARISON.md`** - Comparison of all scraper approaches
- **`archive/scrapers/README.md`** - Why alternative scrapers don't work
- **`SCRAPER_IMPROVEMENTS.md`** - Implementation improvements log

## 🧪 Data Model

See `src/model.py` for the Pydantic Tweet model with validation.

## 🐛 Troubleshooting

### Login Issues
- Check credentials in the script
- Provide email if Twitter asks for verification
- Check for CAPTCHA (run with `headless=False` to see browser)

### No Tweets Collected
- Hashtag might have limited recent content
- Rate limiting - wait 15 minutes and retry
- Check Twitter account isn't suspended

### Slow Performance
- Increase `headless` to True for faster execution
- Reduce `tweets_per_tag` for testing
- Check internet connection

## 📝 License

This is a personal project for educational purposes. Respect Twitter's Terms of Service and rate limits.

## 🤝 Contributing

This is a personal project, but suggestions are welcome!

## 📧 Support

For issues, check:
1. `SCRAPER_COMPARISON.md` for scraper options
2. `archive/scrapers/README.md` for known issues
3. GitHub issues (if repository is public)

---

**Note:** Only the Playwright scraper (`src/scrapers/playwright_scrapper.py`) is currently working. Other scrapers in `archive/` are kept for reference but are not functional.

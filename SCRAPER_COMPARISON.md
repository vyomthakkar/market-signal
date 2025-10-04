# Twitter Scraper Comparison Guide

This project now has **3 different scrapers** to choose from. Here's how they compare:

## 🔧 Quick Start: Which Scraper Should I Use?

### 1. **Nitter Scraper** (RECOMMENDED FOR QUICK START) ⭐
**File:** `nitter_scraper.py`

✅ **Easiest to use - NO authentication needed!**

```bash
# Already installed dependencies
python3 nitter_scraper.py
```

**Pros:**
- No login required
- Works immediately
- Fast and simple
- No rate limits from Twitter

**Cons:**
- Limited to ~20-50 tweets per hashtag per request
- Depends on public Nitter instances being available
- Less control over date ranges

**Best for:** Quick testing, small datasets, avoiding authentication

---

### 2. **Playwright Scraper** (MOST RELIABLE FOR LARGE DATASETS) 💪
**File:** `playwright_scrapper.py`

✅ **Best for production use and large datasets**

```bash
python3 playwright_scrapper.py
```

**Pros:**
- Can collect 500+ tweets per hashtag
- Most reliable - mimics real browser
- Full control over search parameters
- Works with all Twitter features
- Smart scroll detection and retry logic

**Cons:**
- Requires Twitter login
- Slower (browser automation)
- Uses more resources
- Requires playwright installation

**Best for:** Production use, large datasets (500+ tweets), reliability

---

### 3. **twscrape Scraper** (FASTEST BUT REQUIRES SETUP) 🚀
**File:** `twscrape_scraper.py`

✅ **Fastest when it works**

```bash
# Install
pip install twscrape

# One-time setup
python3 twscrape_scraper.py --setup

# Run
python3 twscrape_scraper.py
```

**Pros:**
- Very fast (no browser overhead)
- Setup once, use forever
- Good for automated runs
- Built-in rate limit handling

**Cons:**
- Requires Twitter account setup
- May have issues with Twitter API changes
- Currently returning 0 tweets (needs debugging)
- Accounts can get suspended if overused

**Best for:** Automation, scheduled runs, speed (once working)

---

## 📊 Output Comparison

All three scrapers produce the **same output format**:

```json
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
```

Each scraper also produces statistics:
- `raw_tweets_[scraper].json` - The collected tweets
- `collection_stats_[scraper].json` - Per-hashtag statistics

---

## 🎯 Recommendations

### For Your Current Situation:

Since **twscrape returned 0 tweets**, I recommend:

**Option 1: Try Nitter First (Easiest)**
```bash
python3 nitter_scraper.py
```
No setup needed, should work immediately!

**Option 2: Use Playwright (Most Reliable)**
```bash
python3 playwright_scrapper.py
```
You already have credentials set up, and it's proven to work.

---

## 🐛 Troubleshooting twscrape

If you want to debug twscrape (since it returned 0 tweets):

1. **Check account status:**
```bash
python3 -c "import asyncio; from twscrape import API; api = API(); asyncio.run(api.pool.accounts_info())"
```

2. **Try re-adding your account:**
```bash
python3 twscrape_scraper.py --setup
```

3. **Common issues:**
   - Account might be suspended/locked by Twitter
   - Rate limits (wait 15 minutes)
   - Network/proxy issues
   - Twitter API changes

---

## 📦 Dependencies

```bash
# For Nitter scraper
pip install beautifulsoup4 requests

# For Playwright scraper (already set up)
pip install playwright pydantic
playwright install chromium

# For twscrape scraper
pip install twscrape
```

---

## 🔄 Migration Path

If you need to switch scrapers, the output format is identical, so your downstream processing code doesn't need to change!

```python
# All produce the same format
tweets = json.load(open('raw_tweets_nitter.json'))    # Nitter
tweets = json.load(open('raw_tweets.json'))           # Playwright  
tweets = json.load(open('raw_tweets_twscrape.json'))  # twscrape
```


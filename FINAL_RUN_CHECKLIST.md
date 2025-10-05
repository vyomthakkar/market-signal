# 🚀 Final Run Checklist - 2000 Tweet Extraction

## ✅ Pre-Run Checklist

### 1. **Configuration**
- [ ] Set `SCRAPER_TWEETS_PER_HASHTAG=500` in `.env` file
- [ ] Set `SCRAPER_HEADLESS=true` for faster execution
- [ ] Verify Twitter credentials are in `.env`:
  - `TWITTER_USERNAME=your_username`
  - `TWITTER_PASSWORD=your_password`
  - `TWITTER_EMAIL=your_email` (if verification needed)

### 2. **Environment**
- [ ] Virtual environment activated: `source venv/bin/activate`
- [ ] All dependencies installed: `pip install -r requirements.txt`
- [ ] Playwright browsers installed: `playwright install chromium`

### 3. **Disk Space**
- [ ] At least 100 MB free space (2000 tweets ≈ 5-10 MB compressed)
- [ ] Check: `df -h /Users/vyomthakkar/Downloads/market-signal`

### 4. **Internet & Account**
- [ ] Stable internet connection
- [ ] Twitter account not rate-limited (wait 15 min if recently used)
- [ ] Twitter account not suspended

---

## 📍 Output Location

**All data will be saved to:**
```
/Users/vyomthakkar/Downloads/market-signal/
```

**Files that will be created/updated:**
- `raw_tweets.json` - JSON format (5-10 MB)
- `tweets.parquet` - Parquet format (1-2 MB, compressed)
- `tweets.meta.json` - Metadata about parquet file
- `collection_stats.json` - Collection statistics
- `debug/*.png` - Debug screenshots (if issues occur)

---

## ⚙️ Configuration Summary

### **Target:**
- **Total Tweets:** ~2000 (may vary slightly due to deduplication)
- **Hashtags:** 4 (nifty50, sensex, intraday, banknifty)
- **Tweets per Hashtag:** 500
- **Estimated Time:** 30-60 minutes (depends on rate limiting)

### **Settings to Configure:**

**Option A: Environment Variables (.env file)**
```bash
# Edit .env file
SCRAPER_TWEETS_PER_HASHTAG=500
SCRAPER_HEADLESS=true
SCRAPER_HASHTAGS=nifty50,sensex,intraday,banknifty

# Credentials
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email
```

**Option B: Direct Code Edit (line 710 in playwright_scrapper_v2.py)**
```python
config = load_config(
    headless=True,  # Faster, no browser UI
    tweets_per_hashtag=500  # 500 × 4 hashtags = ~2000 tweets
)
```

---

## 🚀 Run Command

```bash
# Make sure you're in the project root
cd /Users/vyomthakkar/Downloads/market-signal

# Activate virtual environment
source venv/bin/activate

# Run the scraper (V2 - Production)
python run_scraper.py
```

---

## 📊 Expected Output

### **Console Output:**
```
============================================================
  Twitter Scraper V2 - Production Ready
============================================================

Target hashtags: #nifty50, #sensex, #intraday, #banknifty
Tweets per hashtag: 500

============================================================
Starting collection for #nifty50 (1/4)
============================================================
Searching #nifty50 (rate limiter: 10.0 req/s)
#nifty50: 500/500 tweets (+495 new)
✓ #nifty50: 500 tweets collected (duplicates: 5)

[... similar for other hashtags ...]

============================================================
COLLECTION SUMMARY
============================================================
✓ #nifty50: 500/500 (100.0%), 495 unique
✓ #sensex: 500/500 (100.0%), 488 unique
✓ #intraday: 500/500 (100.0%), 492 unique
✓ #banknifty: 500/500 (100.0%), 490 unique

Total collected: 2000
Globally unique: 1965
Duplicates skipped: 35
Deduplication rate: 1.8%

💾 Saving data...
✓ JSON saved: /Users/vyomthakkar/Downloads/market-signal/raw_tweets.json (8.45 MB)
✓ Parquet file written: /Users/vyomthakkar/Downloads/market-signal/tweets.parquet (1.72 MB)
📊 Compression ratio: 4.9x (JSON: 8650KB → Parquet: 1762KB)
✓ Metadata written: /Users/vyomthakkar/Downloads/market-signal/tweets.meta.json
✓ Statistics saved: /Users/vyomthakkar/Downloads/market-signal/collection_stats.json

📊 Total unique tweets: 1965
```

---

## ✅ Post-Run Verification

### 1. **Check Files Exist**
```bash
ls -lh /Users/vyomthakkar/Downloads/market-signal/*.json
ls -lh /Users/vyomthakkar/Downloads/market-signal/*.parquet
```

### 2. **Verify Tweet Count**
```bash
# Quick check using Python
python -c "import json; print(len(json.load(open('raw_tweets.json'))))"
```

### 3. **Inspect Data Quality**
```bash
# View first tweet
python -c "import json; print(json.dumps(json.load(open('raw_tweets.json'))[0], indent=2))"
```

### 4. **Check Statistics**
```bash
cat collection_stats.json
```

---

## 🐛 Troubleshooting

### **"Credentials not found"**
→ Create/edit `.env` file with Twitter credentials

### **"Rate limited"**
→ Normal! Scraper will slow down automatically. Just wait.

### **"Login failed"**
→ Check credentials, may need email verification
→ Check `debug/*.png` screenshots for details

### **Collected fewer than 2000 tweets**
→ Some hashtags may have limited recent tweets (normal)
→ Deduplication removes cross-hashtag duplicates (expected)

### **Process takes longer than 1 hour**
→ Twitter may be rate limiting
→ Scraper will adapt automatically
→ Be patient, it will complete

---

## 📦 Deliverables for Assignment

After successful run, you'll have:

1. **`raw_tweets.json`** - All tweet data in JSON format
2. **`tweets.parquet`** - Compressed tweet data (efficient)
3. **`collection_stats.json`** - Statistics & metrics
4. **`tweets.meta.json`** - Metadata about the collection

**All files will be in:** `/Users/vyomthakkar/Downloads/market-signal/`

---

## 🎓 Assignment Submission Checklist

- [ ] Run completed successfully
- [ ] ~2000 tweets collected (±10% is normal)
- [ ] `raw_tweets.json` file exists and contains data
- [ ] `collection_stats.json` shows success metrics
- [ ] Verified data quality (spot check a few tweets)
- [ ] Ready to submit these files

---

## ⏱️ Estimated Timeline

| Phase | Duration |
|-------|----------|
| Login | 1-2 minutes |
| Scraping #nifty50 (500 tweets) | 8-15 minutes |
| Scraping #sensex (500 tweets) | 8-15 minutes |
| Scraping #intraday (500 tweets) | 8-15 minutes |
| Scraping #banknifty (500 tweets) | 8-15 minutes |
| Processing & Storage | 1-2 minutes |
| **TOTAL** | **30-60 minutes** |

*Note: Time varies based on Twitter's rate limiting and network speed*

---

## 🚀 Ready to Run?

```bash
# One final check
cd /Users/vyomthakkar/Downloads/market-signal
source venv/bin/activate

# Verify config
grep "SCRAPER_TWEETS_PER_HASHTAG" .env

# RUN!
python run_scraper.py
```

**Good luck with your assignment! 🎉**

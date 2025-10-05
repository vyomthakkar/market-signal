# 🎯 Incremental Scraping Guide

## Overview

The **incremental scraper** lets you build your 2000+ tweet dataset gradually, one hashtag at a time. Perfect for:
- **Full control** over which hashtags to scrape
- **Safe incremental building** - never lose previous data
- **Flexible scraping** - stop and resume anytime
- **Automatic deduplication** across all runs

---

## 🚀 Quick Start

### 1. Check Current Status
```bash
python incremental_scraper.py --status
```

### 2. Scrape First Hashtag
```bash
python incremental_scraper.py nifty50 --count 300
```

### 3. Add More Hashtags
```bash
python incremental_scraper.py banknifty --count 300
python incremental_scraper.py sensex --count 250
python incremental_scraper.py stockmarket --count 200
```

### 4. Check Progress
```bash
python incremental_scraper.py --status
```

### 5. Export When Done
```bash
python incremental_scraper.py --export ./final_output
```

---

## 📋 Complete Usage Reference

### Basic Scraping
```bash
# Scrape 300 tweets from #nifty50 (headless by default)
python incremental_scraper.py nifty50 --count 300

# Scrape with visible browser (useful for debugging)
python incremental_scraper.py nifty50 --count 300 --no-headless

# Scrape 500 tweets
python incremental_scraper.py banknifty --count 500
```

### Check Status
```bash
# View current data store summary
python incremental_scraper.py --status
```

**Output:**
```
======================================================================
📊 DATA STORE SUMMARY
======================================================================

📈 Total Unique Tweets: 847
🏷️  Hashtags Scraped: 3
🔄 Scraping Sessions: 3

📋 Per-Hashtag Breakdown:
   #nifty50: 300 scraped, 295 unique added (target: 300)
   #banknifty: 280 scraped, 272 unique added (target: 300)
   #sensex: 290 scraped, 280 unique added (target: 300)
======================================================================
```

### Export Data
```bash
# Export to specific directory
python incremental_scraper.py --export ./final_output

# Export to submission folder
python incremental_scraper.py --export ./assignment_submission
```

### Custom Data Directory
```bash
# Use custom storage location
python incremental_scraper.py nifty50 --count 300 --data-dir ./my_data
```

---

## 📊 Recommended Scraping Plan for 2000+ Tweets

### Strategy: 8 Hashtags with Varied Counts

| Step | Hashtag | Count | Estimated Time | Running Total |
|------|---------|-------|----------------|---------------|
| 1 | `nifty50` | 300 | 12-15 min | ~300 |
| 2 | `banknifty` | 300 | 12-15 min | ~580 |
| 3 | `sensex` | 300 | 12-15 min | ~850 |
| 4 | `stockmarket` | 300 | 12-15 min | ~1120 |
| 5 | `intraday` | 250 | 10-12 min | ~1350 |
| 6 | `nse` | 250 | 10-12 min | ~1570 |
| 7 | `trading` | 250 | 10-12 min | ~1790 |
| 8 | `stocks` | 250 | 10-12 min | ~2000+ ✅ |

**Total Time:** ~90-120 minutes

### Execute Plan

```bash
# Session 1 (First 4 hashtags)
python incremental_scraper.py nifty50 --count 300
python incremental_scraper.py banknifty --count 300
python incremental_scraper.py sensex --count 300
python incremental_scraper.py stockmarket --count 300

# Check progress
python incremental_scraper.py --status

# Session 2 (Next 4 hashtags) - Can run later if needed
python incremental_scraper.py intraday --count 250
python incremental_scraper.py nse --count 250
python incremental_scraper.py trading --count 250
python incremental_scraper.py stocks --count 250

# Final check
python incremental_scraper.py --status
```

---

## 📁 Data Storage Structure

```
data_store/
├── tweets_incremental.json          # All tweets (JSON format)
├── tweets_incremental.parquet       # All tweets (Parquet format)
├── tweets_incremental.meta.json     # Parquet metadata
└── scraping_metadata.json           # Scraping history & stats
```

### Files Explained:

**`tweets_incremental.json`**
- Human-readable JSON format
- All unique tweets collected across all runs
- Automatically deduplicated

**`tweets_incremental.parquet`**
- Compressed binary format (~5x smaller)
- Same data as JSON
- Efficient for data analysis

**`scraping_metadata.json`**
- Tracks which hashtags you've scraped
- When each hashtag was scraped
- How many unique tweets each added
- Complete scraping history

---

## 🎯 Scraping Workflow Example

### Step-by-Step with Checks

```bash
# Start fresh
cd /Users/vyomthakkar/Downloads/market-signal

# Check if data store exists
python incremental_scraper.py --status

# Scrape first hashtag
echo "Scraping #nifty50..."
python incremental_scraper.py nifty50 --count 300

# Check what we got
python incremental_scraper.py --status
# Output: Total Unique Tweets: ~295

# Scrape second hashtag
echo "Scraping #banknifty..."
python incremental_scraper.py banknifty --count 300

# Check again
python incremental_scraper.py --status
# Output: Total Unique Tweets: ~580

# Continue until you hit 2000+...
```

---

## 💡 Pro Tips

### 1. **Run in Batches**
Don't try to do all 8 hashtags in one session. Break it up:
- **Session 1:** 3-4 hashtags (~600-800 tweets)
- **Session 2:** 3-4 more hashtags (~1200-1600 tweets)
- **Session 3:** Final 1-2 hashtags (~2000+ tweets)

### 2. **Check Status Frequently**
After each hashtag, run:
```bash
python incremental_scraper.py --status
```
This shows if you're on track to hit 2000.

### 3. **Adjust Based on Results**
If a hashtag returns fewer tweets than expected:
- Try a different hashtag
- Or scrape more tweets from successful hashtags

### 4. **Use --no-headless for First Run**
For the first hashtag, use visible browser to verify login works:
```bash
python incremental_scraper.py nifty50 --count 50 --no-headless
```
Then switch to headless for speed.

### 5. **Backup Your Data**
After each session, copy the data_store folder:
```bash
cp -r data_store data_store_backup_$(date +%Y%m%d_%H%M%S)
```

---

## 🔧 Advanced Features

### Custom Scraping Strategy

```bash
# Scrape more from high-volume hashtags
python incremental_scraper.py nifty50 --count 500

# Scrape less from low-volume hashtags
python incremental_scraper.py niftyanalysis --count 100

# Use different data directory for testing
python incremental_scraper.py test --count 10 --data-dir ./test_data
```

### Multiple Data Stores

```bash
# Production data
python incremental_scraper.py nifty50 --count 300 --data-dir ./production_data

# Test data
python incremental_scraper.py nifty50 --count 10 --data-dir ./test_data

# Backup data store
python incremental_scraper.py --status --data-dir ./production_data
```

---

## 🐛 Troubleshooting

### "No tweets scraped"
**Causes:**
- Login failed (check credentials in .env)
- Rate limited by Twitter (wait 15 minutes)
- Hashtag has very few tweets (try different hashtag)

**Solution:**
```bash
# Try with visible browser to see what's happening
python incremental_scraper.py nifty50 --count 50 --no-headless
```

### "Duplicates skipped: 250 of 300"
**This is NORMAL!**
- Tweets with multiple hashtags appear in multiple searches
- The scraper automatically deduplicates
- Your unique count is what matters

### Data seems corrupted
**Recovery:**
```bash
# Check if backup exists
ls -la data_store/

# Restore from backup if you made one
cp -r data_store_backup_20251005_1200/* data_store/

# Check status
python incremental_scraper.py --status
```

---

## 📊 Monitoring Progress

### Quick Check Script
Create a file `check_progress.sh`:
```bash
#!/bin/bash
echo "==================================="
echo "Current Progress:"
echo "==================================="
python incremental_scraper.py --status | grep "Total Unique Tweets"
echo "==================================="
echo "Goal: 2000+ tweets"
echo "==================================="
```

Run with: `bash check_progress.sh`

---

## ✅ When You Hit 2000+

### Export for Submission
```bash
# Export final data
python incremental_scraper.py --export ./assignment_submission

# Verify files
ls -lh assignment_submission/
```

You'll get:
- `tweets.json` - All tweets in JSON
- `tweets.parquet` - All tweets in Parquet (compressed)
- `metadata.json` - Complete scraping history

---

## 📈 Example Session Output

```
======================================================================
🚀 INCREMENTAL SCRAPER
======================================================================
📂 Data store: ./data_store
📊 Current tweets: 847
🎯 Scraping: #trading
🔢 Target: 250 tweets
======================================================================

🔍 SCRAPING #trading
======================================================================
Target: 250 tweets
Headless: True

🔐 Logging in...
✓ Login successful!

🎯 Scraping #trading...
#trading: 250/250 tweets (+245 new)
✓ #trading: 250 tweets collected

🧹 Cleaning tweet data...
✓ Processed 250 tweets

✅ Scraped 250 tweets from #trading

📥 Adding 250 tweets to data store...
💾 Saved 1089 tweets to ./data_store/tweets_incremental.json

======================================================================
📊 SCRAPING RESULTS
======================================================================
✅ New tweets scraped: 250
✨ Unique tweets added: 242
🔄 Duplicates skipped: 8
📈 Total before: 847
📈 Total after: 1089
======================================================================

======================================================================
📊 DATA STORE SUMMARY
======================================================================

📈 Total Unique Tweets: 1089
🏷️  Hashtags Scraped: 4
🔄 Scraping Sessions: 4

📋 Per-Hashtag Breakdown:
   #nifty50: 300 scraped, 295 unique added (target: 300)
   #banknifty: 300 scraped, 287 unique added (target: 300)
   #sensex: 265 scraped, 265 unique added (target: 300)
   #trading: 250 scraped, 242 unique added (target: 250)
======================================================================

💡 NEXT STEPS:
   • Scrape another hashtag: python incremental_scraper.py <hashtag> --count 250
   • Check status: python incremental_scraper.py --status
   • Export data: python incremental_scraper.py --export ./output
```

---

## 🎓 Complete Example Workflow

```bash
# 1. Start
cd /Users/vyomthakkar/Downloads/market-signal
python incremental_scraper.py --status

# 2. First hashtag
python incremental_scraper.py nifty50 --count 300
# Wait ~15 minutes
# Total: ~295 tweets

# 3. Second hashtag
python incremental_scraper.py banknifty --count 300
# Wait ~15 minutes
# Total: ~580 tweets

# 4. Third hashtag
python incremental_scraper.py sensex --count 300
# Wait ~15 minutes
# Total: ~850 tweets

# 5. Fourth hashtag
python incremental_scraper.py stockmarket --count 300
# Wait ~15 minutes
# Total: ~1120 tweets

# 6. Check if you need more
python incremental_scraper.py --status
# If < 2000, continue...

# 7. Fifth hashtag
python incremental_scraper.py intraday --count 250
# Total: ~1340 tweets

# 8. Sixth hashtag
python incremental_scraper.py nse --count 250
# Total: ~1560 tweets

# 9. Seventh hashtag
python incremental_scraper.py trading --count 250
# Total: ~1780 tweets

# 10. Eighth hashtag
python incremental_scraper.py stocks --count 250
# Total: ~2000+ tweets ✅

# 11. Export
python incremental_scraper.py --export ./final_submission
```

---

## 🚀 Ready to Start!

```bash
# Quick test with visible browser (verify login works)
python incremental_scraper.py nifty50 --count 10 --no-headless

# If successful, start for real
python incremental_scraper.py nifty50 --count 300
```

**Good luck! 🎉**

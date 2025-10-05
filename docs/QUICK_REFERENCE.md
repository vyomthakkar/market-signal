# 🎯 Quick Reference - Incremental Scraper

## ⚡ Most Common Commands

```bash
# Check current status
python incremental_scraper.py --status

# Scrape one hashtag
python incremental_scraper.py nifty50 --count 300

# Scrape with visible browser (debugging)
python incremental_scraper.py nifty50 --count 300 --no-headless

# Export data
python incremental_scraper.py --export ./output

# Run automated plan (all 8 hashtags)
bash scrape_plan.sh
```

---

## 📋 Recommended Scraping Order

```bash
# ~2400 tweets → ~2000+ unique after deduplication

python incremental_scraper.py nifty50 --count 300      # ~295 tweets
python incremental_scraper.py banknifty --count 300    # ~580 total
python incremental_scraper.py sensex --count 300       # ~850 total
python incremental_scraper.py stockmarket --count 300  # ~1120 total
python incremental_scraper.py intraday --count 250     # ~1340 total
python incremental_scraper.py nse --count 250          # ~1560 total
python incremental_scraper.py trading --count 250      # ~1780 total
python incremental_scraper.py stocks --count 250       # ~2000+ total ✅
```

---

## 📊 Data Files Location

```
data_store/
├── tweets_incremental.json       ← All tweets (submit this)
├── tweets_incremental.parquet    ← Compressed version
└── scraping_metadata.json        ← Scraping history
```

---

## 🎯 Quick Workflow

### Option 1: Manual Control
```bash
# Scrape one at a time, check after each
python incremental_scraper.py nifty50 --count 300
python incremental_scraper.py --status

python incremental_scraper.py banknifty --count 300
python incremental_scraper.py --status

# ... continue until 2000+
```

### Option 2: Automated
```bash
# Run all 8 hashtags automatically
bash scrape_plan.sh

# Wait 90-120 minutes
# Check result
python incremental_scraper.py --status
```

---

## 🔍 Monitoring

```bash
# Quick status check
python incremental_scraper.py --status

# Watch live (during scraping)
# Console will show progress for current hashtag
```

---

## ✅ When Complete

```bash
# 1. Check you have 2000+
python incremental_scraper.py --status

# 2. Export for submission
python incremental_scraper.py --export ./assignment_submission

# 3. Verify exported files
ls -lh assignment_submission/
```

---

## 🆘 Quick Troubleshooting

| Problem | Solution |
|---------|----------|
| No tweets scraped | Check .env has credentials, try `--no-headless` |
| Rate limited | Wait 15 minutes, scraper will adapt |
| < 2000 tweets | Add more hashtags: `stocks`, `bse`, `niftybank` |
| Script error | Check you're in project root, venv activated |

---

## 💡 Pro Tips

1. **Start with visible browser first:**
   ```bash
   python incremental_scraper.py nifty50 --count 10 --no-headless
   ```

2. **Check frequently:**
   ```bash
   python incremental_scraper.py --status
   ```

3. **Backup between sessions:**
   ```bash
   cp -r data_store data_store_backup
   ```

4. **Safe to stop anytime:** Data is saved after each hashtag

---

## 🎓 Full Documentation

- **INCREMENTAL_SCRAPING_GUIDE.md** - Complete guide
- **HASHTAG_STRATEGY.md** - Hashtag recommendations
- **FINAL_RUN_CHECKLIST.md** - Pre-flight checklist

---

## 🚀 Quick Start (First Time)

```bash
# 1. Make sure you're in the right place
cd /Users/vyomthakkar/Downloads/market-signal

# 2. Verify credentials exist
grep "TWITTER_USERNAME" .env

# 3. Test with small scrape (visible browser)
python incremental_scraper.py nifty50 --count 10 --no-headless

# 4. If successful, start real scraping
python incremental_scraper.py nifty50 --count 300

# 5. Continue with more hashtags...
```

---

## 📞 Help

```bash
# Show all options
python incremental_scraper.py --help

# Show examples
python incremental_scraper.py --help | grep -A 20 Examples
```

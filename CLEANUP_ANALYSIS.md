# 📋 Project Cleanup Analysis

## Current Root Directory Files (51 files)

### ✅ **KEEP - Essential Production Files (11)**
1. **`.env`** - Credentials (DO NOT DELETE)
2. **`.gitignore`** - Git configuration
3. **`requirements.txt`** - Python dependencies
4. **`README.md`** - Main project documentation
5. **`run_scraper.py`** - Main entry point
6. **`incremental_scraper.py`** - Production scraper (NEW, IMPORTANT)
7. **`scrape_plan.sh`** - Automated scraping script
8. **`analyze_incremental_data.py`** - Data analysis tool
9. **`view_tweets.py`** - Tweet viewer utility
10. **`TODO.md`** - Project tasks
11. **`TF_IDF_IMPLEMENTATION_PLAN.md`** - Active implementation guide

---

### 📚 **MOVE - Documentation Files to docs/ (15)**
1. `ENGAGEMENT_FIX.md` - Engagement debugging documentation
2. `FEATURES_SUMMARY.md` - Feature documentation
3. `FINAL_RUN_CHECKLIST.md` - Scraping checklist
4. `HASHTAG_STRATEGY.md` - Hashtag recommendations
5. `HOW_TO_USE_OUTPUT.md` - Output usage guide
6. `IMPLEMENTATION_PHASE_1_2_COMPLETE.md` - Implementation docs
7. `IMPLEMENTATION_STATUS.md` - Status documentation
8. `INCREMENTAL_SCRAPING_GUIDE.md` - Scraping guide
9. `INTEGRATION_COMPLETE.md` - Integration docs
10. `INTEGRATION_SUMMARY.md` - Integration summary
11. `LABELING_INSTRUCTIONS.md` - Labeling guide
12. `PHASE_1_2_QUICKSTART.md` - Quick start guide
13. `PHASE_1_2_SUMMARY.txt` - Phase summary
14. `PROJECT_STRUCTURE.md` - Structure documentation
15. `QUICK_REFERENCE.md` - Quick reference guide
16. `QUICK_START.md` - Quick start
17. `README_V2.md` - Alternative readme

---

### 🧪 **MOVE - Test/Debug Scripts to tests/ or debug/ (9)**
1. `debug_engagement_metrics.py` - Debug script
2. `debug_engagement_simple.py` - Debug script
3. `diagnose_engagement.py` - Debug script
4. `test_data_processing.py` - Test script
5. `test_engagement.py` - Test script
6. `test_sentiment.py` - Test script
7. `test_task2.py` - Test script
8. `test_tfidf.py` - Test script
9. `display_tweets_for_labeling.py` - Utility script

---

### 📊 **MOVE - Utility/Analysis Scripts to scripts/ (4)**
1. `analyze_tweets.py` - Analysis utility
2. `check_output.py` - Output checker
3. `examine_data.py` - Data examiner
4. `explore_data.py` - Data explorer
5. `quick_analysis.py` - Quick analysis
6. `interactive_labeling.py` - Labeling tool

---

### 🗑️ **ARCHIVE or DELETE - Old Data Files (11)**
These are old/test outputs that should be in data folders:

1. `collection_stats.json` - Old stats (superseded by data_store/)
2. `raw_tweets.json` - Old data (superseded by data_store/)
3. `tweets.meta.json` - Old metadata
4. `tweets.parquet` - Old data
5. `tweets_clean.json` - Old processed data
6. `tweets_english.parquet` - Old filtered data
7. `tweets_essential.csv` - Old export
8. `sentiment_results.parquet` - Old sentiment results
9. `manual_labels_template.csv` - Template (should be in templates/)
10. `scraper_output.log` - Old log file

---

## 📁 **Proposed New Structure**

```
market-signal/
├── .env                              # Credentials
├── .gitignore                        # Git config
├── requirements.txt                  # Dependencies
├── README.md                         # Main docs
├── TODO.md                           # Tasks
│
├── run_scraper.py                    # Main entry point
├── incremental_scraper.py            # Production scraper
├── scrape_plan.sh                    # Automated plan
│
├── src/                              # Source code (already organized)
│   ├── scrapers/
│   ├── data/
│   ├── analysis/
│   ├── config/
│   └── core/
│
├── scripts/                          # Utility scripts
│   ├── analysis/
│   │   ├── analyze_tweets.py
│   │   ├── analyze_incremental_data.py
│   │   ├── check_output.py
│   │   ├── examine_data.py
│   │   ├── explore_data.py
│   │   └── quick_analysis.py
│   ├── viewing/
│   │   └── view_tweets.py
│   └── labeling/
│       ├── interactive_labeling.py
│       └── display_tweets_for_labeling.py
│
├── tests/                            # All test scripts
│   ├── test_data_processing.py
│   ├── test_engagement.py
│   ├── test_sentiment.py
│   ├── test_task2.py
│   └── test_tfidf.py
│
├── debug/                            # Debug scripts & outputs
│   ├── scripts/
│   │   ├── debug_engagement_metrics.py
│   │   ├── debug_engagement_simple.py
│   │   └── diagnose_engagement.py
│   └── screenshots/                  # Debug screenshots
│
├── docs/                             # All documentation
│   ├── guides/
│   │   ├── INCREMENTAL_SCRAPING_GUIDE.md
│   │   ├── QUICK_REFERENCE.md
│   │   ├── QUICK_START.md
│   │   ├── FINAL_RUN_CHECKLIST.md
│   │   └── HOW_TO_USE_OUTPUT.md
│   ├── implementation/
│   │   ├── IMPLEMENTATION_STATUS.md
│   │   ├── IMPLEMENTATION_PHASE_1_2_COMPLETE.md
│   │   ├── INTEGRATION_COMPLETE.md
│   │   ├── INTEGRATION_SUMMARY.md
│   │   ├── PHASE_1_2_QUICKSTART.md
│   │   └── PHASE_1_2_SUMMARY.txt
│   ├── strategies/
│   │   ├── HASHTAG_STRATEGY.md
│   │   ├── TF_IDF_IMPLEMENTATION_PLAN.md
│   │   └── LABELING_INSTRUCTIONS.md
│   ├── troubleshooting/
│   │   ├── ENGAGEMENT_FIX.md
│   │   └── README_V2.md
│   └── features/
│       ├── FEATURES_SUMMARY.md
│       └── PROJECT_STRUCTURE.md
│
├── data_store/                       # Active data (already good)
│   ├── tweets_incremental.json
│   ├── tweets_incremental.parquet
│   └── scraping_metadata.json
│
├── archive/                          # Old/deprecated files
│   ├── data/                         # Old data files
│   │   ├── raw_tweets.json
│   │   ├── tweets.parquet
│   │   ├── tweets_clean.json
│   │   ├── tweets_english.parquet
│   │   ├── tweets_essential.csv
│   │   ├── sentiment_results.parquet
│   │   ├── collection_stats.json
│   │   └── tweets.meta.json
│   ├── scrapers/                     # Old scraper code
│   └── logs/
│       └── scraper_output.log
│
├── templates/                        # Templates
│   └── manual_labels_template.csv
│
├── output/                           # Current outputs (keep as is)
├── test_engagement/                  # Test data (keep)
├── test_output/                      # Test outputs (keep)
└── venv/                             # Virtual environment (keep)
```

---

## 📊 Summary

| Category | Current Count | Action |
|----------|--------------|--------|
| **Essential Files** | 11 | ✅ Keep in root |
| **Documentation** | 17 | 📁 Move to docs/ |
| **Test Scripts** | 9 | 🧪 Move to tests/ |
| **Utility Scripts** | 6 | 📊 Move to scripts/ |
| **Old Data Files** | 11 | 🗑️ Move to archive/ |
| **Total Root Files** | **51** → **11** | **78% reduction!** |

---

## 🎯 Benefits of This Structure

✅ **Clean root directory** (only 11 essential files)
✅ **Organized by purpose** (docs, tests, scripts)
✅ **Production-ready** structure
✅ **Easy navigation** for new developers
✅ **Preserved history** (nothing deleted, only organized)

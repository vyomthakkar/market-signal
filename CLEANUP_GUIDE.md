# 🧹 Project Cleanup Guide

## 📊 Current Situation

Your root directory has **51 files** - too cluttered for production use!

## 🎯 Goal

Reduce to **11 essential files** in root (78% reduction) while organizing everything else properly.

---

## 🚀 Quick Start (3 Steps)

### Step 1: Preview the Cleanup
See what will be moved (safe, no changes):

```bash
python cleanup_project.py --preview
```

This shows you:
- What stays in root
- What gets moved where
- How many files will be reorganized

### Step 2: Execute the Cleanup
Actually reorganize the files:

```bash
python cleanup_project.py --execute
```

**Safe features:**
- ✅ Creates manifest for undo
- ✅ Creates all needed directories
- ✅ Preserves all files (nothing deleted)
- ✅ Shows progress for each move

### Step 3: Verify
Check the new structure:

```bash
ls -la
ls docs/
ls scripts/
ls tests/
```

### (Optional) Undo if Needed
Restore everything to original state:

```bash
python cleanup_project.py --undo
```

---

## 📁 New Structure After Cleanup

```
market-signal/
├── 📄 Essential Files (11 files in root)
│   ├── .env
│   ├── .gitignore
│   ├── requirements.txt
│   ├── README.md
│   ├── TODO.md
│   ├── run_scraper.py
│   ├── incremental_scraper.py
│   ├── scrape_plan.sh
│   ├── analyze_incremental_data.py
│   ├── view_tweets.py
│   └── TF_IDF_IMPLEMENTATION_PLAN.md
│
├── 📂 docs/ - All Documentation (17 files)
│   ├── guides/
│   ├── implementation/
│   ├── strategies/
│   ├── troubleshooting/
│   └── features/
│
├── 📂 scripts/ - Utility Scripts (6 files)
│   ├── analysis/
│   ├── labeling/
│   └── viewing/
│
├── 📂 tests/ - Test Scripts (9 files)
│   ├── test_data_processing.py
│   ├── test_engagement.py
│   └── ...
│
├── 📂 debug/ - Debug Tools (3 files)
│   └── scripts/
│
├── 📂 archive/ - Old Data (11 files)
│   ├── data/
│   └── logs/
│
├── 📂 templates/ - Templates (1 file)
│   └── manual_labels_template.csv
│
└── 📂 [Unchanged]
    ├── src/ (your source code)
    ├── data_store/ (active data)
    ├── output/
    └── venv/
```

---

## 🔍 What Gets Moved Where

### Root → docs/guides/
- INCREMENTAL_SCRAPING_GUIDE.md
- QUICK_REFERENCE.md
- FINAL_RUN_CHECKLIST.md
- QUICK_START.md
- HOW_TO_USE_OUTPUT.md

### Root → docs/implementation/
- IMPLEMENTATION_STATUS.md
- INTEGRATION_COMPLETE.md
- PHASE_1_2_COMPLETE.md
- And other implementation docs

### Root → scripts/analysis/
- analyze_tweets.py
- check_output.py
- examine_data.py
- explore_data.py
- quick_analysis.py

### Root → tests/
- test_*.py files (9 files)

### Root → debug/scripts/
- debug_*.py files (3 files)

### Root → archive/data/
- Old data files (tweets.parquet, etc.)
- collection_stats.json
- sentiment_results.parquet

---

## 💡 Benefits

### Before Cleanup:
```bash
$ ls | wc -l
51  # Too many files!
```

### After Cleanup:
```bash
$ ls | wc -l
11  # Clean and organized!

$ tree -L 1
.
├── .env
├── .gitignore
├── requirements.txt
├── README.md
├── run_scraper.py
├── incremental_scraper.py
├── docs/
├── scripts/
├── tests/
├── src/
└── data_store/
```

✅ **Professional structure**  
✅ **Easy to navigate**  
✅ **Clear separation of concerns**  
✅ **Production-ready**  

---

## ⚠️ Important Notes

### Files That Stay in Root (DO NOT MOVE):
- `.env` - Your credentials
- `.gitignore` - Git configuration
- `requirements.txt` - Dependencies
- `README.md` - Main documentation
- `run_scraper.py` - Entry point
- `incremental_scraper.py` - Main scraper
- Core utility scripts

### Directories Unchanged:
- `src/` - Your source code
- `data_store/` - Active scraping data
- `output/` - Output files
- `venv/` - Virtual environment

### Safe to Run:
- ✅ Nothing gets deleted
- ✅ Only moved to organized folders
- ✅ Can undo anytime
- ✅ Manifest saved for recovery

---

## 🎯 Recommended Workflow

```bash
# 1. Preview first
python cleanup_project.py --preview

# 2. If looks good, execute
python cleanup_project.py --execute

# 3. Verify new structure
ls
tree -L 2

# 4. Update any scripts with hardcoded paths (if needed)
# Most scripts use relative paths so should work fine

# 5. Test key functionality
python run_scraper.py --help
python incremental_scraper.py --status

# 6. If something breaks, undo and debug
python cleanup_project.py --undo
```

---

## 🔧 After Cleanup

### Update README.md (if needed)
Document the new structure in your main README.

### Update .gitignore (if needed)
May want to add new directories if not tracked.

### Update Project Paths
Most scripts use relative paths and should work fine.

---

## ❓ FAQ

**Q: Will this break my scraper?**  
A: No! Essential scripts stay in root. Only docs and old files are moved.

**Q: What if I need a moved file?**  
A: It's in an organized folder (docs/, scripts/, etc.) - easy to find!

**Q: Can I undo?**  
A: Yes! `python cleanup_project.py --undo` restores everything.

**Q: Will git be affected?**  
A: Git tracks moves. Your history is preserved.

**Q: What about my data?**  
A: `data_store/` is untouched. Only old/test data moves to `archive/`.

---

## ✅ Ready to Clean Up?

```bash
# Preview first (safe)
python cleanup_project.py --preview

# Then execute when ready
python cleanup_project.py --execute
```

**Your project will look much more professional! 🎉**

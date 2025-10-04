# Project Structure

Last updated: October 4, 2025

## Directory Layout

```
market-signal/
│
├── 📁 src/                           # Main source code
│   ├── __init__.py                  # Package initialization
│   ├── model.py                     # Pydantic data models for tweets
│   └── 📁 scrapers/
│       ├── __init__.py
│       └── playwright_scrapper.py   # ✅ WORKING scraper (recommended)
│
├── 📁 archive/                       # Archived/non-working code
│   ├── __init__.py
│   └── 📁 scrapers/
│       ├── README.md                # Explains why these don't work
│       ├── snscrape_scraper.py     # ❌ Python 3.13 incompatible
│       ├── twscrape_scraper.py     # ⚠️ Returns 0 tweets
│       └── nitter_scraper.py       # ⚠️ Unreliable
│
├── 📁 docs/                          # Documentation
│   ├── SCRAPER_COMPARISON.md        # Comparison of all scrapers
│   └── SCRAPER_IMPROVEMENTS.md      # Development notes
│
├── 📁 debug/                         # Debug screenshots (auto-cleaned each run)
│   ├── .gitkeep                     # Keeps folder in git
│   └── README.md                    # Debug folder documentation
│
├── 📁 tests/                         # Unit tests (to be added)
│
├── 📄 run_scraper.py                # Main entry point ⭐
├── 📄 requirements.txt              # Python dependencies
├── 📄 README.md                     # Main documentation
├── 📄 PROJECT_STRUCTURE.md          # This file
├── 📄 .gitignore                    # Git ignore patterns
│
├── 📊 raw_tweets.json               # Output: collected tweets
├── 📊 collection_stats.json         # Output: collection statistics
│
└── 📁 venv/                          # Virtual environment (not in git)
```

## File Descriptions

### Source Code (`src/`)

| File | Purpose | Status |
|------|---------|--------|
| `model.py` | Pydantic Tweet model with validation | ✅ Working |
| `scrapers/playwright_scrapper.py` | Browser-based Twitter scraper | ✅ Working |

### Archive (`archive/`)

| File | Purpose | Status | Issue |
|------|---------|--------|-------|
| `scrapers/snscrape_scraper.py` | snscrape-based scraper | ❌ Broken | Python 3.13 incompatible |
| `scrapers/twscrape_scraper.py` | twscrape-based scraper | ⚠️ Issues | Returns 0 tweets |
| `scrapers/nitter_scraper.py` | Nitter-based scraper | ⚠️ Unreliable | Depends on public instances |

### Documentation (`docs/`)

| File | Purpose |
|------|---------|
| `SCRAPER_COMPARISON.md` | Detailed comparison of all scraper implementations |
| `SCRAPER_IMPROVEMENTS.md` | Development log and improvement notes |

### Root Files

| File | Purpose |
|------|---------|
| `run_scraper.py` | Main entry point - run this! |
| `requirements.txt` | Python package dependencies |
| `README.md` | Main project documentation |
| `.gitignore` | Files to exclude from git |

### Debug Folder (`debug/`)

| File | Content |
|------|---------|
| `.gitkeep` | Keeps folder tracked in git |
| `README.md` | Debug folder documentation |
| `*.png` | Screenshots from most recent run (auto-cleaned) |

### Output Files (Generated)

| File | Content |
|------|---------|
| `raw_tweets.json` | Collected tweets in JSON format |
| `collection_stats.json` | Statistics per hashtag |

## Usage

### Running the Scraper

```bash
# Recommended method
python run_scraper.py

# Direct method
python src/scrapers/playwright_scrapper.py
```

### Project Setup

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium
```

## Design Principles

1. **Separation of Concerns**
   - `src/` for working code
   - `archive/` for non-working/experimental code
   - `docs/` for documentation
   - `tests/` for future tests

2. **Modern Python Structure**
   - Package-based structure with `__init__.py`
   - Clean separation between modules
   - Single entry point (`run_scraper.py`)

3. **Documentation First**
   - Clear README
   - Inline documentation
   - Archived code with explanations

4. **Git-Friendly**
   - Proper `.gitignore`
   - No credentials in code
   - Clean commit history

## Future Enhancements

- [ ] Move credentials to environment variables
- [ ] Add unit tests in `tests/`
- [ ] Create `config.yml` for configuration
- [ ] Add data analysis notebooks
- [ ] Implement CI/CD pipeline
- [ ] Package for PyPI

## Migration Notes

### From Old Structure
```
OLD:                              NEW:
playwright_scrapper.py      →     src/scrapers/playwright_scrapper.py
model.py                    →     src/model.py
snscrape_scraper.py        →     archive/scrapers/snscrape_scraper.py
twscrape_scraper.py        →     archive/scrapers/twscrape_scraper.py
nitter_scraper.py          →     archive/scrapers/nitter_scraper.py
SCRAPER_COMPARISON.md      →     docs/SCRAPER_COMPARISON.md
SCRAPER_IMPROVEMENTS.md    →     docs/SCRAPER_IMPROVEMENTS.md
```

### Import Changes

If you have other Python files importing these modules:

```python
# OLD
from playwright_scrapper import TwitterScraper
from model import Tweet

# NEW
from src.scrapers.playwright_scrapper import TwitterScraper
from src.model import Tweet

# OR (if running from project root with run_scraper.py)
from scrapers.playwright_scrapper import TwitterScraper
from model import Tweet
```


# Archived Scrapers

This folder contains scraper implementations that were attempted but are **not currently working** or **not recommended** for use.

## ❌ Non-Working Scrapers

### 1. `snscrape_scraper.py`
**Status:** Does not work with Python 3.13+

**Issue:** 
- `snscrape` library is not maintained
- Uses deprecated Python import methods removed in Python 3.12+
- Error: `AttributeError: 'FileFinder' object has no attribute 'find_module'`

**Alternatives:** Use twscrape or Playwright scraper

---

### 2. `twscrape_scraper.py`
**Status:** Requires debugging - returns 0 tweets

**Issue:**
- Setup works but search returns no results
- Possible causes:
  - Account login issues
  - Twitter rate limits
  - API changes
  - Account suspended/locked

**To debug:**
```bash
python3 twscrape_scraper.py --setup  # Re-add account
```

**Pros if working:**
- Very fast (no browser overhead)
- Good for automation
- Built-in rate limit handling

---

### 3. `nitter_scraper.py`
**Status:** Depends on public Nitter instances (unreliable)

**Issue:**
- Public Nitter instances often go down
- Limited results (20-50 tweets max per search)
- No pagination support in current implementation

**Pros:**
- No authentication needed
- Simple implementation

**Cons:**
- Unreliable (depends on third-party services)
- Limited data collection
- Cannot control date ranges precisely

---

## ✅ Recommended Scraper

Use **`src/scrapers/playwright_scrapper.py`** instead:
- ✓ Proven to work
- ✓ Can collect 500+ tweets per hashtag
- ✓ Smart scroll detection
- ✓ Full control over search parameters
- ✓ Handles rate limiting

---

## Future Work

If you want to revive these scrapers:

1. **snscrape:** Downgrade to Python 3.11 or find alternative library
2. **twscrape:** Debug account authentication and API calls
3. **nitter:** Implement pagination and instance health checking

---

*Archived on: October 4, 2025*


# Engagement Metrics Fix

## Problem
All engagement metrics (likes, retweets, replies, views) are showing as 0 in scraped data.

## Likely Causes

### 1. **DOM Selector Changed**
Twitter frequently updates their HTML structure. The current selectors may be outdated:
```javascript
// Current code (not working)
const metrics = article.querySelectorAll('[data-testid$="-count"]');
```

### 2. **Different Structure in Search Feed**
Engagement metrics might use different selectors in search results vs home timeline.

### 3. **Aria-Label Based**
Twitter might have moved engagement data to `aria-label` attributes instead of text content.

## Debug Process

### Step 1: Run Debug Script
```bash
python debug_engagement_metrics.py
```

This will:
- Login and load a search page
- Inspect actual tweet HTML
- Find all possible engagement selectors
- Save results to `debug/engagement_debug.json`

### Step 2: Analyze Results
Look for patterns in the debug output:
- Elements with `aria-label` containing numbers
- Elements with `data-testid` related to engagement
- Any visible text showing counts

### Step 3: Update Scraper
Based on findings, update the extraction logic in:
`src/scrapers/playwright_scrapper_v2.py` (lines 529-541)

## Alternative Selectors to Try

### Option A: Aria-Label Based
```javascript
// Extract from aria-labels
const replyButton = article.querySelector('[data-testid="reply"]');
const replyCount = replyButton?.getAttribute('aria-label')?.match(/(\d+)/)?.[1] || '0';

const retweetButton = article.querySelector('[data-testid="retweet"]');
const retweetCount = retweetButton?.getAttribute('aria-label')?.match(/(\d+)/)?.[1] || '0';

const likeButton = article.querySelector('[data-testid="like"]');
const likeCount = likeButton?.getAttribute('aria-label')?.match(/(\d+)/)?.[1] || '0';
```

### Option B: Text Content of Buttons
```javascript
// Look for buttons and extract nearby text
const engagementGroup = article.querySelector('[role="group"]');
if (engagementGroup) {
    const spans = engagementGroup.querySelectorAll('span');
    // Parse through spans to find numbers
}
```

### Option C: Analytics Counter Elements
```javascript
// Twitter sometimes uses specific counter elements
const analytics = article.querySelector('[data-testid="analytics"]');
// Extract view count from analytics
```

## Temporary Workaround

If engagement metrics can't be extracted:

### For Analysis That Doesn't Need Engagement:
- Content analysis (sentiment, topics, keywords) ✅
- User analysis ✅  
- Time distribution ✅
- Hashtag trends ✅

### For Engagement-Based Analysis:
You might need to:
1. Use alternative data sources
2. Focus on qualitative analysis
3. Use engagement as binary (has engagement vs no engagement) based on retweets/quotes

## Testing After Fix

After updating selectors, test with:
```bash
# Scrape just 10 tweets to test
python incremental_scraper.py nifty --count 10 --no-headless

# Check if engagement metrics are captured
python -c "import json; data = json.load(open('data_store/tweets_incremental.json')); print([t for t in data if t['likes'] > 0 or t['retweets'] > 0][:3])"
```

## Need Help?

1. Run debug script first
2. Share the output
3. I'll help identify correct selectors
4. Update the scraper code

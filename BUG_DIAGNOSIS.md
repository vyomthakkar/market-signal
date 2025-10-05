# 🐛 BUG DIAGNOSIS - Zero Tweets in Analysis Output

## Summary
**Root Cause:** The `analyze_tweets()` function in `src/analysis/features.py` does NOT preserve the `hashtags` column from input data, causing the downstream `HashtagAnalyzer` to find 0 hashtags.

## Problem Flow

### 1. Data Collection ✅ WORKING
- `incremental_scraper.py` collects 2030 tweets
- Saves to `data_store/tweets_incremental.parquet` and `.json`
- **Hashtags are present**: 69 hashtags with >= 20 tweets each
- Data structure includes `hashtags` field as a list

### 2. Data Loading ✅ WORKING
- `run/2_analyze_signals.py` loads from `data_store/tweets_incremental.parquet`
- Successfully loads 2030 tweets
- Converts to list of dicts for `analyze_tweets()`
- **Hashtags still present** at this stage

### 3. Feature Analysis ❌ **BUG HERE**
- `src/analysis/features.py::analyze_tweets()` processes each tweet
- **Lines 813-818**: Only preserves these fields:
  ```python
  analysis['tweet_id'] = tweet.get('tweet_id', i)
  analysis['username'] = tweet.get('username', '')
  analysis['content'] = content
  analysis['timestamp'] = tweet.get('timestamp', '')
  ```
- **Missing:** `analysis['hashtags'] = tweet.get('hashtags', [])`
- **Result:** Output DataFrame has NO `hashtags` column

### 4. Hashtag Analysis ❌ FAILS DUE TO BUG
- `run/utils/hashtag_analyzer.py::analyze_by_hashtag()` checks for `hashtags` column
- Line 49: `if 'hashtags' not in df.columns:`
- Since hashtags column is missing → returns empty dict `{}`
- Result: 0 hashtags analyzed

### 5. Market Aggregation ❌ FAILS DUE TO EMPTY DATA
- `run/utils/market_aggregator.py::aggregate_market_signal()`
- Receives empty hashtag_analyses dict
- Line 46: `if not hashtag_analyses:` → returns empty market signal
- **Output:**
  ```
  Total Tweets: 0
  Signal Score: +0.000
  Confidence: 0.0%
  ```

## Verification

### Data Has Hashtags
```bash
$ python3 debug_simple.py
✓ 69 hashtags qualify for analysis (>= 20 tweets)
   #nifty: 1066 tweets
   #nifty50: 726 tweets
   #banknifty: 651 tweets
   ... (and 66 more)
```

### Feature Analysis Drops Hashtags
```python
# In src/analysis/features.py lines 813-818
# Only 4 fields are preserved:
- tweet_id
- username  
- content
- timestamp
# MISSING: hashtags, mentions, likes, retweets, replies, etc.
```

## Solution

### Option 1: Preserve All Original Fields (RECOMMENDED)
Modify `src/analysis/features.py` lines 813-818 to preserve all input fields:

```python
# Add tweet metadata (preserve ALL original fields)
for key, value in tweet.items():
    if key not in analysis:  # Don't overwrite computed features
        analysis[key] = value
```

### Option 2: Explicitly Add Hashtags
Add just the hashtags field:

```python
analysis['hashtags'] = tweet.get('hashtags', [])
```

### Option 3: Merge DataFrames (Alternative)
After analysis, merge with original DataFrame to preserve all columns.

## Impact
- **Current:** 0 tweets analyzed, no signals generated
- **After Fix:** 69 hashtags with 7,521 tweet instances will be analyzed
- **Expected Output:** Meaningful market signals with proper confidence scores

## Files to Modify
1. **Primary Fix:** `src/analysis/features.py` (lines 813-820)
2. **Optional:** Add unit test to verify hashtags are preserved

## Additional Issues Found

### Issue 1: Other Metadata Also Lost
The bug affects more than just hashtags:
- `mentions`: Lost
- `likes`, `retweets`, `replies`, `views`: Lost (needed for engagement re-check)
- `cleaned_content`: Lost
- `detected_language`: Lost

### Issue 2: Engagement Metrics Might Be Redundant
- `analyze_tweets()` calculates engagement from tweet data
- But if original tweet has `likes`, `retweets`, etc., they're lost
- Worth checking if engagement calculation happens before or after this data loss

## Testing Recommendations
After fix, verify:
1. `analyze_tweets()` output has `hashtags` column
2. `HashtagAnalyzer` finds expected number of hashtags (69)
3. Final market signal is non-zero
4. All original tweet fields are preserved in output

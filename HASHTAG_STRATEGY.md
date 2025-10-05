# Hashtag Strategy for 2000+ Tweet Collection

## 🎯 Goal
Collect minimum 2000 tweets from Indian stock market discussions

## 📊 Recommended Hashtag List

### **Tier 1: High Volume (Core - Must Have)**
These are the most active Indian stock market hashtags:

1. `nifty50` - Main Nifty 50 index
2. `nifty` - General Nifty discussions
3. `banknifty` - Bank Nifty index
4. `sensex` - BSE Sensex
5. `stockmarket` - General stock market
6. `intraday` - Intraday trading

### **Tier 2: Medium Volume (Add for Buffer)**
Additional active hashtags to ensure target:

7. `nse` - National Stock Exchange
8. `bse` - Bombay Stock Exchange  
9. `stockmarketindia` - India-specific
10. `trading` - General trading
11. `stocks` - General stocks
12. `indianstockmarket` - India-specific

### **Tier 3: Supplementary (If Needed)**
Add these if still short of 2000:

13. `niftyanalysis` - Technical analysis
14. `sharemarket` - Share market discussions
15. `equitymarket` - Equity discussions
16. `daytrading` - Day trading
17. `swingtrading` - Swing trading
18. `optionstrading` - Options trading

---

## 🔢 Configuration Options

### **Option A: Conservative (10 hashtags × 250 tweets)**
**Total Target:** 2500 tweets → ~2000+ after deduplication

```bash
# In .env file:
SCRAPER_TWEETS_PER_HASHTAG=250
SCRAPER_HASHTAGS=nifty50,nifty,banknifty,sensex,stockmarket,intraday,nse,bse,trading,stocks
```

**Estimated Time:** 40-80 minutes  
**Risk:** Low - Should definitely hit 2000+  
**Pros:** Multiple sources, good diversity

### **Option B: Moderate (8 hashtags × 300 tweets)**
**Total Target:** 2400 tweets → ~2000+ after deduplication

```bash
# In .env file:
SCRAPER_TWEETS_PER_HASHTAG=300
SCRAPER_HASHTAGS=nifty50,banknifty,sensex,stockmarket,intraday,nse,trading,indianstockmarket
```

**Estimated Time:** 50-90 minutes  
**Risk:** Low-Medium  
**Pros:** Balanced approach

### **Option C: Aggressive (6 hashtags × 400 tweets)**
**Total Target:** 2400 tweets → ~2000+ after deduplication

```bash
# In .env file:
SCRAPER_TWEETS_PER_HASHTAG=400
SCRAPER_HASHTAGS=nifty50,banknifty,sensex,stockmarket,intraday,nse
```

**Estimated Time:** 60-100 minutes  
**Risk:** Medium - May fall slightly short if hashtags don't have enough tweets  
**Pros:** Faster, fewer hashtags to manage

---

## ✅ **RECOMMENDED: Option A (Conservative)**

For your assignment, I recommend **Option A** to guarantee 2000+ tweets:

```bash
SCRAPER_TWEETS_PER_HASHTAG=250
SCRAPER_HASHTAGS=nifty50,nifty,banknifty,sensex,stockmarket,intraday,nse,bse,trading,stocks
```

**Why?**
- 10 hashtags × 250 = 2500 tweets (25% buffer)
- Even with 15-20% deduplication, you'll have 2000+
- Covers diverse aspects of Indian stock market
- Based on proven active hashtags from your test run

---

## 📊 Expected Deduplication Rate

Based on typical overlap:
- **Cross-hashtag duplicates:** 10-20% (tweets with multiple hashtags)
- **Example:** A tweet with #nifty50 and #banknifty will be counted once
- **Buffer calculation:** 2500 tweets × 80% unique = 2000 tweets minimum

---

## 🚀 Implementation Steps

### Step 1: Update Configuration
```bash
# Edit your .env file
nano .env

# Add/modify these lines:
SCRAPER_TWEETS_PER_HASHTAG=250
SCRAPER_HASHTAGS=nifty50,nifty,banknifty,sensex,stockmarket,intraday,nse,bse,trading,stocks
SCRAPER_HEADLESS=true
```

### Step 2: Verify Configuration
```bash
# Check the settings
grep "SCRAPER_" .env
```

### Step 3: Run Scraper
```bash
python run_scraper.py
```

### Step 4: Monitor Progress
Watch the console output for collection progress per hashtag.

---

## 🐛 Fallback Plan

If any hashtag returns significantly fewer tweets:

### **Fallback Hashtags (Ready to Add):**
- `niftybank`
- `stockmarketindia`  
- `sharemarket`
- `equitymarket`
- `niftytrading`

### **How to Add Mid-Run:**
You can't modify mid-run, but you can:
1. Let the first run complete
2. Check tweet count
3. If short of 2000, run again with additional hashtags
4. The scraper's deduplication will handle overlaps

---

## 📈 Expected Results

With **Option A (Conservative):**

```
Target Hashtags: 10
Tweets per Hashtag: 250
Total Attempted: 2500

Expected Breakdown:
- nifty50: ~200-250 tweets
- nifty: ~200-250 tweets
- banknifty: ~200-250 tweets
- sensex: ~150-250 tweets
- stockmarket: ~150-250 tweets
- intraday: ~150-250 tweets
- nse: ~100-200 tweets
- bse: ~100-200 tweets
- trading: ~150-250 tweets
- stocks: ~150-250 tweets

Total Collected: ~1800-2500 tweets
After Deduplication: ~2000-2200 unique tweets ✅
```

---

## ⏱️ Time Estimate

**Conservative Approach (Option A):**
- Login: 2 minutes
- 10 hashtags × 250 tweets × ~6 seconds per scroll
- Average: 60-90 minutes total
- Buffer for rate limiting: +20 minutes
- **Total: 80-110 minutes (1.5-2 hours)**

---

## 💡 Pro Tips

1. **Run during off-peak hours** (early morning/late night) for less rate limiting
2. **Keep headless=true** for faster execution
3. **Don't interrupt** - Let it complete fully
4. **Monitor logs** - Check console for progress
5. **Backup strategy** - If first run falls short, add more hashtags and run again

---

## 🎓 Why This Strategy Works

✅ **Multiple sources** - Not dependent on single hashtag  
✅ **Buffer built in** - 25% extra to handle deduplication  
✅ **Proven hashtags** - Based on your test data  
✅ **Diverse coverage** - Indices, exchanges, trading styles  
✅ **Realistic targets** - 250 tweets per hashtag is achievable  

---

## 🚀 Ready to Configure?

Choose your option and I'll help you update the configuration files!

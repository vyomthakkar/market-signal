# 🚀 Quick Start Guide - Market Signal Analysis

## ✅ Everything You Need to Know

All functionality is now integrated into the `run/` directory. No scattered scripts!

---

## 📊 Default Workflow (Target Hashtags: nifty, nifty50, sensex, banknifty, intraday)

### Step 1: Analyze Signals
```bash
python run/2_analyze_signals.py
```

**What you get:**
- ✅ Overall market sentiment
- ✅ Detailed breakdown of your 5 target hashtags
- ✅ Sentiment distribution (bullish/bearish/neutral)
- ✅ Engagement metrics
- ✅ Trending terms per hashtag
- ✅ Signal scores and confidence levels

**Output files:**
- `output/analyzed_tweets.parquet` - Full tweet-level data
- `output/signal_report.json` - Complete analysis report

---

### Step 2: Generate Visualizations
```bash
python run/3_visualize_results.py
```

**What you get:**
- ✅ General market visualizations (signal distribution, timeline, confidence)
- ✅ Interactive dashboard (HTML)
- ✅ **Target hashtag charts** (signal scores, sentiment pies, volume vs confidence)

**Output files:**
- `output/visualizations/signal_distribution.png`
- `output/visualizations/signal_timeline.png`
- `output/visualizations/confidence_components.png`
- `output/visualizations/interactive_dashboard.html`
- `output/visualizations/target_signal_scores.png` ⭐
- `output/visualizations/target_sentiment_distribution.png` ⭐
- `output/visualizations/target_volume_confidence.png` ⭐

---

## 🎨 Advanced Usage

### Analyze Different Hashtags
```bash
# Custom hashtags
python run/2_analyze_signals.py --hashtags stock ipo nasdaq

# All hashtags (no filter)
python run/2_analyze_signals.py --all-hashtags
```

### Quick Testing
```bash
# Test on 50 tweets
python run/2_analyze_signals.py --sample 50
python run/3_visualize_results.py
```

### Custom Visualizations
```bash
# Different target hashtags for charts
python run/3_visualize_results.py --hashtags stock ipo

# Skip target hashtag charts
python run/3_visualize_results.py --skip-target
```

---

## 📁 File Structure

```
run/
├── config.py                    # Default settings (target hashtags, thresholds)
├── 1_collect_data.py           # Data collection wrapper
├── 2_analyze_signals.py        # Main analysis (with target hashtag breakdown)
├── 3_visualize_results.py      # Visualizations (with target hashtag charts)
└── utils/
    ├── hashtag_analyzer.py     # Hashtag-level analysis
    ├── market_aggregator.py    # Overall market signal
    └── report_generator.py     # Report generation
```

---

## ⚙️ Configuration

Edit `run/config.py` to change default target hashtags:

```python
DEFAULT_TARGET_HASHTAGS = [
    'nifty',
    'nifty50',
    'sensex',
    'banknifty',
    'intraday'
]
```

---

## 📊 Sample Output

### Console Output (2_analyze_signals.py)
```
================================================================================
🌐 OVERALL MARKET SENTIMENT
================================================================================
📊 Market Signal: NEUTRAL
📈 Signal Score: +0.080
⭐ Confidence: 44.6%
...

================================================================================
🎯 TARGET HASHTAGS ANALYSIS
================================================================================
Target hashtags: #nifty, #nifty50, #sensex, #banknifty, #intraday

QUICK SUMMARY
Hashtag         Signal          Score   Confidence   Tweets
--------------------------------------------------------------------------------
#nifty          HOLD           +0.098        44.1%     1066 ⏸️
#sensex         HOLD           +0.092        43.5%      482 ⏸️
...

[Detailed breakdown for each hashtag]
```

---

## 🧹 Cleanup (Optional)

Old standalone scripts are now deprecated. They're documented in `DEPRECATED_SCRIPTS.md`.

**To clean up:**
```bash
rm view_hashtag_report.py view_target_hashtags.py visualize_target_hashtags.py \
   test_analysis_sample.py test_hashtag_fix.py test_analysis_quick.sh
```

Keep debug scripts (`debug_*.py`) if you want them for troubleshooting.

---

## 🆘 Need Help?

- **Change target hashtags:** Edit `run/config.py` or use `--hashtags` flag
- **Analyze all hashtags:** Use `--all-hashtags` flag
- **Test on sample:** Use `--sample 50` flag
- **Skip target charts:** Use `--skip-target` flag on step 3

---

## 📚 Full Documentation

See the main `README.md` and docs in the `docs/` directory for more details.

---

**Happy Trading! 📈**

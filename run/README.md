# Market Signal Analysis - Run Scripts

Organized execution scripts for the complete market signal analysis pipeline.

## 📁 Directory Structure

```
run/
├── README.md                    # This file
├── run_all.py                   # Master orchestrator (runs all stages)
├── 1_collect_data.py            # Data collection wrapper
├── 2_analyze_signals.py         # ⭐ Main analysis script
├── 3_visualize_results.py       # Visualization generation
└── utils/
    ├── hashtag_analyzer.py      # Per-hashtag signal aggregation
    ├── market_aggregator.py     # Overall market sentiment
    └── report_generator.py      # JSON report formatting
```

## 🚀 Quick Start

### Option 1: Run Complete Pipeline

```bash
# Run analysis on existing data + generate visualizations
python run/run_all.py

# Collect new data, analyze, and visualize
python run/run_all.py --collect --hashtags nifty50 sensex banknifty

# Run analysis only (skip visualization)
python run/run_all.py --no-viz
```

### Option 2: Run Individual Stages

#### Stage 1: Data Collection (Optional)

```bash
# Collect tweets for default hashtags
python run/1_collect_data.py

# Collect for specific hashtags
python run/1_collect_data.py --hashtags nifty50 sensex --count 300

# Show browser (for debugging)
python run/1_collect_data.py --no-headless
```

#### Stage 2: Signal Analysis (Main Script) ⭐

```bash
# Analyze with default settings
python run/2_analyze_signals.py

# Specify custom input/output
python run/2_analyze_signals.py \
    --input data_store/tweets_incremental.parquet \
    --output output

# Verbose logging
python run/2_analyze_signals.py --verbose
```

#### Stage 3: Visualization

```bash
# Generate all visualizations
python run/3_visualize_results.py

# Customize paths
python run/3_visualize_results.py \
    --input output/analyzed_tweets.parquet \
    --output output/visualizations

# Limit points for memory efficiency
python run/3_visualize_results.py --max-points 3000
```

## 📊 What Does the Analysis Script Do?

The main analysis script (`2_analyze_signals.py`) performs:

1. **Feature Extraction**
   - Sentiment analysis (Twitter-RoBERTa + finance keywords)
   - Engagement metrics (virality, engagement rate)
   - TF-IDF term extraction
   - Trading signal generation

2. **Per-Hashtag Analysis**
   - Groups tweets by hashtag
   - Calculates aggregate signal per hashtag
   - Identifies trending terms
   - Computes confidence breakdown

3. **Overall Market Aggregation**
   - Combines hashtag signals using **volume-based weighting**
   - Calculates market consensus
   - Identifies risk indicators
   - Ranks hashtags by signal strength

4. **Output Generation**
   - JSON report (`signal_report.json`)
   - Analyzed tweets parquet (`analyzed_tweets.parquet`)
   - Console summary with color-coded signals

## 📄 Output Files

After running the analysis, you'll find:

```
output/
├── signal_report.json           # Complete market analysis (JSON)
├── analyzed_tweets.parquet      # Tweet-level features
└── visualizations/              # Charts and dashboards
    ├── signal_distribution.png
    ├── signal_timeline.png
    ├── confidence_components.png
    └── interactive_dashboard.html
```

### signal_report.json Structure

```json
{
  "metadata": {
    "generated_at": "2024-10-05T16:30:00",
    "version": "1.0.0",
    "total_tweets_analyzed": 2030
  },
  "overall_market": {
    "signal_label": "BULLISH",
    "signal_score": 0.35,
    "confidence": 0.642,
    "consensus": "MIXED-BULLISH",
    "total_tweets": 2030,
    "hashtag_count": 4,
    "sentiment_distribution": {...},
    "hashtag_ranking": [...],
    "risk_indicators": {...}
  },
  "hashtags": {
    "nifty50": {
      "signal_label": "BUY",
      "signal_score": 0.42,
      "confidence": 0.685,
      "tweet_count": 487,
      "sentiment_distribution": {...},
      "engagement_metrics": {...},
      "trending_terms": [...]
    },
    ...
  },
  "summary": {
    "market_direction": "BULLISH",
    "recommendation": "..."
  }
}
```

## 🎯 Signal Labels

| Label | Meaning | Signal Score Range |
|-------|---------|-------------------|
| **STRONG_BUY** | Strong bullish signal | ≥ 0.5 |
| **BUY** | Moderate bullish signal | 0.2 to 0.5 |
| **HOLD** | Neutral/weak signal | -0.2 to 0.2 |
| **SELL** | Moderate bearish signal | -0.5 to -0.2 |
| **STRONG_SELL** | Strong bearish signal | ≤ -0.5 |

## ⚙️ Configuration

### Hashtag Analyzer Settings

In `utils/hashtag_analyzer.py`:
- `min_tweets`: Minimum tweets per hashtag (default: 20)
- `min_confidence`: Confidence threshold (default: 0.3)

### Market Aggregator Settings

In `utils/market_aggregator.py`:
- `min_confidence`: Minimum confidence for actionable signals (default: 0.4)
- Weighting method: **volume_based** (more tweets = more influence)

### Modify Settings

Edit the initialization in `2_analyze_signals.py`:

```python
# In analyze_by_hashtag()
analyzer = HashtagAnalyzer(
    min_tweets=30,      # Require more tweets
    min_confidence=0.4  # Higher threshold
)

# In aggregate_market_signal()
aggregator = MarketAggregator(
    min_confidence=0.5  # Stricter confidence requirement
)
```

## 📊 Understanding the Output

### Console Summary

When you run the analysis, you'll see:

```
🌐 OVERALL MARKET SENTIMENT
════════════════════════════════════════════════════════════════════════════════

📊 Market Signal: BULLISH 📈
📈 Signal Score: +0.350
⭐ Confidence: 64.2%
🎯 Consensus: MIXED-BULLISH
📝 Total Tweets: 2,030
#️⃣  Hashtags Analyzed: 4

💡 Recommendation:
   Moderate buy signal. Enter with caution.

📊 Sentiment Distribution:
   Bullish: 1,176 (58.0%)
   Bearish: 487 (24.0%)
   Neutral: 367 (18.0%)

🏆 Hashtag Performance Ranking:
   1. #nifty50: BUY (+0.42, 68.5% conf) 📈
   2. #banknifty: BUY (+0.38, 65.2% conf) 📈
   3. #sensex: HOLD (+0.18, 61.3% conf) ⏸️
   4. #intraday: SELL (-0.15, 58.7% conf) 📉

⚠️  Risk Indicators:
   Signal Volatility: MODERATE (0.31)
   Confidence Level: MODERATE
   Low Confidence Tweets: 412 (20.3%)
```

### Per-Hashtag Details

Each hashtag in `signal_report.json` includes:
- **Signal metrics**: Label, score, confidence
- **Tweet volume**: Total and valid tweet counts
- **Time range**: Earliest to latest tweet
- **Sentiment distribution**: Bullish/bearish/neutral breakdown
- **Engagement metrics**: Virality, likes, retweets
- **Trending terms**: Top TF-IDF terms with scores
- **Confidence breakdown**: Quality, sentiment strength, social proof

## 🔍 Troubleshooting

### Error: Input file not found

```bash
# Make sure you have data collected
python run/1_collect_data.py

# Or check the file path
ls -la data_store/tweets_incremental.parquet
```

### Error: Module not found

```bash
# Install required dependencies
pip install -r requirements.txt

# Or install specific packages
pip install pandas pyarrow transformers torch scikit-learn
```

### Low confidence warnings

If you see many low-confidence signals:
- **Cause**: Not enough high-quality tweets
- **Solution**: Collect more data or lower the confidence threshold

### Empty hashtag analyses

If no hashtags are analyzed:
- **Cause**: Not enough tweets per hashtag (min: 20)
- **Solution**: Lower `min_tweets` in HashtagAnalyzer or collect more data

## 💡 Tips & Best Practices

1. **Data Freshness**: For best results, collect recent data (last 24-48 hours)

2. **Tweet Volume**: Aim for 200+ tweets per hashtag for reliable signals

3. **Confidence Filtering**: Low confidence tweets (<0.3) are automatically filtered from aggregation

4. **Signal Interpretation**:
   - High confidence (>70%) + strong signal = Actionable
   - Moderate confidence (50-70%) = Monitor closely
   - Low confidence (<50%) = Wait for more data

5. **Volatility**: High signal volatility indicates disagreement among hashtags

## 📚 Related Documentation

- **Feature Engineering**: See `src/analysis/features.py` for signal calculation logic
- **Visualization**: See `src/analysis/visualization.py` for plotting functions
- **Data Collection**: See `incremental_scraper.py` for scraping details

## 🆘 Support

For issues or questions:
1. Check the logs (enabled with `--verbose`)
2. Review the output JSON for detailed diagnostics
3. Ensure all dependencies are installed
4. Verify data file format and structure

## 🔮 Future Enhancements

Potential additions (not yet implemented):
- Temporal weighting (recent tweets more important)
- Historical signal tracking
- HTML report generation
- Real-time streaming analysis
- Alert system for significant signal changes

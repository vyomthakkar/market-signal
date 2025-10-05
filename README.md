# X/Twitter posts -> market signals


A three-phase pipeline for collecting, analyzing, and visualizing market sentiment from Twitter/X discussions about Indian stock market indices.

## 🚀 Quick Start

### Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers (for data collection)
playwright install chromium
```

### Configure Twitter Credentials

Create `config/credentials.json`:
```json
{
  "twitter_username": "your_username",
  "twitter_password": "your_password",
  "twitter_email": "your_email"
}
```

---

## 📥 Phase 1: Data Collection

Collect tweets using the incremental scraper (supports one hashtag at a time or batch mode).

### Single Hashtag Collection
```bash
python incremental_scraper.py nifty --count 500
python incremental_scraper.py sensex --count 400
python incremental_scraper.py banknifty --count 300
```

### Batch Collection
```bash
python run/1_collect_data.py --hashtags nifty sensex banknifty --count 500
```

### Output Location: `data_store/`
```
data_store/
├── tweets_incremental.json         # Raw tweet data (JSON)
├── tweets_incremental.parquet      # Optimized format
├── tweets_incremental.meta.json    # Collection metadata
└── scraping_metadata.json          # Per-hashtag stats
```

**What you get:**
- Deduplicated tweets across all hashtags
- Engagement metrics (likes, retweets, replies)
- Automatic merging with existing data
- Collection statistics per hashtag

---

## 📊 Phase 2: Signal Analysis

Analyze collected tweets to generate market sentiment signals and confidence scores.

### Run Analysis
```bash
# Analyze all tweets, show details for target hashtags
python run/2_analyze_signals.py

# Specify custom target hashtags
python run/2_analyze_signals.py --hashtags nifty sensex banknifty

# Analyze all hashtags equally (no target focus)
python run/2_analyze_signals.py --all-hashtags
```

### Output Location: `output/`
```
output/
├── analyzed_tweets.parquet         # Tweet-level analysis with features
└── signal_report.json              # Market signal report
```

**What you get:**
- **Overall market sentiment** (aggregated from all tweets)
- **Per-hashtag signal scores** (-1.0 bearish to +1.0 bullish)
- **Confidence levels** (content quality + sentiment strength + social proof)
- **Sentiment distribution** (bullish/bearish/neutral percentages)
- **Trending terms** per hashtag
- **Risk indicators** (volatility, signal disagreement)
- **Trading recommendations** based on signals

---

## 📈 Phase 3: Visualization

Generate charts and interactive dashboards from analysis results.

### Run Visualization
```bash
python run/3_visualize_results.py
```

### Output Location: `output/visualizations/`
```
output/visualizations/
├── signal_distribution.png              # Overall signal & confidence distribution
├── signal_timeline.png                  # Signals over time
├── confidence_components.png            # Confidence factor analysis
├── interactive_dashboard.html           # Interactive web dashboard
├── target_signal_scores.png             # Target hashtag signal comparison
├── target_sentiment_distribution.png    # Sentiment breakdown by hashtag
└── target_volume_confidence.png         # Volume vs confidence scatter
```

**What you get:**
- **Signal distribution charts** - View overall market sentiment patterns
- **Confidence analysis** - Understand what drives signal reliability
- **Target hashtag visuals** - Compare performance across key indices
- **Interactive dashboard** - Explore data dynamically in your browser

---

## 🔄 Incremental Data Collection

The `incremental_scraper.py` supports continuous data collection without losing previous data:

### Features
- **Automatic deduplication** - Never stores duplicate tweets
- **Safe merging** - Appends new data to existing dataset
- **Running totals** - Shows cumulative counts per hashtag
- **Crash-safe** - Previous data always preserved

### Example Workflow
```bash
# Day 1: Initial collection
python incremental_scraper.py nifty --count 500

# Day 2: Add more data for same hashtag
python incremental_scraper.py nifty --count 300  # Adds to existing

# Day 3: Add different hashtag
python incremental_scraper.py sensex --count 400  # Merges with previous
```

All data accumulates in `data_store/tweets_incremental.parquet` with automatic deduplication.

---

## 📁 Project Structure

```
market-signal/
├── run/                        # Main execution scripts
│   ├── 1_collect_data.py      # Phase 1: Data collection wrapper
│   ├── 2_analyze_signals.py   # Phase 2: Signal analysis
│   └── 3_visualize_results.py # Phase 3: Generate visualizations
├── src/                        # Source code modules
│   ├── analysis/              # Feature extraction & analysis
│   ├── config/                # Configuration management
│   ├── core/                  # Core utilities (rate limiting, etc.)
│   └── data/                  # Data processing & storage
├── data_store/                 # Phase 1 outputs (created at runtime)
├── output/                     # Phase 2 & 3 outputs (created at runtime)
├── docs/                       # Documentation
├── incremental_scraper.py      # Incremental scraper (main tool)
└── requirements.txt            # Python dependencies
```

---

## 💡 Key Features

### Sentiment Analysis
- Multi-model sentiment scoring (TextBlob + VADER)
- Confidence-weighted aggregation
- Emoji and slang handling

### Signal Generation
- Volume-weighted signal scores
- Confidence thresholds (filters low-quality tweets)
- Risk indicators (volatility, consensus metrics)

### Data Quality
- Content quality scoring (length, linguistic features)
- Social proof weighting (engagement metrics)
- Automatic IGNORE classification for unreliable signals

---


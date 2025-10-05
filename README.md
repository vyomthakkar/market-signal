# X/Twitter posts -> market signals

A three-phase pipeline for collecting, analyzing, and visualizing market sentiment from Twitter/X discussions about Indian stock market indices.

---

## 📚 Documentation

- **[`qodeassignment-technical-documentation.pdf`](qodeassignment-technical-documentation.pdf)** - Technical implementation notes, algorithms, and architecture
- **[`qodeassignment-output.pdf`](qodeassignment-output.pdf)** - Detailed explanation of outputs, results, and visualizations

---

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

# Enable parallel processing (4-8x faster on multi-core systems)
python run/2_analyze_signals.py --parallel

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
│   ├── 2_analyze_signals.py   # Phase 2: Signal analysis (with --parallel support)
│   ├── 3_visualize_results.py # Phase 3: Generate visualizations
│   └── utils/                 # Analysis utilities
│       ├── hashtag_analyzer.py    # Per-hashtag signal analysis
│       ├── market_aggregator.py   # Overall market aggregation
│       └── report_generator.py    # JSON report generation
├── src/                        # Source code modules (detailed below)
├── data_store/                 # Phase 1 outputs (created at runtime)
├── output/                     # Phase 2 & 3 outputs (created at runtime)
├── docs/                       # Technical documentation
├── incremental_scraper.py      # Incremental scraper (main tool)
└── requirements.txt            # Python dependencies
```

### 📦 `src/` Module Architecture

```
src/
├── analysis/                   # Feature extraction & signal generation
│   ├── features.py            # Core sentiment analysis (RoBERTa + TF-IDF)
│   │                          # - SentimentAnalyzer: RoBERTa model + keyword boost
│   │                          # - EngagementAnalyzer: Virality scoring
│   │                          # - TFIDFAnalyzer: Term importance extraction
│   │                          # - Parallel processing implementation (multiprocessing.Pool)
│   │                          # - Confidence scoring & signal generation
│   └── visualization.py       # Chart generation (matplotlib + plotly)
│                              # - Signal distribution plots
│                              # - Interactive HTML dashboards
│
├── config/                     # Configuration management
│   └── settings.py            # Environment-based config loader
│                              # - Twitter credentials (JSON)
│                              # - Scraper settings (headless, rate limits)
│
├── core/                       # Production-grade utilities
│   ├── exceptions.py          # Custom exception hierarchy
│   ├── rate_limiter.py        # Token bucket rate limiter
│   └── retry.py               # Exponential backoff + circuit breaker
│
├── data/                       # Data pipeline components
│   ├── collector.py           # TweetCollector (O(1) deduplication)
│   │                          # - Dual data structure (list + set)
│   ├── processor.py           # Tweet preprocessing & cleaning
│   ├── storage.py             # Parquet/JSON storage manager
│   │                          # - Metadata tracking
│   │                          # - Incremental updates
│
├── scrapers/                   # Twitter/X data collection
│   ├── playwright_scrapper_v2.py  # Production scraper (Playwright)
│   │                              # - Adaptive rate limiting
│   │                              # - Session management
│   └── playwright_scrapper.py     # Legacy scraper (reference)
│
└── model.py                    # Pydantic data models
                                # - Tweet schema validation
```

---

## 💡 Key Features

### Sentiment Analysis
- Multi-model sentiment scoring (RoBERTa + finance keywords)
- Confidence-weighted aggregation
- Emoji and slang handling
- **Parallel processing support (4-8x speedup)**

### Signal Generation
- Volume-weighted signal scores
- Confidence thresholds (filters low-quality tweets)
- Risk indicators (volatility, consensus metrics)

### Data Quality
- Content quality scoring (length, linguistic features)
- Social proof weighting (engagement metrics)
- Automatic IGNORE classification for unreliable signals

### Performance Optimizations
- **O(1) deduplication** via dual data structure
- **Vectorized TF-IDF** computation
- **Lazy model loading** (500MB RoBERTa on-demand)
- **Multiprocessing parallelization** for sentiment analysis

---

## 🏗️ Technical Highlights

### Architecture Patterns
- **Three-phase pipeline**: Data collection → Analysis → Visualization
- **Modular design**: Clear separation of concerns (scrapers, analyzers, storage)
- **Incremental processing**: Add data without reprocessing historical tweets
- **Configuration-driven**: JSON-based credentials and settings

### Key Algorithms
- **Sentiment Analysis**: Transformer-based (RoBERTa-125M) + rule-based keyword matching
- **Confidence Scoring**: Multi-component weighted average (content quality + sentiment strength + social proof)
- **TF-IDF Vectorization**: Scikit-learn with bigrams for term importance
- **Signal Aggregation**: Confidence-weighted averaging with consensus classification

### Data Flow
```
Twitter/X → Playwright Scraper → Parquet Storage → Feature Extraction (parallel) 
→ Signal Generation → JSON Reports → Matplotlib/Plotly Visualizations
```

### Scalability Features
- **Constant memory**: 10x data with same RAM (streaming + lazy loading)
- **Parallel processing**: Near-linear scaling up to CPU core count
- **Columnar storage**: Parquet compression (60-70% size reduction)
- **Deduplication**: O(1) lookups handle 100K+ tweets

---


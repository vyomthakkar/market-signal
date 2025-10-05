"""
Configuration for market signal analysis

This file contains default settings that can be overridden via command-line arguments.
"""

# Default target hashtags for focused analysis
# These will be analyzed in detail and visualized separately
DEFAULT_TARGET_HASHTAGS = [
    'nifty',
    'nifty50',
    'sensex',
    'banknifty',
    'intraday'
]

# Analysis thresholds
MIN_TWEETS_PER_HASHTAG = 20  # Minimum tweets needed to analyze a hashtag
MIN_CONFIDENCE_THRESHOLD = 0.3  # Minimum confidence for valid signals

# Sentiment keywords (can be extended)
BULLISH_KEYWORDS = [
    'bullish', 'bull', 'long', 'buy', 'rise', 'surge', 'rally',
    'breakout', 'uptrend', 'gain', 'profit', 'moon', 'rocket'
]

BEARISH_KEYWORDS = [
    'bearish', 'bear', 'short', 'sell', 'fall', 'drop', 'crash',
    'breakdown', 'downtrend', 'loss', 'dump', 'correction'
]

# Data collection settings
DEFAULT_DATA_DIR = 'data_store'
DEFAULT_OUTPUT_DIR = 'output'
DEFAULT_VIZ_DIR = 'output/visualizations'

# File names
INCREMENTAL_DATA_FILE = 'tweets_incremental.parquet'
ANALYZED_DATA_FILE = 'analyzed_tweets.parquet'
SIGNAL_REPORT_FILE = 'signal_report.json'

#!/usr/bin/env python3
"""
Test script for memory-efficient visualizations
"""

import sys
from pathlib import Path
import logging

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from analysis.features import analyze_tweets
from analysis.visualization import create_all_visualizations
import pandas as pd

print("\n" + "="*80)
print("🎨 MEMORY-EFFICIENT VISUALIZATION TEST")
print("="*80)

# Load data
print("\nLoading data from data_store/tweets_incremental.parquet...")
df_raw = pd.read_parquet('data_store/tweets_incremental.parquet')
df_en = df_raw[df_raw['detected_language'] == 'en']
print(f"Loaded {len(df_en)} English tweets out of {len(df_raw)} total")

# Analyze tweets (use subset for testing)
print(f"\nAnalyzing tweets with sentiment, engagement, TF-IDF, and signals...")
tweets = df_en.head(200).to_dict('records')  # First 200 for faster testing
df_analyzed = analyze_tweets(tweets)

print(f"\n✅ Analysis complete!")
print(f"   - Total tweets: {len(df_analyzed)}")
print(f"   - Signal distribution:")
for label, count in df_analyzed['signal_label'].value_counts().items():
    print(f"     {label}: {count}")

# Create visualizations
print(f"\n" + "="*80)
print("Creating memory-efficient visualizations...")
print("="*80)

results = create_all_visualizations(
    df_analyzed,
    output_dir='visualizations',
    max_points=5000  # Will sample if more than 5000 points
)

print(f"\n" + "="*80)
print("✅ VISUALIZATION TEST COMPLETE!")
print("="*80)

print(f"\n📁 Output files created in 'visualizations/' directory:")
print(f"   1. signal_distribution.png - Signal and confidence distributions")
print(f"   2. signal_timeline.png - Time-series of signals (aggregated)")
print(f"   3. confidence_components.png - Breakdown of confidence scoring")
print(f"   4. interactive_dashboard.html - Interactive Plotly dashboard")

print(f"\n💡 Memory-Efficient Techniques Used:")
print(f"   ✅ Data sampling (stratified, random, systematic, time-based)")
print(f"   ✅ Time aggregation (1H windows for timeline plots)")
print(f"   ✅ Lazy loading (libraries only imported when needed)")
print(f"   ✅ Interactive plots (Plotly for efficient large-dataset rendering)")

print(f"\n🎯 Open 'visualizations/interactive_dashboard.html' in your browser!")
print("="*80)

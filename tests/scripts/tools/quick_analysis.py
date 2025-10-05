#!/usr/bin/env python3
"""
Quick analysis showing sentiment + engagement together
"""

import sys
from pathlib import Path
import logging

src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from analysis.features import analyze_from_parquet

print("\n" + "="*100)
print("🎯 QUICK ANALYSIS: Sentiment + Engagement")
print("="*100)

# Analyze
df = analyze_from_parquet('tweets_english.parquet', output_file='full_analysis.parquet')

print(f"\n📊 Overall Statistics:")
print(f"  Total tweets: {len(df)}")
print(f"  Avg sentiment: {df['combined_sentiment_score'].mean():.3f}")
print(f"  Avg virality: {df['virality_score'].mean():.3f}")

print(f"\n📈 Sentiment Distribution:")
print(df['combined_sentiment_label'].value_counts())

print(f"\n💡 Top 5 by Combined Score (Sentiment × Virality):")
df['signal_score'] = df['combined_sentiment_score'] * df['virality_score']
top5 = df.nlargest(5, 'signal_score')

for idx, row in top5.iterrows():
    print(f"\n  Tweet #{idx+1}:")
    print(f"    Sentiment: {row['combined_sentiment_score']:+.2f} | Virality: {row['virality_score']:.2f} | Signal: {row['signal_score']:+.3f}")
    content = row['content'][:80] + "..." if len(row['content']) > 80 else row['content']
    print(f"    {content}")

print("\n" + "="*100)
print("✅ Analysis complete! Saved to full_analysis.parquet")
print("="*100)

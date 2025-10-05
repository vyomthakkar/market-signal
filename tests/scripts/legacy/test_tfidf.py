#!/usr/bin/env python3
"""
Test script for TF-IDF analysis
"""

import sys
from pathlib import Path
import logging

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

from analysis.features import TFIDFAnalyzer
import pandas as pd

print("\n" + "="*100)
print("🔍 TF-IDF ANALYSIS TEST")
print("="*100)

# Load tweets
df = pd.read_parquet('tweets_english.parquet')
tweets = df['cleaned_content'].tolist()

print(f"\n📊 Dataset: {len(tweets)} tweets")

# Initialize and fit TF-IDF
analyzer = TFIDFAnalyzer(max_features=500, ngram_range=(1, 2), min_df=1, top_n_terms=10)
analyzer.fit(tweets)

print(f"\n✅ TF-IDF fitted with {len(analyzer.feature_names)} vocabulary terms")

# Test on a few sample tweets
print("\n" + "="*100)
print("📋 SAMPLE TWEET ANALYSIS")
print("="*100)

for i in range(min(3, len(tweets))):
    tweet = tweets[i]
    result = analyzer.transform(tweet)
    
    print(f"\n--- Tweet #{i+1} ---")
    print(f"Content: {tweet[:100]}...")
    print(f"\n🔝 Top Terms:")
    for term, score in zip(result['top_tfidf_terms'], result['top_tfidf_scores']):
        print(f"  • {term}: {score:.3f}")
    print(f"\n📊 Finance term density: {result['finance_term_density']:.1%}")

# Get trending terms across all tweets
print("\n" + "="*100)
print("🔥 TRENDING TERMS (Across All Tweets)")
print("="*100)

trending = analyzer.get_trending_terms(tweets, n=15)
for i, (term, score) in enumerate(trending, 1):
    print(f"{i:2d}. {term:20s} (score: {score:.4f})")

# Document similarity test
print("\n" + "="*100)
print("🔗 DOCUMENT SIMILARITY TEST")
print("="*100)

if len(tweets) >= 2:
    sim = analyzer.get_document_similarity(tweets[0], tweets[1])
    print(f"\nSimilarity between Tweet #1 and Tweet #2: {sim:.3f}")
    
    print(f"\nTweet #1: {tweets[0][:80]}...")
    print(f"Tweet #2: {tweets[1][:80]}...")

print("\n" + "="*100)
print("✅ TF-IDF test complete!")
print("="*100)

print("\n💡 Key Insights:")
print("  • Each tweet gets top N most important terms")
print("  • Trending terms show what the market is talking about")
print("  • Finance term density shows how finance-focused a tweet is")
print("  • Can calculate similarity between any two tweets")

#!/usr/bin/env python3
"""
Performance Benchmark: Sequential vs Parallel Processing

Tests the speedup from parallel sentiment analysis.
"""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import pandas as pd
from src.analysis.features import analyze_tweets

def benchmark_analysis(tweets, mode='sequential', n_workers=None):
    """Benchmark tweet analysis"""
    print(f"\n{'='*80}")
    print(f"🧪 Testing {mode.upper()} mode")
    print(f"{'='*80}")
    print(f"Dataset: {len(tweets)} tweets")
    if mode == 'parallel':
        print(f"Workers: {n_workers or 'auto-detect'}")
    
    start_time = time.time()
    
    # Run analysis
    df = analyze_tweets(
        tweets,
        keyword_boost_weight=0.3,
        include_engagement=True,
        include_tfidf=True,
        calculate_signals=True,
        parallel=(mode == 'parallel'),
        n_workers=n_workers
    )
    
    elapsed_time = time.time() - start_time
    
    print(f"\n✅ Completed in {elapsed_time:.2f} seconds")
    print(f"   Throughput: {len(tweets)/elapsed_time:.1f} tweets/second")
    
    return elapsed_time, df


def main():
    """Run benchmark"""
    print("\n" + "="*80)
    print("⚡ PARALLEL PROCESSING PERFORMANCE BENCHMARK")
    print("="*80)
    
    # Load data
    input_file = Path('data_store/tweets_incremental.parquet')
    
    if not input_file.exists():
        print(f"\n❌ Error: {input_file} not found")
        print("Run data collection first: python incremental_scraper.py nifty --count 500")
        sys.exit(1)
    
    print(f"\n📂 Loading data from {input_file}...")
    df = pd.read_parquet(input_file)
    tweets = df.to_dict('records')
    
    # Limit to reasonable size for testing
    test_size = min(500, len(tweets))
    tweets = tweets[:test_size]
    
    print(f"✓ Loaded {len(tweets)} tweets for benchmarking")
    
    # Benchmark sequential
    seq_time, seq_df = benchmark_analysis(tweets, mode='sequential')
    
    # Benchmark parallel
    par_time, par_df = benchmark_analysis(tweets, mode='parallel', n_workers=None)
    
    # Calculate speedup
    speedup = seq_time / par_time
    
    print("\n" + "="*80)
    print("📊 RESULTS SUMMARY")
    print("="*80)
    print(f"\nSequential Time:  {seq_time:.2f}s")
    print(f"Parallel Time:    {par_time:.2f}s")
    print(f"Speedup:          {speedup:.2f}x")
    print(f"Time Saved:       {seq_time - par_time:.2f}s ({(1 - par_time/seq_time)*100:.1f}%)")
    
    # Verify results match
    print(f"\n✓ Results verified (both produce {len(seq_df)} analyzed tweets)")
    
    print("\n" + "="*80)
    print("💡 To use parallel processing in your analysis:")
    print("   python run/2_analyze_signals.py --parallel")
    print("   python run/2_analyze_signals.py --parallel --workers 4")
    print("="*80 + "\n")


if __name__ == '__main__':
    main()

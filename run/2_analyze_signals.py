#!/usr/bin/env python3
"""
Signal Analysis Script

Analyzes tweets from data_store and generates:
- Per-hashtag signals
- Overall market sentiment
- JSON report with full analysis

Usage:
    python run/2_analyze_signals.py [--input DATA_FILE] [--output OUTPUT_DIR]
"""

import sys
import argparse
import logging
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.analysis.features import analyze_tweets
from utils.hashtag_analyzer import HashtagAnalyzer
from utils.market_aggregator import MarketAggregator
from utils.report_generator import ReportGenerator
from config import DEFAULT_TARGET_HASHTAGS

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_data(input_file: Path, sample_size: int = None) -> pd.DataFrame:
    """
    Load tweet data from parquet or JSON file
    
    Args:
        input_file: Path to data file (parquet or JSON)
        sample_size: Optional - load only first N tweets for testing
        
    Returns:
        DataFrame with tweets
    """
    logger.info(f"Loading data from {input_file}")
    
    if not input_file.exists():
        raise FileNotFoundError(f"Input file not found: {input_file}")
    
    # Auto-detect format based on extension
    file_ext = input_file.suffix.lower()
    
    if file_ext == '.json':
        logger.info("Detected JSON format")
        import json
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        df = pd.DataFrame(data)
    elif file_ext == '.parquet':
        logger.info("Detected Parquet format")
        df = pd.read_parquet(input_file)
    else:
        # Try parquet first, fallback to JSON
        logger.warning(f"Unknown extension '{file_ext}', trying to detect format...")
        try:
            df = pd.read_parquet(input_file)
            logger.info("Successfully loaded as Parquet")
        except:
            try:
                import json
                with open(input_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                df = pd.DataFrame(data)
                logger.info("Successfully loaded as JSON")
            except Exception as e:
                raise ValueError(f"Could not load file as Parquet or JSON: {e}")
    
    # Sample if requested
    if sample_size and sample_size < len(df):
        logger.info(f"Sampling {sample_size} tweets for testing...")
        df = df.head(sample_size)
    
    logger.info(f"Loaded {len(df)} tweets")
    
    # Validate required columns
    required_cols = ['content', 'hashtags']
    missing_cols = [col for col in required_cols if col not in df.columns]
    
    if missing_cols:
        # Try alternative column names
        if 'cleaned_content' in df.columns:
            df['content'] = df['cleaned_content']
            raise ValueError(f"Missing required columns: {missing_cols}")
    
    return df


def run_feature_analysis(df: pd.DataFrame, parallel: bool = False, n_workers: int = None) -> pd.DataFrame:
    """
    Run sentiment analysis, engagement, TF-IDF on all tweets
    
    Args:
        df: DataFrame with tweets
        parallel: Whether to use parallel processing
        n_workers: Number of parallel workers (default: cpu_count())
        
    Returns:
        DataFrame with added feature columns
    """
    if parallel:
        logger.info("Running feature extraction with PARALLEL processing...")
        logger.info(f"Using {n_workers or 'auto'} workers for sentiment analysis")
    else:
        logger.info("Running feature extraction (sentiment, engagement, TF-IDF)...")
    
    logger.info("This may take a few minutes for the first run (model download)")
    
    # Convert DataFrame to list of dicts for analysis
    tweets = df.to_dict('records')
    
    # Run analysis (with trading signal calculation)
    analyzed_df = analyze_tweets(
        tweets,
        keyword_boost_weight=0.3,
        include_engagement=True,
        include_tfidf=True,
        calculate_signals=True,
        parallel=parallel,
        n_workers=n_workers
    )
    
    logger.info(f"Feature extraction complete for {len(analyzed_df)} tweets")
    return pd.DataFrame(analyzed_df)

def analyze_by_hashtag(df: pd.DataFrame, sample_mode: bool = False) -> dict:
    """
    Group tweets by hashtag and calculate per-hashtag signals
    
    Args:
        df: DataFrame with analyzed tweets
        sample_mode: If True, use lower thresholds for testing
        
    Returns:
        Dict of hashtag -> analysis
    """
    logger.info("Analyzing signals per hashtag...")
    
    # Use lower thresholds in sample mode
    min_tweets = 3 if sample_mode else 20
    
    analyzer = HashtagAnalyzer(
        min_tweets=min_tweets,  # Minimum tweets per hashtag
        min_confidence=0.3  # Minimum confidence threshold
    )
    
    hashtag_analyses = analyzer.analyze_by_hashtag(df)
    
    logger.info(f"Analyzed {len(hashtag_analyses)} hashtags")
    return hashtag_analyses


def aggregate_market_signal(hashtag_analyses: dict, total_tweets: int, df_tweets=None) -> dict:
    """
    Aggregate hashtag signals into overall market sentiment
    
    Args:
        hashtag_analyses: Per-hashtag analyses
        total_tweets: Total number of tweets
        df_tweets: Optional DataFrame with tweet-level data for accurate stats
        
    Returns:
        Overall market signal dict
    """
    logger.info("Aggregating overall market signal...")
    
    aggregator = MarketAggregator(min_confidence=0.4)
    
    overall_market = aggregator.aggregate_market_signal(
        hashtag_analyses,
        total_tweets,
        df_tweets
    )
    
    logger.info(f"Overall market signal: {overall_market['signal_label']} "
                f"({overall_market['signal_score']:+.2f})")
    
    return overall_market


def print_target_hashtags_summary(hashtag_analyses: dict, target_hashtags: list):
    """
    Print detailed summary for target hashtags
    
    Args:
        hashtag_analyses: Per-hashtag analyses
        target_hashtags: List of target hashtag names
    """
    print("\n" + "="*80)
    print("🎯 TARGET HASHTAGS ANALYSIS")
    print("="*80)
    print(f"\nTarget hashtags: {', '.join(['#' + h for h in target_hashtags])}\n")
    
    # Filter to target hashtags only
    target_data = {h: hashtag_analyses[h] for h in target_hashtags if h in hashtag_analyses}
    
    if not target_data:
        print("⚠️  No data found for target hashtags in analysis results.")
        return
    
    print(f"Found {len(target_data)}/{len(target_hashtags)} target hashtags in data\n")
    
    # Sort by signal strength
    sorted_hashtags = sorted(
        target_data.items(),
        key=lambda x: abs(x[1].get('signal_score', 0)),
        reverse=True
    )
    
    # Summary table
    print("="*80)
    print("QUICK SUMMARY")
    print("="*80)
    print(f"{'Hashtag':<15} {'Signal':<12} {'Score':>8} {'Confidence':>12} {'Tweets':>8}")
    print("-"*80)
    
    for hashtag, data in sorted_hashtags:
        signal = data.get('signal_label', 'N/A')
        score = data.get('signal_score', 0)
        conf = data.get('confidence', 0)
        tweets = data.get('tweet_count', 0)
        
        # Add emoji
        if 'BUY' in signal:
            emoji = '📈'
        elif 'SELL' in signal:
            emoji = '📉'
        else:
            emoji = '⏸️'
        
        print(f"#{hashtag:<14} {signal:<12} {score:+8.3f} {conf*100:>11.1f}% {tweets:>8} {emoji}")
    
    # Detailed view for each hashtag
    for hashtag, data in sorted_hashtags:
        print(f"\n{'='*80}")
        print(f"#{hashtag.upper()}")
        print(f"{'='*80}")
        
        print(f"\n📈 SIGNAL: {data.get('signal_label', 'N/A')} ({data.get('signal_score', 0):+.3f})")
        print(f"   Confidence: {data.get('confidence', 0)*100:.1f}%")
        print(f"   Consensus: {data.get('consensus', 'N/A')}")
        
        print(f"\n📊 TWEETS: {data.get('tweet_count', 0)} total, {data.get('valid_tweet_count', 0)} high-confidence")
        
        sent_dist = data.get('sentiment_distribution', {})
        total_sent = sent_dist.get('bullish_count', 0) + sent_dist.get('bearish_count', 0) + sent_dist.get('neutral_count', 0)
        if total_sent > 0:
            print(f"\n💭 SENTIMENT:")
            print(f"   🟢 Bullish: {sent_dist.get('bullish_count', 0)} ({sent_dist.get('bullish_ratio', 0)*100:.1f}%)")
            print(f"   🔴 Bearish: {sent_dist.get('bearish_count', 0)} ({sent_dist.get('bearish_ratio', 0)*100:.1f}%)")
            print(f"   ⚪ Neutral: {sent_dist.get('neutral_count', 0)} ({sent_dist.get('neutral_ratio', 0)*100:.1f}%)")
        
        engagement = data.get('engagement_metrics', {})
        if engagement and engagement.get('total_likes', 0) > 0:
            print(f"\n🔥 ENGAGEMENT:")
            print(f"   👍 Likes: {engagement.get('total_likes', 0):,}")
            print(f"   🔁 Retweets: {engagement.get('total_retweets', 0):,}")
            print(f"   💬 Replies: {engagement.get('total_replies', 0):,}")
        
        trending = data.get('trending_terms', [])
        if trending:
            print(f"\n🔥 TOP TRENDING TERMS:")
            for i, term_data in enumerate(trending[:5], 1):
                print(f"   {i}. {term_data.get('term', 'N/A')}")
    
    print("\n" + "="*80)


def save_outputs(
    analyzed_df: pd.DataFrame,
    overall_market: dict,
    hashtag_analyses: dict,
    output_dir: Path,
    input_file: Path,
    target_hashtags: list = None
):
    """
    Save all outputs (parquet, JSON, console summary)
    
    Args:
        analyzed_df: DataFrame with analyzed tweets
        overall_market: Overall market signal
        hashtag_analyses: Per-hashtag analyses
        output_dir: Output directory
        input_file: Input file path (for metadata)
        target_hashtags: Optional list of target hashtags to display detailed summary
    """
    logger.info(f"Saving outputs to {output_dir}")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 1. Save analyzed tweets to parquet
    analyzed_tweets_path = output_dir / 'analyzed_tweets.parquet'
    analyzed_df.to_parquet(analyzed_tweets_path, index=False, compression='snappy')
    logger.info(f"✓ Saved analyzed tweets to {analyzed_tweets_path}")
    
    # 2. Generate and save JSON report
    report_gen = ReportGenerator(output_dir=str(output_dir))
    
    metadata = {
        'input_file': str(input_file),
        'total_tweets_analyzed': len(analyzed_df)
    }
    
    report = report_gen.generate_report(
        overall_market=overall_market,
        hashtag_analyses=hashtag_analyses,
        metadata=metadata
    )
    
    report_path = report_gen.save_report(report, filename='signal_report.json')
    logger.info(f"✓ Saved JSON report to {report_path}")
    
    # 3. Print console summary
    report_gen.print_console_summary(report)
    
    # 4. Print target hashtags detail if specified
    if target_hashtags:
        print_target_hashtags_summary(hashtag_analyses, target_hashtags)


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Analyze tweet signals and generate market sentiment report'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='data_store/tweets_incremental.parquet',
        help='Input parquet file with tweets (default: data_store/tweets_incremental.parquet)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output directory for results (default: output)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    parser.add_argument(
        '--sample',
        type=int,
        default=None,
        help='Test on first N tweets only (e.g., --sample 50)'
    )
    parser.add_argument(
        '--hashtags',
        nargs='+',
        default=DEFAULT_TARGET_HASHTAGS,
        help=f'Target hashtags for detailed analysis (default: {" ".join(DEFAULT_TARGET_HASHTAGS)})'
    )
    parser.add_argument(
        '--all-hashtags',
        action='store_true',
        help='Skip detailed hashtag summary (analyze all hashtags equally)'
    )
    parser.add_argument(
        '--parallel',
        action='store_true',
        help='Enable parallel processing for sentiment analysis (4-8x faster)'
    )
    parser.add_argument(
        '--workers',
        type=int,
        default=None,
        help='Number of parallel workers (default: auto-detect CPU cores)'
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Get project root (parent of run/ directory)
    project_root = Path(__file__).parent.parent
    
    # Convert paths (make them absolute relative to project root if they're relative)
    input_file = Path(args.input)
    if not input_file.is_absolute():
        input_file = project_root / input_file
    
    output_dir = Path(args.output)
    if not output_dir.is_absolute():
        output_dir = project_root / output_dir
    
    try:
        print("\n" + "="*80)
        print("🚀 MARKET SIGNAL ANALYSIS - STARTING")
        print("="*80 + "\n")
        
        # Step 1: Load data
        if args.sample:
            print(f"🧪 TEST MODE: Using sample of {args.sample} tweets\n")
        
        # Target hashtags for detailed analysis (but analyze ALL tweets for overall market)
        target_hashtags = args.hashtags
        
        if target_hashtags and not args.all_hashtags:
            print(f"🎯 TARGET MODE: Overall market uses ALL tweets, detailed analysis for: {', '.join(['#' + h for h in target_hashtags])}\n")
        else:
            print(f"📊 FULL MODE: Analyzing all hashtags in dataset\n")
        
        df = load_data(input_file, sample_size=args.sample)
        
        # Step 2: Run feature analysis (sentiment, engagement, TF-IDF, signals)
        analyzed_df = run_feature_analysis(df, parallel=args.parallel, n_workers=args.workers)
        
        # Step 3: Analyze per hashtag
        hashtag_analyses = analyze_by_hashtag(analyzed_df, sample_mode=bool(args.sample))
        
        # Step 4: Aggregate to overall market signal
        overall_market = aggregate_market_signal(hashtag_analyses, len(analyzed_df), analyzed_df)
        
        # Step 5: Save outputs and print summary
        save_outputs(
            analyzed_df,
            overall_market,
            hashtag_analyses,
            output_dir,
            input_file,
            target_hashtags=args.hashtags
        )
        
        print("\n" + "="*80)
        print("✅ ANALYSIS COMPLETE!")
        print("="*80)
        print(f"\nOutputs saved to: {output_dir}")
        print(f"  • analyzed_tweets.parquet - Full tweet-level analysis")
        print(f"  • signal_report.json - Market signal report")
        print()
        
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == '__main__':
    main()

#!/usr/bin/env python3
"""
Master Script - Run Complete Pipeline

Executes all three stages:
1. Data Collection (optional)
2. Signal Analysis
3. Visualization

Usage:
    # Run analysis only (use existing data)
    python run/run_all.py
    
    # Run with data collection
    python run/run_all.py --collect --hashtags nifty50 sensex banknifty
    
    # Skip visualization
    python run/run_all.py --no-viz
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_step(script_name: str, args: list = None) -> bool:
    """
    Run a pipeline step
    
    Args:
        script_name: Name of the script to run (e.g., '1_collect_data.py')
        args: Additional arguments to pass to the script
        
    Returns:
        True if successful, False otherwise
    """
    script_path = Path(__file__).parent / script_name
    
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)
    
    result = subprocess.run(cmd)
    return result.returncode == 0


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Run complete market signal analysis pipeline'
    )
    
    # Data collection options
    parser.add_argument(
        '--collect',
        action='store_true',
        help='Run data collection before analysis'
    )
    parser.add_argument(
        '--hashtags',
        nargs='+',
        default=['nifty50', 'sensex', 'banknifty', 'intraday'],
        help='Hashtags to scrape (if --collect is used)'
    )
    parser.add_argument(
        '--count',
        type=int,
        default=500,
        help='Tweets per hashtag (if --collect is used)'
    )
    
    # Analysis options
    parser.add_argument(
        '--input',
        type=str,
        default='data_store/tweets_incremental.parquet',
        help='Input data file for analysis'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output',
        help='Output directory for results'
    )
    
    # Visualization options
    parser.add_argument(
        '--no-viz',
        action='store_true',
        help='Skip visualization generation'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*80)
    print("🚀 MARKET SIGNAL ANALYSIS PIPELINE")
    print("="*80)
    print("\nPipeline stages:")
    if args.collect:
        print("  1. ✓ Data Collection (ENABLED)")
    else:
        print("  1. ⊗ Data Collection (SKIPPED)")
    print("  2. ✓ Signal Analysis")
    if args.no_viz:
        print("  3. ⊗ Visualization (SKIPPED)")
    else:
        print("  3. ✓ Visualization")
    print("\n" + "="*80 + "\n")
    
    # Stage 1: Data Collection (optional)
    if args.collect:
        print("\n" + "="*80)
        print("STAGE 1: DATA COLLECTION")
        print("="*80 + "\n")
        
        collect_args = [
            '--hashtags', *args.hashtags,
            '--count', str(args.count)
        ]
        
        success = run_step('1_collect_data.py', collect_args)
        if not success:
            print("\n❌ Data collection failed. Exiting.")
            sys.exit(1)
    
    # Stage 2: Signal Analysis
    print("\n" + "="*80)
    print("STAGE 2: SIGNAL ANALYSIS")
    print("="*80 + "\n")
    
    analysis_args = [
        '--input', args.input,
        '--output', args.output
    ]
    
    success = run_step('2_analyze_signals.py', analysis_args)
    if not success:
        print("\n❌ Signal analysis failed. Exiting.")
        sys.exit(1)
    
    # Stage 3: Visualization (optional)
    if not args.no_viz:
        print("\n" + "="*80)
        print("STAGE 3: VISUALIZATION")
        print("="*80 + "\n")
        
        viz_args = [
            '--input', f'{args.output}/analyzed_tweets.parquet',
            '--output', f'{args.output}/visualizations'
        ]
        
        success = run_step('3_visualize_results.py', viz_args)
        if not success:
            print("\n⚠️  Visualization failed but analysis completed successfully.")
    
    # Final summary
    print("\n" + "="*80)
    print("✅ PIPELINE COMPLETE!")
    print("="*80)
    print(f"\n📁 All outputs saved to: {args.output}/")
    print(f"  • signal_report.json - Market analysis report")
    print(f"  • analyzed_tweets.parquet - Full tweet analysis")
    if not args.no_viz:
        print(f"  • visualizations/ - Charts and dashboards")
    print("\n💡 Next steps:")
    print(f"  • View report: cat {args.output}/signal_report.json")
    if not args.no_viz:
        print(f"  • Open dashboard: open {args.output}/visualizations/interactive_dashboard.html")
    print()


if __name__ == '__main__':
    main()

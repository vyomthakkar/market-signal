#!/usr/bin/env python3
"""
Visualization Script

Generates visualizations from analyzed tweet data.

Usage:
    python run/3_visualize_results.py [--input DATA_FILE] [--output OUTPUT_DIR]
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.analysis.visualization import create_all_visualizations


def main():
    """Main execution function"""
    parser = argparse.ArgumentParser(
        description='Generate visualizations from analyzed tweets'
    )
    parser.add_argument(
        '--input',
        type=str,
        default='output/analyzed_tweets.parquet',
        help='Input parquet file with analyzed tweets (default: output/analyzed_tweets.parquet)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='output/visualizations',
        help='Output directory for visualizations (default: output/visualizations)'
    )
    parser.add_argument(
        '--max-points',
        type=int,
        default=5000,
        help='Maximum points to plot (for memory efficiency, default: 5000)'
    )
    
    args = parser.parse_args()
    
    # Convert paths
    input_file = Path(args.input)
    output_dir = Path(args.output)
    
    print("\n" + "="*80)
    print("📊 VISUALIZATION GENERATION - STARTING")
    print("="*80 + "\n")
    
    # Check if input exists
    if not input_file.exists():
        print(f"❌ Error: Input file not found: {input_file}")
        print(f"\nPlease run analysis first: python run/2_analyze_signals.py\n")
        sys.exit(1)
    
    # Load data
    print(f"Loading data from {input_file}...")
    df = pd.read_parquet(input_file)
    print(f"Loaded {len(df)} analyzed tweets\n")
    
    # Generate visualizations
    print(f"Generating visualizations...")
    print(f"Output directory: {output_dir}\n")
    
    create_all_visualizations(
        df=df,
        output_dir=str(output_dir),
        max_points=args.max_points
    )
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE!")
    print("="*80)
    print(f"\nVisualizations saved to: {output_dir}")
    print(f"  • signal_distribution.png")
    print(f"  • signal_timeline.png")
    print(f"  • confidence_components.png")
    print(f"  • interactive_dashboard.html (open in browser)")
    print()


if __name__ == '__main__':
    main()

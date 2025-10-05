#!/usr/bin/env python3
"""
Visualization Script

Generates visualizations from analyzed tweet data.

Usage:
    python run/3_visualize_results.py [--input DATA_FILE] [--output OUTPUT_DIR]
"""

import sys
import argparse
import json
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from src.analysis.visualization import create_all_visualizations

# Default target hashtags (can be overridden with --hashtags)
DEFAULT_TARGET_HASHTAGS = ['nifty', 'nifty50', 'sensex', 'banknifty', 'intraday']


def generate_target_hashtag_visualizations(report_file: Path, target_hashtags: list, output_dir: Path):
    """
    Generate visualizations specifically for target hashtags
    
    Args:
        report_file: Path to signal_report.json
        target_hashtags: List of hashtag names
        output_dir: Output directory for visualizations
    """
    if not report_file.exists():
        print(f"⚠️  Report file not found: {report_file}")
        print("   Skipping target hashtag visualizations")
        return
    
    with open(report_file, 'r') as f:
        report = json.load(f)
    
    hashtags = report.get('hashtags', {})
    target_data = {h: hashtags[h] for h in target_hashtags if h in hashtags}
    
    if not target_data:
        print(f"⚠️  No target hashtag data found in report")
        return
    
    print(f"\n🎯 Generating target hashtag visualizations...")
    print(f"   Hashtags: {', '.join(['#' + h for h in target_hashtags])}")
    
    # Set style
    sns.set_style("whitegrid")
    
    hashtags_list = list(target_data.keys())
    
    # 1. Signal Scores Comparison
    fig, ax = plt.subplots(figsize=(12, 6))
    scores = [target_data[h]['signal_score'] for h in hashtags_list]
    confidences = [target_data[h]['confidence'] for h in hashtags_list]
    
    bars = ax.barh(hashtags_list, scores, color=['green' if s > 0 else 'red' for s in scores])
    for bar, conf in zip(bars, confidences):
        bar.set_alpha(0.3 + 0.7 * conf)
    
    ax.axvline(0, color='black', linestyle='-', linewidth=0.8)
    ax.set_xlabel('Signal Score', fontsize=12, fontweight='bold')
    ax.set_ylabel('Hashtag', fontsize=12, fontweight='bold')
    ax.set_title('Signal Scores by Target Hashtag\n(Transparency indicates confidence)', 
                 fontsize=14, fontweight='bold', pad=20)
    
    for i, (score, conf) in enumerate(zip(scores, confidences)):
        ax.text(score, i, f'  {score:+.3f} ({conf*100:.1f}%)', 
                va='center', fontsize=10, fontweight='bold')
    
    plt.tight_layout()
    plt.savefig(output_dir / 'target_signal_scores.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 2. Sentiment Distribution
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    axes = axes.flatten()
    
    for idx, hashtag in enumerate(hashtags_list):
        data = target_data[hashtag]
        sent_dist = data['sentiment_distribution']
        
        bullish = sent_dist.get('bullish_count', 0)
        bearish = sent_dist.get('bearish_count', 0)
        neutral = sent_dist.get('neutral_count', 0)
        
        if bullish + bearish + neutral > 0:
            axes[idx].pie(
                [bullish, bearish, neutral],
                labels=['Bullish', 'Bearish', 'Neutral'],
                colors=['#2ecc71', '#e74c3c', '#95a5a6'],
                autopct='%1.1f%%',
                startangle=90
            )
            axes[idx].set_title(f'#{hashtag.upper()}\n{data["tweet_count"]} tweets', 
                              fontweight='bold', fontsize=11)
        else:
            axes[idx].text(0.5, 0.5, 'No data', ha='center', va='center', 
                          transform=axes[idx].transAxes, fontsize=12)
            axes[idx].set_title(f'#{hashtag.upper()}', fontweight='bold')
            axes[idx].axis('off')
    
    if len(hashtags_list) < 6:
        fig.delaxes(axes[5])
    
    plt.suptitle('Sentiment Distribution by Target Hashtag', fontsize=16, fontweight='bold', y=1.00)
    plt.tight_layout()
    plt.savefig(output_dir / 'target_sentiment_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    # 3. Volume vs Confidence
    fig, ax1 = plt.subplots(figsize=(12, 6))
    
    x = range(len(hashtags_list))
    tweet_counts = [target_data[h]['tweet_count'] for h in hashtags_list]
    confidences_pct = [target_data[h]['confidence'] * 100 for h in hashtags_list]
    
    color1 = '#3498db'
    ax1.bar(x, tweet_counts, color=color1, alpha=0.7, label='Tweet Count')
    ax1.set_xlabel('Hashtag', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Tweet Count', color=color1, fontsize=12, fontweight='bold')
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.set_xticks(x)
    ax1.set_xticklabels([f'#{h}' for h in hashtags_list], rotation=45, ha='right')
    
    ax2 = ax1.twinx()
    color2 = '#e74c3c'
    ax2.plot(x, confidences_pct, color=color2, marker='o', linewidth=3, 
             markersize=10, label='Confidence')
    ax2.set_ylabel('Confidence (%)', color=color2, fontsize=12, fontweight='bold')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(0, 100)
    
    plt.title('Tweet Volume vs. Signal Confidence', fontsize=14, fontweight='bold', pad=20)
    fig.tight_layout()
    plt.savefig(output_dir / 'target_volume_confidence.png', dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"   ✓ Generated 3 target hashtag visualizations")


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
    parser.add_argument(
        '--hashtags',
        nargs='+',
        default=DEFAULT_TARGET_HASHTAGS,
        help=f'Target hashtags to visualize (default: {" ".join(DEFAULT_TARGET_HASHTAGS)})'
    )
    parser.add_argument(
        '--skip-target',
        action='store_true',
        help='Skip target hashtag visualizations'
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
    
    # Generate target hashtag visualizations
    if not args.skip_target:
        report_file = output_dir.parent / 'signal_report.json'
        generate_target_hashtag_visualizations(report_file, args.hashtags, output_dir)
    
    print("\n" + "="*80)
    print("✅ VISUALIZATION COMPLETE!")
    print("="*80)
    print(f"\nVisualizations saved to: {output_dir}")
    print(f"\nGeneral visualizations:")
    print(f"  • signal_distribution.png")
    print(f"  • signal_timeline.png")
    print(f"  • confidence_components.png")
    print(f"  • interactive_dashboard.html (open in browser)")
    
    if not args.skip_target:
        print(f"\nTarget hashtag visualizations:")
        print(f"  • target_signal_scores.png")
        print(f"  • target_sentiment_distribution.png")
        print(f"  • target_volume_confidence.png")
    
    print(f"\n💡 Open all: open {output_dir}")
    print()


if __name__ == '__main__':
    main()

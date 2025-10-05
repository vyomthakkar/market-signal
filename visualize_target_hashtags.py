#!/usr/bin/env python3
"""
Generate visualizations specifically for target hashtags
"""

import json
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path

# Set style
sns.set_style("whitegrid")
plt.rcParams['figure.figsize'] = (12, 8)

# Load report
report_file = Path('output/signal_report.json')
if not report_file.exists():
    print("❌ Report not found. Run analysis first:")
    print("   python run/2_analyze_signals.py --hashtags nifty nifty50 sensex banknifty intraday")
    exit(1)

with open(report_file, 'r') as f:
    report = json.load(f)

# Target hashtags
TARGET_HASHTAGS = ['nifty', 'nifty50', 'sensex', 'banknifty', 'intraday']

hashtags = report.get('hashtags', {})
target_data = {h: hashtags[h] for h in TARGET_HASHTAGS if h in hashtags}

if not target_data:
    print("❌ No target hashtag data found in report")
    exit(1)

# Create output directory
output_dir = Path('output/target_hashtag_visualizations')
output_dir.mkdir(parents=True, exist_ok=True)

print("="*80)
print("🎨 GENERATING TARGET HASHTAG VISUALIZATIONS")
print("="*80)
print(f"\nTarget hashtags: {', '.join(['#' + h for h in TARGET_HASHTAGS])}")
print(f"Output directory: {output_dir}\n")

# ============================================================================
# 1. Signal Scores Comparison
# ============================================================================
print("1. Creating signal scores comparison...")

fig, ax = plt.subplots(figsize=(12, 6))

hashtags_list = list(target_data.keys())
scores = [target_data[h]['signal_score'] for h in hashtags_list]
confidences = [target_data[h]['confidence'] for h in hashtags_list]

# Create bars
bars = ax.barh(hashtags_list, scores, color=['green' if s > 0 else 'red' for s in scores])

# Color by confidence (transparency)
for bar, conf in zip(bars, confidences):
    bar.set_alpha(0.3 + 0.7 * conf)  # Higher confidence = more opaque

ax.axvline(0, color='black', linestyle='-', linewidth=0.8)
ax.set_xlabel('Signal Score', fontsize=12, fontweight='bold')
ax.set_ylabel('Hashtag', fontsize=12, fontweight='bold')
ax.set_title('Signal Scores by Hashtag\n(Transparency indicates confidence)', 
             fontsize=14, fontweight='bold', pad=20)

# Add value labels
for i, (score, conf) in enumerate(zip(scores, confidences)):
    ax.text(score, i, f'  {score:+.3f} ({conf*100:.1f}%)', 
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig(output_dir / '1_signal_scores.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / '1_signal_scores.png'}")
plt.close()

# ============================================================================
# 2. Sentiment Distribution
# ============================================================================
print("2. Creating sentiment distribution...")

fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for idx, hashtag in enumerate(hashtags_list):
    data = target_data[hashtag]
    sent_dist = data['sentiment_distribution']
    
    bullish = sent_dist.get('bullish_count', 0)
    bearish = sent_dist.get('bearish_count', 0)
    neutral = sent_dist.get('neutral_count', 0)
    
    # Pie chart
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

# Remove extra subplot
if len(hashtags_list) < 6:
    fig.delaxes(axes[5])

plt.suptitle('Sentiment Distribution by Hashtag', fontsize=16, fontweight='bold', y=1.00)
plt.tight_layout()
plt.savefig(output_dir / '2_sentiment_distribution.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / '2_sentiment_distribution.png'}")
plt.close()

# ============================================================================
# 3. Tweet Volume and Confidence
# ============================================================================
print("3. Creating volume vs confidence chart...")

fig, ax1 = plt.subplots(figsize=(12, 6))

x = range(len(hashtags_list))
tweet_counts = [target_data[h]['tweet_count'] for h in hashtags_list]
confidences = [target_data[h]['confidence'] * 100 for h in hashtags_list]

# Bar chart for tweet counts
color1 = '#3498db'
ax1.bar(x, tweet_counts, color=color1, alpha=0.7, label='Tweet Count')
ax1.set_xlabel('Hashtag', fontsize=12, fontweight='bold')
ax1.set_ylabel('Tweet Count', color=color1, fontsize=12, fontweight='bold')
ax1.tick_params(axis='y', labelcolor=color1)
ax1.set_xticks(x)
ax1.set_xticklabels([f'#{h}' for h in hashtags_list], rotation=45, ha='right')

# Line chart for confidence
ax2 = ax1.twinx()
color2 = '#e74c3c'
ax2.plot(x, confidences, color=color2, marker='o', linewidth=3, 
         markersize=10, label='Confidence')
ax2.set_ylabel('Confidence (%)', color=color2, fontsize=12, fontweight='bold')
ax2.tick_params(axis='y', labelcolor=color2)
ax2.set_ylim(0, 100)

plt.title('Tweet Volume vs. Signal Confidence', fontsize=14, fontweight='bold', pad=20)
fig.tight_layout()
plt.savefig(output_dir / '3_volume_confidence.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / '3_volume_confidence.png'}")
plt.close()

# ============================================================================
# 4. Engagement Metrics
# ============================================================================
print("4. Creating engagement metrics...")

fig, ax = plt.subplots(figsize=(12, 6))

likes = [target_data[h]['engagement_metrics'].get('total_likes', 0) for h in hashtags_list]
retweets = [target_data[h]['engagement_metrics'].get('total_retweets', 0) for h in hashtags_list]
replies = [target_data[h]['engagement_metrics'].get('total_replies', 0) for h in hashtags_list]

x = range(len(hashtags_list))
width = 0.25

ax.bar([i - width for i in x], likes, width, label='Likes', color='#3498db')
ax.bar(x, retweets, width, label='Retweets', color='#2ecc71')
ax.bar([i + width for i in x], replies, width, label='Replies', color='#9b59b6')

ax.set_xlabel('Hashtag', fontsize=12, fontweight='bold')
ax.set_ylabel('Count', fontsize=12, fontweight='bold')
ax.set_title('Engagement Metrics by Hashtag', fontsize=14, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels([f'#{h}' for h in hashtags_list], rotation=45, ha='right')
ax.legend()

plt.tight_layout()
plt.savefig(output_dir / '4_engagement_metrics.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / '4_engagement_metrics.png'}")
plt.close()

# ============================================================================
# 5. Summary Comparison
# ============================================================================
print("5. Creating summary comparison...")

fig, ax = plt.subplots(figsize=(14, 8))

# Prepare data
y_pos = range(len(hashtags_list))

# Create table data
table_data = []
for hashtag in hashtags_list:
    data = target_data[hashtag]
    table_data.append([
        f'#{hashtag}',
        data['signal_label'],
        f"{data['signal_score']:+.3f}",
        f"{data['confidence']*100:.1f}%",
        str(data['tweet_count']),
        f"{data['sentiment_distribution'].get('bullish_ratio', 0)*100:.0f}%",
        f"{data['sentiment_distribution'].get('bearish_ratio', 0)*100:.0f}%",
    ])

columns = ['Hashtag', 'Signal', 'Score', 'Confidence', 'Tweets', 'Bullish', 'Bearish']

# Create table
table = ax.table(cellText=table_data, colLabels=columns, 
                cellLoc='center', loc='center',
                colWidths=[0.15, 0.15, 0.12, 0.13, 0.12, 0.12, 0.12])

table.auto_set_font_size(False)
table.set_fontsize(10)
table.scale(1, 2.5)

# Style header
for i in range(len(columns)):
    table[(0, i)].set_facecolor('#34495e')
    table[(0, i)].set_text_props(weight='bold', color='white')

# Color code rows
for i in range(len(table_data)):
    # Color based on signal score
    score = target_data[hashtags_list[i]]['signal_score']
    if score > 0.1:
        color = '#d5f4e6'  # Light green
    elif score < -0.1:
        color = '#fadbd8'  # Light red
    else:
        color = '#f8f9fa'  # Light gray
    
    for j in range(len(columns)):
        table[(i+1, j)].set_facecolor(color)

ax.axis('off')
plt.title('Target Hashtags - Complete Summary', fontsize=16, fontweight='bold', pad=20)
plt.tight_layout()
plt.savefig(output_dir / '5_summary_table.png', dpi=300, bbox_inches='tight')
print(f"   ✓ Saved: {output_dir / '5_summary_table.png'}")
plt.close()

print("\n" + "="*80)
print("✅ VISUALIZATION COMPLETE!")
print("="*80)
print(f"\nGenerated 5 visualizations in: {output_dir}")
print("\nView them:")
print(f"  open {output_dir}")
print(f"\nOr individually:")
print(f"  open {output_dir}/1_signal_scores.png")
print(f"  open {output_dir}/2_sentiment_distribution.png")
print(f"  open {output_dir}/3_volume_confidence.png")
print(f"  open {output_dir}/4_engagement_metrics.png")
print(f"  open {output_dir}/5_summary_table.png")
print()

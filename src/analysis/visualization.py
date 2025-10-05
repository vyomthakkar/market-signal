"""
Memory-Efficient Visualization Module

Creates low-memory plotting solutions for large datasets using:
- Data sampling techniques (stratified, random, systematic)
- Streaming plots (process data in chunks)
- Aggregated visualizations (avoid plotting every point)
- Interactive plots with Plotly (efficient rendering)
"""

import logging
from typing import Dict, List, Optional, Tuple, TYPE_CHECKING
import numpy as np
import pandas as pd
from pathlib import Path

# Lazy imports for visualization libraries
if TYPE_CHECKING:
    from matplotlib.figure import Figure
    import plotly.graph_objects as go

try:
    import matplotlib.pyplot as plt
    import matplotlib.dates as mdates
    from matplotlib.figure import Figure
    import seaborn as sns
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MATPLOTLIB_AVAILABLE = False
    plt = None
    sns = None
    Figure = None  # type: ignore

try:
    import plotly.graph_objects as go
    import plotly.express as px
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False
    go = None
    px = None

logger = logging.getLogger(__name__)


# ==================== Data Sampling Techniques ====================

def sample_data_for_viz(
    df: pd.DataFrame,
    max_points: int = 1000,
    method: str = 'stratified'
) -> pd.DataFrame:
    """
    Sample data for memory-efficient visualization
    
    Args:
        df: Full dataset
        max_points: Maximum points to plot (default: 1000)
        method: Sampling method ('stratified', 'random', 'systematic', 'time_based')
        
    Returns:
        Sampled DataFrame suitable for plotting
    """
    if len(df) <= max_points:
        return df  # No sampling needed
    
    logger.info(f"Sampling {len(df)} points down to {max_points} using {method} method")
    
    if method == 'random':
        # Simple random sampling
        return df.sample(n=max_points, random_state=42)
    
    elif method == 'systematic':
        # Every Nth point
        step = len(df) // max_points
        return df.iloc[::step]
    
    elif method == 'stratified':
        # Stratified by signal_label to ensure all categories represented
        if 'signal_label' in df.columns:
            return df.groupby('signal_label', group_keys=False).apply(
                lambda x: x.sample(min(len(x), max_points // df['signal_label'].nunique()))
            ).sample(n=min(max_points, len(df)), random_state=42)
        else:
            return df.sample(n=max_points, random_state=42)
    
    elif method == 'time_based':
        # Ensure temporal distribution preserved
        if 'timestamp' in df.columns:
            df = df.sort_values('timestamp')
            step = len(df) // max_points
            return df.iloc[::step]
        else:
            return df.sample(n=max_points, random_state=42)
    
    else:
        raise ValueError(f"Unknown sampling method: {method}")


def aggregate_for_timeseries(
    df: pd.DataFrame,
    freq: str = '1H',
    agg_funcs: Optional[Dict] = None
) -> pd.DataFrame:
    """
    Aggregate data for memory-efficient time-series plots
    
    Instead of plotting thousands of points, aggregate by time windows.
    
    Args:
        df: DataFrame with timestamp column
        freq: Aggregation frequency ('1H', '15T', '1D', etc.)
        agg_funcs: Dict of column -> aggregation function
        
    Returns:
        Aggregated DataFrame
    """
    if 'timestamp' not in df.columns:
        raise ValueError("DataFrame must have 'timestamp' column for time-series aggregation")
    
    df = df.copy()
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.set_index('timestamp')
    
    if agg_funcs is None:
        agg_funcs = {
            'signal_score': 'mean',
            'confidence': 'mean',
            'combined_sentiment_score': 'mean',
            'virality_score': 'mean',
            'finance_term_density': 'mean'
        }
    
    # Only aggregate columns that exist
    agg_funcs = {k: v for k, v in agg_funcs.items() if k in df.columns}
    
    aggregated = df.resample(freq).agg(agg_funcs)
    aggregated['tweet_count'] = df.resample(freq).size()
    
    return aggregated.reset_index()


# ==================== Static Plots (Matplotlib) ====================

def plot_signal_distribution(
    df: pd.DataFrame,
    save_path: Optional[str] = None,
    max_points: int = 10000
) -> Optional['Figure']:
    """
    Plot distribution of trading signals with confidence
    
    Memory-efficient: Samples data if > max_points
    
    Args:
        df: DataFrame with signal analysis
        save_path: Path to save plot (optional)
        max_points: Maximum points to plot
        
    Returns:
        matplotlib Figure or None if matplotlib not available
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib not available. Install: pip install matplotlib seaborn")
        return None
    
    # Sample data if needed
    df_plot = sample_data_for_viz(df, max_points=max_points, method='stratified')
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Trading Signal Analysis (n={len(df):,}, plotted={len(df_plot):,})', 
                 fontsize=14, fontweight='bold')
    
    # 1. Signal score distribution
    ax = axes[0, 0]
    ax.hist(df_plot['signal_score'], bins=50, alpha=0.7, edgecolor='black')
    ax.axvline(0, color='red', linestyle='--', linewidth=2, label='Neutral')
    ax.set_xlabel('Signal Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Signal Score Distribution')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Signal label pie chart
    ax = axes[0, 1]
    label_counts = df_plot['signal_label'].value_counts()
    colors = {'STRONG_BUY': '#00AA00', 'BUY': '#88FF88', 'HOLD': '#FFFF88',
              'SELL': '#FF8888', 'STRONG_SELL': '#AA0000', 'IGNORE': '#888888'}
    pie_colors = [colors.get(label, '#CCCCCC') for label in label_counts.index]
    ax.pie(label_counts.values, labels=label_counts.index, autopct='%1.1f%%',
           colors=pie_colors, startangle=90)
    ax.set_title('Signal Label Distribution')
    
    # 3. Confidence distribution
    ax = axes[1, 0]
    ax.hist(df_plot['confidence'], bins=50, alpha=0.7, color='blue', edgecolor='black')
    ax.axvline(df_plot['confidence'].mean(), color='red', linestyle='--', 
               linewidth=2, label=f'Mean: {df_plot["confidence"].mean():.2f}')
    ax.set_xlabel('Confidence Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Confidence Score Distribution')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 4. Signal vs Confidence scatter
    ax = axes[1, 1]
    scatter = ax.scatter(df_plot['signal_score'], df_plot['confidence'], 
                        c=df_plot['finance_term_density'], cmap='viridis',
                        alpha=0.6, s=20)
    ax.set_xlabel('Signal Score')
    ax.set_ylabel('Confidence')
    ax.set_title('Signal vs Confidence (colored by finance density)')
    ax.grid(alpha=0.3)
    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label('Finance Term Density')
    
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved plot to {save_path}")
    
    return fig


def plot_signal_timeline(
    df: pd.DataFrame,
    save_path: Optional[str] = None,
    aggregate_freq: str = '1H'
) -> Optional['Figure']:
    """
    Plot trading signal over time with confidence intervals
    
    Memory-efficient: Aggregates data by time windows
    
    Args:
        df: DataFrame with timestamp and signal columns
        save_path: Path to save plot (optional)
        aggregate_freq: Time aggregation frequency ('1H', '15T', '1D')
        
    Returns:
        matplotlib Figure or None if matplotlib not available
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib not available")
        return None
    
    if 'timestamp' not in df.columns:
        logger.warning("No timestamp column found")
        return None
    
    # Aggregate by time
    df_agg = aggregate_for_timeseries(df, freq=aggregate_freq)
    
    fig, axes = plt.subplots(3, 1, figsize=(14, 10), sharex=True)
    fig.suptitle(f'Trading Signal Timeline (aggregated by {aggregate_freq})', 
                 fontsize=14, fontweight='bold')
    
    # 1. Signal score over time
    ax = axes[0]
    ax.plot(df_agg['timestamp'], df_agg['signal_score'], linewidth=2, color='blue', label='Signal')
    ax.fill_between(df_agg['timestamp'], 0, df_agg['signal_score'], 
                     where=(df_agg['signal_score'] > 0), alpha=0.3, color='green', label='Bullish')
    ax.fill_between(df_agg['timestamp'], 0, df_agg['signal_score'], 
                     where=(df_agg['signal_score'] < 0), alpha=0.3, color='red', label='Bearish')
    ax.axhline(0, color='black', linestyle='--', linewidth=1)
    ax.set_ylabel('Signal Score')
    ax.set_title('Aggregate Signal Over Time')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Confidence over time
    ax = axes[1]
    ax.plot(df_agg['timestamp'], df_agg['confidence'], linewidth=2, color='purple', label='Confidence')
    ax.fill_between(df_agg['timestamp'], 0, df_agg['confidence'], alpha=0.3, color='purple')
    ax.set_ylabel('Confidence')
    ax.set_title('Average Confidence Over Time')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 3. Tweet volume
    ax = axes[2]
    ax.bar(df_agg['timestamp'], df_agg['tweet_count'], width=0.02, color='gray', alpha=0.7)
    ax.set_xlabel('Time')
    ax.set_ylabel('Tweet Count')
    ax.set_title('Tweet Volume Over Time')
    ax.grid(alpha=0.3)
    
    # Format x-axis
    for ax in axes:
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m-%d %H:%M'))
        ax.xaxis.set_major_locator(mdates.AutoDateLocator())
    
    plt.xticks(rotation=45)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved timeline plot to {save_path}")
    
    return fig


def plot_confidence_components(
    df: pd.DataFrame,
    save_path: Optional[str] = None,
    max_points: int = 5000
) -> Optional['Figure']:
    """
    Plot breakdown of confidence components
    
    Args:
        df: DataFrame with confidence_components
        save_path: Path to save plot
        max_points: Maximum points to sample
        
    Returns:
        matplotlib Figure or None
    """
    if not MATPLOTLIB_AVAILABLE:
        logger.warning("Matplotlib not available")
        return None
    
    df_plot = sample_data_for_viz(df, max_points=max_points, method='random')
    
    # Extract confidence components (stored as dict in DataFrame)
    if 'confidence_components' not in df_plot.columns:
        logger.warning("No confidence_components column found")
        return None
    
    # Extract components into separate columns
    df_plot['content_quality'] = df_plot['confidence_components'].apply(lambda x: x.get('content_quality', 0) if isinstance(x, dict) else 0)
    df_plot['sentiment_strength'] = df_plot['confidence_components'].apply(lambda x: x.get('sentiment_strength', 0) if isinstance(x, dict) else 0)
    df_plot['social_proof'] = df_plot['confidence_components'].apply(lambda x: x.get('social_proof', 0) if isinstance(x, dict) else 0)
    
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    fig.suptitle(f'Confidence Components Analysis (n={len(df_plot):,})', 
                 fontsize=14, fontweight='bold')
    
    # 1. Component distributions
    ax = axes[0, 0]
    components = ['content_quality', 'sentiment_strength', 'social_proof']
    for comp in components:
        ax.hist(df_plot[comp], bins=30, alpha=0.5, label=comp.replace('_', ' ').title())
    ax.set_xlabel('Score')
    ax.set_ylabel('Frequency')
    ax.set_title('Component Score Distributions')
    ax.legend()
    ax.grid(alpha=0.3)
    
    # 2. Component contributions (stacked bar)
    ax = axes[0, 1]
    means = [df_plot[comp].mean() for comp in components]
    ax.bar(range(len(components)), means, color=['#FF6B6B', '#4ECDC4', '#45B7D1'])
    ax.set_xticks(range(len(components)))
    ax.set_xticklabels([c.replace('_', '\n').title() for c in components])
    ax.set_ylabel('Average Score')
    ax.set_title('Average Component Scores')
    ax.grid(alpha=0.3, axis='y')
    
    # 3. Content quality vs confidence
    ax = axes[1, 0]
    ax.scatter(df_plot['content_quality'], df_plot['confidence'], alpha=0.5, s=20)
    ax.set_xlabel('Content Quality')
    ax.set_ylabel('Overall Confidence')
    ax.set_title('Content Quality Impact on Confidence')
    ax.grid(alpha=0.3)
    
    # 4. Component correlation heatmap
    ax = axes[1, 1]
    corr_data = df_plot[components + ['confidence']].corr()
    im = ax.imshow(corr_data, cmap='coolwarm', vmin=-1, vmax=1)
    ax.set_xticks(range(len(corr_data)))
    ax.set_yticks(range(len(corr_data)))
    ax.set_xticklabels([c.replace('_', '\n').title() for c in corr_data.columns], rotation=45)
    ax.set_yticklabels([c.replace('_', ' ').title() for c in corr_data.columns])
    ax.set_title('Component Correlations')
    
    # Add correlation values
    for i in range(len(corr_data)):
        for j in range(len(corr_data)):
            text = ax.text(j, i, f'{corr_data.iloc[i, j]:.2f}',
                          ha="center", va="center", color="black", fontsize=10)
    
    plt.colorbar(im, ax=ax)
    plt.tight_layout()
    
    if save_path:
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        logger.info(f"Saved confidence components plot to {save_path}")
    
    return fig


# ==================== Interactive Plots (Plotly) ====================

def create_interactive_signal_dashboard(
    df: pd.DataFrame,
    save_path: Optional[str] = None,
    max_points: int = 5000
) -> Optional['go.Figure']:
    """
    Create interactive dashboard with Plotly
    
    Memory-efficient: Samples data and uses efficient rendering
    
    Args:
        df: DataFrame with signal analysis
        save_path: Path to save HTML (optional)
        max_points: Maximum points for scatter plots
        
    Returns:
        Plotly Figure or None if plotly not available
    """
    if not PLOTLY_AVAILABLE:
        logger.warning("Plotly not available. Install: pip install plotly")
        return None
    
    df_plot = sample_data_for_viz(df, max_points=max_points, method='stratified')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=('Signal Score Distribution', 'Signal vs Confidence',
                       'Confidence Distribution', 'Finance Density vs Signal'),
        specs=[[{'type': 'histogram'}, {'type': 'scatter'}],
               [{'type': 'histogram'}, {'type': 'scatter'}]]
    )
    
    # 1. Signal score histogram
    fig.add_trace(
        go.Histogram(x=df_plot['signal_score'], name='Signal Score', nbinsx=50,
                    marker_color='steelblue'),
        row=1, col=1
    )
    
    # 2. Signal vs Confidence scatter
    fig.add_trace(
        go.Scatter(x=df_plot['signal_score'], y=df_plot['confidence'],
                  mode='markers', name='Tweets',
                  marker=dict(size=6, color=df_plot['finance_term_density'],
                             colorscale='Viridis', showscale=True,
                             colorbar=dict(title="Finance<br>Density", x=1.15)),
                  text=df_plot['signal_label'],
                  hovertemplate='Signal: %{x:.2f}<br>Confidence: %{y:.2f}<br>Label: %{text}'),
        row=1, col=2
    )
    
    # 3. Confidence histogram
    fig.add_trace(
        go.Histogram(x=df_plot['confidence'], name='Confidence', nbinsx=50,
                    marker_color='purple'),
        row=2, col=1
    )
    
    # 4. Finance density vs Signal
    fig.add_trace(
        go.Scatter(x=df_plot['finance_term_density'], y=df_plot['signal_score'],
                  mode='markers', name='Tweets',
                  marker=dict(size=6, color=df_plot['confidence'],
                             colorscale='RdYlGn', showscale=False),
                  text=df_plot['signal_label'],
                  hovertemplate='Finance Density: %{x:.1%}<br>Signal: %{y:.2f}<br>Label: %{text}'),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text=f'Interactive Signal Analysis Dashboard (n={len(df):,}, plotted={len(df_plot):,})',
        showlegend=False,
        height=800,
        hovermode='closest'
    )
    
    fig.update_xaxes(title_text="Signal Score", row=1, col=1)
    fig.update_xaxes(title_text="Signal Score", row=1, col=2)
    fig.update_xaxes(title_text="Confidence", row=2, col=1)
    fig.update_xaxes(title_text="Finance Term Density", row=2, col=2)
    
    fig.update_yaxes(title_text="Frequency", row=1, col=1)
    fig.update_yaxes(title_text="Confidence", row=1, col=2)
    fig.update_yaxes(title_text="Frequency", row=2, col=1)
    fig.update_yaxes(title_text="Signal Score", row=2, col=2)
    
    if save_path:
        fig.write_html(save_path)
        logger.info(f"Saved interactive dashboard to {save_path}")
    
    return fig


# ==================== Convenience Function ====================

def create_all_visualizations(
    df: pd.DataFrame,
    output_dir: str = 'visualizations',
    max_points: int = 5000
) -> Dict[str, Optional['Figure']]:
    """
    Create all visualizations at once
    
    Args:
        df: DataFrame with complete signal analysis
        output_dir: Directory to save plots
        max_points: Maximum points for sampling
        
    Returns:
        Dict of figure_name -> Figure object
    """
    output_path = Path(output_dir)
    output_path.mkdir(exist_ok=True)
    
    logger.info(f"Creating visualizations for {len(df)} tweets")
    logger.info(f"Output directory: {output_path}")
    
    results = {}
    
    # Static plots
    logger.info("Creating signal distribution plot...")
    results['signal_distribution'] = plot_signal_distribution(
        df, save_path=str(output_path / 'signal_distribution.png'), max_points=max_points
    )
    
    logger.info("Creating signal timeline...")
    results['signal_timeline'] = plot_signal_timeline(
        df, save_path=str(output_path / 'signal_timeline.png')
    )
    
    logger.info("Creating confidence components plot...")
    results['confidence_components'] = plot_confidence_components(
        df, save_path=str(output_path / 'confidence_components.png'), max_points=max_points
    )
    
    # Interactive dashboard
    logger.info("Creating interactive dashboard...")
    results['interactive_dashboard'] = create_interactive_signal_dashboard(
        df, save_path=str(output_path / 'interactive_dashboard.html'), max_points=max_points
    )
    
    logger.info(f"✓ All visualizations saved to {output_path}")
    
    return results

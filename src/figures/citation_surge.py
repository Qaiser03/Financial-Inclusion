"""Citation surge figure (fig14)"""

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_citation_surge(
    surge_df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (12, 6),
    dpi: int = 300,
    highlight_color: str = 'red',
    normal_color: str = 'steelblue'
) -> None:
    """
    Plot citation trends with surge years highlighted.
    
    Args:
        surge_df: DataFrame from detect_citation_surges with columns:
                  year, citations, z_score, is_surge
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
        highlight_color: Color for surge years
        normal_color: Color for normal years
    """
    logger.info("Generating citation surge figure")
    
    if len(surge_df) == 0:
        logger.warning("No citation data available")
        return
    
    df = surge_df.sort_values('year')
    
    # Create figure with two y-axes
    fig, ax1 = plt.subplots(figsize=figsize)
    ax2 = ax1.twinx()
    
    # Determine colors based on surge status
    colors = [highlight_color if surge else normal_color for surge in df['is_surge']]
    
    # Bar chart for citations
    bars = ax1.bar(df['year'], df['citations'], color=colors, alpha=0.7, label='Citations')
    
    # Line for z-scores
    ax2.plot(df['year'], df['z_score'], color='darkgreen', linewidth=2, 
             marker='s', markersize=5, label='Z-score')
    
    # Add horizontal line at threshold
    threshold = df[df['is_surge']]['z_score'].min() if df['is_surge'].any() else 1.5
    ax2.axhline(y=threshold, color='red', linestyle='--', linewidth=1.5, 
                alpha=0.7, label=f'Surge Threshold (z={threshold:.1f})')
    
    # Labels
    ax1.set_xlabel('Year', fontsize=12)
    ax1.set_ylabel('Total Citations', fontsize=12, color=normal_color)
    ax2.set_ylabel('Z-Score', fontsize=12, color='darkgreen')
    
    ax1.tick_params(axis='y', labelcolor=normal_color)
    ax2.tick_params(axis='y', labelcolor='darkgreen')
    
    # Title
    surge_years = df[df['is_surge']]['year'].tolist()
    surge_str = ', '.join(map(str, surge_years[:5])) if surge_years else 'None detected'
    ax1.set_title(f'Citation Surge Detection\nSurge Years: {surge_str}', 
                  fontsize=14, fontweight='bold')
    
    # Legend
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    
    # Add custom legend entries
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor=normal_color, alpha=0.7, label='Normal Year'),
        Patch(facecolor=highlight_color, alpha=0.7, label='Surge Year'),
        plt.Line2D([0], [0], color='darkgreen', marker='s', label='Z-score'),
        plt.Line2D([0], [0], color='red', linestyle='--', label=f'Threshold (z≥{threshold:.1f})')
    ]
    ax1.legend(handles=legend_elements, loc='upper left', fontsize=9)
    
    ax1.grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved citation surge figure: {output_path}")


def plot_citation_growth(
    yearly_df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (12, 5),
    dpi: int = 300
) -> None:
    """
    Plot citation growth rate over time.
    
    Args:
        yearly_df: DataFrame with year, citations, growth_rate columns
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating citation growth figure")
    
    if len(yearly_df) == 0:
        logger.warning("No citation data available")
        return
    
    df = yearly_df.sort_values('year')
    
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color bars by positive/negative growth
    colors = ['green' if g >= 0 else 'red' for g in df['growth_rate']]
    
    ax.bar(df['year'], df['growth_rate'], color=colors, alpha=0.7)
    
    ax.axhline(y=0, color='black', linewidth=0.5)
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Citation Growth (Year-over-Year)', fontsize=12)
    ax.set_title('Annual Citation Growth Rate', fontsize=14, fontweight='bold')
    ax.grid(alpha=0.3, axis='y')
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved citation growth figure: {output_path}")

"""Topic evolution figure (fig13)"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def plot_topic_evolution(
    evolution_df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (14, 8),
    dpi: int = 300,
    plot_type: str = 'stacked_area'
) -> None:
    """
    Plot topic evolution over time.
    
    Args:
        evolution_df: DataFrame from topic_evolution_by_year with columns:
                      year, topic_id, topic_name, share
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
        plot_type: 'stacked_area', 'line', or 'stream'
    """
    logger.info("Generating topic evolution figure")
    
    if len(evolution_df) == 0:
        logger.warning("No topic evolution data available")
        return
    
    # Aggregate duplicate year/topic combinations (take mean share)
    agg_df = evolution_df.groupby(['year', 'topic_name'], as_index=False).agg({
        'share': 'mean',
        'topic_id': 'first'
    })
    
    # Pivot for plotting
    pivot = agg_df.pivot(
        index='year',
        columns='topic_name',
        values='share'
    ).fillna(0)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Color palette
    colors = plt.cm.Set2(range(len(pivot.columns)))
    
    if plot_type == 'stacked_area':
        ax.stackplot(
            pivot.index,
            [pivot[col] for col in pivot.columns],
            labels=pivot.columns,
            colors=colors,
            alpha=0.8
        )
    elif plot_type == 'line':
        for i, col in enumerate(pivot.columns):
            ax.plot(
                pivot.index,
                pivot[col],
                label=col,
                color=colors[i],
                linewidth=2,
                marker='o',
                markersize=4
            )
    else:  # stream
        ax.stackplot(
            pivot.index,
            [pivot[col] for col in pivot.columns],
            labels=pivot.columns,
            colors=colors,
            alpha=0.8,
            baseline='wiggle'
        )
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Topic Share' if plot_type != 'stream' else 'Topic Distribution', fontsize=12)
    ax.set_title('Thematic Evolution of Financial Inclusion Research', fontsize=14, fontweight='bold')
    
    # Legend outside plot
    ax.legend(
        bbox_to_anchor=(1.02, 1),
        loc='upper left',
        fontsize=9,
        title='Topics'
    )
    
    ax.grid(alpha=0.3, axis='y')
    
    # Set y-axis limits for percentage view
    if plot_type == 'stacked_area':
        ax.set_ylim(0, 1)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, _: f'{y:.0%}'))
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved topic evolution figure: {output_path}")


def plot_topic_heatmap(
    evolution_df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (12, 8),
    dpi: int = 300
) -> None:
    """
    Plot topic evolution as a heatmap.
    
    Args:
        evolution_df: DataFrame from topic_evolution_by_year
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating topic heatmap")
    
    if len(evolution_df) == 0:
        logger.warning("No topic evolution data available")
        return
    
    # Aggregate duplicate year/topic combinations (take mean share)
    agg_df = evolution_df.groupby(['year', 'topic_name'], as_index=False).agg({
        'share': 'mean',
        'topic_id': 'first'
    })
    
    # Pivot for plotting
    pivot = agg_df.pivot(
        index='topic_name',
        columns='year',
        values='share'
    ).fillna(0)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    im = ax.imshow(pivot.values, cmap='YlOrRd', aspect='auto')
    
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
    ax.set_yticklabels(pivot.index)
    
    plt.colorbar(im, ax=ax, label='Topic Share')
    
    ax.set_title('Topic Intensity Over Time', fontsize=14, fontweight='bold')
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Topic', fontsize=12)
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved topic heatmap: {output_path}")

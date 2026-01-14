"""Annual production figure (fig02)"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_annual_production(
    df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (10, 6),
    dpi: int = 300
) -> None:
    """
    Plot annual publication production.
    
    Args:
        df: Canonical DataFrame with year_clean
        output_path: Output file path (PNG or PDF)
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating annual production figure")
    
    # Count publications by year
    year_counts = df['year_clean'].value_counts().sort_index()
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot bar chart
    ax.bar(year_counts.index, year_counts.values, color='steelblue', alpha=0.7)
    
    # Add line for trend
    ax.plot(year_counts.index, year_counts.values, color='red', marker='o', linewidth=2, markersize=4)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Publications', fontsize=12)
    ax.set_title('Annual Production of Financial Inclusion Research', fontsize=14, fontweight='bold')
    ax.grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved annual production figure: {output_path}")

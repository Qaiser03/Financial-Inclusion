"""FIT trends figure (fig08)"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_fit_trends(
    df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (12, 6),
    dpi: int = 300
) -> None:
    """
    Plot trends in FIT categories over time.
    
    Args:
        df: Canonical DataFrame with fit_labels and year_clean
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating FIT trends figure")
    
    # Expand FIT labels to rows
    fit_records = []
    for _, row in df.iterrows():
        year = row.get('year_clean')
        fit_labels = row.get('fit_labels', [])
        
        if pd.isna(year) or not isinstance(fit_labels, list):
            continue
        
        for fit_label in fit_labels:
            fit_records.append({
                'year': year,
                'fit': fit_label,
            })
    
    fit_df = pd.DataFrame(fit_records)
    
    if len(fit_df) == 0:
        logger.warning("No FIT data available")
        return
    
    # Count by year and FIT
    fit_year_counts = fit_df.groupby(['fit', 'year']).size().reset_index(name='count')
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot line for each FIT category
    fit_categories = fit_df['fit'].unique()
    for fit in fit_categories:
        fit_data = fit_year_counts[fit_year_counts['fit'] == fit]
        ax.plot(fit_data['year'], fit_data['count'], marker='o', label=fit, linewidth=2)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Publications', fontsize=12)
    ax.set_title('Financial Inclusion Tools (FIT) Trends Over Time', fontsize=14, fontweight='bold')
    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize=8)
    ax.grid(alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved FIT trends figure: {output_path}")

"""FIT co-occurrence heatmap figure (fig10)"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import numpy as np

logger = logging.getLogger(__name__)


def plot_fit_cooccurrence_heatmap(
    cooccurrence_df: pd.DataFrame,
    output_path: str,
    figsize: tuple = (10, 8),
    dpi: int = 300
) -> None:
    """
    Plot FIT co-occurrence heatmap.
    
    Args:
        cooccurrence_df: DataFrame with FIT co-occurrence matrix (from tables module)
        output_path: Output file path
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating FIT co-occurrence heatmap")
    
    # Create pivot table if needed
    if 'FIT_i' in cooccurrence_df.columns and 'FIT_j' in cooccurrence_df.columns:
        pivot = cooccurrence_df.pivot(index='FIT_i', columns='FIT_j', values='R_ij')
    else:
        # Assume first two columns are indices, third is value
        pivot = cooccurrence_df.set_index(cooccurrence_df.columns[0]).iloc[:, 0]
        pivot = pivot.unstack()
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot heatmap using matplotlib
    im = ax.imshow(pivot.values, cmap='RdYlBu_r', aspect='auto', vmin=-pivot.abs().max().max(), vmax=pivot.abs().max().max())
    ax.set_xticks(range(len(pivot.columns)))
    ax.set_yticks(range(len(pivot.index)))
    ax.set_xticklabels(pivot.columns, rotation=45, ha='right')
    ax.set_yticklabels(pivot.index)
    
    # Add text annotations
    for i in range(len(pivot.index)):
        for j in range(len(pivot.columns)):
            text = ax.text(j, i, f'{pivot.iloc[i, j]:.2f}',
                         ha="center", va="center", color="black", fontsize=8)
    
    # Add colorbar
    cbar = plt.colorbar(im, ax=ax)
    cbar.set_label('Residual (R_ij)', rotation=270, labelpad=20)
    
    ax.set_title('FIT Co-occurrence Heatmap (Residuals)', fontsize=14, fontweight='bold')
    ax.set_xlabel('FIT Category j', fontsize=12)
    ax.set_ylabel('FIT Category i', fontsize=12)
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved FIT co-occurrence heatmap: {output_path}")

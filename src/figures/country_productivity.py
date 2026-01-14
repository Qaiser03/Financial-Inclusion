"""Country productivity figure (fig03)"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging
import re

logger = logging.getLogger(__name__)


def extract_countries(affiliations: str) -> list:
    """
    Extract country names from affiliations string.
    
    Args:
        affiliations: Affiliations string
        
    Returns:
        List of country names
    """
    if pd.isna(affiliations) or not affiliations:
        return []
    
    # Simple extraction: look for common country patterns
    # This is a basic implementation; may need refinement
    countries = []
    affiliation_list = str(affiliations).split(';')
    
    for aff in affiliation_list:
        # Try to extract country (last part often contains country)
        parts = aff.split(',')
        if parts:
            potential_country = parts[-1].strip()
            if len(potential_country) > 2 and len(potential_country) < 50:
                countries.append(potential_country)
    
    return countries


def plot_country_productivity(
    df: pd.DataFrame,
    output_path: str,
    top_n: int = 20,
    figsize: tuple = (10, 8),
    dpi: int = 300
) -> None:
    """
    Plot country productivity (top N countries by publication count).
    
    Args:
        df: Canonical DataFrame with affiliations_raw
        output_path: Output file path
        top_n: Number of top countries to show
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating country productivity figure")
    
    # Extract countries from affiliations
    all_countries = []
    for _, row in df.iterrows():
        countries = extract_countries(row.get('affiliations_raw', ''))
        all_countries.extend(countries)
    
    # Count by country
    country_counts = pd.Series(all_countries).value_counts()
    
    # Get top N
    top_countries = country_counts.head(top_n)
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Horizontal bar chart
    ax.barh(range(len(top_countries)), top_countries.values, color='steelblue', alpha=0.7)
    ax.set_yticks(range(len(top_countries)))
    ax.set_yticklabels(top_countries.index)
    ax.invert_yaxis()
    
    ax.set_xlabel('Number of Publications', fontsize=12)
    ax.set_ylabel('Country', fontsize=12)
    ax.set_title(f'Top {top_n} Countries by Publication Count', fontsize=14, fontweight='bold')
    ax.grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    
    # Save
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    if output_path.endswith('.png'):
        plt.savefig(output_path, dpi=dpi, bbox_inches='tight')
    else:
        plt.savefig(output_path, bbox_inches='tight')
    
    plt.close()
    
    logger.info(f"Saved country productivity figure: {output_path}")

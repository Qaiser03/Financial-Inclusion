"""Author production over time figure (fig04)"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


def plot_author_production_over_time(
    df: pd.DataFrame,
    output_path: str,
    top_n: int = 10,
    figsize: tuple = (12, 6),
    dpi: int = 300
) -> None:
    """
    Plot top authors' production over time.
    
    Args:
        df: Canonical DataFrame with authors_raw and year_clean
        output_path: Output file path
        top_n: Number of top authors to show
        figsize: Figure size in inches
        dpi: DPI for PNG output
    """
    logger.info("Generating author production over time figure")
    
    # Parse authors (semicolon-separated)
    author_records = []
    for _, row in df.iterrows():
        if pd.isna(row.get('authors_raw')) or not row.get('authors_raw'):
            continue
        
        authors_str = str(row['authors_raw'])
        year = row.get('year_clean')
        
        if pd.isna(year):
            continue
        
        # Split authors
        authors = [a.strip() for a in authors_str.split(';') if a.strip()]
        
        for author in authors:
            # Extract first author name (before comma if present)
            author_name = author.split(',')[0].strip()
            author_records.append({
                'author': author_name,
                'year': year,
            })
    
    author_df = pd.DataFrame(author_records)
    
    if len(author_df) == 0:
        logger.warning("No author data available")
        return
    
    # Count publications per author
    author_counts = author_df['author'].value_counts()
    top_authors = author_counts.head(top_n).index.tolist()
    
    # Filter to top authors
    author_df_top = author_df[author_df['author'].isin(top_authors)]
    
    # Count by author and year
    author_year_counts = author_df_top.groupby(['author', 'year']).size().reset_index(name='count')
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Plot line for each top author
    for author in top_authors:
        author_data = author_year_counts[author_year_counts['author'] == author]
        ax.plot(author_data['year'], author_data['count'], marker='o', label=author, linewidth=2)
    
    ax.set_xlabel('Year', fontsize=12)
    ax.set_ylabel('Number of Publications', fontsize=12)
    ax.set_title(f'Top {top_n} Authors: Production Over Time', fontsize=14, fontweight='bold')
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
    
    logger.info(f"Saved author production figure: {output_path}")

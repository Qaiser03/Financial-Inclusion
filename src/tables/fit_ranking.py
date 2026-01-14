"""FIT ranking table (tab09)"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging
from scipy import stats

logger = logging.getLogger(__name__)


def calculate_fit_ranking(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate FIT ranking metrics.
    
    Metrics per FIT category:
    - docs: Number of documents
    - citations_per_doc: Average citations per document
    - citations_per_doc_per_year: Average citations per document per year
    - growth_slope: Linear regression slope of publications over time
    
    Args:
        df: Canonical DataFrame with fit_labels, year_clean, cited_by_raw
        
    Returns:
        DataFrame with ranking metrics
    """
    logger.info("Calculating FIT ranking metrics")
    
    # Get all FIT categories
    all_fits = set()
    for fit_labels in df['fit_labels']:
        if isinstance(fit_labels, list):
            all_fits.update(fit_labels)
    
    all_fits = sorted(list(all_fits))
    
    ranking_records = []
    
    for fit in all_fits:
        # Filter documents with this FIT
        fit_mask = df['fit_labels'].apply(
            lambda labels: fit in labels if isinstance(labels, list) else False
        )
        fit_df = df[fit_mask].copy()
        
        # Number of documents
        docs = len(fit_df)
        
        # Citations per document
        citations = fit_df['cited_by_raw'].fillna(0)
        citations_per_doc = citations.mean() if docs > 0 else 0
        
        # Citations per document per year
        # Calculate average age of documents
        current_year = pd.Timestamp.now().year
        fit_df['age'] = current_year - fit_df['year_clean']
        fit_df['age'] = fit_df['age'].clip(lower=1)  # Minimum 1 year
        citations_per_doc_per_year = (citations / fit_df['age']).mean() if docs > 0 else 0
        
        # Growth slope (publications over time)
        if docs > 0 and fit_df['year_clean'].notna().sum() > 1:
            years = fit_df['year_clean'].dropna().sort_values()
            year_counts = years.value_counts().sort_index()
            
            if len(year_counts) > 1:
                x = year_counts.index.values
                y = year_counts.values.cumsum()  # Cumulative count
                slope, intercept, r_value, p_value, std_err = stats.linregress(x, y)
                growth_slope = slope
            else:
                growth_slope = 0
        else:
            growth_slope = 0
        
        ranking_records.append({
            'FIT': fit,
            'docs': docs,
            'citations_per_doc': round(citations_per_doc, 2),
            'citations_per_doc_per_year': round(citations_per_doc_per_year, 2),
            'growth_slope': round(growth_slope, 2),
        })
    
    ranking_df = pd.DataFrame(ranking_records)
    
    # Sort by docs (descending)
    ranking_df = ranking_df.sort_values('docs', ascending=False).reset_index(drop=True)
    
    logger.info(f"Calculated ranking for {len(all_fits)} FIT categories")
    
    return ranking_df


def save_fit_ranking_table(
    ranking_df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Save FIT ranking table to CSV.
    
    Args:
        ranking_df: Ranking DataFrame
        output_path: Output file path
    """
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    ranking_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    logger.info(f"Saved FIT ranking table: {output_file}")

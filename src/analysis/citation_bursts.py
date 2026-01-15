"""Citation burst/surge detection using z-score analysis.

Identifies years with unusually high citation activity using
statistical z-score thresholding.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)


def compute_yearly_citations(
    df: pd.DataFrame,
    year_field: str = 'year_clean',
    cite_field: str = 'cited_by_raw'
) -> pd.DataFrame:
    """
    Compute total citations per publication year.
    
    Args:
        df: DataFrame with year and citation data
        year_field: Column name for publication year
        cite_field: Column name for citation count
        
    Returns:
        DataFrame with columns: year, citations, pub_count
    """
    logger.info("Computing yearly citation statistics")
    
    if year_field not in df.columns:
        logger.warning(f"Year field '{year_field}' not found")
        return pd.DataFrame(columns=['year', 'citations', 'pub_count'])
    
    # Extract citation counts
    def safe_int(x):
        if pd.isna(x):
            return 0
        try:
            return int(float(x))
        except (ValueError, TypeError):
            return 0
    
    df_copy = df.copy()
    if cite_field in df_copy.columns:
        df_copy['_cites'] = df_copy[cite_field].apply(safe_int)
    else:
        logger.warning(f"Citation field '{cite_field}' not found, using pub count only")
        df_copy['_cites'] = 1
    
    # Group by year
    yearly = df_copy.groupby(year_field).agg(
        citations=('_cites', 'sum'),
        pub_count=(year_field, 'count')
    ).reset_index()
    
    yearly = yearly.rename(columns={year_field: 'year'})
    yearly = yearly[yearly['year'] > 1900].sort_values('year')
    
    logger.info(f"Computed citations for {len(yearly)} years")
    return yearly


def detect_citation_surges(
    yearly_df: pd.DataFrame,
    method: str = 'full_series',
    z_threshold: float = 1.5,
    rolling_window: int = 5,
    min_year: Optional[int] = None,
    max_year: Optional[int] = None
) -> pd.DataFrame:
    """
    Detect citation surges using z-score analysis.
    
    Two methods available:
    - 'full_series': z-score computed against entire time series mean/std
    - 'rolling': z-score computed against rolling window mean/std
    
    Args:
        yearly_df: DataFrame from compute_yearly_citations
        method: 'full_series' or 'rolling'
        z_threshold: Z-score threshold for surge detection (default 1.5)
        rolling_window: Window size for rolling method
        min_year: Optional minimum year to include
        max_year: Optional maximum year to include
        
    Returns:
        DataFrame with columns: year, citations, z_score, is_surge
    """
    logger.info(f"Detecting citation surges (method={method}, threshold={z_threshold})")
    
    if len(yearly_df) == 0:
        return pd.DataFrame(columns=['year', 'citations', 'z_score', 'is_surge'])
    
    df = yearly_df.copy()
    
    # Filter by year range if specified
    if min_year:
        df = df[df['year'] >= min_year]
    if max_year:
        df = df[df['year'] <= max_year]
    
    df = df.sort_values('year').reset_index(drop=True)
    
    citations = df['citations'].values
    
    if method == 'rolling':
        # Rolling window z-score
        z_scores = []
        for i in range(len(citations)):
            start = max(0, i - rolling_window)
            window = citations[start:i+1]
            if len(window) > 1:
                mean = np.mean(window[:-1]) if len(window) > 1 else 0
                std = np.std(window[:-1]) if len(window) > 1 else 1
                std = std if std > 0 else 1
                z = (citations[i] - mean) / std
            else:
                z = 0
            z_scores.append(z)
    else:
        # Full series z-score
        mean = np.mean(citations)
        std = np.std(citations)
        std = std if std > 0 else 1
        z_scores = [(c - mean) / std for c in citations]
    
    df['z_score'] = z_scores
    df['is_surge'] = df['z_score'] >= z_threshold
    
    surge_count = df['is_surge'].sum()
    logger.info(f"Detected {surge_count} surge years out of {len(df)}")
    
    return df[['year', 'citations', 'pub_count', 'z_score', 'is_surge']]


def get_surge_summary(surge_df: pd.DataFrame) -> pd.DataFrame:
    """
    Get summary of surge years only.
    
    Args:
        surge_df: DataFrame from detect_citation_surges
        
    Returns:
        DataFrame with surge years sorted by z-score
    """
    surges = surge_df[surge_df['is_surge']].copy()
    surges = surges.sort_values('z_score', ascending=False)
    return surges


def compute_citation_growth_rate(yearly_df: pd.DataFrame) -> pd.DataFrame:
    """
    Compute year-over-year citation growth rate.
    
    Args:
        yearly_df: DataFrame with year and citations columns
        
    Returns:
        DataFrame with growth_rate and growth_pct columns added
    """
    df = yearly_df.copy().sort_values('year')
    
    df['prev_citations'] = df['citations'].shift(1)
    df['growth_rate'] = df['citations'] - df['prev_citations']
    df['growth_pct'] = (df['growth_rate'] / df['prev_citations'] * 100).round(2)
    
    # Handle first row and infinite values
    df.loc[df.index[0], 'growth_rate'] = 0
    df.loc[df.index[0], 'growth_pct'] = 0
    df['growth_pct'] = df['growth_pct'].replace([np.inf, -np.inf], np.nan).fillna(0)
    
    return df.drop(columns=['prev_citations'])


def save_surge_table(
    surge_df: pd.DataFrame,
    output_path: str
) -> None:
    """
    Save surge detection results to CSV.
    
    Args:
        surge_df: DataFrame from detect_citation_surges
        output_path: Output file path
    """
    from pathlib import Path
    
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    surge_df.to_csv(output_path, index=False, encoding='utf-8-sig')
    logger.info(f"Saved surge table: {output_path}")

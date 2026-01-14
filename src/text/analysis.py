"""Text analysis modules for keyword extraction and co-occurrence"""

import pandas as pd
from collections import Counter
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


def extract_top_keywords(
    df: pd.DataFrame,
    field: str = 'keywords_raw',
    top_n: int = 50
) -> List[Tuple[str, int]]:
    """
    Extract top keywords by frequency.
    
    Args:
        df: DataFrame with keyword field
        field: Field name containing keywords
        top_n: Number of top keywords to return
        
    Returns:
        List of (keyword, count) tuples
    """
    all_keywords = []
    
    for _, row in df.iterrows():
        if pd.isna(row.get(field)) or not row.get(field):
            continue
        
        keywords_str = str(row[field])
        keywords = [k.strip() for k in keywords_str.split(';') if k.strip()]
        all_keywords.extend(keywords)
    
    # Count frequencies
    keyword_counts = Counter(all_keywords)
    
    # Return top N
    return keyword_counts.most_common(top_n)


def calculate_keyword_cooccurrence(
    df: pd.DataFrame,
    field: str = 'keywords_raw',
    min_cooccurrence: int = 2
) -> pd.DataFrame:
    """
    Calculate keyword co-occurrence matrix.
    
    Args:
        df: DataFrame with keyword field
        field: Field name containing keywords
        min_cooccurrence: Minimum co-occurrence count to include
        
    Returns:
        DataFrame with co-occurrence pairs and counts
    """
    cooccurrence_records = []
    
    for _, row in df.iterrows():
        if pd.isna(row.get(field)) or not row.get(field):
            continue
        
        keywords_str = str(row[field])
        keywords = [k.strip() for k in keywords_str.split(';') if k.strip()]
        
        # All pairs in this document
        for i, kw1 in enumerate(keywords):
            for kw2 in keywords[i+1:]:
                # Sort to ensure consistent ordering
                pair = tuple(sorted([kw1, kw2]))
                cooccurrence_records.append(pair)
    
    # Count co-occurrences
    from collections import Counter
    cooccurrence_counts = Counter(cooccurrence_records)
    
    # Filter by minimum
    filtered = {
        pair: count
        for pair, count in cooccurrence_counts.items()
        if count >= min_cooccurrence
    }
    
    # Convert to DataFrame
    cooccurrence_df = pd.DataFrame([
        {'keyword1': pair[0], 'keyword2': pair[1], 'count': count}
        for pair, count in filtered.items()
    ])
    
    return cooccurrence_df

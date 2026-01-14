"""Data validation and completeness scoring modules"""

import pandas as pd
import logging
from typing import Dict

logger = logging.getLogger(__name__)


def calculate_completeness_score(row: pd.Series) -> int:
    """
    Calculate metadata completeness score for a record.
    
    Canvas specification:
    - Abstract present: +3
    - Keywords present: +2
    - References present: +2
    - Affiliations/countries present: +1
    - Cited by present: +1
    
    Args:
        row: DataFrame row with canonical schema fields
        
    Returns:
        Completeness score (integer, no maximum)
    """
    score = 0
    
    # Abstract present (+3)
    if pd.notna(row.get('abstract_raw')) and str(row.get('abstract_raw', '')).strip():
        score += 3
    
    # Keywords present (+2)
    if pd.notna(row.get('keywords_raw')) and str(row.get('keywords_raw', '')).strip():
        score += 2
    
    # References present (+2)
    if pd.notna(row.get('references_raw')) and str(row.get('references_raw', '')).strip():
        score += 2
    
    # Affiliations/countries present (+1)
    has_affiliations = pd.notna(row.get('affiliations_raw')) and str(row.get('affiliations_raw', '')).strip()
    has_countries = pd.notna(row.get('countries_raw')) and str(row.get('countries_raw', '')).strip()
    if has_affiliations or has_countries:
        score += 1
    
    # Cited by present (+1)
    if pd.notna(row.get('cited_by_raw')) and row.get('cited_by_raw', 0) > 0:
        score += 1
    
    return score


def add_completeness_scores(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add metadata completeness scores to dataframe.
    
    Args:
        df: DataFrame with canonical schema fields
        
    Returns:
        DataFrame with added 'metadata_completeness_score' column
    """
    logger.info("Calculating metadata completeness scores")
    
    df = df.copy()
    df['metadata_completeness_score'] = df.apply(calculate_completeness_score, axis=1)
    
    avg_score = df['metadata_completeness_score'].mean()
    logger.info(f"Average completeness score: {avg_score:.1f}/100")
    
    return df


def validate_schema(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate that dataframe conforms to canonical schema.
    
    Args:
        df: DataFrame to validate
        
    Returns:
        Dictionary with validation results
    """
    required_fields = [
        'source_db',
        'raw_record_id',
        'title_raw',
        'year_raw',
        'doi_raw',
        'authors_raw',
        'affiliations_raw',
        'abstract_raw',
        'keywords_raw',
        'references_raw',
        'cited_by_raw',
    ]
    
    results = {
        'has_all_required_fields': True,
        'missing_fields': [],
        'source_db_valid': True,
        'schema_valid': True,
    }
    
    # Check required fields
    missing = [field for field in required_fields if field not in df.columns]
    if missing:
        results['has_all_required_fields'] = False
        results['missing_fields'] = missing
        results['schema_valid'] = False
    
    # Validate source_db values
    if 'source_db' in df.columns:
        valid_sources = {'scopus', 'wos'}
        invalid_sources = set(df['source_db'].unique()) - valid_sources
        if invalid_sources:
            results['source_db_valid'] = False
            results['schema_valid'] = False
    
    return results


def validate_cleaned_fields(df: pd.DataFrame) -> Dict[str, bool]:
    """
    Validate cleaned fields (doi_clean, title_norm, year_clean).
    
    Args:
        df: DataFrame with cleaned fields
        
    Returns:
        Dictionary with validation results
    """
    results = {
        'doi_clean_valid': True,
        'year_clean_valid': True,
        'all_valid': True,
    }
    
    # Validate doi_clean format
    if 'doi_clean' in df.columns:
        doi_mask = df['doi_clean'].notna()
        if doi_mask.any():
            invalid_dois = df.loc[doi_mask, 'doi_clean'].apply(
                lambda x: not (isinstance(x, str) and x.startswith('10.') and '/' in x)
            )
            if invalid_dois.any():
                results['doi_clean_valid'] = False
                results['all_valid'] = False
    
    # Validate year_clean range
    if 'year_clean' in df.columns:
        year_mask = df['year_clean'].notna()
        if year_mask.any():
            invalid_years = df.loc[year_mask, 'year_clean'].apply(
                lambda x: not (isinstance(x, (int, float)) and 1900 <= x <= 2100)
            )
            if invalid_years.any():
                results['year_clean_valid'] = False
                results['all_valid'] = False
    
    return results

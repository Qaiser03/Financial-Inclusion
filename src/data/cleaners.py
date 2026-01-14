"""Data cleaning modules for deterministic field normalization"""

import re
import unicodedata
from typing import Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)


def clean_doi(doi_raw: str) -> Optional[str]:
    """
    Clean DOI string according to deterministic rules.
    
    Steps:
    1. Convert to lowercase
    2. Strip leading/trailing whitespace
    3. Remove prefixes (doi:, https://doi.org/, etc.)
    4. Strip trailing punctuation
    5. Split multi-DOI cells and take first valid
    6. Validate: must start with "10." and contain "/"
    
    Args:
        doi_raw: Raw DOI string (may be None, empty, or contain multiple DOIs)
        
    Returns:
        Cleaned DOI string or None if invalid
    """
    if pd.isna(doi_raw) or not doi_raw or not isinstance(doi_raw, str):
        return None
    
    # Step 1: Convert to lowercase
    doi = doi_raw.lower()
    
    # Step 2: Strip whitespace
    doi = doi.strip()
    
    if not doi:
        return None
    
    # Step 3: Remove prefixes
    prefixes = [
        'doi:',
        'doi/',
        'https://doi.org/',
        'http://doi.org/',
        'dx.doi.org/',
        'doi.org/',
    ]
    for prefix in prefixes:
        if doi.startswith(prefix):
            doi = doi[len(prefix):].strip()  # Strip after removing prefix
            break
    
    # Step 4: Strip trailing punctuation (but preserve DOI structure)
    # Remove trailing period, comma, semicolon if not part of DOI
    doi = re.sub(r'[.,;]+$', '', doi)
    
    # Step 5: Handle multiple DOIs (split by semicolon, comma, or "and")
    # Take first valid DOI
    separators = [';', ',', ' and ', ' & ']
    for sep in separators:
        if sep in doi:
            doi = doi.split(sep)[0].strip()
            break
    
    # Step 6: Validate
    # Must start with "10." and contain at least one "/"
    if doi.startswith('10.') and '/' in doi:
        return doi
    else:
        return None


def normalize_title(title_raw: str) -> str:
    """
    Normalize title string for secondary-key matching.
    
    Steps:
    1. Unicode normalize to NFKD (decompose diacritics)
    2. Strip diacritics (remove combining marks)
    3. Convert to lowercase
    4. Replace "&" with "and"
    5. Remove all punctuation and symbols (keep alphanumeric and spaces)
    6. Collapse multiple spaces to single space
    7. Strip leading/trailing spaces
    
    Args:
        title_raw: Raw title string
        
    Returns:
        Normalized title string (empty string if input is invalid)
    """
    if pd.isna(title_raw) or not title_raw or not isinstance(title_raw, str):
        return ''
    
    # Step 1: Unicode normalize to NFKD
    title = unicodedata.normalize('NFKD', title_raw)
    
    # Step 2: Strip diacritics (remove combining marks)
    title = ''.join(c for c in title if unicodedata.category(c) != 'Mn')
    
    # Step 3: Convert to lowercase
    title = title.lower()
    
    # Step 4: Replace "&" with "and"
    title = title.replace('&', 'and')
    
    # Step 5: Remove all punctuation and symbols (keep alphanumeric and spaces)
    title = re.sub(r'[^\w\s]', '', title)
    
    # Step 6: Collapse multiple spaces to single space
    title = re.sub(r'\s+', ' ', title)
    
    # Step 7: Strip leading/trailing spaces
    title = title.strip()
    
    return title


def clean_year(year_raw: str) -> Optional[int]:
    """
    Extract valid 4-digit publication year.
    
    Steps:
    1. Extract first 4-digit sequence in range 1900-2100
    2. If no valid year found, return None
    3. Handle ranges (e.g., "2023-2024" → 2023)
    
    Args:
        year_raw: Raw year string (may contain ranges, text, etc.)
        
    Returns:
        Integer year (1900-2100) or None if invalid
    """
    if pd.isna(year_raw) or not year_raw:
        return None
    
    # Convert to string if not already
    year_str = str(year_raw).strip()
    
    if not year_str:
        return None
    
    # Extract first 4-digit sequence in valid range
    year_match = re.search(r'\b(19\d{2}|20[0-9]\d|2100)\b', year_str)
    
    if year_match:
        year = int(year_match.group(1))
        if 1900 <= year <= 2100:
            return year
    
    return None


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply all cleaning rules to a dataframe with canonical schema.
    
    Adds cleaned fields: doi_clean, title_norm, year_clean
    
    Args:
        df: DataFrame with raw fields (title_raw, year_raw, doi_raw)
        
    Returns:
        DataFrame with added cleaned fields
    """
    logger.info("Applying cleaning rules to dataframe")
    
    df = df.copy()
    
    # Clean DOI
    df['doi_clean'] = df['doi_raw'].apply(clean_doi)
    
    # Normalize title
    df['title_norm'] = df['title_raw'].apply(normalize_title)
    
    # Clean year
    df['year_clean'] = df['year_raw'].apply(clean_year)
    
    logger.info(f"Cleaning complete. DOI coverage: {df['doi_clean'].notna().sum() / len(df) * 100:.1f}%")
    
    return df

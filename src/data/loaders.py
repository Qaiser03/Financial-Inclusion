"""Data loading modules for Scopus and Web of Science exports"""

import pandas as pd
from pathlib import Path
from typing import Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


def find_scopus_file() -> Optional[Path]:
    """
    Find available Scopus export file (CSV or XLSX).
    Checks in order: data/raw/scopus_fi.csv, data/raw/scopus.xlsx, scopus.xlsx (root)
    
    Returns:
        Path to file or None if not found
    """
    candidates = [
        Path('data/raw/scopus_fi.csv'),
        Path('data/raw/scopus.xlsx'),
        Path('scopus.xlsx'),
        Path('data/raw/scopus.csv'),
    ]
    
    for candidate in candidates:
        if candidate.exists():
            logger.info(f"Found Scopus file: {candidate}")
            return candidate
    
    return None


def find_wos_file() -> Optional[Path]:
    """
    Find available Web of Science export file (TXT, CSV, or XLSX).
    Checks in order: data/raw/wos_fi.txt, data/raw/WoS.xlsx, WoS.xlsx (root), data/raw/wos_fi.csv
    
    Returns:
        Path to file or None if not found
    """
    candidates = [
        Path('data/raw/wos_fi.txt'),
        Path('data/raw/WoS.xlsx'),
        Path('WoS.xlsx'),
        Path('data/raw/wos_fi.csv'),
        Path('data/raw/wos.xlsx'),
    ]
    
    for candidate in candidates:
        if candidate.exists():
            logger.info(f"Found WoS file: {candidate}")
            return candidate
    
    return None


def load_scopus_file(file_path: Path) -> pd.DataFrame:
    """
    Load Scopus export CSV and map to canonical schema.
    
    Args:
        file_path: Path to Scopus CSV export
        
    Returns:
        DataFrame with canonical schema fields
    """
    logger.info(f"Loading Scopus data from {file_path}")
    
    # Handle both CSV and Excel
    if file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Map Scopus fields to canonical schema
    canonical_df = pd.DataFrame()
    
    # Source database identifier
    canonical_df['source_db'] = 'scopus'
    
    # Record ID
    canonical_df['raw_record_id'] = df.get('EID', df.index.astype(str))
    
    # Title
    canonical_df['title_raw'] = df.get('Title', '')
    
    # Year
    canonical_df['year_raw'] = df.get('Year', '').astype(str)
    
    # DOI
    canonical_df['doi_raw'] = df.get('DOI', '').astype(str)
    
    # Authors
    canonical_df['authors_raw'] = df.get('Authors', '')
    
    # Affiliations
    canonical_df['affiliations_raw'] = df.get('Affiliations', '')
    
    # Countries (extract from affiliations if available, else empty)
    canonical_df['countries_raw'] = ''  # Can be enhanced with country extraction
    
    # Abstract
    canonical_df['abstract_raw'] = df.get('Abstract', '')
    
    # Keywords: combine Author Keywords and Index Keywords
    author_keywords = df.get('Author Keywords', '').fillna('')
    index_keywords = df.get('Index Keywords', '').fillna('')
    canonical_df['keywords_raw'] = (
        author_keywords.astype(str) + '; ' + index_keywords.astype(str)
    ).str.strip('; ').replace('; ;', '')
    
    # References
    canonical_df['references_raw'] = df.get('References', '')
    
    # Cited by
    canonical_df['cited_by_raw'] = pd.to_numeric(df.get('Cited by', 0), errors='coerce').fillna(0).astype(int)
    
    # Replace empty strings with None for consistency
    canonical_df = canonical_df.replace('', None)
    canonical_df = canonical_df.replace('nan', None)
    
    logger.info(f"Loaded {len(canonical_df)} records from Scopus")
    
    return canonical_df


def load_wos_file(file_path: Path) -> pd.DataFrame:
    """
    Load Web of Science export (TXT, CSV, or XLSX) and map to canonical schema.
    
    Args:
        file_path: Path to WoS export file
        
    Returns:
        DataFrame with canonical schema fields
    """
    logger.info(f"Loading Web of Science data from {file_path}")
    
    # Handle different formats
    if file_path.suffix.lower() == '.txt':
        # WoS exports are tab-delimited
        df = pd.read_csv(file_path, sep='\t', encoding='utf-8', low_memory=False)
    elif file_path.suffix.lower() == '.csv':
        df = pd.read_csv(file_path, encoding='utf-8', low_memory=False)
    elif file_path.suffix.lower() in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path, engine='openpyxl')
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")
    
    # Map WoS fields to canonical schema
    canonical_df = pd.DataFrame()
    
    # Source database identifier
    canonical_df['source_db'] = 'wos'
    
    # Record ID (UT - Unique WOS ID)
    canonical_df['raw_record_id'] = df.get('UT (Unique WOS ID)', df.index.astype(str))
    
    # Title
    canonical_df['title_raw'] = df.get('Article Title', '')
    
    # Year
    canonical_df['year_raw'] = df.get('Publication Year', '').astype(str)
    
    # DOI
    canonical_df['doi_raw'] = df.get('DOI', '').astype(str)
    
    # Authors
    canonical_df['authors_raw'] = df.get('Authors', '')
    
    # Affiliations
    canonical_df['affiliations_raw'] = df.get('Affiliations', '')
    
    # Countries (extract from affiliations if available, else empty)
    canonical_df['countries_raw'] = ''  # Can be enhanced with country extraction
    
    # Abstract
    canonical_df['abstract_raw'] = df.get('Abstract', '')
    
    # Keywords: combine Author Keywords and Keywords Plus
    author_keywords = df.get('Author Keywords', '').fillna('')
    keywords_plus = df.get('Keywords Plus', '').fillna('')
    canonical_df['keywords_raw'] = (
        author_keywords.astype(str) + '; ' + keywords_plus.astype(str)
    ).str.strip('; ').replace('; ;', '')
    
    # References
    canonical_df['references_raw'] = df.get('Cited References', '')
    
    # Cited by (Times Cited, WoS Core)
    canonical_df['cited_by_raw'] = pd.to_numeric(
        df.get('Times Cited, WoS Core', 0), errors='coerce'
    ).fillna(0).astype(int)
    
    # Replace empty strings with None for consistency
    canonical_df = canonical_df.replace('', None)
    canonical_df = canonical_df.replace('nan', None)
    
    logger.info(f"Loaded {len(canonical_df)} records from Web of Science")
    
    return canonical_df


def load_raw_data(scopus_path: Optional[str] = None, wos_path: Optional[str] = None) -> Tuple[Dict[str, pd.DataFrame], Dict[str, str]]:
    """
    Load both Scopus and Web of Science data, auto-detecting files if paths not provided.
    
    Args:
        scopus_path: Optional path to Scopus export (if None, auto-detect)
        wos_path: Optional path to WoS export (if None, auto-detect)
        
    Returns:
        Tuple of (data dictionary, file_paths dictionary)
    """
    data = {}
    file_paths = {}
    
    # Auto-detect Scopus file if not provided
    if scopus_path is None:
        scopus_file = find_scopus_file()
        if scopus_file:
            scopus_path = str(scopus_file)
            file_paths['scopus'] = str(scopus_file)
        else:
            logger.warning("No Scopus file found (checked data/raw/scopus_fi.csv, data/raw/scopus.xlsx, scopus.xlsx)")
            data['scopus'] = pd.DataFrame()
            file_paths['scopus'] = None
    else:
        scopus_file = Path(scopus_path)
        file_paths['scopus'] = str(scopus_file) if scopus_file.exists() else None
    
    # Load Scopus if found
    if scopus_path and Path(scopus_path).exists():
        data['scopus'] = load_scopus_file(Path(scopus_path))
    elif 'scopus' not in data:
        data['scopus'] = pd.DataFrame()
    
    # Auto-detect WoS file if not provided
    if wos_path is None:
        wos_file = find_wos_file()
        if wos_file:
            wos_path = str(wos_file)
            file_paths['wos'] = str(wos_file)
        else:
            logger.warning("No WoS file found (checked data/raw/wos_fi.txt, data/raw/WoS.xlsx, WoS.xlsx)")
            data['wos'] = pd.DataFrame()
            file_paths['wos'] = None
    else:
        wos_file = Path(wos_path)
        file_paths['wos'] = str(wos_file) if wos_file.exists() else None
    
    # Load WoS if found
    if wos_path and Path(wos_path).exists():
        data['wos'] = load_wos_file(Path(wos_path))
    elif 'wos' not in data:
        data['wos'] = pd.DataFrame()
    
    return data, file_paths

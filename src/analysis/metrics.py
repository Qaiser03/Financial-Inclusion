"""Advanced bibliometric metrics computation.

Provides h-index and comprehensive metrics for authors, countries,
institutions, and sources (journals).
"""

import pandas as pd
import numpy as np
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


def h_index(citations: List[int]) -> int:
    """
    Calculate the h-index from a list of citation counts.
    
    The h-index is defined as the maximum value h such that the author
    has published h papers that have each been cited at least h times.
    
    Args:
        citations: List of citation counts per publication
        
    Returns:
        The h-index value
        
    Examples:
        >>> h_index([10, 8, 5, 4, 3])
        4
        >>> h_index([25, 8, 5, 3, 3])
        3
        >>> h_index([])
        0
        >>> h_index([0, 0, 0])
        0
    """
    if not citations:
        return 0
    
    # Sort citations in descending order
    sorted_citations = sorted(citations, reverse=True)
    
    h = 0
    for i, c in enumerate(sorted_citations, 1):
        if c >= i:
            h = i
        else:
            break
    
    return h


def _parse_entities(
    value: str,
    delimiters: List[str] = [';', ','],
    normalize_case: bool = True
) -> List[str]:
    """
    Parse a delimited string into a list of entities.
    
    Args:
        value: The string to parse
        delimiters: List of delimiter characters to try (in order)
        normalize_case: Whether to normalize to title case
        
    Returns:
        List of parsed, cleaned entity names
    """
    if pd.isna(value) or not str(value).strip():
        return []
    
    text = str(value)
    
    # Try delimiters in order - use first one that produces multiple parts
    entities = [text]
    for delim in delimiters:
        if delim in text:
            entities = text.split(delim)
            break
    
    # Clean and filter
    result = []
    for entity in entities:
        cleaned = entity.strip()
        if cleaned and len(cleaned) > 1:
            if normalize_case:
                # Title case but preserve acronyms
                if not cleaned.isupper() or len(cleaned) > 5:
                    cleaned = cleaned.title()
            result.append(cleaned)
    
    return result


def _extract_citation_count(row: pd.Series, cite_field: str = 'cited_by_raw') -> int:
    """Extract citation count from a row, handling various formats."""
    if cite_field not in row.index:
        return 0
    
    value = row[cite_field]
    if pd.isna(value):
        return 0
    
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return 0


def compute_author_metrics(
    df: pd.DataFrame,
    author_field: str = 'authors_raw',
    cite_field: str = 'cited_by_raw'
) -> pd.DataFrame:
    """
    Compute bibliometric metrics for each author.
    
    Args:
        df: Canonical DataFrame with author and citation data
        author_field: Column containing author names (delimited)
        cite_field: Column containing citation counts
        
    Returns:
        DataFrame with columns: author, pubs, cites, avg_cites, h_index
    """
    logger.info("Computing author metrics")
    
    if author_field not in df.columns:
        logger.warning(f"Author field '{author_field}' not found in data")
        return pd.DataFrame(columns=['author', 'pubs', 'cites', 'avg_cites', 'h_index'])
    
    # Collect author-publication-citation data
    author_data: Dict[str, List[int]] = {}
    
    for _, row in df.iterrows():
        authors = _parse_entities(row.get(author_field, ''), delimiters=[';', ','])
        citations = _extract_citation_count(row, cite_field)
        
        for author in authors:
            if author not in author_data:
                author_data[author] = []
            author_data[author].append(citations)
    
    # Compute metrics
    records = []
    for author, cite_list in author_data.items():
        pubs = len(cite_list)
        total_cites = sum(cite_list)
        avg_cites = total_cites / pubs if pubs > 0 else 0
        h_idx = h_index(cite_list)
        
        records.append({
            'author': author,
            'pubs': pubs,
            'cites': total_cites,
            'avg_cites': round(avg_cites, 2),
            'h_index': h_idx
        })
    
    result = pd.DataFrame(records)
    if len(result) > 0:
        result = result.sort_values('pubs', ascending=False).reset_index(drop=True)
    
    logger.info(f"Computed metrics for {len(result)} authors")
    return result


def compute_country_metrics(
    df: pd.DataFrame,
    affiliation_field: str = 'affiliations_raw',
    cite_field: str = 'cited_by_raw'
) -> pd.DataFrame:
    """
    Compute bibliometric metrics for each country.
    
    Extracts countries from affiliation strings (typically the last
    comma-separated element).
    
    Args:
        df: Canonical DataFrame with affiliation and citation data
        affiliation_field: Column containing affiliations
        cite_field: Column containing citation counts
        
    Returns:
        DataFrame with columns: country, pubs, cites, avg_cites, h_index
    """
    logger.info("Computing country metrics")
    
    if affiliation_field not in df.columns:
        logger.warning(f"Affiliation field '{affiliation_field}' not found")
        return pd.DataFrame(columns=['country', 'pubs', 'cites', 'avg_cites', 'h_index'])
    
    country_data: Dict[str, List[int]] = {}
    
    for _, row in df.iterrows():
        affiliations = str(row.get(affiliation_field, ''))
        citations = _extract_citation_count(row, cite_field)
        
        # Parse affiliations (semicolon-separated institutions)
        for aff in affiliations.split(';'):
            if not aff.strip():
                continue
            # Country is typically last comma-separated element
            parts = aff.split(',')
            if parts:
                country = parts[-1].strip()
                # Filter out likely non-countries
                if len(country) > 2 and len(country) < 50:
                    country = country.title()
                    if country not in country_data:
                        country_data[country] = []
                    country_data[country].append(citations)
    
    records = []
    for country, cite_list in country_data.items():
        pubs = len(cite_list)
        total_cites = sum(cite_list)
        avg_cites = total_cites / pubs if pubs > 0 else 0
        h_idx = h_index(cite_list)
        
        records.append({
            'country': country,
            'pubs': pubs,
            'cites': total_cites,
            'avg_cites': round(avg_cites, 2),
            'h_index': h_idx
        })
    
    result = pd.DataFrame(records)
    if len(result) > 0:
        result = result.sort_values('pubs', ascending=False).reset_index(drop=True)
    
    logger.info(f"Computed metrics for {len(result)} countries")
    return result


def compute_institution_metrics(
    df: pd.DataFrame,
    affiliation_field: str = 'affiliations_raw',
    cite_field: str = 'cited_by_raw'
) -> pd.DataFrame:
    """
    Compute bibliometric metrics for each institution.
    
    Extracts institution names from affiliation strings.
    
    Args:
        df: Canonical DataFrame with affiliation and citation data
        affiliation_field: Column containing affiliations
        cite_field: Column containing citation counts
        
    Returns:
        DataFrame with columns: institution, pubs, cites, avg_cites, h_index
    """
    logger.info("Computing institution metrics")
    
    if affiliation_field not in df.columns:
        logger.warning(f"Affiliation field '{affiliation_field}' not found")
        return pd.DataFrame(columns=['institution', 'pubs', 'cites', 'avg_cites', 'h_index'])
    
    institution_data: Dict[str, List[int]] = {}
    
    for _, row in df.iterrows():
        affiliations = str(row.get(affiliation_field, ''))
        citations = _extract_citation_count(row, cite_field)
        
        # Parse affiliations (semicolon-separated)
        for aff in affiliations.split(';'):
            aff = aff.strip()
            if not aff or len(aff) < 5:
                continue
            
            # Use full affiliation as institution (or first part before comma)
            parts = aff.split(',')
            institution = parts[0].strip() if parts else aff
            
            if len(institution) > 3:
                if institution not in institution_data:
                    institution_data[institution] = []
                institution_data[institution].append(citations)
    
    records = []
    for institution, cite_list in institution_data.items():
        pubs = len(cite_list)
        total_cites = sum(cite_list)
        avg_cites = total_cites / pubs if pubs > 0 else 0
        h_idx = h_index(cite_list)
        
        records.append({
            'institution': institution,
            'pubs': pubs,
            'cites': total_cites,
            'avg_cites': round(avg_cites, 2),
            'h_index': h_idx
        })
    
    result = pd.DataFrame(records)
    if len(result) > 0:
        result = result.sort_values('pubs', ascending=False).reset_index(drop=True)
    
    logger.info(f"Computed metrics for {len(result)} institutions")
    return result


def compute_source_metrics(
    df: pd.DataFrame,
    source_field: str = 'source_title',
    cite_field: str = 'cited_by_raw'
) -> pd.DataFrame:
    """
    Compute bibliometric metrics for each source (journal/conference).
    
    Args:
        df: Canonical DataFrame with source and citation data
        source_field: Column containing source/journal names
        cite_field: Column containing citation counts
        
    Returns:
        DataFrame with columns: source, pubs, cites, avg_cites, h_index
    """
    logger.info("Computing source metrics")
    
    # Try multiple possible field names
    possible_fields = [source_field, 'source_raw', 'journal', 'source']
    actual_field = None
    
    for field in possible_fields:
        if field in df.columns:
            actual_field = field
            break
    
    if actual_field is None:
        logger.warning("No source/journal field found in data")
        return pd.DataFrame(columns=['source', 'pubs', 'cites', 'avg_cites', 'h_index'])
    
    source_data: Dict[str, List[int]] = {}
    
    for _, row in df.iterrows():
        source = row.get(actual_field, '')
        if pd.isna(source) or not str(source).strip():
            continue
        
        source = str(source).strip()
        citations = _extract_citation_count(row, cite_field)
        
        if source not in source_data:
            source_data[source] = []
        source_data[source].append(citations)
    
    records = []
    for source, cite_list in source_data.items():
        pubs = len(cite_list)
        total_cites = sum(cite_list)
        avg_cites = total_cites / pubs if pubs > 0 else 0
        h_idx = h_index(cite_list)
        
        records.append({
            'source': source,
            'pubs': pubs,
            'cites': total_cites,
            'avg_cites': round(avg_cites, 2),
            'h_index': h_idx
        })
    
    result = pd.DataFrame(records)
    if len(result) > 0:
        result = result.sort_values('pubs', ascending=False).reset_index(drop=True)
    
    logger.info(f"Computed metrics for {len(result)} sources")
    return result

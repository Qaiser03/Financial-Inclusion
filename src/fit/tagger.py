"""Financial Inclusion Tools (FIT) tagging modules"""

import yaml
import pandas as pd
import re
from pathlib import Path
from typing import Dict, List, Set
import logging

logger = logging.getLogger(__name__)


def load_fit_dictionary(dictionary_path: str) -> Dict:
    """
    Load FIT dictionary from YAML file.
    
    Args:
        dictionary_path: Path to FIT_DICTIONARY.yml
        
    Returns:
        Dictionary with FIT categories and terms
    """
    with open(dictionary_path, 'r', encoding='utf-8') as f:
        dictionary = yaml.safe_load(f)
    
    return dictionary


def match_terms(
    text: str,
    terms: List[str],
    case_sensitive: bool = False,
    whole_words_only: bool = True
) -> Set[str]:
    """
    Match terms in text.
    
    Args:
        text: Text to search in
        terms: List of terms to match
        case_sensitive: Whether matching is case-sensitive
        whole_words_only: Whether to match whole words only
        
    Returns:
        Set of matched terms
    """
    if pd.isna(text) or not text or not isinstance(text, str):
        return set()
    
    matched = set()
    
    for term in terms:
        if case_sensitive:
            search_text = text
            search_term = term
        else:
            search_text = text.lower()
            search_term = term.lower()
        
        if whole_words_only:
            # Match whole words only (word boundaries)
            pattern = r'\b' + re.escape(search_term) + r'\b'
            if re.search(pattern, search_text):
                matched.add(term)
        else:
            # Substring matching
            if search_term in search_text:
                matched.add(term)
    
    return matched


def tag_record(
    record: pd.Series,
    fit_dictionary: Dict,
    search_fields: List[str] = None
) -> Dict:
    """
    Tag a single record with FIT categories.
    
    Args:
        record: DataFrame row with text fields
        fit_dictionary: FIT dictionary loaded from YAML
        search_fields: Fields to search in (default: title_raw, abstract_raw, keywords_raw)
        
    Returns:
        Dictionary with 'fit_labels' (list) and 'matched_terms' (dict)
    """
    if search_fields is None:
        search_fields = ['title_raw', 'abstract_raw', 'keywords_raw']
    
    # Get tagging rules
    tagging_rules = fit_dictionary.get('tagging_rules', {})
    case_sensitive = tagging_rules.get('case_sensitive', False)
    whole_words_only = tagging_rules.get('whole_words_only', True)
    
    # Combine text from search fields
    text_parts = []
    for field in search_fields:
        if field in record and pd.notna(record[field]):
            text_parts.append(str(record[field]))
    
    combined_text = ' '.join(text_parts)
    
    # Match terms for each FIT category
    fit_labels = []
    matched_terms_by_fit = {}
    
    for fit_key, fit_data in fit_dictionary.items():
        if fit_key == 'tagging_rules':
            continue
        
        if not isinstance(fit_data, dict) or 'terms' not in fit_data:
            continue
        
        terms = fit_data['terms']
        matched_terms = match_terms(
            combined_text,
            terms,
            case_sensitive=case_sensitive,
            whole_words_only=whole_words_only
        )
        
        if matched_terms:
            fit_labels.append(fit_key)
            matched_terms_by_fit[fit_key] = list(matched_terms)
    
    return {
        'fit_labels': fit_labels,
        'matched_terms': matched_terms_by_fit,
    }


def tag_dataframe(
    df: pd.DataFrame,
    fit_dictionary_path: str
) -> pd.DataFrame:
    """
    Tag all records in dataframe with FIT categories.
    
    Args:
        df: DataFrame with canonical schema
        fit_dictionary_path: Path to FIT_DICTIONARY.yml
        
    Returns:
        DataFrame with added 'fit_labels' column (list of FIT categories)
    """
    logger.info("Tagging records with FIT categories")
    
    # Load dictionary
    fit_dictionary = load_fit_dictionary(fit_dictionary_path)
    
    # Get search fields from dictionary
    tagging_rules = fit_dictionary.get('tagging_rules', {})
    search_fields = tagging_rules.get('search_fields', ['title_raw', 'abstract_raw', 'keywords_raw'])
    
    # Tag each record
    fit_results = df.apply(
        lambda row: tag_record(row, fit_dictionary, search_fields),
        axis=1
    )
    
    # Extract FIT labels and matched terms
    df = df.copy()
    df['fit_labels'] = fit_results.apply(lambda x: x['fit_labels'])
    df['fit_matched_terms'] = fit_results.apply(lambda x: x['matched_terms'])
    
    # Count FIT labels per record
    df['fit_count'] = df['fit_labels'].apply(len)
    
    # Statistics
    total_tagged = (df['fit_count'] > 0).sum()
    logger.info(f"Tagged {total_tagged}/{len(df)} records ({total_tagged/len(df)*100:.1f}%)")
    
    # Count by FIT category
    fit_counts = {}
    for fit_key in fit_dictionary.keys():
        if fit_key != 'tagging_rules':
            fit_counts[fit_key] = df['fit_labels'].apply(
                lambda labels: fit_key in labels if isinstance(labels, list) else False
            ).sum()
    
    logger.info("FIT category counts:")
    for fit_key, count in sorted(fit_counts.items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {fit_key}: {count}")
    
    return df

"""Text preprocessing modules for wordclouds and MCA"""

import pandas as pd
import re
import unicodedata
from typing import List
import logging

logger = logging.getLogger(__name__)


def normalize_text(text: str) -> str:
    """
    Normalize text for analysis (similar to title normalization but preserves more structure).
    
    Args:
        text: Input text string
        
    Returns:
        Normalized text
    """
    if pd.isna(text) or not text or not isinstance(text, str):
        return ''
    
    # Unicode normalize
    text = unicodedata.normalize('NFKD', text)
    
    # Convert to lowercase
    text = text.lower()
    
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text)
    
    return text.strip()


def extract_keywords(text: str, min_length: int = 3) -> List[str]:
    """
    Extract keywords from text.
    
    Args:
        text: Input text
        min_length: Minimum keyword length
        
    Returns:
        List of keywords
    """
    if not text:
        return []
    
    # Split by common delimiters
    keywords = re.split(r'[;,\n]', text)
    
    # Clean and filter
    keywords = [
        kw.strip().lower()
        for kw in keywords
        if kw.strip() and len(kw.strip()) >= min_length
    ]
    
    return keywords


def preprocess_for_wordcloud(df: pd.DataFrame, field: str) -> str:
    """
    Preprocess text field for wordcloud generation.
    
    Args:
        df: DataFrame
        field: Field name to process
        
    Returns:
        Combined text string
    """
    texts = df[field].dropna().astype(str).tolist()
    combined = ' '.join(texts)
    return normalize_text(combined)

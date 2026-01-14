"""Tests for deduplication modules"""

import pytest
import pandas as pd
from src.data.deduplicators import deduplicate_within_db


def test_deduplicate_within_db():
    """Test within-database deduplication"""
    # Create test data with duplicates
    df = pd.DataFrame({
        'source_db': ['scopus', 'scopus', 'scopus'],
        'raw_record_id': ['1', '2', '3'],
        'doi_clean': ['10.1234/test', '10.1234/test', '10.5678/other'],
        'metadata_completeness_score': [80, 90, 85],
        'references_raw': ['ref1', 'ref2', None],
        'title_raw': ['Title 1', 'Title 2', 'Title 3'],
    })
    
    result = deduplicate_within_db(df, 'scopus')
    
    # Should keep record with highest completeness score for duplicate DOI
    assert len(result) == 2
    assert '10.1234/test' in result['doi_clean'].values
    assert '10.5678/other' in result['doi_clean'].values

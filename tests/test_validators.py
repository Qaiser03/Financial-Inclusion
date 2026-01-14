"""Tests for validation modules"""

import pytest
import pandas as pd
from src.data.validators import calculate_completeness_score, validate_schema


def test_calculate_completeness_score():
    """Test completeness score calculation (DATA_DICTIONARY spec: DOI=20, title=15, abstract=15, authors=15, year=10, keywords=10, references=10, cited_by=5)"""
    # Complete record
    row_complete = pd.Series({
        'doi_clean': '10.1234/test',
        'title_raw': 'Test Title',
        'abstract_raw': 'Test abstract',
        'authors_raw': 'Author, A.',
        'year_clean': 2023,
        'keywords_raw': 'keyword1; keyword2',
        'references_raw': 'Ref1; Ref2',
        'cited_by_raw': 10,
        'affiliations_raw': 'Affiliation 1',
        'countries_raw': '',
    })
    
    score = calculate_completeness_score(row_complete)
    # DATA_DICTIONARY spec: DOI(20) + title(15) + abstract(15) + authors(15) + year(10) + keywords(10) + references(10) + cited_by(5) = 100
    assert score == 100
    
    # Incomplete record (only title)
    row_incomplete = pd.Series({
        'doi_clean': None,
        'title_raw': 'Test Title',
        'abstract_raw': None,
        'authors_raw': None,
        'year_clean': None,
        'keywords_raw': None,
        'references_raw': None,
        'cited_by_raw': 0,
    })
    
    score = calculate_completeness_score(row_incomplete)
    assert score == 15  # DATA_DICTIONARY spec: only title(15)


def test_validate_schema():
    """Test schema validation"""
    df_valid = pd.DataFrame({
        'source_db': ['scopus', 'wos'],
        'raw_record_id': ['1', '2'],
        'title_raw': ['Title 1', 'Title 2'],
    })
    
    result = validate_schema(df_valid)
    # Should have missing fields (not all required fields present)
    assert 'missing_fields' in result

"""Tests for FIT tagging modules"""

import pytest
import pandas as pd
from pathlib import Path
from src.fit.tagger import tag_record, load_fit_dictionary


def test_tag_record():
    """Test FIT tagging on a record"""
    # Create minimal dictionary
    fit_dictionary = {
        'FIT1_Mobile_Money': {
            'terms': ['mobile money', 'mobile payment']
        },
        'tagging_rules': {
            'case_sensitive': False,
            'whole_words_only': True,
        }
    }
    
    record = pd.Series({
        'title_raw': 'Mobile money in financial inclusion',
        'abstract_raw': 'This paper discusses mobile payment systems',
        'keywords_raw': 'mobile money; financial inclusion',
    })
    
    result = tag_record(record, fit_dictionary)
    
    assert 'FIT1_Mobile_Money' in result['fit_labels']
    assert len(result['matched_terms']) > 0

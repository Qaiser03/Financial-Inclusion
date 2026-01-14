"""Tests for data cleaning modules"""

import pytest
import pandas as pd
from src.data.cleaners import clean_doi, normalize_title, clean_year


def test_clean_doi():
    """Test DOI cleaning"""
    assert clean_doi("https://doi.org/10.1234/example") == "10.1234/example"
    assert clean_doi("DOI: 10.5678/test") == "10.5678/test"
    assert clean_doi("10.9999/valid") == "10.9999/valid"
    assert clean_doi("invalid-doi") is None
    assert clean_doi("") is None
    assert clean_doi(None) is None


def test_normalize_title():
    """Test title normalization"""
    assert normalize_title("Financial Inclusion & Digital Payments") == "financial inclusion and digital payments"
    assert normalize_title("AI/ML in Finance") == "aiml in finance"
    assert normalize_title("") == ""
    assert normalize_title(None) == ""


def test_clean_year():
    """Test year cleaning"""
    assert clean_year("2023") == 2023
    assert clean_year("2023-2024") == 2023
    assert clean_year("Published in 2021") == 2021
    assert clean_year("n.d.") is None
    assert clean_year("") is None
    assert clean_year(None) is None

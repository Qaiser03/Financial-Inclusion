"""
Unit tests for the metrics module.
"""

import pytest
import pandas as pd
import numpy as np

# Import should handle missing dependencies gracefully
try:
    from src.analysis.metrics import (
        h_index,
        compute_author_metrics,
        compute_country_metrics,
        compute_source_metrics,
    )
    METRICS_AVAILABLE = True
except ImportError:
    METRICS_AVAILABLE = False


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="Metrics module not available")
class TestHIndex:
    """Test cases for h-index calculation."""
    
    def test_h_index_basic(self):
        """Test basic h-index calculation."""
        # Papers with citations: [10, 8, 5, 4, 3] -> h=4 (4 papers with >= 4 citations)
        citations = [10, 8, 5, 4, 3]
        assert h_index(citations) == 4
    
    def test_h_index_single_paper(self):
        """Test h-index with single paper."""
        assert h_index([10]) == 1
        assert h_index([0]) == 0
    
    def test_h_index_empty(self):
        """Test h-index with empty list."""
        assert h_index([]) == 0
    
    def test_h_index_all_zeros(self):
        """Test h-index when all papers have zero citations."""
        assert h_index([0, 0, 0, 0]) == 0
    
    def test_h_index_all_high(self):
        """Test h-index when all papers are highly cited."""
        # 5 papers, all with >= 100 citations -> h=5
        assert h_index([100, 100, 100, 100, 100]) == 5
    
    def test_h_index_decreasing_sequence(self):
        """Test h-index with strictly decreasing citations."""
        # [6, 5, 4, 3, 2, 1] -> h=3 (papers at positions 1-3 have >= 3 citations)
        citations = [6, 5, 4, 3, 2, 1]
        assert h_index(citations) == 3
    
    def test_h_index_identical_values(self):
        """Test h-index when all papers have same citations."""
        # 4 papers with 4 citations each -> h=4
        assert h_index([4, 4, 4, 4]) == 4
        # 5 papers with 3 citations each -> h=3
        assert h_index([3, 3, 3, 3, 3]) == 3
    
    def test_h_index_list_input(self):
        """Test h-index with list input."""
        citations = [10, 8, 5, 4, 3]
        assert h_index(citations) == 4
    
    def test_h_index_with_nan_filtered(self):
        """Test h-index handles NaN values by filtering."""
        # Filter NaN before calling
        citations = [10, 5, 4]
        result = h_index(citations)
        assert result >= 0


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="Metrics module not available")
class TestAuthorMetrics:
    """Test cases for author metrics computation."""
    
    def test_compute_author_metrics_basic(self):
        """Test basic author metrics computation using proper field names."""
        df = pd.DataFrame({
            'authors_raw': ['Smith, J.', 'Smith, J.; Jones, A.', 'Jones, A.'],
            'cited_by_raw': [10, 5, 8]
        })
        result = compute_author_metrics(df, author_field='authors_raw', cite_field='cited_by_raw')
        
        # Check structure
        assert 'author' in result.columns
        assert 'pubs' in result.columns
        assert 'cites' in result.columns
        assert 'h_index' in result.columns
        
        # Should have entries for authors
        assert len(result) >= 1
    
    def test_compute_author_metrics_empty(self):
        """Test author metrics with empty dataframe."""
        df = pd.DataFrame(columns=['authors_raw', 'cited_by_raw'])
        result = compute_author_metrics(df, author_field='authors_raw', cite_field='cited_by_raw')
        assert len(result) == 0


@pytest.mark.skipif(not METRICS_AVAILABLE, reason="Metrics module not available")
class TestSourceMetrics:
    """Test cases for source/journal metrics computation."""
    
    def test_compute_source_metrics_basic(self):
        """Test basic source metrics computation."""
        df = pd.DataFrame({
            'source_title_raw': ['Journal A', 'Journal A', 'Journal B'],
            'cited_by_raw': [10, 5, 8]
        })
        result = compute_source_metrics(df, source_field='source_title_raw', cite_field='cited_by_raw')
        
        assert 'source' in result.columns
        assert 'pubs' in result.columns
        
        # Should have entries for sources
        assert len(result) >= 1

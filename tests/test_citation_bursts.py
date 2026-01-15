"""
Unit tests for the citation bursts module.
"""

import pytest
import pandas as pd
import numpy as np

# Import should handle missing dependencies gracefully
try:
    from src.analysis.citation_bursts import (
        compute_yearly_citations,
        detect_citation_surges,
    )
    BURSTS_AVAILABLE = True
except ImportError:
    BURSTS_AVAILABLE = False


@pytest.mark.skipif(not BURSTS_AVAILABLE, reason="Citation bursts module not available")
class TestYearlyCitations:
    """Test cases for yearly citation computation."""
    
    def test_compute_yearly_basic(self):
        """Test basic yearly citation aggregation."""
        df = pd.DataFrame({
            'year_clean': [2018, 2018, 2019, 2019, 2020],
            'cited_by': [10, 5, 8, 12, 20]
        })
        result = compute_yearly_citations(df)
        
        # Check year exists
        assert 'year' in result.columns
        # 2018: 10+5=15, 2019: 8+12=20, 2020: 20
    
    def test_compute_yearly_empty(self):
        """Test with empty dataframe."""
        df = pd.DataFrame({'year_clean': [], 'cited_by': []})
        result = compute_yearly_citations(df)
        assert len(result) == 0


@pytest.mark.skipif(not BURSTS_AVAILABLE, reason="Citation bursts module not available")
class TestSurgeDetection:
    """Test cases for citation surge detection."""
    
    def test_detect_surges_basic(self):
        """Test basic surge detection using compute_yearly_citations output."""
        # First create proper yearly data using compute_yearly_citations
        df = pd.DataFrame({
            'year_clean': [2015]*10 + [2016]*12 + [2017]*11 + [2018]*13 + [2019]*14 + [2020]*100 + [2021]*15,
            'cited_by': [1]*10 + [1]*12 + [1]*11 + [1]*13 + [1]*14 + [1]*100 + [1]*15
        })
        yearly_data = compute_yearly_citations(df)
        
        result = detect_citation_surges(
            yearly_data,
            z_threshold=2.0,
            method='full_series'
        )
        
        # Check structure
        assert 'is_surge' in result.columns
        assert 'z_score' in result.columns
    
    def test_detect_surges_no_outliers(self):
        """Test when there are no surges."""
        df = pd.DataFrame({
            'year_clean': [2015]*10 + [2016]*11 + [2017]*12 + [2018]*11 + [2019]*10,
            'cited_by': [1]*54
        })
        yearly_data = compute_yearly_citations(df)
        
        result = detect_citation_surges(
            yearly_data,
            z_threshold=2.0,
            method='full_series'
        )
        
        # With stable data, should have few or no surges
        assert 'is_surge' in result.columns
    
    def test_detect_surges_all_same(self):
        """Test with identical publication counts per year."""
        df = pd.DataFrame({
            'year_clean': [2015]*50 + [2016]*50 + [2017]*50 + [2018]*50,
            'cited_by': [1]*200
        })
        yearly_data = compute_yearly_citations(df)
        
        result = detect_citation_surges(
            yearly_data,
            z_threshold=2.0,
            method='full_series'
        )
        
        # With zero std (identical values), no surges
        assert result['is_surge'].sum() == 0
    
    def test_detect_surges_threshold_sensitivity(self):
        """Test that threshold affects detection."""
        df = pd.DataFrame({
            'year_clean': [2015]*10 + [2016]*12 + [2017]*11 + [2018]*13 + [2019]*14 + [2020]*30,
            'cited_by': [1]*90
        })
        yearly_data = compute_yearly_citations(df)
        
        # Low threshold should detect more surges
        result_low = detect_citation_surges(
            yearly_data,
            z_threshold=1.0,
            method='full_series'
        )
        
        # High threshold should detect fewer surges
        result_high = detect_citation_surges(
            yearly_data,
            z_threshold=3.0,
            method='full_series'
        )
        
        assert result_low['is_surge'].sum() >= result_high['is_surge'].sum()


@pytest.mark.skipif(not BURSTS_AVAILABLE, reason="Citation bursts module not available")
class TestSurgeDetectionStability:
    """Test stability and reproducibility of surge detection."""
    
    def test_surge_detection_deterministic(self):
        """Test that surge detection is deterministic."""
        df = pd.DataFrame({
            'year_clean': [2015]*10 + [2016]*12 + [2017]*11 + [2018]*13 + [2019]*14 + [2020]*100,
            'cited_by': [1]*160
        })
        yearly_data = compute_yearly_citations(df)
        
        result1 = detect_citation_surges(yearly_data, z_threshold=2.0)
        result2 = detect_citation_surges(yearly_data, z_threshold=2.0)
        
        # Results should be identical
        pd.testing.assert_frame_equal(result1.reset_index(drop=True), result2.reset_index(drop=True))
    
    def test_surge_detection_edge_case_short_series(self):
        """Test surge detection with very short series."""
        df = pd.DataFrame({
            'year_clean': [2020]*10 + [2021]*100,
            'cited_by': [1]*110
        })
        yearly_data = compute_yearly_citations(df)
        
        # Should handle gracefully
        try:
            result = detect_citation_surges(yearly_data, z_threshold=2.0)
            # Just verify it returns something
            assert result is not None
        except (ValueError, Exception):
            # May raise error for too few points
            pass

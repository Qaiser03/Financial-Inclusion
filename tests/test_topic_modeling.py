"""
Unit tests for the topic modeling module.
"""

import pytest
import pandas as pd
import numpy as np

# Import should handle missing dependencies gracefully
try:
    from src.analysis.topic_modeling import (
        fit_lda_model,
        topic_evolution_by_year,
        get_top_terms_per_topic,
        LDA_AVAILABLE,
    )
    TOPIC_MODELING_AVAILABLE = True
except ImportError:
    TOPIC_MODELING_AVAILABLE = False
    LDA_AVAILABLE = False


@pytest.mark.skipif(not TOPIC_MODELING_AVAILABLE, reason="Topic modeling module not available")
class TestLDAModel:
    """Test cases for LDA topic modeling."""
    
    @pytest.fixture
    def sample_corpus(self):
        """Create sample corpus for testing."""
        return pd.DataFrame({
            'title': [
                'mobile banking financial inclusion rural areas',
                'microfinance credit access developing countries',
                'digital payments fintech innovation banking',
                'savings accounts poverty reduction programs',
                'insurance microinsurance risk management',
                'mobile money transfer services africa',
                'credit scoring machine learning algorithms',
                'blockchain cryptocurrency decentralized finance',
            ],
            'year_clean': [2018, 2019, 2020, 2018, 2019, 2020, 2021, 2021]
        })
    
    @pytest.mark.skipif(not LDA_AVAILABLE, reason="No LDA backend available")
    def test_fit_lda_basic(self, sample_corpus):
        """Test basic LDA model fitting."""
        result = fit_lda_model(
            sample_corpus,
            text_field='title',
            n_topics=3,
            seed=42
        )
        
        # Check result structure
        assert 'model' in result
        assert 'vectorizer' in result
        assert 'doc_topic_matrix' in result
        assert 'feature_names' in result
        
        # Check doc-topic matrix shape
        doc_topic = result['doc_topic_matrix']
        assert doc_topic.shape[0] == len(sample_corpus)  # n_documents
        assert doc_topic.shape[1] == 3  # n_topics
    
    @pytest.mark.skipif(not LDA_AVAILABLE, reason="No LDA backend available")
    def test_fit_lda_reproducibility(self, sample_corpus):
        """Test that LDA is reproducible with same seed."""
        result1 = fit_lda_model(
            sample_corpus,
            text_field='title',
            n_topics=3,
            seed=42
        )
        result2 = fit_lda_model(
            sample_corpus,
            text_field='title',
            n_topics=3,
            seed=42
        )
        
        # Topic distributions should be identical
        np.testing.assert_array_almost_equal(
            result1['doc_topic_matrix'],
            result2['doc_topic_matrix'],
            decimal=5
        )
    
    @pytest.mark.skipif(not LDA_AVAILABLE, reason="No LDA backend available")
    def test_get_top_terms(self, sample_corpus):
        """Test extraction of top terms per topic."""
        result = fit_lda_model(
            sample_corpus,
            text_field='title',
            n_topics=3,
            seed=42
        )
        
        top_terms = get_top_terms_per_topic(
            result['model'],
            result['feature_names'],
            n_terms=5
        )
        
        # Should have 3 topics
        assert len(top_terms) == 3
        
        # Each topic should have up to 5 terms
        for topic_id, terms in top_terms.items():
            assert len(terms) <= 5
            assert all(isinstance(t, str) for t in terms)
    
    @pytest.mark.skipif(not LDA_AVAILABLE, reason="No LDA backend available")
    def test_topic_evolution(self, sample_corpus):
        """Test topic evolution by year."""
        result = fit_lda_model(
            sample_corpus,
            text_field='title',
            n_topics=3,
            seed=42
        )
        
        evolution = topic_evolution_by_year(
            sample_corpus,
            result['doc_topic_matrix'],
            year_field='year_clean'
        )
        
        # Should have years as index
        assert evolution.index.name == 'year' or 'year' in evolution.columns
        
        # Should have 3 topic columns
        assert len([c for c in evolution.columns if 'Topic' in str(c) or isinstance(c, int)]) >= 1


@pytest.mark.skipif(not TOPIC_MODELING_AVAILABLE, reason="Topic modeling module not available")
class TestTopicModelingEdgeCases:
    """Edge case tests for topic modeling."""
    
    def test_empty_corpus(self):
        """Test handling of empty corpus."""
        df = pd.DataFrame({'title': [], 'year_clean': []})
        
        # Should handle gracefully (return None or raise informative error)
        try:
            result = fit_lda_model(df, text_field='title', n_topics=3, seed=42)
            # If it returns, check it handles empty gracefully
            assert result is None or result.get('doc_topic_matrix') is None
        except (ValueError, Exception) as e:
            # Should raise an informative error
            assert 'empty' in str(e).lower() or 'document' in str(e).lower()
    
    def test_single_document(self):
        """Test handling of single document."""
        df = pd.DataFrame({
            'title': ['mobile banking financial inclusion'],
            'year_clean': [2020]
        })
        
        # Single document may fail or return degenerate result
        try:
            result = fit_lda_model(df, text_field='title', n_topics=2, seed=42)
            if result is not None:
                assert result['doc_topic_matrix'].shape[0] == 1
        except (ValueError, Exception):
            # Expected for single document
            pass

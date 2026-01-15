"""
Unit tests for the networks module.
"""

import pytest
import pandas as pd
import numpy as np

# Import should handle missing dependencies gracefully
try:
    from src.analysis.networks import (
        build_coauthorship_graph,
        build_keyword_cooccurrence_graph,
        compute_centrality_metrics,
        NETWORKX_AVAILABLE,
    )
    NETWORKS_AVAILABLE = True
except ImportError:
    NETWORKS_AVAILABLE = False
    NETWORKX_AVAILABLE = False


@pytest.mark.skipif(not NETWORKS_AVAILABLE, reason="Networks module not available")
class TestCoauthorshipNetwork:
    """Test cases for co-authorship network building."""
    
    @pytest.fixture
    def sample_papers(self):
        """Create sample papers for testing."""
        return pd.DataFrame({
            'authors_raw': [
                'Smith, J.; Jones, A.',
                'Smith, J.; Brown, B.',
                'Jones, A.; Brown, B.; Davis, C.',
                'Davis, C.',  # Single author
                '',  # Empty
            ]
        })
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_build_coauthorship_basic(self, sample_papers):
        """Test basic co-authorship graph construction."""
        G = build_coauthorship_graph(sample_papers, author_field='authors_raw')
        
        # Check nodes exist
        assert len(G.nodes()) > 0
        
        # Should have edges from collaborations
        assert len(G.edges()) > 0
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_build_coauthorship_edge_weights(self, sample_papers):
        """Test that edge weights count collaborations."""
        G = build_coauthorship_graph(sample_papers, author_field='authors_raw')
        
        # Check that edges have weight attribute
        assert len(G.edges()) > 0
        for u, v, data in G.edges(data=True):
            assert 'weight' in data
            assert data['weight'] >= 1
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_build_coauthorship_single_author_papers(self):
        """Test papers with only single authors - no collaborations."""
        # Single names without commas (to avoid splitting)
        df = pd.DataFrame({
            'authors_raw': ['Smith', 'Jones', 'Brown']
        })
        G = build_coauthorship_graph(df, author_field='authors_raw')
        
        # Should have nodes but no edges (no collaborations)
        assert len(G.nodes()) == 3
        assert len(G.edges()) == 0
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_build_coauthorship_empty(self):
        """Test with empty dataframe."""
        df = pd.DataFrame({'authors_raw': []})
        G = build_coauthorship_graph(df, author_field='authors_raw')
        
        assert len(G.nodes()) == 0
        assert len(G.edges()) == 0


@pytest.mark.skipif(not NETWORKS_AVAILABLE, reason="Networks module not available")
class TestKeywordNetwork:
    """Test cases for keyword co-occurrence network building."""
    
    @pytest.fixture
    def sample_keywords(self):
        """Create sample keyword data for testing."""
        return pd.DataFrame({
            'keywords_raw': [
                'financial inclusion; mobile banking; rural',
                'mobile banking; fintech; digital',
                'financial inclusion; microfinance',
                'fintech; blockchain',
                '',  # Empty
            ]
        })
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_build_keyword_basic(self, sample_keywords):
        """Test basic keyword co-occurrence graph."""
        G = build_keyword_cooccurrence_graph(
            sample_keywords,
            keyword_field='keywords_raw',
            min_cooccurrences=1
        )
        
        assert len(G.nodes()) > 0
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_build_keyword_min_cooccurrences(self, sample_keywords):
        """Test minimum co-occurrence filtering."""
        G = build_keyword_cooccurrence_graph(
            sample_keywords,
            keyword_field='keywords_raw',
            min_cooccurrences=2
        )
        
        # Only edges with weight >= 2 should remain
        for u, v, data in G.edges(data=True):
            assert data.get('weight', 1) >= 2


@pytest.mark.skipif(not NETWORKS_AVAILABLE, reason="Networks module not available")
class TestCentralityMetrics:
    """Test cases for centrality computation."""
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_compute_centrality_basic(self):
        """Test basic centrality computation."""
        import networkx as nx
        
        # Create simple test graph
        G = nx.Graph()
        G.add_edges_from([
            ('A', 'B'),
            ('A', 'C'),
            ('A', 'D'),
            ('B', 'C'),
        ])
        
        metrics = compute_centrality_metrics(G)
        
        # Should have centrality columns
        assert 'degree' in metrics.columns or 'degree_centrality' in metrics.columns
        assert len(metrics) > 0
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_compute_centrality_empty_graph(self):
        """Test centrality on empty graph."""
        import networkx as nx
        
        G = nx.Graph()
        metrics = compute_centrality_metrics(G)
        
        assert len(metrics) == 0


@pytest.mark.skipif(not NETWORKS_AVAILABLE, reason="Networks module not available")
class TestNetworkStability:
    """Test stability and reproducibility of network building."""
    
    @pytest.mark.skipif(not NETWORKX_AVAILABLE, reason="NetworkX not available")
    def test_network_building_deterministic(self):
        """Test that network building is deterministic."""
        df = pd.DataFrame({
            'authors_raw': [
                'Smith, J.; Jones, A.',
                'Smith, J.; Brown, B.',
            ]
        })
        
        G1 = build_coauthorship_graph(df, author_field='authors_raw')
        G2 = build_coauthorship_graph(df, author_field='authors_raw')
        
        # Same nodes and edges
        assert set(G1.nodes()) == set(G2.nodes())
        assert set(G1.edges()) == set(G2.edges())

"""Advanced bibliometric analysis modules.

This package contains modules for:
- metrics: Author, country, institution, and source metrics (h-index, etc.)
- topic_modeling: LDA topic modeling with thematic evolution
- citation_bursts: Citation surge/burst detection using z-scores
- networks: Co-authorship and keyword co-occurrence network analysis
"""

from .metrics import (
    h_index,
    compute_author_metrics,
    compute_country_metrics,
    compute_institution_metrics,
    compute_source_metrics,
)

__all__ = [
    'h_index',
    'compute_author_metrics',
    'compute_country_metrics',
    'compute_institution_metrics',
    'compute_source_metrics',
]

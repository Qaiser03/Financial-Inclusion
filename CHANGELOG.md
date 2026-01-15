# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-01-15

### Added

#### Advanced Bibliometric Analysis
- **Topic Modeling (LDA)**: Latent Dirichlet Allocation with gensim/sklearn fallback
  - `src/analysis/topic_modeling.py`: Full LDA implementation with thematic evolution
  - `fig13`: Topic evolution over time (stacked area plot)
  - `tab10`: Top terms per topic with descriptive topic names
  - `tab11`: Topic shares by year for longitudinal analysis

- **Citation Surge Detection**: Z-score based burst detection
  - `src/analysis/citation_bursts.py`: Statistical surge detection
  - `fig14`: Citation trends with surge years highlighted
  - `tab12`: Surge years with z-scores and citation counts

- **Network Analysis**: Co-authorship and keyword networks
  - `src/analysis/networks.py`: Graph building with networkx
  - `fig15`: Co-authorship network visualization
  - `fig16`: Keyword co-occurrence network visualization
  - `tab13`: Top author centrality metrics (degree, betweenness)
  - `tab14`: Top keyword centrality metrics
  - Network edge/node exports for reproducibility

- **Extended Bibliometric Metrics**
  - `src/analysis/metrics.py`: H-index and entity-level metrics
  - `compute_author_metrics()`: Publications, citations, h-index per author
  - `compute_country_metrics()`: Country-level bibliometric indicators
  - `compute_institution_metrics()`: Institution-level analysis
  - `compute_source_metrics()`: Journal/source-level metrics

#### Infrastructure & Reproducibility
- **CI/CD**: GitHub Actions workflow (`.github/workflows/ci.yml`)
  - Automated testing on push/PR
  - Python 3.10, 3.11, 3.12 matrix
  - Requirements installation and pytest execution

- **Licensing & Citation**
  - `LICENSE`: MIT License
  - `CITATION.cff`: Machine-readable citation metadata

- **Requirements Management**
  - `requirements-core.txt`: Minimal dependencies for core functionality
  - `requirements.txt`: Full dependencies including optional extras

- **Documentation**
  - Updated `docs/PARAMETERS.yml` with new configuration sections
  - Updated `docs/REPRODUCIBILITY.md` with new analysis documentation
  - Enhanced `README.md` with license and citation information

#### Testing
- `tests/test_metrics.py`: H-index edge cases and metric computation
- `tests/test_topic_modeling.py`: LDA output shape validation
- `tests/test_citation_bursts.py`: Surge detection stability
- `tests/test_networks.py`: Network builder correctness

### Changed
- **Pipeline Registry**: Extended `src/figures/registry.py` with fig13-fig16
- **CLI Arguments**: Added `--make-figures` choices for fig13-16
- **CLI Arguments**: Added `--make-tables` choices for tab10-14
- **Figure Generation**: Refactored to use centralized `generate_figure()` helper

### Fixed
- Duplicate PNG/PDF generation code eliminated via registry pattern
- Improved error handling with graceful degradation for missing dependencies

### Technical Details
- All new analysis functions use deterministic seeds from `docs/PARAMETERS.yml`
- Topic names are inferred from keyword indicators (not generic "Topic 0")
- Networks use spring layout with seeded random state
- All outputs saved to appropriate directories under `outputs/`

---

## [1.0.0] - 2026-01-14

### Added
- Initial release with core bibliometric analysis pipeline
- Scopus and Web of Science data loading and cleaning
- Deterministic deduplication (DOI primary, title+year secondary)
- FIT (Financial Inclusion Tools) categorization with 8 categories
- Figures: fig02-fig10 (annual production, country, author, wordclouds, etc.)
- Tables: tab08-tab09 (FIT co-occurrence, ranking)
- VOSviewer export support
- Comprehensive audit trail for deduplication and FIT tagging
- Virtual environment setup with activation scripts
- Full test suite (7 tests, 100% passing)

### Technical Stack
- Python 3.13.5
- pandas, numpy, matplotlib, scikit-learn
- networkx, wordcloud, gensim (optional)
- pytest for testing

# Financial Inclusion Bibliometric Analysis

[![CI](https://github.com/qa-fi/Financial-Inclusion/actions/workflows/ci.yml/badge.svg)](https://github.com/qa-fi/Financial-Inclusion/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

A comprehensive bibliometric analysis of Financial Inclusion (FI) and Financial Inclusion Tools (FITs) research, using data from Scopus and Web of Science databases.

## Overview

This repository provides a reproducible pipeline for analyzing bibliometric data on Financial Inclusion, including:
- Deterministic data cleaning and deduplication across Scopus and Web of Science
- Multi-label tagging of Financial Inclusion Tools (FITs)
- Network analysis using VOSviewer
- Publication trends, country productivity, and author analysis
- FIT co-occurrence and ranking analysis

### Advanced Features (v2.0.0)

- **Topic Modeling (LDA)**: Latent Dirichlet Allocation with thematic evolution analysis
- **Citation Burst Detection**: Z-score based surge detection for identifying high-impact periods
- **Network Analysis**: Co-authorship and keyword co-occurrence networks with centrality metrics
- **Extended Metrics**: H-index, author/country/institution/source-level bibliometric indicators

## Repository Structure

```
financial_inclusion_bibliometric/
├── data/           # Raw and processed data
├── docs/           # Documentation and configuration
├── outputs/        # Generated figures, tables, and audits
├── src/            # Source code modules
│   ├── analysis/   # Advanced bibliometric analysis (topic modeling, bursts, networks)
│   ├── data/       # Data loading, cleaning, validation
│   ├── figures/    # Figure generation modules
│   ├── fit/        # FIT tagging and auditing
│   ├── tables/     # Table generation modules
│   ├── text/       # Text preprocessing and analysis
│   └── vos/        # VOSviewer integration
├── vosviewer/      # VOSviewer integration files
└── tests/          # Unit tests
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

   For minimal installation (core functionality only):
   ```bash
   pip install -r requirements-core.txt
   ```

2. **Place raw data:**
   - Export Scopus data to `data/raw/scopus_fi.csv`
   - Export Web of Science data to `data/raw/wos_fi.txt`

3. **Run the pipeline:**
   ```bash
   python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures all --make-tables all
   ```

4. **Run tests:**
   ```bash
   python -m pytest tests/ -v
   ```

## Documentation

- [docs/SEARCH_PROTOCOL.md](docs/SEARCH_PROTOCOL.md) - Database search queries and export instructions
- [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) - Data schema and field definitions
- [docs/REPRODUCIBILITY.md](docs/REPRODUCIBILITY.md) - Environment setup and reproducibility guidelines
- [docs/FIT_DICTIONARY.yml](docs/FIT_DICTIONARY.yml) - Financial Inclusion Tools categorization
- [docs/PARAMETERS.yml](docs/PARAMETERS.yml) - Pipeline configuration
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) - Codebase architecture overview
- [CHANGELOG.md](CHANGELOG.md) - Version history and changes

## Key Features

- **Deterministic Deduplication**: Primary key (DOI) and secondary key (normalized title + year) matching
- **Comprehensive Auditing**: Full audit trail for deduplication and FIT tagging
- **Reproducible Visualizations**: Fixed seeds for all random operations
- **Multi-label FIT Tagging**: 8 categories of Financial Inclusion Tools
- **Graceful Degradation**: Optional dependencies handled transparently

## Outputs

All outputs are generated in `outputs/`:

### Figures
| Figure | Description |
|--------|-------------|
| fig02-fig10 | Core bibliometric visualizations (trends, countries, authors, wordclouds) |
| fig13 | Topic evolution over time (LDA) |
| fig14 | Citation surge detection |
| fig15 | Co-authorship network |
| fig16 | Keyword co-occurrence network |

### Tables
| Table | Description |
|-------|-------------|
| tab08-tab09 | FIT co-occurrence and ranking |
| tab10 | Top terms per topic |
| tab11 | Topic shares by year |
| tab12 | Citation surge years |
| tab13 | Author centrality metrics |
| tab14 | Keyword centrality metrics |

### Audits
- Deduplication summaries and logs
- FIT tagging audit trails

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Citation

If you use this repository in your research, please cite it using the information in [CITATION.cff](CITATION.cff):

```bibtex
@software{aziz2026financial,
  author = {Aziz, Qaiser},
  title = {Financial Inclusion Bibliometric Analysis Pipeline},
  version = {2.0.0},
  year = {2026},
  url = {https://github.com/qa-fi/Financial-Inclusion}
}
```

## Contributing

Contributions are welcome! Please read the documentation and ensure all tests pass before submitting a pull request.

## Acknowledgments

- VOSviewer for network visualization capabilities
- The bibliometric research community for methodological guidance

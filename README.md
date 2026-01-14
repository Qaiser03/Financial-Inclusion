# Financial Inclusion Bibliometric Analysis

A comprehensive bibliometric analysis of Financial Inclusion (FI) and Financial Inclusion Tools (FITs) research, using data from Scopus and Web of Science databases.

## Overview

This repository provides a reproducible pipeline for analyzing bibliometric data on Financial Inclusion, including:
- Deterministic data cleaning and deduplication across Scopus and Web of Science
- Multi-label tagging of Financial Inclusion Tools (FITs)
- Network analysis using VOSviewer
- Publication trends, country productivity, and author analysis
- FIT co-occurrence and ranking analysis

## Repository Structure

```
financial_inclusion_bibliometric/
├── data/           # Raw and processed data
├── docs/           # Documentation and configuration
├── outputs/        # Generated figures, tables, and audits
├── src/            # Source code modules
├── vosviewer/      # VOSviewer integration files
└── tests/          # Unit tests
```

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Place raw data:**
   - Export Scopus data to `data/raw/scopus_fi.csv`
   - Export Web of Science data to `data/raw/wos_fi.txt`

3. **Run the pipeline:**
   ```bash
   python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures all --make-tables all
   ```

## Documentation

- `docs/SEARCH_PROTOCOL.md` - Database search queries and export instructions
- `docs/DATA_DICTIONARY.md` - Data schema and field definitions
- `docs/REPRODUCIBILITY.md` - Environment setup and reproducibility guidelines
- `docs/FIT_DICTIONARY.yml` - Financial Inclusion Tools categorization
- `docs/PARAMETERS.yml` - Pipeline configuration

## Key Features

- **Deterministic Deduplication**: Primary key (DOI) and secondary key (normalized title + year) matching
- **Comprehensive Auditing**: Full audit trail for deduplication and FIT tagging
- **Reproducible Visualizations**: Fixed seeds for all random operations
- **Multi-label FIT Tagging**: 8 categories of Financial Inclusion Tools

## Outputs

All outputs are generated in `outputs/`:
- `figures/` - Publication trends, network visualizations, FIT analysis
- `tables/` - FIT rankings and co-occurrence matrices
- `audits/` - Deduplication summaries and FIT tagging logs

## License

[Specify license]

## Citation

[Add citation information]

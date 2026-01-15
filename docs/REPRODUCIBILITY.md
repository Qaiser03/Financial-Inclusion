# Reproducibility Guidelines

This document ensures that all analyses in this repository can be reproduced exactly, including environment setup, version information, and seed values.

## Environment Setup

### Python Version

- **Required**: Python 3.10 or higher
- **Recommended**: Python 3.11 or 3.12

### Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

For minimal installation (core functionality only):

```bash
pip install -r requirements-core.txt
```

### Package Versions

All package versions are specified in `requirements.txt`. Key dependencies:

**Core (Required):**
- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- scikit-learn >= 1.3.0
- pyyaml >= 6.0
- openpyxl >= 3.1.0

**Optional (Graceful Degradation):**
- networkx >= 3.1 (for network analysis: fig15, fig16, tab13, tab14)
- gensim >= 4.3.0 (for topic modeling: fig13, tab10, tab11)
- wordcloud >= 1.9.0 (for wordcloud figures)

## Random Seed Configuration

All random operations use fixed seeds defined in `docs/PARAMETERS.yml`:

| Seed Purpose | Config Path | Default | Used By |
|--------------|-------------|---------|---------|
| Figure generation | `seeds.figure_generation` | 42 | VOSviewer replotting, MCA, layouts |
| Sampling | `seeds.sampling` | 42 | Data sampling operations |
| Clustering | `seeds.clustering` | 42 | Clustering algorithms |
| Network layout | `seeds.network_layout` | 42 | Network visualization layouts |
| Topic modeling | `topic_modeling.seed` | 42 | LDA model training |
| Network viz | `network_analysis.visualization.seed` | 42 | Network graph layouts |

**Default seed**: 42 (configurable in `PARAMETERS.yml`)

## Advanced Bibliometric Analysis (v2.0.0)

### Topic Modeling (LDA)

The pipeline supports Latent Dirichlet Allocation for thematic analysis:

**Configuration** (`docs/PARAMETERS.yml` → `topic_modeling`):
- `n_topics`: Number of topics (default: 8)
- `n_iterations`: Training iterations (default: 500)
- `top_n_terms`: Terms per topic (default: 10)
- `backend`: "gensim" (preferred) or "sklearn" (fallback)
- `seed`: Random seed for reproducibility

**Outputs**:
- `fig13`: Topic evolution over time (stacked area)
- `tab10`: Top terms per topic
- `tab11`: Topic shares by year

**Graceful Degradation**: If gensim is unavailable, falls back to sklearn's LatentDirichletAllocation.

### Citation Burst Detection

Z-score based detection of citation surges:

**Configuration** (`citation_bursts`):
- `z_threshold`: Z-score threshold (default: 2.0)
- `method`: "full_series" or "rolling"
- `rolling_window`: Window size in years (default: 5)

**Outputs**:
- `fig14`: Citation trends with surge years highlighted
- `tab12`: Surge years with z-scores

**Determinism**: Purely statistical; no random components.

### Network Analysis

Co-authorship and keyword co-occurrence networks:

**Configuration** (`network_analysis`):
- `coauthorship.min_edge_weight`: Minimum collaborations (default: 1)
- `coauthorship.top_n_authors`: Authors to include (default: 50)
- `keyword_cooccurrence.min_edge_weight`: Minimum co-occurrences (default: 2)
- `visualization.layout`: "spring", "kamada_kawai", or "circular"
- `visualization.seed`: Layout random seed

**Outputs**:
- `fig15`: Co-authorship network
- `fig16`: Keyword co-occurrence network
- `tab13`: Author centrality metrics
- `tab14`: Keyword centrality metrics

**Graceful Degradation**: Requires networkx. If unavailable, network figures/tables are skipped with a warning.

## VOSviewer Version

- **Version**: Latest stable (document version used in analysis)
- **Download**: https://www.vosviewer.com/
- **Manual steps**: Documented in `vosviewer/README.md`

## Data Export Information

When running the pipeline, document:

- **Export date**: Date when data was exported from databases
- **Scopus export date**: [Date]
- **Web of Science export date**: [Date]
- **Record counts**: 
  - Scopus: [Number]
  - Web of Science: [Number]
- **Search query version**: See `docs/SEARCH_PROTOCOL.md` for exact queries

## Deterministic Operations

All operations are designed to be deterministic:

1. **Data Cleaning**: No random operations; all transformations are rule-based
2. **Deduplication**: Deterministic selection based on completeness score and tie-breaking rules
3. **FIT Tagging**: Dictionary-based matching (no randomness)
4. **Figure Generation**: Fixed seeds for all random operations (network layouts, sampling)
5. **Topic Modeling**: Fixed seed in LDA training
6. **Citation Bursts**: Purely statistical (mean, std, z-score)
7. **Network Construction**: Deterministic graph building; seeded layouts

## Manual Steps

Some steps require manual intervention:

### VOSviewer Network Construction

1. Export co-citation data from canonical dataset (automated)
2. Import into VOSviewer (manual)
3. Configure network parameters (manual)
4. Export network files (manual)
5. Replot in Python with fixed seed (automated)

**Documentation**: See `vosviewer/README.md` for detailed steps.

## Configuration Files

All configuration is centralized in:

- `docs/PARAMETERS.yml`: Pipeline parameters, seeds, paths, preferences
- `docs/FIT_DICTIONARY.yml`: FIT tagging dictionary

## Output Verification

To verify reproducibility:

1. Run pipeline with same configuration
2. Compare hash values of output files (if implemented)
3. Verify audit files match expected structure
4. Check that figure layouts are identical (with same seed)

### Verification Commands

```bash
# Run full pipeline
python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures all --make-tables all

# Run tests
python -m pytest tests/ -v

# Check specific outputs
diff outputs/figures/fig13_topic_evolution.png reference_outputs/fig13_topic_evolution.png
```

## Version Control

- **Git**: Use version control for all code and configuration
- **Data**: Raw data files are NOT committed (see `.gitignore`)
- **Outputs**: Outputs may be committed for reference, but are regenerated from data

## Platform Considerations

- **Operating System**: Tested on Windows, Linux, macOS
- **File Paths**: Use relative paths (not absolute)
- **Encoding**: All text files use UTF-8 encoding

## Troubleshooting

### Common Issues

1. **Different figure layouts**: Ensure same seed value is used
2. **Different deduplication results**: Check that cleaning rules are applied identically
3. **Missing dependencies**: Verify `requirements.txt` is installed correctly
4. **Topic model differences**: Ensure same backend (gensim vs sklearn) is used
5. **Network layout variations**: Verify `network_analysis.visualization.seed` matches

### Reporting Issues

When reporting reproducibility issues, include:
- Python version
- Package versions (`pip freeze`)
- Operating system
- Configuration file contents
- Error messages or unexpected outputs

## Citation

If using this repository, please cite using the provided `CITATION.cff` file or:

```
Aziz, Q. (2026). Financial Inclusion Bibliometric Analysis Pipeline (Version 2.0.0).
https://github.com/qa-fi/Financial-Inclusion
```

See also:
- VOSviewer: van Eck, N.J. & Waltman, L. (2010). Software survey: VOSviewer

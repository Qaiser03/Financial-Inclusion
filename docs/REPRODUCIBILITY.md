# Reproducibility Guidelines

This document ensures that all analyses in this repository can be reproduced exactly, including environment setup, version information, and seed values.

## Environment Setup

### Python Version

- **Required**: Python 3.8 or higher
- **Recommended**: Python 3.10 or 3.11

### Virtual Environment

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Package Versions

All package versions are specified in `requirements.txt`. Key dependencies:

- pandas >= 2.0.0
- numpy >= 1.24.0
- matplotlib >= 3.7.0
- scikit-learn >= 1.3.0
- networkx >= 3.1

## Random Seed Configuration

All random operations use fixed seeds defined in `docs/PARAMETERS.yml`:

- **Figure generation seed**: Used for VOSviewer network replotting, MCA mapping, and other stochastic visualizations
- **Sampling seed**: Used for any data sampling operations
- **Clustering seed**: Used for any clustering algorithms (if applicable)

**Default seed**: 42 (configurable in `PARAMETERS.yml`)

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

### Reporting Issues

When reporting reproducibility issues, include:
- Python version
- Package versions (`pip freeze`)
- Operating system
- Configuration file contents
- Error messages or unexpected outputs

## Citation

If using this repository, please cite:
- The original baseline repository (if applicable)
- This repository
- VOSviewer (if using network visualizations)

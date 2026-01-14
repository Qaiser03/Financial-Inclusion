# Code Structure & Architecture Guide

## Project Overview

This is a bibliometric analysis pipeline for **Financial Inclusion** research. It processes publication data from Scopus and Web of Science, removes duplicates, categorizes by Financial Inclusion Tools (FIT), and generates visualizations.

## Architecture

### Data Flow

```
1. Raw Data
   ├── data/raw/*.xlsx (Scopus & WoS exports)
   
2. Data Processing (src/data/)
   ├── Loaders: Raw export → DataFrame
   ├── Cleaners: Field normalization (DOI, title, year, etc.)
   ├── Validators: Schema check, completeness scoring
   ├── Deduplicators: Within-DB and cross-DB dedup
   
3. Deduplication Auditing (src/audits/)
   ├── Dedup auditor: Summary, mapping, collisions
   ├── FIT auditor: Category tagging audit trail
   
4. FIT Tagging (src/fit/)
   ├── Tagger: Match records to FIT categories
   ├── Auditor: Log matched terms
   
5. Outputs
   ├── data/processed/canonical_fi.csv (7,153 unique records)
   ├── outputs/audits/ (dedup & FIT logs)
   ├── outputs/figures/ (8 visualizations)
   ├── outputs/tables/ (2 summary tables)
```

## Module Organization

### Core Data Processing (`src/data/`)

| Module | Purpose | Key Functions |
|--------|---------|-----------------|
| `loaders.py` | Load exports from Scopus/WoS | `load_raw_data()`, `load_scopus_file()`, `load_wos_file()` |
| `cleaners.py` | Normalize fields | `clean_dataframe()`, `clean_doi()`, `clean_year()` |
| `validators.py` | Data quality checks | `validate_schema()`, `add_completeness_scores()` |
| `deduplicators.py` | Remove duplicates | `deduplicate_within_db()`, `deduplicate_cross_db()` |

**Deduplication Algorithm**:
1. **Within-DB**: Group by DOI (primary), then by (title, year) (secondary)
2. **Cross-DB**: Merge Scopus + WoS, apply same grouping
3. **Collision Handling**: Flag secondary-key matches for review

### Audit & Reporting (`src/audits/`)

| Module | Purpose |
|--------|---------|
| `dedup_auditor.py` | Dedup summary, mapping, collision report |
| `fit_auditor.py` | FIT tagging audit with matched terms |

**Outputs**:
- `dedup_summary.json`: Counts before/after dedup
- `dedup_mapping.csv`: Record-level mapping
- `dedup_collisions.csv`: 56 secondary-key collisions
- `fit_tagging_audit.csv`: 7,153 records with FIT categories

### FIT Tagging (`src/fit/`)

| Module | Purpose |
|--------|---------|
| `tagger.py` | Match 8 FIT categories based on dictionary |
| `auditor.py` | Log FIT category assignments |

**FIT Dictionary** (`docs/FIT_DICTIONARY.yml`):
- 8 categories (Financial Education, Mobile Money, etc.)
- 120+ keywords per category
- Multi-label: records can have multiple FIT tags

### Visualization (`src/figures/`)

**NEW: Registry Pattern** - Eliminates duplication

```python
# Before: Each figure required 2 calls (PNG + PDF)
plot_annual_production(df, "fig.png", ...)  # 9 lines
plot_annual_production(df, "fig.pdf", ...)  # Duplicate

# After: Single call handles both
generate_figure(
    plot_func=plot_annual_production,
    data=df,
    output_dir='outputs/figures',
    figure_name='fig02_annual_production'
)
```

| Figure | Module | Type |
|--------|--------|------|
| fig02 | `annual_production.py` | Time series |
| fig03 | `country_productivity.py` | Geographic |
| fig04 | `author_production.py` | Trends |
| fig05 | `cocitation_network.py` | Network (VOSviewer) |
| fig06 | `wordclouds.py` | Text visualization |
| fig07 | `mca_map.py` | Multivariate analysis |
| fig08 | `fit_trends.py` | Category trends |
| fig10 | `fit_cooccurrence.py` | Category relationships |

**Figure Helper** (`registry.py`):
- `generate_figure()`: Unified PNG/PDF generation
- `FIGURE_REGISTRY`: Metadata for all figures
- `validate_figure_request()`: User input validation

### Tables (`src/tables/`)

| Module | Purpose | Output |
|--------|---------|--------|
| `fit_cooccurrence.py` | Co-occurrence matrix | `tab08_fit_cooccurrence.csv` |
| `fit_ranking.py` | Category popularity | `tab09_fit_ranking.csv` |

### Supporting Modules

| Module | Purpose |
|--------|---------|
| `src/text/` | NLP: preprocessing, analysis |
| `src/vos/` | VOSviewer: exporter, importer, replotter |
| `src/config.py` | Configuration loading & path resolution |

## Refactoring Improvements (Jan 2026)

### ✅ Completed: Figure Code Deduplication

**Problem**: 
- Each figure duplicated PNG/PDF generation code
- ~150 lines of repetitive if/elif blocks
- Maintenance burden: change one figure = update twice

**Solution**:
- Created `src/figures/registry.py` with `generate_figure()` helper
- Extracted figure metadata to `FIGURE_REGISTRY` dict
- Reduced `run_pipeline.py` from 318 → 291 lines

**Impact**:
- 2x faster to add new figures
- Single source of truth for figure config
- Cleaner main() function

### 📋 Pending Improvements

#### Phase 2: Deduplication Logic
- `deduplicators.py` and `dedup_auditor.py` have overlapping logic
- Pass dedup metadata through pipeline to avoid recreation

#### Phase 3: Code Cleanup
- Archive `scripts/convert_excel_to_canonical.py` (unused)
- Document VOSviewer integration (currently manual)

## Configuration

### Main Configuration (`docs/PARAMETERS.yml`)

```yaml
paths:
  raw_data:
    scopus: data/raw/scopus_export.csv
    wos: data/raw/wos_export.csv
  processed_data:
    canonical: data/processed/canonical_fi.csv
  outputs:
    audits: outputs/audits/
    figures: outputs/figures/
    tables: outputs/tables/

deduplication:
  preferred_db: scopus  # Tie-breaker for cross-DB dedup

figures:
  dpi: 300
  sizes:
    standard: [10, 6]
    wide: [16, 6]
    square: [8, 8]
  wordcloud:
    max_words: 100

figure_generation_seed: 42

fit_tagging:
  min_term_length: 3  # Minimum keyword length
  fuzzy_match: true
```

### FIT Dictionary (`docs/FIT_DICTIONARY.yml`)

8 Financial Inclusion Tools with keywords:
- **FIT1**: Mobile Money (e-money, SMS banking)
- **FIT2**: Nonbank Distribution (agents, outlets)
- **FIT3**: Behavioral Credit Risk
- **FIT4**: Workers Remittances
- **FIT5**: Adapted Regulation
- **FIT6**: Financial Education
- **FIT7**: Microfinance Models
- **FIT8**: Blockchain/DLT

### Reproducibility (`docs/REPRODUCIBILITY.md`)

- Python 3.13.5 (from virtual environment)
- Fixed random seeds for all stochastic operations
- All 7 unit tests pass
- Deterministic deduplication via DOI + (title, year) keys

## Running the Pipeline

### Full Pipeline
```bash
python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures all
```

### Selective Generation
```bash
# Specific figures only
python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures fig02 fig03 fig04

# Specific tables only
python -m src.run_pipeline --config docs/PARAMETERS.yml --make-tables tab08 tab09
```

### Testing
```bash
pytest tests/ -v          # Run all tests
pytest tests/test_fit_tagger.py -v  # Specific test
```

## Key Statistics

- **Raw Records**: 9,918 (6,403 Scopus + 3,540 WoS)
- **Duplicates Removed**: 2,765 (27.9%)
- **Unique Records**: 7,153
- **FIT-Tagged**: 5,418 (75.7%)
- **Secondary-Key Collisions**: 56 (needs manual review)

### FIT Category Distribution
- FIT6 Financial Education: 2,122 (39.2%)
- FIT7 Microfinance Models: 1,212 (22.4%)
- FIT1 Mobile Money: 1,089 (20.1%)
- FIT8 Blockchain/DLT: 810 (15.0%)
- Others: 1,185 (21.9%)

## File Size Summary

```
src/                    2,847 lines (core logic)
  ├── data/              540 lines (loading, cleaning, dedup)
  ├── figures/           640 lines (8 visualization modules + registry)
  ├── fit/               180 lines (tagging + auditing)
  ├── audits/            280 lines (dedup + FIT audits)
  ├── tables/            120 lines (summary tables)
  ├── text/              120 lines (NLP utilities)
  ├── vos/               180 lines (VOSviewer integration)
  └── run_pipeline.py    291 lines (main orchestration)

docs/                   Documentation
tests/                  270 lines (7 unit tests, 100% passing)
outputs/                Generated artifacts
```

## Dependencies

**Core**:
- pandas, numpy: Data manipulation
- scikit-learn, statsmodels: Analysis & ML

**Visualization**:
- matplotlib, wordcloud, seaborn: Figure generation
- networkx: Network analysis

**Text**:
- nltk, scikit-learn: NLP preprocessing

**DevOps**:
- pytest, pytest-cov: Testing
- black, flake8: Code quality
- PyYAML: Configuration

See `requirements.txt` for full list with versions.

## Git History

Key commits:
- Initial setup with tests
- Virtual environment with all dependencies
- Figure generation (all 8 working)
- Refactoring: Figure code deduplication (this commit)

---

## Questions?

Refer to:
- **Data issues**: `docs/DATA_DICTIONARY.md`
- **FIT categories**: `docs/FIT_DICTIONARY.yml`
- **Reproducibility**: `docs/REPRODUCIBILITY.md`
- **Search protocol**: `docs/SEARCH_PROTOCOL.md`
- **Refactoring notes**: `REFACTORING_ROADMAP.md`

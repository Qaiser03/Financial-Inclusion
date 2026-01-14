# Sample Data

This directory contains sample data files for testing the pipeline without requiring full database exports.

## Files

- `scopus_sample_10.csv`: 10-row sample from Scopus export format
- `wos_sample_10.txt`: 10-row sample from Web of Science export format

## Usage

To test the pipeline with sample data:

1. Copy sample files to `data/raw/`:
   ```bash
   cp data/sample/scopus_sample_10.csv data/raw/scopus_fi.csv
   cp data/sample/wos_sample_10.txt data/raw/wos_fi.txt
   ```

2. Run pipeline:
   ```bash
   python -m src.run_pipeline --config docs/PARAMETERS.yml --make-figures all --make-tables all
   ```

## Generating Sample Data

Sample data can be generated from full exports by taking the first N rows:

```bash
head -n 11 data/raw/scopus_fi.csv > data/sample/scopus_sample_10.csv
head -n 11 data/raw/wos_fi.txt > data/sample/wos_sample_10.txt
```

Note: Include header row (hence 11 rows for 10 data rows).

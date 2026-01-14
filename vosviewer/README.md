# VOSviewer Integration Guide

This directory contains files and documentation for integrating VOSviewer network analysis into the bibliometric pipeline.

## Overview

VOSviewer is used for constructing bibliometric networks (co-citation, co-occurrence, etc.). The workflow involves:
1. **Automated**: Export data from canonical dataset in VOSviewer-compatible format
2. **Manual**: Import into VOSviewer and construct network
3. **Manual**: Export network files (nodes, edges, map)
4. **Automated**: Replot network in Python with deterministic layout (fixed seed)

## Directory Structure

```
vosviewer/
├── exports/              # VOSviewer export files (.net, .map, .txt)
├── thesaurus_fi.txt      # Keyword normalization mapping
└── README.md            # This file
```

## Manual Steps in VOSviewer

### Step 1: Prepare Input Data

The Python pipeline will automatically generate VOSviewer input files from the canonical dataset. These files will be placed in `vosviewer/exports/` with names like:
- `cocitation_input.txt` - Co-citation data
- `cooccurrence_input.txt` - Keyword co-occurrence data

### Step 2: Import into VOSviewer

1. Open VOSviewer
2. Select **File → Create → Create a map based on bibliographic data**
3. Choose data source:
   - For co-citation: Select "Co-citation" → "Cited references"
   - For keyword co-occurrence: Select "Co-occurrence" → "All keywords"
4. Click **Read data from bibliographic database files**
5. Select the input file (e.g., `cocitation_input.txt`)
6. Configure import settings:
   - **Counting method**: Full counting (or fractional, document your choice)
   - **Minimum number of citations/occurrences**: 1 (or higher threshold)
7. Click **Finish**

### Step 3: Configure Network

1. In the network visualization:
   - Adjust **Normalization method**: Association strength (recommended)
   - Set **Resolution**: 1.0 (or adjust for clarity)
   - Set **Minimum cluster size**: 1
2. Apply **Thesaurus file** (`thesaurus_fi.txt`) if using keyword analysis:
   - **File → Apply thesaurus file**
   - Select `thesaurus_fi.txt`
   - This normalizes keyword variations (e.g., "mobile money" = "mobile payments")

### Step 4: Export Network Files

1. **Export network file**:
   - **File → Save → Network file**
   - Save as: `vosviewer/exports/cocitation_network.net`
2. **Export map file**:
   - **File → Save → Map file**
   - Save as: `vosviewer/exports/cocitation_network.map`

### Step 5: Document Settings

Record the following settings in `docs/REPRODUCIBILITY.md`:
- VOSviewer version used
- Normalization method
- Minimum citation/occurrence threshold
- Resolution parameter
- Counting method (full vs. fractional)

## Thesaurus File

The `thesaurus_fi.txt` file contains keyword normalization mappings. Format:

```
TERM1 = TERM2
TERM3 = TERM4
```

Example:
```
mobile money = mobile payments
e-wallet = digital wallet
```

This ensures that variations of the same concept are treated as one term in the network analysis.

## Python Replotting

After exporting network files, the Python pipeline will:
1. Load nodes and edges from `.net` and `.map` files
2. Reconstruct network using NetworkX
3. Apply deterministic layout algorithm with fixed seed
4. Generate publication-quality figures (PNG and PDF)

See `src/vos/replotter.py` for implementation.

## Troubleshooting

### Network is too dense

- Increase minimum citation/occurrence threshold
- Use fractional counting instead of full counting
- Increase resolution parameter

### Keywords not merging

- Verify thesaurus file format is correct
- Check that terms match exactly (case-sensitive in thesaurus)
- Ensure thesaurus is applied before network construction

### Export files not found

- Verify export paths match configuration in `docs/PARAMETERS.yml`
- Check file permissions
- Ensure VOSviewer export completed successfully

## Notes

- VOSviewer network construction is a **manual step** and cannot be fully automated
- Network parameters should be documented for reproducibility
- The Python replotting uses fixed seeds to ensure deterministic layouts
- Original VOSviewer visualizations can be saved as reference, but final figures use Python replots

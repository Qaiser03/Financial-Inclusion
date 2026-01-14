# Search Protocol for Financial Inclusion Bibliometric Analysis

This document specifies the exact search queries used to retrieve bibliometric data from Scopus and Web of Science databases. Both queries are designed to capture the same topic scope to ensure comparability.

## Database Selection

- **Scopus**: Elsevier's abstract and citation database
- **Web of Science (WoS)**: Clarivate Analytics' Core Collection

## Search Strategy

The search strategy combines two components:
1. **Financial Inclusion Core Terms**: General terms related to financial inclusion, access to finance, and financial exclusion
2. **Financial Inclusion Tools (FITs) and Indicators**: Specific tools, technologies, and indicators used to measure or promote financial inclusion

## Scopus Advanced Search Query

**Query String:**
```
TITLE-ABS-KEY(
  "financial inclusion" OR "digital financial inclusion" OR "inclusive finance" OR
  "financial access" OR "access to finance" OR "financial exclusion" OR
  unbanked OR underbanked OR "bank account*" OR "account ownership" OR
  "financial capability"
)
AND
TITLE-ABS-KEY(
  "financial inclusion index" OR "index of financial inclusion" OR
  "financial inclusion indicator*" OR findex OR "global findex" OR
  "financial access indicator*" OR
  "mobile money" OR "mobile payment*" OR "mobile wallet*" OR "e-wallet*" OR "digital wallet*" OR
  "mobile banking" OR "branchless banking" OR "agent banking" OR "banking agent*" OR
  "correspondent banking" OR nonbank* OR "non-bank*" OR
  "credit scoring" OR "digital credit" OR "alternative data" OR psychometric* OR
  behavio?r* OR "digital footprint*" OR
  remittanc* OR "cross-border payment*" OR "international transfer*" OR
  "proportionate regulation" OR "tiered kyc" OR "simplified kyc" OR ekyc OR "e-kyc" OR
  "digital identit*" OR "regulatory sandbox*" OR "aml/cft" OR "consumer protection" OR
  "financial literacy" OR "financial education" OR
  microfinance OR microcredit OR "group lending" OR
  blockchain OR "distributed ledger" OR dlt OR stablecoin* OR cbdc OR "central bank digital currency"
)
```

## Web of Science Advanced Search Query

**Query String:**
```
TS=(
  "financial inclusion" OR "digital financial inclusion" OR "inclusive finance" OR
  "financial access" OR "access to finance" OR "financial exclusion" OR
  unbanked OR underbanked OR "bank account*" OR "account ownership" OR
  "financial capability"
)
AND
TS=(
  "financial inclusion index" OR "index of financial inclusion" OR
  "financial inclusion indicator*" OR findex OR "global findex" OR
  "financial access indicator*" OR
  "mobile money" OR "mobile payment*" OR "mobile wallet*" OR "e-wallet*" OR "digital wallet*" OR
  "mobile banking" OR "branchless banking" OR "agent banking" OR "banking agent*" OR
  "correspondent banking" OR nonbank* OR "non-bank*" OR
  "credit scoring" OR "digital credit" OR "alternative data" OR psychometric* OR
  behavio?r* OR "digital footprint*" OR
  remittanc* OR "cross-border payment*" OR "international transfer*" OR
  "proportionate regulation" OR "tiered kyc" OR "simplified kyc" OR ekyc OR "e-kyc" OR
  "digital identit*" OR "regulatory sandbox*" OR "aml/cft" OR "consumer protection" OR
  "financial literacy" OR "financial education" OR
  microfinance OR microcredit OR "group lending" OR
  blockchain OR "distributed ledger" OR dlt OR stablecoin* OR cbdc OR "central bank digital currency"
)
```

## Filter Policy

Apply **identical filters** in both database UIs:

- **Document Types**: Include all types (Article, Review, Conference Paper, etc.)
- **Language**: No language restriction (document language distribution in audits)
- **Year Range**: No year restriction (include all available years)
- **Access Type**: Include both open access and subscription-based publications

**Note**: Document any filters applied during export in the export metadata.

## Export Instructions

### Scopus Export

1. After running the search query, click "Export"
2. Select "All results" (or specific range if needed)
3. Choose export format: **CSV**
4. Select fields to export:
   - Authors
   - Author full names
   - Author(s) ID
   - Title
   - Year
   - Source title
   - Volume, Issue, Pages
   - Cited by
   - DOI
   - Affiliations
   - Authors with affiliations
   - Abstract
   - Author Keywords
   - Index Keywords
   - References
   - Correspondence Address
   - Document Type
   - Language of Original Document
   - Open Access
   - EID
5. Save as: `data/raw/scopus_fi.csv`

### Web of Science Export

1. After running the search query, select all records
2. Click "Export" → "Save to Other File Formats"
3. Select record count (all records)
4. Choose format: **Tab-delimited (Win, UTF-8)**
5. Select fields to export:
   - Authors
   - Author Full Names
   - Article Title
   - Source Title
   - Publication Year
   - DOI
   - Abstract
   - Author Keywords
   - Keywords Plus
   - Addresses
   - Affiliations
   - Cited References
   - Times Cited, WoS Core
   - Document Type
   - Language
   - UT (Unique WOS ID)
6. Save as: `data/raw/wos_fi.txt`

## Data Validation

After export, verify:
- File encoding is UTF-8
- All expected fields are present
- Record count matches search results
- No truncation warnings (if export limit reached, export in batches)

## Important Notes

- **Raw exports must NOT be committed** to version control (see `.gitignore`)
- Export date and search parameters should be documented in `docs/REPRODUCIBILITY.md`
- If export limits are encountered, document the date range split and merge strategy

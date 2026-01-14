# Data Dictionary

This document defines the canonical schema for bibliometric data in this repository, including raw fields from database exports and derived cleaned fields.

## Canonical Schema

### Raw Fields (from database exports)

These fields are extracted directly from Scopus and Web of Science exports with minimal transformation.

| Field Name | Type | Description | Source Mapping |
|------------|------|-------------|----------------|
| `source_db` | string | Database source: "scopus" or "wos" | Added during loading |
| `raw_record_id` | string | Original record identifier | Scopus: EID; WoS: UT |
| `title_raw` | string | Original title as exported | Scopus: Title; WoS: Article Title |
| `year_raw` | string | Original year string (may contain ranges) | Scopus: Year; WoS: Publication Year |
| `doi_raw` | string | Original DOI string (may contain prefixes, multiple DOIs) | Scopus: DOI; WoS: DOI |
| `authors_raw` | string | Original authors string (semicolon-separated) | Scopus: Authors; WoS: Authors |
| `affiliations_raw` | string | Original affiliations string | Scopus: Affiliations; WoS: Affiliations |
| `countries_raw` | string | Extracted countries (if available) | Derived from affiliations |
| `abstract_raw` | string | Original abstract text | Scopus: Abstract; WoS: Abstract |
| `keywords_raw` | string | Combined keywords | Scopus: Author Keywords + Index Keywords; WoS: Author Keywords + Keywords Plus |
| `references_raw` | string | Original references string | Scopus: References; WoS: Cited References |
| `cited_by_raw` | string/int | Citation count | Scopus: Cited by; WoS: Times Cited, WoS Core |

### Cleaned Fields (derived)

These fields are generated through deterministic cleaning rules.

| Field Name | Type | Description | Cleaning Rule |
|------------|------|-------------|---------------|
| `doi_clean` | string/null | Cleaned DOI (primary key for deduplication) | See cleaning rules below |
| `title_norm` | string | Normalized title (secondary key component) | See cleaning rules below |
| `year_clean` | int/null | Parsed 4-digit year (secondary key component) | See cleaning rules below |
| `metadata_completeness_score` | int | Completeness score 0-100 | Sum of: DOI=20, title=15, abstract=15, authors=15, year=10, keywords=10, references=10, cited_by=5 |

## Field Mappings

### Scopus Field Mappings

| Canonical Field | Scopus Export Field | Notes |
|----------------|---------------------|-------|
| `raw_record_id` | EID | Scopus Electronic Identifier |
| `title_raw` | Title | |
| `year_raw` | Year | |
| `doi_raw` | DOI | May contain "https://doi.org/" prefix |
| `authors_raw` | Authors | Semicolon-separated |
| `affiliations_raw` | Affiliations | |
| `abstract_raw` | Abstract | |
| `keywords_raw` | Author Keywords + Index Keywords | Combined with semicolon separator |
| `references_raw` | References | |
| `cited_by_raw` | Cited by | Integer |

### Web of Science Field Mappings

| Canonical Field | WoS Export Field | Notes |
|----------------|------------------|-------|
| `raw_record_id` | UT (Unique WOS ID) | Web of Science Unique Identifier |
| `title_raw` | Article Title | |
| `year_raw` | Publication Year | |
| `doi_raw` | DOI | May contain "https://doi.org/" prefix |
| `authors_raw` | Authors | Semicolon-separated |
| `affiliations_raw` | Affiliations | |
| `abstract_raw` | Abstract | |
| `keywords_raw` | Author Keywords + Keywords Plus | Combined with semicolon separator |
| `references_raw` | Cited References | |
| `cited_by_raw` | Times Cited, WoS Core | Integer |

## Cleaning Rules

### DOI Cleaning (`doi_clean`)

**Purpose**: Create a standardized DOI for deduplication matching.

**Steps**:
1. Convert to lowercase
2. Strip leading/trailing whitespace
3. Remove prefixes:
   - "doi:"
   - "doi/"
   - "https://doi.org/"
   - "http://doi.org/"
   - "dx.doi.org/"
4. Strip trailing punctuation (period, comma, semicolon) unless part of DOI structure
5. If cell contains multiple DOIs (separated by semicolon, comma, or "and"), split and take first valid DOI
6. Validate:
   - Must start with "10."
   - Must contain at least one "/"
7. If validation fails, set to `null`

**Examples**:
- `"https://doi.org/10.1234/example"` → `"10.1234/example"`
- `"DOI: 10.5678/test"` → `"10.5678/test"`
- `"10.9999/invalid"` → `"10.9999/invalid"` (valid)
- `"invalid-doi"` → `null`

### Title Normalization (`title_norm`)

**Purpose**: Create a normalized title string for secondary-key matching when DOI is missing.

**Steps**:
1. Unicode normalize to NFKD (decompose diacritics)
2. Strip diacritics (remove combining marks)
3. Convert to lowercase
4. Replace "&" with "and"
5. Remove all punctuation and symbols (keep alphanumeric and spaces)
6. Collapse multiple spaces to single space
7. Strip leading/trailing spaces

**Examples**:
- `"Financial Inclusion & Digital Payments"` → `"financial inclusion and digital payments"`
- `"Étude sur l'inclusion financière"` → `"etude sur linclusion financiere"`
- `"AI/ML in Finance"` → `"aiml in finance"`

### Year Cleaning (`year_clean`)

**Purpose**: Extract a valid 4-digit publication year.

**Steps**:
1. Extract first 4-digit sequence in range 1900-2100
2. If no valid 4-digit year found, set to `null`
3. Handle ranges (e.g., "2023-2024" → 2023)

**Examples**:
- `"2023"` → `2023`
- `"2023-2024"` → `2023`
- `"Published in 2021"` → `2021`
- `"n.d."` → `null`

## Metadata Completeness Scoring

The `metadata_completeness_score` is calculated as the sum of the following components:

| Component | Score | Condition |
|-----------|-------|-----------|
| DOI present | 20 | `doi_clean` is not null |
| Title present | 15 | `title_raw` is not null and not empty |
| Abstract present | 15 | `abstract_raw` is not null and not empty |
| Authors present | 15 | `authors_raw` is not null and not empty |
| Year present | 10 | `year_clean` is not null |
| Keywords present | 10 | `keywords_raw` is not null and not empty |
| References present | 10 | `references_raw` is not null and not empty |
| Cited by present | 5 | `cited_by_raw` is not null and > 0 |

**Maximum score**: 100

## Data Types and Constraints

- All string fields: UTF-8 encoded, may contain null/empty values
- `year_clean`: Integer in range 1900-2100, or null
- `cited_by_raw`: Integer >= 0, or null
- `metadata_completeness_score`: Integer in range 0-100
- `source_db`: Must be exactly "scopus" or "wos"
- `doi_clean`: Must start with "10." and contain "/", or null

## Notes

- Field coalescing: When merging records, fill missing fields only; never concatenate abstracts or other text fields
- All cleaning operations are deterministic (no random operations)
- Null values are preserved as `null` (not converted to empty strings for numeric fields)

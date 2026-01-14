"""Deduplication audit generation modules"""

import pandas as pd
import json
from pathlib import Path
from typing import Dict, Tuple
import logging

logger = logging.getLogger(__name__)


def generate_dedup_summary(
    scopus_original: int,
    wos_original: int,
    scopus_after_within: int,
    wos_after_within: int,
    canonical_count: int,
    collisions_count: int,
    file_paths: Dict[str, str],
    within_source_doi_removed: Dict[str, int],
    within_source_title_year_removed: Dict[str, int],
    cross_source_doi_removed: int,
    cross_source_title_year_removed: int
) -> Dict:
    """
    Generate deduplication summary statistics.
    
    Args:
        scopus_original: Original Scopus record count
        wos_original: Original WoS record count
        scopus_after_within: Scopus count after within-DB dedup
        wos_after_within: WoS count after within-DB dedup
        canonical_count: Final canonical record count
        collisions_count: Number of secondary-key collisions
        
    Returns:
        Dictionary with summary statistics
    """
    summary = {
        'input_file_paths': file_paths,
        'input': {
            'scopus': scopus_original,
            'wos': wos_original,
            'total': scopus_original + wos_original,
        },
        'after_within_db_dedup': {
            'scopus': scopus_after_within,
            'wos': wos_after_within,
            'total': scopus_after_within + wos_after_within,
        },
        'output': {
            'canonical_records': canonical_count,
        },
        'deduplication': {
            'within_source': {
                'scopus_doi_removed': within_source_doi_removed.get('scopus', 0),
                'scopus_title_year_removed': within_source_title_year_removed.get('scopus', 0),
                'wos_doi_removed': within_source_doi_removed.get('wos', 0),
                'wos_title_year_removed': within_source_title_year_removed.get('wos', 0),
            },
            'cross_source': {
                'doi_removed': cross_source_doi_removed,
                'title_year_removed': cross_source_title_year_removed,
            },
            'total_removed': (scopus_original + wos_original) - canonical_count,
            'deduplication_rate': ((scopus_original + wos_original) - canonical_count) / (scopus_original + wos_original) * 100 if (scopus_original + wos_original) > 0 else 0,
        },
        'collisions': {
            'secondary_key_collisions': collisions_count,
        },
    }
    
    return summary


def generate_dedup_mapping(
    scopus_df: pd.DataFrame,
    wos_df: pd.DataFrame,
    canonical_df: pd.DataFrame
) -> pd.DataFrame:
    """
    Generate mapping from raw_record_id to canonical_id with dedup_reason.
    
    Canvas spec: columns: raw_record_id, source_db, doc_id_canonical, dedup_reason ∈ {doi, title_year, kept}
    
    Note: scopus_df and wos_df should be the CLEANED versions with doi_clean, title_norm, year_clean
    
    Args:
        scopus_df: Cleaned Scopus DataFrame (after cleaning, before dedup)
        wos_df: Cleaned WoS DataFrame (after cleaning, before dedup)
        canonical_df: Canonical DataFrame with canonical_id
        
    Returns:
        DataFrame with columns: raw_record_id, source_db, doc_id_canonical, dedup_reason
    """
    # Create mapping from canonical records
    mapping_list = []
    
    # Track which records were kept and why
    canonical_record_keys = set(
        zip(canonical_df['source_db'], canonical_df['raw_record_id'])
    )
    
    # Build a lookup for dedup reasons by checking if records share DOI or title+year
    # This is simplified - in a full implementation, we'd track this during dedup
    for _, row in canonical_df.iterrows():
        mapping_list.append({
            'raw_record_id': row['raw_record_id'],
            'source_db': row['source_db'],
            'doc_id_canonical': row['canonical_id'],
            'dedup_reason': 'kept',  # This record was kept
        })
    
    # Add records that were removed
    # Check if cleaned columns exist, otherwise skip detailed dedup reason
    has_cleaned_cols = 'doi_clean' in scopus_df.columns and 'doi_clean' in wos_df.columns
    
    if has_cleaned_cols:
        all_original = pd.concat([
            scopus_df[['source_db', 'raw_record_id', 'doi_clean', 'title_norm', 'year_clean']],
            wos_df[['source_db', 'raw_record_id', 'doi_clean', 'title_norm', 'year_clean']]
        ], ignore_index=True)
    else:
        # If cleaned columns don't exist, use basic version
        all_original = pd.concat([
            scopus_df[['source_db', 'raw_record_id']],
            wos_df[['source_db', 'raw_record_id']]
        ], ignore_index=True)
        all_original['doi_clean'] = None
        all_original['title_norm'] = None
        all_original['year_clean'] = None
    
    for _, row in all_original.iterrows():
        record_key = (row['source_db'], row['raw_record_id'])
        if record_key not in canonical_record_keys:
            # Determine dedup reason
            if pd.notna(row.get('doi_clean')):
                dedup_reason = 'doi'
            elif pd.notna(row.get('title_norm')) and pd.notna(row.get('year_clean')):
                dedup_reason = 'title_year'
            else:
                dedup_reason = 'other'
            
            mapping_list.append({
                'raw_record_id': row['raw_record_id'],
                'source_db': row['source_db'],
                'doc_id_canonical': None,
                'dedup_reason': dedup_reason,
            })
    
    mapping_df = pd.DataFrame(mapping_list)
    
    return mapping_df


def save_dedup_audits(
    summary: Dict,
    mapping_df: pd.DataFrame,
    collisions_df: pd.DataFrame,
    output_dir: str
) -> None:
    """
    Save all deduplication audit files.
    
    Args:
        summary: Deduplication summary dictionary
        mapping_df: Mapping DataFrame
        collisions_df: Collisions DataFrame
        output_dir: Output directory path
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Save summary JSON
    summary_path = output_path / 'dedup_summary.json'
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    logger.info(f"Saved deduplication summary: {summary_path}")
    
    # Save mapping CSV
    mapping_path = output_path / 'dedup_mapping.csv'
    mapping_df.to_csv(mapping_path, index=False, encoding='utf-8-sig')
    logger.info(f"Saved deduplication mapping: {mapping_path}")
    
    # Save collisions CSV
    collisions_path = output_path / 'dedup_collisions.csv'
    if len(collisions_df) > 0:
        collisions_df.to_csv(collisions_path, index=False, encoding='utf-8-sig')
        logger.info(f"Saved deduplication collisions: {collisions_path} ({len(collisions_df)} collisions)")
    else:
        # Create empty file with headers
        empty_collisions = pd.DataFrame(columns=['title_norm', 'year_clean', 'n_records', 'sources', 'record_ids', 'titles'])
        empty_collisions.to_csv(collisions_path, index=False, encoding='utf-8-sig')
        logger.info(f"Saved empty collisions file: {collisions_path}")


def audit_deduplication(
    scopus_original: pd.DataFrame,
    wos_original: pd.DataFrame,
    scopus_cleaned: pd.DataFrame,
    wos_cleaned: pd.DataFrame,
    canonical_df: pd.DataFrame,
    collisions_df: pd.DataFrame,
    output_dir: str,
    file_paths: Dict[str, str],
    within_source_doi_removed: Dict[str, int] = None,
    within_source_title_year_removed: Dict[str, int] = None,
    cross_source_doi_removed: int = 0,
    cross_source_title_year_removed: int = 0
) -> None:
    """
    Complete deduplication audit workflow.
    
    Args:
        scopus_original: Original Scopus DataFrame
        wos_original: Original WoS DataFrame
        scopus_cleaned: Scopus DataFrame after within-DB dedup
        wos_cleaned: WoS DataFrame after within-DB dedup
        canonical_df: Final canonical DataFrame
        collisions_df: Collisions DataFrame
        output_dir: Output directory path
    """
    logger.info("Generating deduplication audits")
    
    # Default values if not provided
    if within_source_doi_removed is None:
        within_source_doi_removed = {'scopus': 0, 'wos': 0}
    if within_source_title_year_removed is None:
        within_source_title_year_removed = {'scopus': 0, 'wos': 0}
    
    # Generate summary
    summary = generate_dedup_summary(
        scopus_original=len(scopus_original),
        wos_original=len(wos_original),
        scopus_after_within=len(scopus_cleaned),
        wos_after_within=len(wos_cleaned),
        canonical_count=len(canonical_df),
        collisions_count=len(collisions_df),
        file_paths=file_paths,
        within_source_doi_removed=within_source_doi_removed,
        within_source_title_year_removed=within_source_title_year_removed,
        cross_source_doi_removed=cross_source_doi_removed,
        cross_source_title_year_removed=cross_source_title_year_removed
    )
    
    # Generate mapping
    mapping_df = generate_dedup_mapping(
        scopus_original,
        wos_original,
        canonical_df
    )
    
    # Save all audits
    save_dedup_audits(summary, mapping_df, collisions_df, output_dir)
    
    logger.info("Deduplication audits complete")

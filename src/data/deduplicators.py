"""Deduplication modules for within-DB and cross-DB deduplication"""

import pandas as pd
import logging
from typing import Dict, Tuple, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


def deduplicate_within_db(df: pd.DataFrame, source_db: str) -> pd.DataFrame:
    """
    Deduplicate records within a single database.
    
    Canvas specification:
    Rule A: Group by doi_clean (non-null) → keep one canonical
    Rule B: For doi_clean null → group by (title_norm, year_clean) → keep one canonical
    
    Args:
        df: DataFrame with cleaned fields (doi_clean, title_norm, year_clean, metadata_completeness_score)
        source_db: Database name ('scopus' or 'wos')
        
    Returns:
        Deduplicated DataFrame
    """
    logger.info(f"Deduplicating {source_db} records (n={len(df)})")
    
    if len(df) == 0:
        return df
    
    df = df.copy()
    
    # Rule A: Deduplicate by DOI
    has_doi = df['doi_clean'].notna()
    df_with_doi = df[has_doi].copy()
    df_without_doi = df[~has_doi].copy()
    
    if len(df_with_doi) > 0:
        # Group by doi_clean and select best record from each group
        # Sort first, then take first from each group
        df_with_doi['has_references'] = df_with_doi['references_raw'].notna() & (
            df_with_doi['references_raw'].astype(str).str.strip() != ''
        )
        
        df_with_doi_sorted = df_with_doi.sort_values(
            by=['doi_clean', 'metadata_completeness_score', 'has_references', 'raw_record_id'],
            ascending=[True, False, False, True]
        )
        
        df_with_doi_dedup = df_with_doi_sorted.drop_duplicates(subset=['doi_clean'], keep='first').drop(columns=['has_references'])
    else:
        df_with_doi_dedup = pd.DataFrame()
    
    # Rule B: Deduplicate by title_norm + year_clean for records without DOI
    if len(df_without_doi) > 0:
        # Filter: must have both title_norm and year_clean
        has_secondary_key = (
            df_without_doi['title_norm'].notna() &
            (df_without_doi['title_norm'] != '') &
            df_without_doi['year_clean'].notna()
        )
        
        df_with_secondary = df_without_doi[has_secondary_key].copy()
        df_without_secondary = df_without_doi[~has_secondary_key].copy()
        
        if len(df_with_secondary) > 0:
            # Create composite key
            df_with_secondary['secondary_key'] = (
                df_with_secondary['title_norm'] + '|' + 
                df_with_secondary['year_clean'].astype(str)
            )
            
            # Sort and deduplicate by secondary key
            df_with_secondary['has_references'] = df_with_secondary['references_raw'].notna() & (
                df_with_secondary['references_raw'].astype(str).str.strip() != ''
            )
            
            df_with_secondary_sorted = df_with_secondary.sort_values(
                by=['secondary_key', 'metadata_completeness_score', 'has_references', 'raw_record_id'],
                ascending=[True, False, False, True]
            )
            
            df_with_secondary_dedup = df_with_secondary_sorted.drop_duplicates(subset=['secondary_key'], keep='first')
            # Drop temporary columns
            df_with_secondary_dedup = df_with_secondary_dedup.drop(columns=['secondary_key', 'has_references'], errors='ignore')
        else:
            df_with_secondary_dedup = pd.DataFrame()
        
        # Combine: deduplicated secondary-key records + records without secondary key
        df_without_doi_dedup = pd.concat(
            [df_with_secondary_dedup, df_without_secondary],
            ignore_index=True
        )
    else:
        df_without_doi_dedup = pd.DataFrame()
    
    # Final merge
    df_dedup = pd.concat([df_with_doi_dedup, df_without_doi_dedup], ignore_index=True)
    
    removed = len(df) - len(df_dedup)
    logger.info(f"Removed {removed} duplicate records from {source_db} (kept {len(df_dedup)})")
    
    return df_dedup


def deduplicate_cross_db(
    scopus_df: pd.DataFrame,
    wos_df: pd.DataFrame,
    preferred_db: str = 'scopus'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Merge and deduplicate across databases.
    
    Steps:
    1. Concatenate cleaned datasets
    2. Primary key dedup: group by doi_clean, keep best record
    3. Secondary key dedup: group by (title_norm, year_clean), keep best record
    4. Generate collision warnings for secondary-key matches
    
    Args:
        scopus_df: Cleaned Scopus DataFrame
        wos_df: Cleaned WoS DataFrame
        preferred_db: Preferred database for tie-breaking ('scopus' or 'wos')
        
    Returns:
        Tuple of (deduplicated DataFrame, collisions DataFrame)
    """
    logger.info("Merging and deduplicating across databases")
    
    # Step 1: Concatenate
    merged_df = pd.concat([scopus_df, wos_df], ignore_index=True)
    logger.info(f"Total records after merge: {len(merged_df)}")
    
    # Step 2: Primary key deduplication (by DOI)
    has_doi = merged_df['doi_clean'].notna()
    df_with_doi = merged_df[has_doi].copy()
    df_without_doi = merged_df[~has_doi].copy()
    
    collisions_primary = []
    
    if len(df_with_doi) > 0:
        # Group by doi_clean to detect collisions, then deduplicate
        doi_counts = df_with_doi.groupby('doi_clean').size()
        collision_dois = doi_counts[doi_counts > 1].index
        
        for doi_val in collision_dois:
            group = df_with_doi[df_with_doi['doi_clean'] == doi_val]
            collision_info = {
                'doi_clean': doi_val,
                'n_records': len(group),
                'sources': group['source_db'].tolist(),
                'record_ids': group['raw_record_id'].tolist(),
            }
            collisions_primary.append(collision_info)
        
        # Sort and deduplicate
        df_with_doi['has_references'] = df_with_doi['references_raw'].notna() & (
            df_with_doi['references_raw'].astype(str).str.strip() != ''
        )
        df_with_doi['is_preferred'] = (df_with_doi['source_db'] == preferred_db)
        
        df_with_doi_sorted = df_with_doi.sort_values(
            by=['doi_clean', 'metadata_completeness_score', 'has_references', 'is_preferred', 'raw_record_id'],
            ascending=[True, False, False, False, True]
        )
        
        df_with_doi_dedup = df_with_doi_sorted.drop_duplicates(subset=['doi_clean'], keep='first').drop(columns=['has_references', 'is_preferred'])
    else:
        df_with_doi_dedup = pd.DataFrame()
    
    # Step 3: Secondary key deduplication (by title_norm + year_clean)
    # Only for records without DOI
    collisions_secondary = []
    
    if len(df_without_doi) > 0:
        # Filter: must have both title_norm and year_clean
        has_secondary_key = (
            df_without_doi['title_norm'].notna() &
            (df_without_doi['title_norm'] != '') &
            df_without_doi['year_clean'].notna()
        )
        
        df_with_secondary = df_without_doi[has_secondary_key].copy()
        df_without_secondary = df_without_doi[~has_secondary_key].copy()
        
        if len(df_with_secondary) > 0:
            # Create composite key
            df_with_secondary['secondary_key'] = (
                df_with_secondary['title_norm'] + '|' + 
                df_with_secondary['year_clean'].astype(str)
            )
            
            # Group by secondary key to detect collisions
            sec_key_counts = df_with_secondary.groupby('secondary_key').size()
            collision_keys = sec_key_counts[sec_key_counts > 1].index
            
            for key_val in collision_keys:
                group = df_with_secondary[df_with_secondary['secondary_key'] == key_val]
                collision_info = {
                    'title_norm': group['title_norm'].iloc[0],
                    'year_clean': group['year_clean'].iloc[0],
                    'n_records': len(group),
                    'sources': group['source_db'].tolist(),
                    'record_ids': group['raw_record_id'].tolist(),
                    'titles': group['title_raw'].tolist(),
                }
                collisions_secondary.append(collision_info)
            
            # Sort and deduplicate
            df_with_secondary['has_references'] = df_with_secondary['references_raw'].notna() & (
                df_with_secondary['references_raw'].astype(str).str.strip() != ''
            )
            df_with_secondary['is_preferred'] = (df_with_secondary['source_db'] == preferred_db)
            
            df_with_secondary_sorted = df_with_secondary.sort_values(
                by=['secondary_key', 'metadata_completeness_score', 'has_references', 'is_preferred', 'raw_record_id'],
                ascending=[True, False, False, False, True]
            )
            
            df_with_secondary_dedup = df_with_secondary_sorted.drop_duplicates(subset=['secondary_key'], keep='first')
            # Drop temporary columns
            df_with_secondary_dedup = df_with_secondary_dedup.drop(columns=['secondary_key', 'has_references', 'is_preferred'], errors='ignore')
        else:
            df_with_secondary_dedup = pd.DataFrame()
        
        # Combine: deduplicated secondary-key records + records without secondary key
        df_without_doi_dedup = pd.concat(
            [df_with_secondary_dedup, df_without_secondary],
            ignore_index=True
        )
    else:
        df_without_doi_dedup = pd.DataFrame()
    
    # Final merge
    canonical_df = pd.concat([df_with_doi_dedup, df_without_doi_dedup], ignore_index=True)
    
    # Add source provenance flags (has_scopus, has_wos)
    canonical_df['has_scopus'] = canonical_df['source_db'] == 'scopus'
    canonical_df['has_wos'] = canonical_df['source_db'] == 'wos'
    
    # For records that came from cross-DB dedup, we need to check if they originated from both
    # This is simplified - in reality, we'd need to track which original records contributed
    # For now, we mark based on the kept record's source_db
    
    # Create collisions DataFrame
    collisions_df = pd.DataFrame(collisions_secondary) if collisions_secondary else pd.DataFrame()
    
    removed = len(merged_df) - len(canonical_df)
    logger.info(f"Removed {removed} duplicate records across databases (kept {len(canonical_df)})")
    logger.info(f"Found {len(collisions_secondary)} secondary-key collisions requiring review")
    
    return canonical_df, collisions_df


def deduplicate_full_pipeline(
    scopus_df: pd.DataFrame,
    wos_df: pd.DataFrame,
    preferred_db: str = 'scopus'
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Full deduplication pipeline: within-DB then cross-DB.
    
    Args:
        scopus_df: Cleaned Scopus DataFrame
        wos_df: Cleaned WoS DataFrame
        preferred_db: Preferred database for tie-breaking
        
    Returns:
        Tuple of (canonical DataFrame, collisions DataFrame)
    """
    logger.info("Starting full deduplication pipeline")
    
    # Step 1: Within-DB deduplication
    scopus_dedup = deduplicate_within_db(scopus_df, 'scopus')
    wos_dedup = deduplicate_within_db(wos_df, 'wos')
    
    # Step 2: Cross-DB deduplication
    canonical_df, collisions_df = deduplicate_cross_db(
        scopus_dedup,
        wos_dedup,
        preferred_db=preferred_db
    )
    
    # Add canonical ID
    canonical_df = canonical_df.reset_index(drop=True)
    canonical_df['canonical_id'] = 'FI_' + canonical_df.index.astype(str).str.zfill(6)
    
    logger.info(f"Canonical dataset: {len(canonical_df)} unique records")
    
    return canonical_df, collisions_df
